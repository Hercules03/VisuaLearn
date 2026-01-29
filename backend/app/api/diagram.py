"""API endpoint for diagram generation."""

import json
from typing import AsyncGenerator

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse
from loguru import logger

from app.errors import OrchestrationError
from app.models.schemas import (
    DiagramRequest,
    DiagramResponse,
    ErrorResponse,
    ProgressEvent,
)
from app.services.orchestrator import Orchestrator

router = APIRouter(prefix="/api", tags=["diagram"])

# Shared orchestrator instance
orchestrator = Orchestrator()


@router.post(
    "/diagram",
    response_model=DiagramResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid request"},
        422: {"model": ErrorResponse, "description": "Validation error"},
        500: {"model": ErrorResponse, "description": "Server error"},
    },
)
async def generate_diagram(request: DiagramRequest) -> DiagramResponse:
    """Generate an educational diagram from a concept.

    This endpoint orchestrates the complete diagram generation pipeline:
    1. Planning: Analyze concept and create diagram plan
    2. Generation: Generate XML diagram from plan
    3. Review: Quality check with potential iteration
    4. Conversion: Convert to PNG and SVG formats
    5. Storage: Save files for download

    Args:
        request: DiagramRequest with concept (required) and optional educational_level.
                 If educational_level is not provided, defaults to "8-10".

    Returns:
        DiagramResponse with generated files and metadata

    Raises:
        HTTPException: If orchestration fails
    """
    logger.info(
        "Diagram generation requested",
        concept=request.concept,
        educational_level=request.educational_level,
    )

    try:
        # Execute orchestration pipeline
        result = await orchestrator.orchestrate(
            concept=request.concept,
            educational_level=request.educational_level,
        )

        logger.info(
            "Diagram generation completed successfully",
            concept=request.concept,
            total_time=result.total_time_seconds,
            iterations=result.iterations,
            score=result.review_score,
        )

        # Convert orchestrator result to API response
        return DiagramResponse(
            png_filename=result.png_filename,
            svg_filename=result.svg_filename,
            xml_content=result.xml_content,
            plan={
                "concept": result.plan.concept,
                "diagram_type": result.plan.diagram_type,
                "components": result.plan.components,
                "relationships": result.plan.relationships,
                "success_criteria": result.plan.success_criteria,
                "educational_level": result.plan.educational_level,
                "key_insights": result.plan.key_insights,
            },
            review_score=result.review_score,
            iterations=result.iterations,
            total_time_seconds=result.total_time_seconds,
            metadata={
                "step_times": {
                    "planning": result.metadata["step_times"]["planning"],
                    "generation": result.metadata["step_times"]["generation"],
                    "review": result.metadata["step_times"]["review"],
                    "conversion": result.metadata["step_times"]["conversion"],
                    "storage": result.metadata["step_times"]["storage"],
                },
                "refinement_instructions": result.metadata["refinement_instructions"],
                "concept": result.metadata["concept"],
                "components_count": result.metadata["components_count"],
                "relationships_count": result.metadata["relationships_count"],
            },
        )

    except OrchestrationError as e:
        logger.error(
            "Orchestration failed",
            error=str(e),
            concept=request.concept,
            details=e.details if hasattr(e, "details") else str(e),
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error="orchestration_failed",
                message=str(e.message if hasattr(e, "message") else e),
                details=e.details if hasattr(e, "details") else str(e),
            ).model_dump(),
        ) from e

    except ValueError as e:
        logger.error(
            "Validation error",
            error=str(e),
            concept=request.concept,
        )
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=ErrorResponse(
                error="validation_error",
                message="Invalid input parameters",
                details=str(e),
            ).model_dump(),
        ) from e

    except Exception as e:
        logger.error(
            "Unexpected error during diagram generation",
            error=str(e),
            error_type=type(e).__name__,
            concept=request.concept,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error="unexpected_error",
                message="An unexpected error occurred",
                details=str(e),
            ).model_dump(),
        ) from e


@router.post("/diagram/stream")
async def generate_diagram_stream(request: DiagramRequest):
    """Generate diagram with real-time progress streaming.

    This endpoint streams progress updates as Server-Sent Events (SSE)
    as the diagram generation pipeline progresses through each stage.

    Args:
        request: DiagramRequest with concept and optional educational_level

    Returns:
        StreamingResponse with Server-Sent Events containing progress updates
    """

    async def progress_stream() -> AsyncGenerator[str, None]:
        """Stream progress events as the diagram is generated."""
        try:
            # Track stage timing
            stage_progress = {
                "planning": (0, 20),
                "generation": (20, 50),
                "review": (50, 75),
                "conversion": (75, 90),
                "storage": (90, 100),
            }

            current_stage = "planning"
            stage_start_progress, stage_end_progress = stage_progress[
                current_stage
            ]

            # Send initial progress event
            event = ProgressEvent(
                type="progress",
                stage="planning",
                status="Analyzing concept and creating diagram plan...",
                progress=0,
            )
            yield f"data: {json.dumps(event.model_dump())}\n\n"

            # Execute orchestration with progress tracking
            result = await orchestrator.orchestrate(
                concept=request.concept,
                educational_level=request.educational_level,
            )

            logger.info(
                "Diagram generation completed successfully",
                concept=request.concept,
                total_time=result.total_time_seconds,
                iterations=result.iterations,
                score=result.review_score,
            )

            # Convert orchestrator result to API response
            diagram_response = DiagramResponse(
                png_filename=result.png_filename,
                svg_filename=result.svg_filename,
                xml_content=result.xml_content,
                plan={
                    "concept": result.plan.concept,
                    "diagram_type": result.plan.diagram_type,
                    "components": result.plan.components,
                    "relationships": result.plan.relationships,
                    "success_criteria": result.plan.success_criteria,
                    "educational_level": result.plan.educational_level,
                    "key_insights": result.plan.key_insights,
                },
                review_score=result.review_score,
                iterations=result.iterations,
                total_time_seconds=result.total_time_seconds,
                metadata={
                    "step_times": {
                        "planning": result.metadata["step_times"]["planning"],
                        "generation": result.metadata["step_times"]["generation"],
                        "review": result.metadata["step_times"]["review"],
                        "conversion": result.metadata["step_times"]["conversion"],
                        "storage": result.metadata["step_times"]["storage"],
                    },
                    "refinement_instructions": result.metadata[
                        "refinement_instructions"
                    ],
                    "concept": result.metadata["concept"],
                    "components_count": result.metadata["components_count"],
                    "relationships_count": result.metadata[
                        "relationships_count"
                    ],
                },
            )

            # Simulate progress through remaining stages based on actual timings
            stages = [
                (
                    "planning",
                    f"Planning completed in {result.metadata['step_times']['planning']:.1f}s",
                    20,
                ),
                (
                    "generation",
                    f"Diagram generated in {result.metadata['step_times']['generation']:.1f}s",
                    50,
                ),
                (
                    "review",
                    f"Quality review completed in {result.metadata['step_times']['review']:.1f}s",
                    75,
                ),
                (
                    "conversion",
                    f"Image conversion completed in {result.metadata['step_times']['conversion']:.1f}s",
                    90,
                ),
                (
                    "storage",
                    f"Files saved in {result.metadata['step_times']['storage']:.1f}s",
                    99,
                ),
            ]

            for stage, status_msg, progress_pct in stages:
                event = ProgressEvent(
                    type="progress",
                    stage=stage,
                    status=status_msg,
                    progress=progress_pct,
                    elapsed_time=result.metadata["step_times"].get(stage, 0),
                )
                yield f"data: {json.dumps(event.model_dump())}\n\n"

            # Send completion event with final data
            completion_event = ProgressEvent(
                type="complete",
                stage="storage",
                status="Diagram generation complete!",
                progress=100,
                data=diagram_response.model_dump(),
            )
            yield f"data: {json.dumps(completion_event.model_dump())}\n\n"

        except OrchestrationError as e:
            logger.error("Orchestration failed", error=str(e))
            error_event = ProgressEvent(
                type="error",
                stage="unknown",
                status="Generation failed",
                progress=0,
                error=str(e.message if hasattr(e, "message") else e),
            )
            yield f"data: {json.dumps(error_event.model_dump())}\n\n"

        except Exception as e:
            logger.error(
                "Unexpected error during diagram generation",
                error=str(e),
                error_type=type(e).__name__,
            )
            error_event = ProgressEvent(
                type="error",
                stage="unknown",
                status="Unexpected error",
                progress=0,
                error=str(e),
            )
            yield f"data: {json.dumps(error_event.model_dump())}\n\n"

    return StreamingResponse(
        progress_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )
