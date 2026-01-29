#!/usr/bin/env python3
"""Test the streaming diagram generation endpoint."""

import asyncio
import json

import httpx


async def test_streaming():
    """Test the /api/diagram/stream endpoint."""
    url = "http://localhost:8000/api/diagram/stream"
    payload = {"concept": "How bees make honey"}

    print("Connecting to streaming endpoint...")
    print(f"URL: {url}")
    print(f"Payload: {json.dumps(payload)}\n")
    print("=" * 80)

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream("POST", url, json=payload) as response:
                print(f"Status: {response.status_code}\n")

                try:
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            try:
                                event_data = json.loads(line[6:])  # Remove "data: " prefix

                                # Pretty print the event
                                event_type = event_data.get("type", "unknown")
                                stage = event_data.get("stage", "?")
                                status = event_data.get("status", "")
                                progress = event_data.get("progress", 0)

                                print(
                                    f"[{event_type.upper()}] {stage:12} | "
                                    f"{progress:3.0f}% | {status}"
                                )

                                # Print error details if present
                                if event_data.get("error"):
                                    print(f"  Error: {event_data['error']}")

                                # Print completion info
                                if event_type == "complete" and event_data.get(
                                    "data"
                                ):
                                    data = event_data["data"]
                                    print("\n" + "=" * 80)
                                    print("COMPLETION DATA:")
                                    print(f"  PNG File: {data.get('png_filename')}")
                                    print(f"  SVG File: {data.get('svg_filename')}")
                                    print(
                                        f"  Total Time: {data.get('total_time_seconds')}s"
                                    )
                                    print(
                                        f"  Review Score: {data.get('review_score')}/100"
                                    )
                                    print(f"  Iterations: {data.get('iterations')}")
                                    print("=" * 80)

                            except json.JSONDecodeError:
                                pass  # Skip non-JSON lines

                except (httpx.RemoteProtocolError, httpx.ReadError) as e:
                    print(f"\nConnection closed: {e}")
                    print(
                        "(This is normal if the API hit the quota or took too long)"
                    )

    except Exception as e:
        print(f"Error: {type(e).__name__}: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_streaming())
