"""Utility for storing orchestrator step responses for debugging."""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from loguru import logger

# Response storage directory
RESPONSES_DIR = Path(__file__).parent.parent / "responses"


def _ensure_responses_dir():
    """Ensure responses directory exists."""
    RESPONSES_DIR.mkdir(parents=True, exist_ok=True)


def _get_timestamp_ms() -> str:
    """Get current timestamp in milliseconds for filename uniqueness."""
    return str(int(time.time() * 1000))


def store_planning_response(
    planning_output: dict, request_id: str = ""
) -> str:
    """Store planning agent response.

    Args:
        planning_output: Planning output dict
        request_id: Optional request ID for correlation

    Returns:
        Filename of stored response
    """
    _ensure_responses_dir()

    filename = f"01_planning_{_get_timestamp_ms()}.json"
    filepath = RESPONSES_DIR / filename

    response_data = {
        "timestamp": datetime.now().isoformat(),
        "request_id": request_id,
        "step": "planning_agent",
        "data": planning_output,
    }

    try:
        with open(filepath, "w") as f:
            json.dump(response_data, f, indent=2)
        logger.debug(f"Stored planning response: {filename}")
    except Exception as e:
        logger.error(f"Failed to store planning response: {e}")

    return filename


def store_generation_response(
    xml_content: str, request_id: str = ""
) -> str:
    """Store diagram generation (XML) response.

    Args:
        xml_content: Generated XML diagram
        request_id: Optional request ID for correlation

    Returns:
        Filename of stored response
    """
    _ensure_responses_dir()

    filename = f"02_generation_{_get_timestamp_ms()}.json"
    filepath = RESPONSES_DIR / filename

    response_data = {
        "timestamp": datetime.now().isoformat(),
        "request_id": request_id,
        "step": "diagram_generation",
        "xml_length": len(xml_content),
        "xml_preview": xml_content[:500] if xml_content else "",
        "xml_full": xml_content,  # Full XML for debugging
    }

    try:
        with open(filepath, "w") as f:
            json.dump(response_data, f, indent=2)
        logger.debug(f"Stored generation response: {filename}")
    except Exception as e:
        logger.error(f"Failed to store generation response: {e}")

    return filename


def store_review_response(
    review_output: dict, iteration: int, request_id: str = ""
) -> str:
    """Store review agent response.

    Args:
        review_output: Review output dict
        iteration: Review iteration number (1-3)
        request_id: Optional request ID for correlation

    Returns:
        Filename of stored response
    """
    _ensure_responses_dir()

    filename = f"03_review_iter{iteration}_{_get_timestamp_ms()}.json"
    filepath = RESPONSES_DIR / filename

    response_data = {
        "timestamp": datetime.now().isoformat(),
        "request_id": request_id,
        "step": "review_agent",
        "iteration": iteration,
        "data": review_output,
    }

    try:
        with open(filepath, "w") as f:
            json.dump(response_data, f, indent=2)
        logger.debug(f"Stored review response: {filename}")
    except Exception as e:
        logger.error(f"Failed to store review response: {e}")

    return filename


def store_refinement_response(
    xml_before: str, xml_after: str, feedback: str, iteration: int, request_id: str = ""
) -> str:
    """Store MCP refinement response.

    Args:
        xml_before: XML before refinement
        xml_after: XML after refinement
        feedback: Refinement feedback used
        iteration: Refinement iteration number
        request_id: Optional request ID for correlation

    Returns:
        Filename of stored response
    """
    _ensure_responses_dir()

    filename = f"03b_refinement_iter{iteration}_{_get_timestamp_ms()}.json"
    filepath = RESPONSES_DIR / filename

    response_data = {
        "timestamp": datetime.now().isoformat(),
        "request_id": request_id,
        "step": "mcp_refinement",
        "iteration": iteration,
        "feedback": feedback,
        "xml_before_length": len(xml_before),
        "xml_after_length": len(xml_after),
        "xml_before_preview": xml_before[:300] if xml_before else "",
        "xml_after_preview": xml_after[:300] if xml_after else "",
        "xml_before_full": xml_before,
        "xml_after_full": xml_after,
    }

    try:
        with open(filepath, "w") as f:
            json.dump(response_data, f, indent=2)
        logger.debug(f"Stored refinement response: {filename}")
    except Exception as e:
        logger.error(f"Failed to store refinement response: {e}")

    return filename


def store_conversion_response(
    svg_content: str, request_id: str = ""
) -> str:
    """Store SVG conversion response.

    Args:
        svg_content: Generated SVG content
        request_id: Optional request ID for correlation

    Returns:
        Filename of stored response
    """
    _ensure_responses_dir()

    filename = f"04_conversion_{_get_timestamp_ms()}.json"
    filepath = RESPONSES_DIR / filename

    response_data = {
        "timestamp": datetime.now().isoformat(),
        "request_id": request_id,
        "step": "svg_conversion",
        "svg_length": len(svg_content),
        "svg_preview": svg_content[:500] if svg_content else "",
        "svg_full": svg_content,  # Full SVG for debugging
    }

    try:
        with open(filepath, "w") as f:
            json.dump(response_data, f, indent=2)
        logger.debug(f"Stored conversion response: {filename}")
    except Exception as e:
        logger.error(f"Failed to store conversion response: {e}")

    return filename


def clear_responses_dir():
    """Clear all stored responses (for cleanup)."""
    _ensure_responses_dir()

    try:
        for file in RESPONSES_DIR.glob("*.json"):
            file.unlink()
        logger.info("Cleared all stored responses")
    except Exception as e:
        logger.error(f"Failed to clear responses: {e}")
