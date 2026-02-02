"""Review Agent service for diagram quality assessment and refinement."""

import asyncio
import json
from concurrent.futures import ThreadPoolExecutor

from loguru import logger

from app.config import settings
from app.errors import ReviewError
from app.services.planning_agent import PlanningOutput


class ReviewOutput:
    """Output structure for review agent."""

    def __init__(
        self,
        score: int,
        approved: bool,
        feedback: str,
        refinement_instructions: list[str],
        iteration: int,
    ):
        """Initialize review output.

        Args:
            score: Quality score 0-100
            approved: Whether diagram is approved
            feedback: Human-readable feedback
            refinement_instructions: List of specific improvements needed
            iteration: Which iteration this review is
        """
        self.score = score
        self.approved = approved
        self.feedback = feedback
        self.refinement_instructions = refinement_instructions
        self.iteration = iteration

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "score": self.score,
            "approved": self.approved,
            "feedback": self.feedback,
            "refinement_instructions": self.refinement_instructions,
            "iteration": self.iteration,
        }


class ReviewAgent:
    """AI agent for reviewing and scoring diagrams."""

    def __init__(self):
        """Initialize review agent with Gemini client."""
        self.timeout = settings.review_timeout
        self.gemini_api_key = settings.google_api_key
        self.max_iterations = settings.review_max_iterations
        self.executor = ThreadPoolExecutor(max_workers=1)

        # Initialize Gemini client
        try:
            import google.generativeai as genai

            genai.configure(api_key=self.gemini_api_key)
            self.client = genai.GenerativeModel("gemini-2.5-flash")
            logger.info("Review agent initialized with Gemini 2.5 Flash")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {e}")
            raise ReviewError(f"Failed to initialize LLM: {e}")

    async def validate(
        self, xml: str, plan: PlanningOutput, iteration: int = 1
    ) -> ReviewOutput:
        """Validate diagram quality and provide feedback.

        Assesses the generated diagram XML against the planning output
        using a quality scoring system:
        - Score ≥90: Auto-approve
        - Score 70-89: Request refinement
        - Score <70 on iteration 3: Accept anyway

        Args:
            xml: draw.io XML diagram content
            plan: Original planning output specification
            iteration: Current iteration number (1-3)

        Returns:
            ReviewOutput with score and feedback

        Raises:
            ReviewError: If validation fails or timeout occurs
        """
        # Validate inputs
        if not xml or not xml.strip():
            raise ReviewError("Diagram XML cannot be empty")

        if iteration < 1 or iteration > self.max_iterations:
            raise ReviewError(f"Invalid iteration {iteration}")

        logger.info(
            "Review validation started",
            iteration=iteration,
            plan_concept=plan.concept,
        )

        try:
            # Run validation with timeout
            result = await asyncio.wait_for(
                self._validate_internal(xml, plan, iteration),
                timeout=self.timeout,
            )
            logger.info(
                "Review validation completed",
                score=result.score,
                approved=result.approved,
                iteration=iteration,
            )
            return result
        except asyncio.TimeoutError:
            logger.error(f"Review timed out after {self.timeout}s")
            raise ReviewError(
                f"Review timed out after {self.timeout}s. Using fallback score."
            )
        except ReviewError:
            # Re-raise ReviewErrors as-is
            raise
        except Exception as e:
            logger.error(f"Review validation failed: {e}")
            raise ReviewError(f"Failed to review diagram: {str(e)}")

    async def _validate_internal(
        self, xml: str, plan: PlanningOutput, iteration: int
    ) -> ReviewOutput:
        """Internal validation implementation using Gemini.

        Args:
            xml: draw.io XML diagram content
            plan: Original planning output specification
            iteration: Current iteration number

        Returns:
            ReviewOutput with score and feedback

        Raises:
            ReviewError: If validation or JSON parsing fails
        """
        # Create review prompt with full XML for accurate assessment
        prompt = f"""Review this diagram XML against the requirements.

Concept: {plan.concept}
Diagram Type: {plan.diagram_type}

Required Components ({len(plan.components)} total):
{', '.join(plan.components)}

Required Relationships ({len(plan.relationships)} total):
{', '.join([f"{r['from']} → {r['to']}" for r in plan.relationships[:5]])}{'...' if len(plan.relationships) > 5 else ''}

Diagram XML:
{xml}

Task: Score the diagram 0-100 on:
- Completeness: Do ALL required components appear in the diagram?
- Accuracy: Do the components and relationships correctly represent the concept?
- Clarity: Are labels clear and readable? Is the layout organized?

For iteration {iteration}/3: approve if score ≥80 (iterations 1+), or ≥60 (iteration 2+), or any score (iteration 3).

Respond with ONLY JSON (no markdown, no code blocks):
{{
    "score": <0-100 number>,
    "feedback": "brief one-sentence assessment",
    "refinement_instructions": [],
    "approved": <true or false>
}}"""

        try:
            # Call Gemini API in thread pool (blocking call) with timeout
            loop = asyncio.get_event_loop()
            response = await asyncio.wait_for(
                loop.run_in_executor(
                    self.executor,
                    self.client.generate_content,
                    prompt
                ),
                timeout=self.timeout
            )
            response_text = response.text

            logger.debug(f"Gemini review response: {response_text[:200]}...")

            # Parse JSON from response
            json_data = self._parse_json_response(response_text)

            # Validate required fields
            required_fields = ["score", "feedback", "refinement_instructions"]
            missing_fields = [f for f in required_fields if f not in json_data]
            if missing_fields:
                raise ReviewError(
                    f"Missing required fields in response: {', '.join(missing_fields)}"
                )

            # Validate score range
            score = int(json_data["score"])
            if score < 0 or score > 100:
                raise ReviewError(f"Invalid score: {score}. Must be 0-100.")

            # Determine approval based on score and iteration
            approved = self._determine_approval(score, iteration)

            # Create ReviewOutput
            return ReviewOutput(
                score=score,
                approved=approved,
                feedback=str(json_data["feedback"]),
                refinement_instructions=list(
                    json_data.get("refinement_instructions", [])
                ),
                iteration=iteration,
            )

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            raise ReviewError(f"Invalid JSON response from review: {e}")
        except ReviewError:
            raise
        except (KeyError, ValueError) as e:
            logger.error(f"Invalid field in parsed response: {e}")
            raise ReviewError(f"Invalid field in review response: {e}")

    def _determine_approval(self, score: int, iteration: int) -> bool:
        """Determine if diagram should be approved.

        Logic:
        - Score ≥80: Always approve (good quality)
        - Score 60-79: Approve on iteration 2+ (acceptable quality)
        - Score <60: Approve on iteration 3 (final fallback)

        Args:
            score: Quality score 0-100
            iteration: Current iteration number (1-3)

        Returns:
            True if approved, False if needs refinement
        """
        if score >= 80:
            return True  # Good quality
        elif score >= 60:
            return iteration >= 2  # Acceptable - approve on iteration 2+
        else:
            # Accept anyway if we're on the last iteration
            return iteration >= self.max_iterations

    def _parse_json_response(self, response_text: str) -> dict:
        """Parse JSON from Gemini response.

        Handles cases where response might have markdown code blocks,
        extra whitespace, or malformed escape sequences.

        Args:
            response_text: Raw response text from Gemini

        Returns:
            Parsed JSON dictionary

        Raises:
            json.JSONDecodeError: If JSON parsing fails
            ReviewError: If response format is invalid
        """
        text = response_text.strip()

        # Remove markdown code blocks if present
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()

        # Parse JSON with error recovery
        try:
            data = json.loads(text)
            return data
        except json.JSONDecodeError as e:
            logger.debug(f"Initial JSON parsing failed: {e}, attempting recovery")

            # Try to fix common JSON issues
            # 1. Fix unescaped backslashes in strings (e.g., \... instead of \\...)
            text_fixed = text
            try:
                # Find strings and escape unescaped backslashes
                import re
                # This regex finds strings and we'll fix backslashes within them
                def fix_backslashes(match):
                    string_content = match.group(1)
                    # Only fix backslashes that are not part of valid escapes
                    # Replace \ followed by non-valid-escape characters with \\
                    fixed = re.sub(r'\\([^"\\/bfnrtu])', r'\\\\\1', string_content)
                    return f'"{fixed}"'

                text_fixed = re.sub(r'"((?:[^"\\]|\\.)*)"', fix_backslashes, text)
                logger.debug("Applied backslash fix")
            except Exception as e:
                logger.debug(f"Backslash fix failed: {e}")

            # Try parsing again
            try:
                data = json.loads(text_fixed)
                logger.debug("JSON parsing succeeded after recovery")
                return data
            except json.JSONDecodeError as e2:
                logger.error(f"JSON parsing failed even after recovery: {e2}")
                logger.error(f"Response preview: {text[:500]}")
                raise ReviewError(
                    f"Failed to parse review response: {str(e2)}"
                )
