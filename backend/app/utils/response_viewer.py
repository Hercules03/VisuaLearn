"""Utility for viewing and analyzing stored orchestrator responses."""

import json
from pathlib import Path
from typing import Optional

# Response storage directory
RESPONSES_DIR = Path(__file__).parent.parent / "responses"


def list_responses(request_id: Optional[str] = None) -> list[dict]:
    """List all stored responses, optionally filtered by request_id.

    Args:
        request_id: Optional request ID to filter by

    Returns:
        List of response metadata
    """
    responses = []

    for file in sorted(RESPONSES_DIR.glob("*.json"), reverse=True):
        try:
            with open(file) as f:
                data = json.load(f)

            if request_id and data.get("request_id") != request_id:
                continue

            responses.append(
                {
                    "filename": file.name,
                    "timestamp": data.get("timestamp"),
                    "request_id": data.get("request_id"),
                    "step": data.get("step"),
                    "iteration": data.get("iteration"),
                }
            )
        except Exception:
            continue

    return responses


def view_response(filename: str) -> dict:
    """View full content of a response file.

    Args:
        filename: Name of response file

    Returns:
        Complete response data
    """
    filepath = RESPONSES_DIR / filename

    if not filepath.exists():
        raise FileNotFoundError(f"Response file not found: {filename}")

    with open(filepath) as f:
        return json.load(f)


def view_request(request_id: str) -> dict:
    """View all responses for a specific request ID.

    Args:
        request_id: Request ID to view

    Returns:
        Dictionary with all steps
    """
    result = {"request_id": request_id, "steps": {}}

    for file in sorted(RESPONSES_DIR.glob("*.json")):
        try:
            with open(file) as f:
                data = json.load(f)

            if data.get("request_id") == request_id:
                step_name = data.get("step", "unknown")
                iteration = data.get("iteration")

                key = step_name
                if iteration:
                    key = f"{step_name}_iter{iteration}"

                result["steps"][key] = {
                    "filename": file.name,
                    "timestamp": data.get("timestamp"),
                    "data": data.get("data"),
                }
        except Exception:
            continue

    return result


def print_response_summary(filename: str) -> None:
    """Print a summary of a response file.

    Args:
        filename: Name of response file
    """
    filepath = RESPONSES_DIR / filename

    if not filepath.exists():
        print(f"Response file not found: {filename}")
        return

    with open(filepath) as f:
        data = json.load(f)

    print(f"\n{'='*60}")
    print(f"File: {filename}")
    print(f"{'='*60}")
    print(f"Timestamp: {data.get('timestamp')}")
    print(f"Request ID: {data.get('request_id')}")
    print(f"Step: {data.get('step')}")

    if data.get("iteration"):
        print(f"Iteration: {data.get('iteration')}")

    step = data.get("step")

    if step == "planning_agent":
        plan_data = data.get("data", {})
        print(f"\nConcept: {plan_data.get('concept')}")
        print(f"Diagram Type: {plan_data.get('diagram_type')}")
        print(f"Components: {len(plan_data.get('components', []))} items")
        print(f"Relationships: {len(plan_data.get('relationships', []))} items")

    elif step == "diagram_generation":
        print(f"XML Length: {data.get('xml_length')} bytes")
        print(f"\nXML Preview:")
        print(data.get("xml_preview", "")[:300])

    elif step == "review_agent":
        review_data = data.get("data", {})
        print(f"Score: {review_data.get('score')}/100")
        print(f"Approved: {review_data.get('approved')}")
        print(f"Issues: {len(review_data.get('issues', []))} items")
        print(f"\nFeedback: {review_data.get('feedback', '')[:200]}")

    elif step == "mcp_refinement":
        print(f"Feedback: {data.get('feedback', '')[:200]}")
        print(f"XML Before: {data.get('xml_before_length')} bytes")
        print(f"XML After: {data.get('xml_after_length')} bytes")

    elif step == "svg_conversion":
        print(f"SVG Length: {data.get('svg_length')} bytes")
        print(f"\nSVG Preview:")
        print(data.get("svg_preview", "")[:300])

    print(f"\n{'='*60}\n")


def compare_xml_iterations(request_id: str) -> None:
    """Compare XML changes across review iterations.

    Args:
        request_id: Request ID to analyze
    """
    print(f"\n{'='*60}")
    print(f"XML Changes for Request: {request_id}")
    print(f"{'='*60}")

    refinements = []

    for file in sorted(RESPONSES_DIR.glob("*refinement_*.json")):
        try:
            with open(file) as f:
                data = json.load(f)

            if data.get("request_id") == request_id:
                refinements.append(
                    {
                        "iteration": data.get("iteration"),
                        "before_length": data.get("xml_before_length"),
                        "after_length": data.get("xml_after_length"),
                        "feedback": data.get("feedback"),
                    }
                )
        except Exception:
            continue

    if not refinements:
        print("No refinement data found")
        return

    print(f"\n{'Iter':<5} {'Before':<12} {'After':<12} {'Change':<10} {'Feedback':<20}")
    print("-" * 60)

    for ref in refinements:
        iteration = ref["iteration"]
        before = ref["before_length"]
        after = ref["after_length"]
        change = after - before
        feedback = ref["feedback"][:20] + "..." if ref["feedback"] else ""

        print(f"{iteration:<5} {before:<12} {after:<12} {change:+<10} {feedback:<20}")

    print(f"\n{'='*60}\n")


def print_all_requests() -> None:
    """Print summary of all stored requests."""
    requests = {}

    for file in RESPONSES_DIR.glob("*.json"):
        try:
            with open(file) as f:
                data = json.load(f)

            req_id = data.get("request_id")
            if req_id not in requests:
                requests[req_id] = {"steps": [], "timestamp": data.get("timestamp")}

            requests[req_id]["steps"].append(data.get("step"))
        except Exception:
            continue

    if not requests:
        print("No stored requests found")
        return

    print(f"\n{'='*60}")
    print("Stored Requests")
    print(f"{'='*60}")
    print(f"{'Request ID':<15} {'Timestamp':<25} {'Steps':<40}")
    print("-" * 80)

    for req_id in sorted(requests.keys(), reverse=True):
        data = requests[req_id]
        timestamp = data["timestamp"][:19] if data["timestamp"] else "N/A"
        steps = ", ".join(set(data["steps"]))

        print(f"{req_id:<15} {timestamp:<25} {steps:<40}")

    print(f"\n{'='*60}\n")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print_all_requests()
    elif sys.argv[1] == "list":
        print_all_requests()
    elif sys.argv[1] == "view":
        if len(sys.argv) < 3:
            print("Usage: python response_viewer.py view <filename>")
        else:
            print_response_summary(sys.argv[2])
    elif sys.argv[1] == "request":
        if len(sys.argv) < 3:
            print("Usage: python response_viewer.py request <request_id>")
        else:
            request_data = view_request(sys.argv[2])
            print(json.dumps(request_data, indent=2))
    else:
        print("Usage:")
        print("  python response_viewer.py list          # List all requests")
        print("  python response_viewer.py view <file>   # View response file")
        print(
            "  python response_viewer.py request <id>  # View all steps for request"
        )
