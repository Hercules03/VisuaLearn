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
    educational_level: str = Field(
        default="8-10",
        pattern="^(8-10|11-13|14-15)$",
        description="Target age group (8-10, 11-13, or 14-15). Defaults to 8-10 if not provided.",
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
    educational_level: str = Field(..., description="Target age group")
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
    refinement_instructions: list[str] = Field(
        ..., description="Refinements applied during review"
    )
    concept: str = Field(..., description="Core concept")
    components_count: int = Field(..., description="Number of diagram components")
    relationships_count: int = Field(..., description="Number of relationships")


class DiagramResponse(BaseModel):
    """Response model for successful diagram generation."""

    svg_filename: str = Field(..., description="Filename of generated SVG image for download")
    xml_filename: str = Field(..., description="Filename of generated XML for download/editing")
    svg_content: str = Field(..., description="SVG diagram content for inline display")
    xml_content: str = Field(..., description="Raw draw.io XML diagram")
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
