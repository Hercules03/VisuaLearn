"""Pydantic models for API requests and responses."""

from typing import Any, Literal

from pydantic import BaseModel, Field


class DiagramRequest(BaseModel):
    """Request model for diagram generation."""

    concept: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Core concept to explain with diagram",
    )

class PlanningData(BaseModel):
    """Planning output embedded in response."""

    concept: str = Field(..., description="Core concept being explained")
    diagram_type: str = Field(
        ..., description="Type of diagram (flowchart, mindmap, etc)"
    )
    components: list[str] = Field(..., description="Diagram elements")
    relationships: list[dict[str, Any]] = Field(
        ..., description="Relationships between components"
    )
    success_criteria: list[str] = Field(..., description="Validation criteria")
    key_insights: list[str] = Field(..., description="Important teaching points")


class StepTimes(BaseModel):
    """Timing information for each pipeline step."""

    planning: float = Field(..., description="Planning agent duration (seconds)")
    generation: float = Field(..., description="Diagram generation duration")
    review: float = Field(..., description="Review iteration duration")
    conversion: float = Field(..., description="Image conversion duration")
    storage: float = Field(..., description="File storage duration")


class DiagramMetadata(BaseModel):
    """Metadata about diagram generation."""

    step_times: StepTimes = Field(..., description="Timing for each step")
    refinement_attempts: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Refinement attempts made via MCP (iteration, score, feedback)",
    )
    concept: str = Field(..., description="Core concept")
    components_count: int = Field(..., description="Number of diagram components")
    relationships_count: int = Field(..., description="Number of relationships")


class DiagramResponse(BaseModel):
    """Response model for successful diagram generation.

    Diagram rendering architecture:
    - Backend: Generates draw.io XML, validates, and converts to SVG
    - Backend: SVG rendering via Playwright + mxGraph
    - Frontend: Renders SVG directly (no external dependencies)
    - Client: Native SVG viewing with zoom, pan, export via backend APIs

    This approach provides accurate rendering with no client-side complexity.
    """

    svg_filename: str = Field(..., description="Filename of generated SVG image for download")
    xml_filename: str = Field(..., description="Filename of generated XML for download/editing")
    diagram_svg: str = Field(
        ...,
        description="Generated SVG diagram for direct frontend rendering. "
        "Frontend renders via native <svg> or react-svg component.",
    )
    plan: PlanningData = Field(..., description="Planning analysis")
    review_score: int = Field(
        ..., ge=0, le=100, description="Final review score (0-100)"
    )
    iterations: int = Field(..., ge=1, le=3, description="Number of review iterations")
    total_time_seconds: float = Field(..., description="Total pipeline duration")
    metadata: DiagramMetadata = Field(..., description="Generation metadata")


class ErrorResponse(BaseModel):
    """Error response model."""

    error: str = Field(..., description="Error type")
    message: str = Field(..., description="User-friendly error message")
    details: str = Field(default="", description="Technical details for debugging")


class ProgressEvent(BaseModel):
    """Progress update event for streaming responses."""

    type: Literal["progress", "complete", "error"] = Field(
        ..., description="Event type"
    )
    stage: Literal[
        "planning", "generation", "review", "conversion", "storage"
    ] = Field(..., description="Current pipeline stage")
    status: str = Field(..., description="Human-readable status message")
    progress: float = Field(
        ...,
        ge=0,
        le=100,
        description="Progress percentage (0-100)",
    )
    elapsed_time: float = Field(
        default=0, description="Elapsed time for this stage in seconds"
    )
    error: str = Field(
        default="", description="Error message if type is 'error'"
    )
    data: Any = Field(
        default=None,
        description="Additional data (e.g., final result on completion)",
    )
