"""Orchestrator service for coordinating the diagram generation pipeline."""

import asyncio
import time
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


class OrchestrationResult:
    """Result structure for complete orchestration pipeline."""

    def __init__(
        self,
        png_filename: str,
        svg_filename: str,
        xml_content: str,
        plan: PlanningOutput,
        review_score: int,
        iterations: int,
        total_time_seconds: float,
        metadata: dict,
    ):
        """Initialize orchestration result.

        Args:
            png_filename: Filename of saved PNG image
            svg_filename: Filename of saved SVG image
            xml_content: Raw XML diagram content
            plan: Planning output with concept analysis
            review_score: Final review score (0-100)
            iterations: Number of review iterations performed
            total_time_seconds: Total time for entire pipeline
            metadata: Additional metadata (step times, refinements)
        """
        self.png_filename = png_filename
        self.svg_filename = svg_filename
        self.xml_content = xml_content
        self.plan = plan
        self.review_score = review_score
        self.iterations = iterations
        self.total_time_seconds = total_time_seconds
        self.metadata = metadata

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "png_filename": self.png_filename,
            "svg_filename": self.svg_filename,
            "xml_content": self.xml_content,
            "plan": self.plan.to_dict(),
            "review_score": self.review_score,
            "iterations": self.iterations,
            "total_time_seconds": self.total_time_seconds,
            "metadata": self.metadata,
        }


class Orchestrator:
    """Service for orchestrating the complete diagram generation pipeline."""

    def __init__(self):
        """Initialize orchestrator with all required services."""
        self.planning_agent = PlanningAgent()
        self.diagram_generator = DiagramGenerator()
        self.review_agent = ReviewAgent()
        self.image_converter = ImageConverter()
        self.file_manager = FileManager()

        logger.info("Orchestrator initialized with all services")

    async def orchestrate(
        self, concept: str, educational_level: str
    ) -> OrchestrationResult:
        """Execute complete diagram generation pipeline.

        Pipeline:
        1. Planning: Analyze concept and create diagram plan
        2. Generation: Generate XML diagram from plan
        3. Review: Review quality (iterate up to 3 times if needed)
        4. Conversion: Convert XML to PNG and SVG images
        5. Storage: Save files to temporary storage

        Args:
            concept: Core concept to explain with diagram
            educational_level: Target age group (e.g., "8-10", "11-13", "14-15")

        Returns:
            OrchestrationResult with all generated files and metadata

        Raises:
            OrchestrationError: If any step fails or max iterations exceeded
        """
        start_time = time.time()
        step_times = {}
        png_filename: Optional[str] = None
        svg_filename: Optional[str] = None

        try:
            # Step 1: Planning
            logger.info(
                "Starting orchestration",
                concept=concept,
                educational_level=educational_level,
            )
            step_start = time.time()

            plan = await self.planning_agent.analyze(concept)

            step_times["planning"] = time.time() - step_start
            logger.info("Planning completed", plan_type=plan.diagram_type)

            # Step 2: Diagram Generation
            step_start = time.time()

            xml_content = await self.diagram_generator.generate(plan)

            step_times["generation"] = time.time() - step_start
            logger.info("Diagram generation completed", xml_length=len(xml_content))

            # Step 3: Review Loop (max 3 iterations)
            step_start = time.time()
            iteration = 0
            review_result: Optional[ReviewOutput] = None
            refinement_instructions: list[str] = []

            while iteration < self.review_agent.max_iterations:
                iteration += 1
                logger.info("Starting review iteration", iteration=iteration)

                review_result = await self.review_agent.validate(
                    xml_content, plan, iteration
                )

                logger.info(
                    "Review completed",
                    iteration=iteration,
                    score=review_result.score,
                    approved=review_result.approved,
                )

                if review_result.approved:
                    logger.info("Diagram approved", iteration=iteration)
                    break

                # If not approved and not final iteration, collect refinements
                if iteration < self.review_agent.max_iterations:
                    refinement_instructions.extend(
                        review_result.refinement_instructions
                    )
                    logger.info(
                        "Refinement needed",
                        iteration=iteration,
                        feedback=review_result.feedback,
                    )
                else:
                    logger.warning(
                        "Max iterations reached, using final diagram",
                        iteration=iteration,
                        score=review_result.score,
                    )

            if review_result is None:
                raise OrchestrationError("Review process failed to produce result")

            step_times["review"] = time.time() - step_start

            # Step 4: Image Conversion (parallel)
            step_start = time.time()

            png_bytes, svg_str = await asyncio.gather(
                self.image_converter.to_png(xml_content),
                self.image_converter.to_svg(xml_content),
            )

            step_times["conversion"] = time.time() - step_start
            logger.info(
                "Image conversion completed",
                png_size=len(png_bytes),
                svg_size=len(svg_str),
            )

            # Step 5: File Storage
            step_start = time.time()

            png_filename, svg_filename = await asyncio.gather(
                self.file_manager.save_file(png_bytes, "png"),
                self.file_manager.save_file(svg_str.encode("utf-8"), "svg"),
            )

            step_times["storage"] = time.time() - step_start
            logger.info(
                "Files stored",
                png_filename=png_filename,
                svg_filename=svg_filename,
            )

            # Construct result
            total_time = time.time() - start_time
            metadata = {
                "step_times": step_times,
                "refinement_instructions": refinement_instructions,
                "concept": concept,
                "components_count": len(plan.components),
                "relationships_count": len(plan.relationships),
            }

            result = OrchestrationResult(
                png_filename=png_filename,
                svg_filename=svg_filename,
                xml_content=xml_content,
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
            )

            return result

        except PlanningError as e:
            logger.error(f"Planning failed: {e}")
            raise OrchestrationError(f"Concept analysis failed: {str(e)}")
        except GenerationError as e:
            logger.error(f"Diagram generation failed: {e}")
            raise OrchestrationError(f"Diagram generation failed: {str(e)}")
        except ReviewError as e:
            logger.error(f"Review validation failed: {e}")
            raise OrchestrationError(f"Quality review failed: {str(e)}")
        except Exception as e:
            # Cleanup generated files on error
            if png_filename:
                try:
                    await self.file_manager.delete_file(png_filename)
                except FileOperationError as cleanup_error:
                    logger.warning(f"Failed to cleanup PNG file: {cleanup_error}")

            if svg_filename:
                try:
                    await self.file_manager.delete_file(svg_filename)
                except FileOperationError as cleanup_error:
                    logger.warning(f"Failed to cleanup SVG file: {cleanup_error}")

            logger.error(f"Orchestration failed: {e}")
            raise OrchestrationError(f"Pipeline failed: {str(e)}")
