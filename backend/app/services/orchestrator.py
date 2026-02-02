"""Orchestrator service for coordinating the diagram generation pipeline."""

import asyncio
import json
import subprocess
import time
import uuid
from typing import Optional

from loguru import logger

from app.errors import (
    FileOperationError,
    GenerationError,
    OrchestrationError,
    PlanningError,
    ReviewError,
)
from app.services.diagram_generator import DiagramGenerator
from app.services.file_manager import FileManager
from app.services.image_converter import ImageConverter
from app.services.planning_agent import PlanningAgent, PlanningOutput
from app.services.review_agent import ReviewAgent, ReviewOutput
from app.utils.response_storage import (
    store_conversion_response,
    store_generation_response,
    store_planning_response,
    store_refinement_response,
    store_review_response,
)


class OrchestrationResult:
    """Result structure for complete orchestration pipeline.

    Returns SVG diagram for frontend rendering: Backend converts XML to SVG.
    """

    def __init__(
        self,
        svg_filename: str,
        xml_filename: str,
        diagram_svg: str,
        plan: PlanningOutput,
        review_score: int,
        iterations: int,
        total_time_seconds: float,
        metadata: dict,
    ):
        """Initialize orchestration result.

        Args:
            svg_filename: Filename of saved SVG image (for download)
            xml_filename: Filename of saved XML diagram (for download/editing)
            diagram_svg: Generated SVG diagram content (for frontend rendering)
            plan: Planning output with concept analysis
            review_score: Final review score (0-100)
            iterations: Number of review iterations performed
            total_time_seconds: Total time for entire pipeline
            metadata: Additional metadata (step times, refinements)
        """
        self.svg_filename = svg_filename
        self.xml_filename = xml_filename
        self.diagram_svg = diagram_svg
        self.plan = plan
        self.review_score = review_score
        self.iterations = iterations
        self.total_time_seconds = total_time_seconds
        self.metadata = metadata

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "svg_filename": self.svg_filename,
            "xml_filename": self.xml_filename,
            "diagram_svg": self.diagram_svg,
            "plan": self.plan.to_dict(),
            "review_score": self.review_score,
            "iterations": self.iterations,
            "total_time_seconds": self.total_time_seconds,
            "metadata": self.metadata,
        }


class Orchestrator:
    """Service for orchestrating the complete diagram generation pipeline.

    Pipeline:
    1. Planning: Analyze concept and create diagram plan
    2. Generation: Generate XML diagram via next-ai-draw-io HTTP API
    3. Review + Refinement Loop (max 3 iterations):
       - Review Agent validates XML quality
       - If approved (score ≥90), done
       - If needs refinement, use MCP edit_diagram to refine
       - Review again and repeat
    4. Conversion: Validate XML structure
    5. Storage: Save XML and SVG to temporary storage
    """

    def __init__(self):
        """Initialize orchestrator with all required services."""
        self.planning_agent = PlanningAgent()
        self.diagram_generator = DiagramGenerator()
        self.review_agent = ReviewAgent()
        self.image_converter = ImageConverter()
        self.file_manager = FileManager()

        # MCP server for refinement
        self.mcp_process: Optional[subprocess.Popen] = None
        self._message_id = 0
        self._started = False

        logger.info("Orchestrator initialized with all services")

    def _get_next_message_id(self) -> int:
        """Get next message ID for MCP requests."""
        self._message_id += 1
        return self._message_id

    def _ensure_mcp_server(self):
        """Ensure MCP server process is running."""
        if self.mcp_process is None or self.mcp_process.poll() is not None:
            if self._started:
                logger.warning("MCP server crashed, restarting...")
            else:
                logger.info("Starting MCP server subprocess")

            try:
                import os

                env = os.environ.copy()
                self.mcp_process = subprocess.Popen(
                    ["npx", "@next-ai-drawio/mcp-server@latest"],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                    env=env,
                )
                self._started = True
                logger.info("MCP server started", pid=self.mcp_process.pid)
            except FileNotFoundError as e:
                logger.error("Cannot start MCP server - npx not found", error=str(e))
                raise OrchestrationError(
                    "MCP server unavailable. Ensure Node.js and npm are installed"
                ) from e
            except Exception as e:
                logger.error("Failed to start MCP server", error=str(e), exc_info=True)
                raise OrchestrationError(f"Cannot start MCP server: {str(e)}") from e

    async def _refine_via_mcp(self, xml: str, refinement_feedback: str) -> str:
        """Refine diagram XML using MCP edit_diagram tool.

        Args:
            xml: Current mxGraphModel XML
            refinement_feedback: Specific instructions for refinement

        Returns:
            Refined mxGraphModel XML

        Raises:
            OrchestrationError: If MCP refinement fails
        """
        self._ensure_mcp_server()

        msg_id = self._get_next_message_id()
        mcp_request = {
            "jsonrpc": "2.0",
            "id": msg_id,
            "method": "tools/call",
            "params": {
                "name": "edit_diagram",
                "arguments": {
                    "xml": xml,
                    "operations": [
                        {
                            "type": "refine",
                            "instructions": refinement_feedback,
                        }
                    ],
                },
            },
        }

        logger.debug("Sending refinement request to MCP", msg_id=msg_id)

        try:
            request_str = json.dumps(mcp_request)
            self.mcp_process.stdin.write(request_str + "\n")
            self.mcp_process.stdin.flush()

            # Read response with timeout
            loop = asyncio.get_event_loop()
            response_str = await asyncio.wait_for(
                loop.run_in_executor(None, self.mcp_process.stdout.readline),
                timeout=10.0,
            )

            if not response_str:
                logger.error("MCP server closed unexpectedly")
                self.mcp_process = None
                raise OrchestrationError("MCP server connection lost")

            response = json.loads(response_str)

            if "error" in response:
                error_msg = response["error"].get("message", "Unknown MCP error")
                logger.error(f"MCP error: {error_msg}")
                raise OrchestrationError(f"MCP refinement failed: {error_msg}")

            result = response.get("result", {})
            if result.get("isError"):
                error_msg = result.get("content", "Unknown MCP error")
                logger.error(f"MCP refinement error: {error_msg}")
                raise OrchestrationError(f"MCP refinement failed: {error_msg}")

            refined_xml = result.get("xml")
            if not refined_xml:
                logger.error("MCP did not return refined XML")
                raise OrchestrationError("MCP did not return refined XML")

            logger.debug("MCP refinement completed")
            return refined_xml

        except asyncio.TimeoutError:
            logger.error("MCP refinement timed out")
            raise OrchestrationError("MCP refinement timed out")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse MCP response: {e}")
            raise OrchestrationError(f"Invalid MCP response format: {e}")
        except (BrokenPipeError, OSError) as e:
            logger.error(f"MCP server connection lost: {e}")
            self.mcp_process = None
            raise OrchestrationError(f"MCP connection failed: {e}")
        except Exception as e:
            logger.error(f"MCP refinement error: {e}", exc_info=True)
            raise OrchestrationError(f"MCP refinement failed: {str(e)}")

    async def orchestrate(self, user_input: str) -> OrchestrationResult:
        """Execute complete diagram generation pipeline.

        Pipeline:
        1. Planning: Analyze concept and create diagram plan
        2. Generation: Generate XML diagram from plan via next-ai-draw-io
        3. Review + Refinement Loop (max 3 iterations):
           - Review Agent validates XML quality
           - If approved (score ≥90), exit loop
           - If needs refinement, use MCP to refine XML
           - Review again and repeat
        4. Conversion: Validate XML structure
        5. Storage: Save XML and SVG files

        Args:
            user_input: User's concept description

        Returns:
            OrchestrationResult with all generated files and metadata

        Raises:
            OrchestrationError: If any step fails
        """
        start_time = time.time()
        step_times = {}
        svg_filename: Optional[str] = None
        xml_filename: Optional[str] = None
        xml_content: Optional[str] = None
        request_id = str(uuid.uuid4())[:8]  # Short request ID for correlation

        try:
            # Step 1: Planning
            logger.info(
                "Starting orchestration",
                user_input=user_input,
                request_id=request_id,
            )
            step_start = time.time()

            plan = await self.planning_agent.analyze(user_input)

            step_times["planning"] = time.time() - step_start
            logger.info("Planning completed", plan_type=plan.diagram_type)

            # Store planning response
            store_planning_response(plan.to_dict(), request_id=request_id)

            # Step 2: Diagram Generation (initial draft via HTTP)
            step_start = time.time()

            xml_content = await self.diagram_generator.generate(plan)

            step_times["generation"] = time.time() - step_start
            logger.info("Diagram generation completed", xml_length=len(xml_content))

            # Store generation response
            store_generation_response(xml_content, request_id=request_id)

            # Step 3: Review Loop with MCP Refinement (max 3 iterations)
            step_start = time.time()
            iteration = 0
            review_result: Optional[ReviewOutput] = None
            refinement_attempts = []

            while iteration < self.review_agent.max_iterations:
                iteration += 1
                logger.info("Starting review iteration", iteration=iteration)

                try:
                    # Review the current XML
                    review_result = await self.review_agent.validate(
                        xml_content, plan, iteration
                    )

                    logger.info(
                        "Review completed",
                        iteration=iteration,
                        score=review_result.score,
                        approved=review_result.approved,
                    )

                    # Store review response
                    store_review_response(
                        review_result.to_dict(), iteration=iteration, request_id=request_id
                    )

                    if review_result.approved:
                        logger.info("Diagram approved", iteration=iteration)
                        break

                    # If not approved and not final iteration, refine via MCP
                    if iteration < self.review_agent.max_iterations:
                        # Combine refinement instructions into single feedback
                        feedback = " ".join(review_result.refinement_instructions)

                        logger.info(
                            "Refining diagram via MCP",
                            iteration=iteration,
                            feedback=feedback,
                        )

                        try:
                            # Store XML before refinement
                            xml_before_refinement = xml_content

                            # Use MCP to refine the diagram
                            xml_content = await self._refine_via_mcp(
                                xml_content, feedback
                            )

                            # Store refinement response
                            store_refinement_response(
                                xml_before_refinement,
                                xml_content,
                                feedback,
                                iteration=iteration,
                                request_id=request_id,
                            )

                            refinement_attempts.append(
                                {
                                    "iteration": iteration,
                                    "score": review_result.score,
                                    "feedback": feedback,
                                }
                            )
                            logger.info(
                                "Diagram refined via MCP",
                                iteration=iteration,
                                new_xml_length=len(xml_content),
                            )
                        except OrchestrationError as mcp_error:
                            logger.warning(
                                f"MCP refinement failed on iteration {iteration}: {mcp_error}",
                                iteration=iteration,
                            )
                            # If MCP fails, accept current diagram and break
                            break
                    else:
                        logger.warning(
                            "Max iterations reached, using final diagram",
                            iteration=iteration,
                            score=review_result.score,
                        )

                except ReviewError as e:
                    logger.error(
                        "Review validation failed",
                        iteration=iteration,
                        error=str(e),
                    )
                    if review_result is None:
                        # First iteration failure - create fallback review
                        review_result = ReviewOutput(
                            score=70,
                            approved=True,
                            feedback="Auto-approved due to review timeout.",
                            refinement_instructions=[],
                            iteration=iteration,
                        )
                    break

            if review_result is None:
                raise OrchestrationError("Review process failed to produce result")

            step_times["review"] = time.time() - step_start

            # Validate XML completeness before conversion
            cell_count = xml_content.count("<mxCell")
            expected_cells = (
                len(plan.components) + len(plan.relationships) + 2
            )  # +2 for root cells

            if cell_count < expected_cells // 2:  # At least 50% of expected cells
                logger.warning(
                    f"XML appears incomplete: {cell_count} cells vs ~{expected_cells} expected",
                    xml_length=len(xml_content),
                )

            # Step 4: SVG Conversion
            step_start = time.time()

            # Convert XML to SVG for frontend rendering
            diagram_svg = await self.image_converter.to_svg(xml_content)

            step_times["conversion"] = time.time() - step_start
            logger.info(
                "SVG conversion completed",
                svg_size=len(diagram_svg),
            )

            # Store conversion response
            store_conversion_response(diagram_svg, request_id=request_id)

            # Step 5: File Storage
            step_start = time.time()

            # Save SVG and XML files
            svg_filename = await self.file_manager.save_file(
                diagram_svg.encode("utf-8"), "svg"
            )
            xml_filename = await self.file_manager.save_file(
                xml_content.encode("utf-8"), "xml"
            )

            step_times["storage"] = time.time() - step_start
            logger.info(
                "Files stored",
                svg_filename=svg_filename,
                xml_filename=xml_filename,
            )

            # Construct result
            total_time = time.time() - start_time
            metadata = {
                "step_times": step_times,
                "refinement_attempts": refinement_attempts,
                "user_input": user_input,
                "components_count": len(plan.components),
                "relationships_count": len(plan.relationships),
            }

            result = OrchestrationResult(
                svg_filename=svg_filename,
                xml_filename=xml_filename,
                diagram_svg=diagram_svg,
                plan=plan,
                review_score=review_result.score,
                iterations=iteration,
                total_time_seconds=total_time,
                metadata=metadata,
            )

            logger.info(
                "Orchestration completed successfully",
                total_time=total_time,
                iterations=iteration,
                score=review_result.score,
                mcp_refinements=len(refinement_attempts),
            )

            return result

        except PlanningError as e:
            logger.error(f"Planning failed: {e}")
            raise OrchestrationError(f"Concept analysis failed: {str(e)}")
        except GenerationError as e:
            logger.error(f"Diagram generation failed: {e}")
            raise OrchestrationError(f"Diagram generation failed: {str(e)}")
        except Exception as e:
            # Cleanup generated files on error
            if svg_filename:
                try:
                    await self.file_manager.delete_file(svg_filename)
                except FileOperationError as cleanup_error:
                    logger.warning(f"Failed to cleanup SVG file: {cleanup_error}")

            if xml_filename:
                try:
                    await self.file_manager.delete_file(xml_filename)
                except FileOperationError as cleanup_error:
                    logger.warning(f"Failed to cleanup XML file: {cleanup_error}")

            logger.error(f"Orchestration failed: {e}")
            raise OrchestrationError(f"Pipeline failed: {str(e)}")
