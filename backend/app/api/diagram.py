"""API endpoint for diagram generation."""

from fastapi import APIRouter, HTTPException, status
from loguru import logger

from app.errors import OrchestrationError
from app.models.schemas import DiagramRequest, DiagramResponse, ErrorResponse
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
        request: DiagramRequest with concept and educational_level

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
