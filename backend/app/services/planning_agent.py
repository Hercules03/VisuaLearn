"""Planning Agent service for concept analysis and diagram planning."""

import asyncio
import json
from concurrent.futures import ThreadPoolExecutor

from loguru import logger

from app.config import settings
from app.errors import PlanningError


class PlanningOutput:
    """Output structure for planning agent."""

    def __init__(
        self,
        concept: str,
        diagram_type: str,
        components: list[str],
        relationships: list[dict],
        success_criteria: list[str],
        key_insights: list[str],
    ):
        """Initialize planning output.

        Args:
            concept: Core concept being explained
            diagram_type: Type of diagram (flowchart, mindmap, sequence, hierarchy)
            components: List of diagram elements
            relationships: List of relationships between components
            success_criteria: Measurable criteria for validation
            key_insights: Important teaching points
        """
        self.concept = concept
        self.diagram_type = diagram_type
        self.components = components
        self.relationships = relationships
        self.success_criteria = success_criteria
        self.key_insights = key_insights

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "concept": self.concept,
            "diagram_type": self.diagram_type,
            "components": self.components,
            "relationships": self.relationships,
            "success_criteria": self.success_criteria,
            "key_insights": self.key_insights,
        }


class PlanningAgent:
    """AI agent for analyzing concepts and creating diagram plans."""

    def __init__(self):
        """Initialize planning agent with Gemini client."""
        self.timeout = settings.planning_timeout
        self.gemini_api_key = settings.google_api_key
        self.executor = ThreadPoolExecutor(max_workers=1)
        self.model = settings.model

        # Initialize Gemini client
        try:
            import google.generativeai as genai

            genai.configure(api_key=self.gemini_api_key)
            self.client = genai.GenerativeModel(self.model)
            logger.info(f"Planning agent initialized with {self.model}")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {e}")
            raise PlanningError(f"Failed to initialize LLM: {e}")

    async def analyze(self, user_input: str) -> PlanningOutput:
        """Analyze user input and create diagram plan.

        Analyzes the user's question/topic and generates specifications for
        creating an educational diagram including:
        - Concept identification
        - Diagram type selection
        - Component identification
        - Relationship mapping
        - Success criteria for validation
        - Educational level assessment

        Args:
            user_input: User's question or topic (1-1000 chars)

        Returns:
            PlanningOutput with complete diagram specifications

        Raises:
            PlanningError: If validation fails, timeout occurs, or API fails
        """
        # Validate input
        if not user_input or not user_input.strip():
            raise PlanningError("Topic cannot be empty")
        if len(user_input) > 1000:
            raise PlanningError("Topic is too long (max 1000 characters)")

        logger.info(
            "Planning analysis started",
            user_input=user_input[:100],
        )

        try:
            # Run analysis with timeout
            result = await asyncio.wait_for(
                self._analyze_internal(user_input),
                timeout=self.timeout,
            )
            logger.info(
                "Planning analysis completed",
                concept=result.concept,
                diagram_type=result.diagram_type,
                components_count=len(result.components),
            )
            return result
        except asyncio.TimeoutError:
            logger.error(f"Planning timed out after {self.timeout}s")
            raise PlanningError(
                f"Planning timed out after {self.timeout}s. Try a simpler topic."
            )
        except PlanningError:
            # Re-raise PlanningErrors as-is
            raise
        except Exception as e:
            logger.error(f"Planning analysis failed: {e}")
            raise PlanningError(f"Failed to analyze concept: {str(e)}")

    async def _analyze_internal(self, user_input: str) -> PlanningOutput:
        """Internal analysis implementation using Gemini.

        Args:
            user_input: User's question or topic

        Returns:
            PlanningOutput with diagram specifications

        Raises:
            PlanningError: If analysis or JSON parsing fails
        """
        # Create detailed prompt for concept analysis
        prompt = f"""You are an expert educational diagram designer specializing in creating visual explanations for the user.

Task: Analyze this topic and create a detailed diagram plan.

Topic: {user_input}

Requirements:
1. Identify the core concept clearly
2. Choose appropriate diagram type (flowchart for processes, mindmap for relationships, sequence for steps, hierarchy for structure)
3. Identify all key components (5-15 elements)
4. Define clear relationships between components
5. Define measurable success criteria
6. Define key insights

Respond ONLY with valid JSON in this exact structure (no markdown, no code blocks):
{{
    "concept": "the main concept being explained",
    "diagram_type": "flowchart|mindmap|sequence|hierarchy",
    "components": ["element1", "element2", "element3"],
    "relationships": [
        {{"from": "source", "to": "destination", "label": "relationship_description"}},
        {{"from": "source2", "to": "destination2", "label": "relationship_description2"}}
    ],
    "success_criteria": ["criterion1", "criterion2"],
    "key_insights": ["insight1", "insight2"]
}}

Ensure:
- Components are specific and relevant
- All relationships show meaningful connections
- Success criteria are measurable
- Key insights highlight important teaching points"""

        try:
            # Call Gemini API in thread pool (blocking call)
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                self.executor,
                self.client.generate_content,
                prompt
            )
            response_text = response.text

            logger.debug(f"Gemini response: {response_text[:200]}...")

            # Parse JSON from response
            json_data = self._parse_json_response(response_text)

            # Validate required fields
            required_fields = [
                "concept",
                "diagram_type",
                "components",
                "relationships",
                "success_criteria",
                "key_insights",
            ]
            missing_fields = [f for f in required_fields if f not in json_data]
            if missing_fields:
                raise PlanningError(
                    f"Missing required fields in response: {', '.join(missing_fields)}"
                )

            # Validate diagram_type
            valid_types = ["flowchart", "mindmap", "sequence", "hierarchy"]
            if json_data["diagram_type"] not in valid_types:
                raise PlanningError(
                    f"Invalid diagram type: {json_data['diagram_type']}. "
                    f"Must be one of: {', '.join(valid_types)}"
                )

            # Ensure lists are not empty
            if not json_data["components"]:
                raise PlanningError("Components list cannot be empty")

            # Create PlanningOutput
            return PlanningOutput(
                concept=str(json_data["concept"]),
                diagram_type=str(json_data["diagram_type"]),
                components=list(json_data["components"]),
                relationships=list(json_data["relationships"]),
                success_criteria=list(json_data["success_criteria"]),
                key_insights=list(json_data["key_insights"]),
            )

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            raise PlanningError(f"Invalid JSON response from analysis: {e}")
        except PlanningError:
            raise
        except KeyError as e:
            logger.error(f"Missing field in parsed response: {e}")
            raise PlanningError(f"Missing field in analysis response: {e}")

    def _parse_json_response(self, response_text: str) -> dict:
        """Parse JSON from Gemini response.

        Handles cases where response might have markdown code blocks
        or extra whitespace.

        Args:
            response_text: Raw response text from Gemini

        Returns:
            Parsed JSON dictionary

        Raises:
            json.JSONDecodeError: If JSON parsing fails
            PlanningError: If response format is invalid
        """
        text = response_text.strip()

        # Remove markdown code blocks if present
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()

        # Parse JSON
        try:
            data = json.loads(text)
            return data
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing failed: {e}")
            logger.debug(f"Response text: {text[:500]}")
            raise
