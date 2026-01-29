# VisuaLearn Streaming API Guide

## Overview

The diagram generation process now supports **real-time progress streaming** using Server-Sent Events (SSE). This allows your frontend to show users exactly what stage the backend is in as their diagram is being generated.

## Endpoints

### 1. Traditional Endpoint (Final Result Only)
```
POST /api/diagram
```
Returns the complete result when finished. Simple for basic use cases.

**Request:**
```json
{
  "concept": "How plants grow from seeds",
  "educational_level": "8-10"  // Optional, defaults to 8-10
}
```

**Response:**
```json
{
  "png_filename": "550e8400-e29b-41d4-a716-446655440000.png",
  "svg_filename": "550e8400-e29b-41d4-a716-446655440000.svg",
  "xml_content": "<mxfile>...</mxfile>",
  "plan": {...},
  "review_score": 92.5,
  "iterations": 2,
  "total_time_seconds": 42.3,
  "metadata": {...}
}
```

### 2. Streaming Endpoint (Real-time Progress)
```
POST /api/diagram/stream
```
Streams progress events as Server-Sent Events (SSE). Perfect for showing real-time progress to users.

**Request:**
```json
{
  "concept": "How plants grow from seeds",
  "educational_level": "8-10"  // Optional, defaults to 8-10
}
```

**Response:** Server-Sent Events stream

## Progress Events

The streaming endpoint sends the following types of events:

### Progress Event
```json
{
  "type": "progress",
  "stage": "planning",
  "status": "Analyzing concept and creating diagram plan...",
  "progress": 0,
  "elapsed_time": 0
}
```

**Stages:** `planning` → `generation` → `review` → `conversion` → `storage`

**Fields:**
- `type`: Event type (`"progress"`, `"complete"`, or `"error"`)
- `stage`: Current pipeline stage
- `status`: Human-readable status message
- `progress`: Progress percentage (0-100)
- `elapsed_time`: Time spent on this stage in seconds
- `error`: Error message (if `type` is `"error"`)
- `data`: Final diagram response (if `type` is `"complete"`)

### Completion Event
```json
{
  "type": "complete",
  "stage": "storage",
  "status": "Diagram generation complete!",
  "progress": 100,
  "data": {
    "png_filename": "550e8400-e29b-41d4-a716-446655440000.png",
    "svg_filename": "550e8400-e29b-41d4-a716-446655440000.svg",
    "xml_content": "<mxfile>...</mxfile>",
    "plan": {...},
    "review_score": 92.5,
    "iterations": 2,
    "total_time_seconds": 42.3,
    "metadata": {...}
  }
}
```

### Error Event
```json
{
  "type": "error",
  "stage": "unknown",
  "status": "Generation failed",
  "progress": 0,
  "error": "Failed to extract diagram from draw.io response"
}
```

## Frontend Implementation

### JavaScript/Fetch Example

```javascript
const response = await fetch('http://localhost:8000/api/diagram/stream', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ concept: 'How plants grow' })
});

const reader = response.body.getReader();
const decoder = new TextDecoder();

while (true) {
  const { done, value } = await reader.read();
  if (done) break;

  const text = decoder.decode(value);
  const lines = text.split('\n');

  for (const line of lines) {
    if (line.startsWith('data: ')) {
      const event = JSON.parse(line.slice(6));

      if (event.type === 'progress') {
        // Update progress bar
        console.log(`${event.stage}: ${event.progress}% - ${event.status}`);
      } else if (event.type === 'complete') {
        // Show final diagram
        console.log('Done!', event.data);
      } else if (event.type === 'error') {
        // Show error
        console.error(event.error);
      }
    }
  }
}
```

### React Example

```jsx
function DiagramGenerator() {
  const [progress, setProgress] = useState(0);
  const [currentStage, setCurrentStage] = useState('');
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const generateDiagram = async (concept) => {
    try {
      const response = await fetch('http://localhost:8000/api/diagram/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ concept })
      });

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value);
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const event = JSON.parse(line.slice(6));

            switch (event.type) {
              case 'progress':
                setProgress(event.progress);
                setCurrentStage(event.stage);
                break;
              case 'complete':
                setProgress(100);
                setResult(event.data);
                break;
              case 'error':
                setError(event.error);
                break;
            }
          }
        }
      }
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div>
      <button onClick={() => generateDiagram('How plants grow')}>
        Generate
      </button>

      <div>
        <p>Stage: {currentStage}</p>
        <progress value={progress} max="100" />
        <p>{progress}%</p>
      </div>

      {result && <DiagramDisplay result={result} />}
      {error && <ErrorMessage error={error} />}
    </div>
  );
}
```

## Pipeline Stages

The diagram generation pipeline consists of 5 stages:

1. **Planning** (0-20%)
   - Analyzes the concept
   - Creates diagram specifications
   - Identifies components and relationships

2. **Generation** (20-50%)
   - Sends plan to next-ai-draw-io service
   - Generates draw.io XML format diagram

3. **Review** (50-75%)
   - Quality validation
   - Potential refinement iterations
   - Final approval check

4. **Conversion** (75-90%)
   - Converts XML to PNG image
   - Creates SVG vector version
   - Generates high-res export

5. **Storage** (90-100%)
   - Saves files to temp directory
   - Sets up auto-cleanup timers
   - Generates export URLs

## Event Timing

Each stage's actual duration is included in the metadata. Use this for more accurate progress estimation:

```javascript
// After receiving a progress event
const elapsedMs = event.elapsed_time * 1000;
const stageLabel = `${event.stage} (${event.elapsed_time.toFixed(1)}s)`;
```

## Error Handling

The streaming API gracefully handles errors:

1. **Generation Errors** - Sent as `error` events mid-stream
2. **Connection Issues** - Stream terminates with last received event
3. **API Quota** - Error event with quota message

Always listen for `error` type events and display them to users.

## Testing

### Quick Browser Test

1. Open `test_streaming_api.html` in a browser
2. Enter a concept
3. Click "Generate Diagram"
4. Watch real-time progress updates

### Python Test

```bash
python3 test_streaming_endpoint.py
```

## Timeout Configuration

The following timeouts apply (in `/backend/.env`):

```env
GENERATION_TIMEOUT=60      # Maximum time for diagram generation
PLANNING_TIMEOUT=15        # Maximum time for planning agent
REVIEW_TIMEOUT=10          # Maximum time per review iteration
IMAGE_TIMEOUT=8            # Maximum time for image conversion
```

If the entire process exceeds browser timeout, the connection will close. The frontend should handle this gracefully.

## Migration Notes

If you're currently using the traditional `/api/diagram` endpoint:

1. No changes needed - it still works as-is
2. Optionally migrate to `/api/diagram/stream` for better UX
3. Both endpoints accept the same request format
4. Stream endpoint returns data via SSE instead of a single JSON response

## Troubleshooting

**No progress events received:**
- Check browser console for CORS errors
- Verify backend is running: `curl http://localhost:8000/api/diagram/stream -X POST -H "Content-Type: application/json" -d '{"concept":"test"}'`

**Connection drops during generation:**
- Increase `GENERATION_TIMEOUT` in `.env` if needed
- Check backend logs for errors
- Verify Gemini API quota is not exceeded

**Progress doesn't match actual process:**
- The streaming endpoint simulates progress based on actual stage completion times
- Actual timing may vary based on API response times
- Real-time streaming with actual progress callbacks coming in future update
