# Orchestrator Debug Responses

This directory stores responses from each step of the diagram generation pipeline for debugging purposes.

## Response Files

Files are named with a prefix indicating which step they come from:

### `01_planning_*.json`
**Planning Agent Response**

Contains the planning analysis output:
- `concept`: The core concept being explained
- `diagram_type`: Type of diagram (flowchart, mindmap, sequence, hierarchy)
- `components`: List of diagram elements
- `relationships`: Relationships between components
- `success_criteria`: Validation criteria for the review agent
- `key_insights`: Important teaching points

### `02_generation_*.json`
**Diagram Generation Response**

Contains the XML generation result:
- `xml_length`: Length of generated XML
- `xml_preview`: First 500 chars of XML for quick review
- `xml_full`: Complete XML content for detailed analysis

### `03_review_iter{N}_*.json`
**Review Agent Response (Per Iteration)**

Contains the review validation output for each iteration:
- `iteration`: Review iteration number (1-3)
- `score`: Quality score (0-100)
- `approved`: Whether diagram was approved
- `issues`: List of identified issues
- `refinement_instructions`: Specific improvements needed
- `educational_alignment`: Assessment of pedagogical quality

### `03b_refinement_iter{N}_*.json`
**MCP Refinement Response (Per Iteration)**

Contains the XML refinement details:
- `iteration`: Refinement iteration number
- `feedback`: Refinement instructions used
- `xml_before_length`: Size of XML before refinement
- `xml_after_length`: Size of XML after refinement
- `xml_before_full`: Complete XML before refinement
- `xml_after_full`: Complete XML after refinement

### `04_conversion_*.json`
**SVG Conversion Response**

Contains the SVG rendering result:
- `svg_length`: Length of generated SVG
- `svg_preview`: First 500 chars of SVG for quick review
- `svg_full`: Complete SVG content for detailed analysis

## Request Correlation

All responses from the same orchestration run share the same `request_id` field, allowing you to trace a complete diagram generation pipeline.

## File Naming Format

- Prefix: `01`, `02`, `03`, `03b`, `04` (indicates pipeline step)
- Timestamp: milliseconds since epoch (ensures uniqueness)
- Extension: `.json`

Example: `01_planning_1704067200123.json`

## Usage

### View All Planning Responses
```bash
ls -la app/responses/01_planning_*.json
```

### Track a Specific Request
```bash
# Find all files for request ID "abc12345"
grep -l "abc12345" app/responses/*.json
```

### Compare XML Before/After Refinement
```bash
# View refinement details
cat app/responses/03b_refinement_iter1_*.json | jq '.data | {before_length, after_length, feedback}'
```

### Check Review Scores
```bash
# View all review scores
for file in app/responses/03_review_*.json; do
  echo "File: $file"
  jq '.data.score' "$file"
done
```

## Cleanup

To clear all stored responses:

```python
from app.utils.response_storage import clear_responses_dir
clear_responses_dir()
```

Or via CLI:
```bash
rm app/responses/*.json
```

## Performance Impact

Response storage is minimal (~1-5KB per response) and has negligible performance impact. Each JSON file is written asynchronously and errors are logged but don't affect the pipeline.
