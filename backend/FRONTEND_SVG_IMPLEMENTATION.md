# Frontend SVG Implementation Guide

## Overview

The backend now returns SVG content directly in API responses. This guide shows how to implement SVG rendering in the frontend using `react-svg` with proper optimization and styling.

## API Response Structure

The diagram generation endpoint returns:

```json
{
  "svg_filename": "uuid.svg",           // For file downloads
  "xml_filename": "uuid.xml",           // For file downloads
  "svg_content": "<svg>...</svg>",      // For inline display ✨
  "xml_content": "<mxfile>...",         // Raw XML (reference)
  "plan": {...},
  "review_score": 92,
  "iterations": 1,
  "total_time_seconds": 15.3,
  "metadata": {...}
}
```

**Key field**: `svg_content` - Contains the complete SVG markup for display.

## Installation

### 1. Install react-svg

```bash
npm install react-svg
# or
yarn add react-svg
# or
pnpm add react-svg
```

### 2. Install SVGO for optimization (optional but recommended)

```bash
npm install svgo
```

## Implementation Patterns

### Pattern 1: Basic SVG Display with react-svg

```tsx
import { ReactSVG } from 'react-svg';
import { useState } from 'react';

export function DiagramDisplay({ svgContent, title }) {
  const [loading, setLoading] = useState(true);

  return (
    <div className="diagram-container">
      <h2>{title}</h2>
      <div className="svg-wrapper">
        <ReactSVG
          src={`data:image/svg+xml;base64,${btoa(svgContent)}`}
          wrapper="div"
          loading={() => <div className="spinner">Loading diagram...</div>}
          fallback={() => <div className="error">Failed to load diagram</div>}
          beforeInjection={(svg) => {
            // Ensure responsive sizing
            svg.setAttribute('width', '100%');
            svg.setAttribute('height', 'auto');
            svg.style.maxWidth = '100%';
            svg.style.display = 'block';
            setLoading(false);
          }}
          afterInjection={() => {
            // Optional: Add click handlers, animation, etc.
          }}
        />
      </div>
    </div>
  );
}
```

### Pattern 2: SVG with Zoom/Pan (Recommended)

```tsx
import { ReactSVG } from 'react-svg';
import svgPanZoom from 'svg-pan-zoom';
import { useRef, useEffect } from 'react';

export function InteractiveDiagramDisplay({ svgContent }) {
  const containerRef = useRef(null);

  useEffect(() => {
    if (containerRef.current) {
      const svg = containerRef.current.querySelector('svg');
      if (svg) {
        svgPanZoom(svg, {
          zoomEnabled: true,
          controlIconsEnabled: true,
          fit: true,
          center: true,
          minZoom: 0.5,
          maxZoom: 10,
        });
      }
    }
  }, [svgContent]);

  return (
    <div ref={containerRef} className="interactive-diagram">
      <ReactSVG
        src={`data:image/svg+xml;base64,${btoa(svgContent)}`}
        wrapper="div"
        beforeInjection={(svg) => {
          svg.setAttribute('width', '100%');
          svg.setAttribute('height', '100%');
        }}
      />
    </div>
  );
}
```

### Pattern 3: Optimized SVG with SVGO

```tsx
import { ReactSVG } from 'react-svg';
import { optimize } from 'svgo';
import { useMemo } from 'react';

export function OptimizedDiagramDisplay({ svgContent }) {
  // Optimize SVG on client-side
  const optimizedSvg = useMemo(() => {
    try {
      const result = optimize(svgContent, {
        multipass: true,
        plugins: [
          'removeDoctype',
          'removeXMLProcInst',
          'removeComments',
          'removeMetadata',
          'removeDesc',
          'removeTitle',
          'removeEditorsNSData',
          'removeEmptyAttrs',
          'removeEmptyContainers',
          'removeEmptyText',
          'removeHiddenElems',
          'removeHiddenPaths',
          'removeUselessDefs',
          'removeUselessGroups',
          'removeUselessStrokeAndFill',
          'removeViewBox',
          'cleanupEnableBackground',
          'removeHiddenRects',
          'removeEmptyRects',
          'convertTransform',
          'convertEllipseToCircle',
          'sortAttrs',
          'convertPathData',
          'convertTransform',
          'removeUnknownsAndDefaults',
          'removeNonInheritableGroupAttrs',
          'removeUselessStrokeAndFill',
          'removeViewBox',
          'cleanupNumericValues',
          'convertPathData',
          'convertTransform',
          'removeUnknownsAndDefaults',
        ],
      });
      return result.data;
    } catch (error) {
      console.warn('SVG optimization failed, using original:', error);
      return svgContent;
    }
  }, [svgContent]);

  return (
    <ReactSVG
      src={`data:image/svg+xml;base64,${btoa(optimizedSvg)}`}
      wrapper="div"
      beforeInjection={(svg) => {
        svg.setAttribute('width', '100%');
        svg.setAttribute('height', 'auto');
      }}
    />
  );
}
```

## Styling Guide

### CSS for Responsive SVG Container

```css
.diagram-container {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.svg-wrapper {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  overflow: hidden;
}

.svg-wrapper svg {
  width: 100%;
  height: auto;
  display: block;
  max-height: 600px;
}

/* Responsive for mobile */
@media (max-width: 768px) {
  .svg-wrapper svg {
    max-height: 400px;
  }
}

/* Interactive diagram container */
.interactive-diagram {
  width: 100%;
  height: 600px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  overflow: hidden;
  background: #f9fafb;
}

.interactive-diagram svg {
  width: 100% !important;
  height: 100% !important;
}
```

## Complete Component Example

```tsx
// DiagramViewer.tsx
import { ReactSVG } from 'react-svg';
import svgPanZoom from 'svg-pan-zoom';
import { useState, useRef, useEffect } from 'react';

interface DiagramResponse {
  svg_content: string;
  svg_filename: string;
  xml_filename: string;
  review_score: number;
  iterations: number;
  total_time_seconds: number;
  plan: {
    concept: string;
    diagram_type: string;
    components: string[];
    relationships: Array<{ from: string; to: string; label: string }>;
  };
}

export function DiagramViewer({ data }: { data: DiagramResponse }) {
  const [isInteractive, setIsInteractive] = useState(false);
  const svgContainerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (isInteractive && svgContainerRef.current) {
      const svg = svgContainerRef.current.querySelector('svg');
      if (svg) {
        svgPanZoom(svg, {
          zoomEnabled: true,
          controlIconsEnabled: true,
          fit: true,
          center: true,
          minZoom: 0.5,
          maxZoom: 10,
          beforePan: (oldPan, newPan) => newPan,
        });
      }
    }
  }, [isInteractive, data.svg_content]);

  const downloadSvg = () => {
    const element = document.createElement('a');
    element.setAttribute(
      'href',
      `data:image/svg+xml;base64,${btoa(data.svg_content)}`
    );
    element.setAttribute('download', data.svg_filename);
    element.style.display = 'none';
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  const downloadXml = () => {
    // Fetch XML from /api/export/{xml_filename}
    window.location.href = `/api/export/${data.xml_filename}`;
  };

  return (
    <div className="diagram-viewer">
      {/* Header */}
      <div className="viewer-header">
        <div>
          <h2>{data.plan.concept}</h2>
          <p className="metadata">
            Type: {data.plan.diagram_type} | Score: {data.review_score}/100 |
            {data.iterations} iterations | {data.total_time_seconds.toFixed(1)}s
          </p>
        </div>

        {/* Controls */}
        <div className="controls">
          <button onClick={() => setIsInteractive(!isInteractive)}>
            {isInteractive ? '🔓 Lock' : '🔓 Interactive Mode'}
          </button>
          <button onClick={downloadSvg}>⬇️ SVG</button>
          <button onClick={downloadXml}>⬇️ XML</button>
        </div>
      </div>

      {/* Diagram Display */}
      <div
        ref={svgContainerRef}
        className={isInteractive ? 'interactive-diagram' : 'diagram-container'}
      >
        <div className="svg-wrapper">
          <ReactSVG
            src={`data:image/svg+xml;base64,${btoa(data.svg_content)}`}
            wrapper="div"
            loading={() => <div className="spinner">Rendering diagram...</div>}
            fallback={() => (
              <div className="error">Failed to render diagram</div>
            )}
            beforeInjection={(svg) => {
              svg.setAttribute('width', '100%');
              svg.setAttribute('height', 'auto');
              svg.style.display = 'block';
              svg.style.maxWidth = '100%';
            }}
          />
        </div>
      </div>

      {/* Details */}
      <div className="diagram-details">
        <div className="section">
          <h3>Components ({data.plan.components.length})</h3>
          <ul>
            {data.plan.components.slice(0, 5).map((comp, idx) => (
              <li key={idx}>{comp}</li>
            ))}
            {data.plan.components.length > 5 && (
              <li>... and {data.plan.components.length - 5} more</li>
            )}
          </ul>
        </div>

        <div className="section">
          <h3>Relationships ({data.plan.relationships.length})</h3>
          <ul>
            {data.plan.relationships.slice(0, 5).map((rel, idx) => (
              <li key={idx}>
                {rel.from} <strong>→</strong> {rel.to}
              </li>
            ))}
            {data.plan.relationships.length > 5 && (
              <li>
                ... and {data.plan.relationships.length - 5} more relationships
              </li>
            )}
          </ul>
        </div>
      </div>
    </div>
  );
}
```

### Corresponding CSS

```css
.diagram-viewer {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem 1rem;
}

.viewer-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding: 1rem;
  background: #f9fafb;
  border-radius: 8px;
}

.viewer-header h2 {
  margin: 0 0 0.5rem 0;
  font-size: 1.5rem;
}

.metadata {
  margin: 0;
  font-size: 0.875rem;
  color: #6b7280;
}

.controls {
  display: flex;
  gap: 0.75rem;
}

.controls button {
  padding: 0.5rem 1rem;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.875rem;
}

.controls button:hover {
  background: #2563eb;
}

.diagram-container {
  width: 100%;
  margin: 2rem 0;
}

.svg-wrapper {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  overflow: hidden;
  padding: 1rem;
}

.svg-wrapper svg {
  width: 100%;
  height: auto;
  display: block;
}

.interactive-diagram {
  width: 100%;
  height: 600px;
  margin: 2rem 0;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  overflow: hidden;
  background: #f9fafb;
}

.interactive-diagram svg {
  width: 100% !important;
  height: 100% !important;
}

.spinner {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 400px;
  font-size: 1rem;
  color: #6b7280;
}

.error {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 400px;
  background: #fee2e2;
  color: #991b1b;
  font-weight: 500;
  border-radius: 6px;
}

.diagram-details {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
  margin-top: 2rem;
  padding: 1.5rem;
  background: #f9fafb;
  border-radius: 8px;
}

.diagram-details .section h3 {
  margin: 0 0 1rem 0;
  font-size: 1rem;
}

.diagram-details ul {
  margin: 0;
  padding: 0 0 0 1.5rem;
  font-size: 0.875rem;
  color: #6b7280;
}

.diagram-details li {
  margin: 0.5rem 0;
}

@media (max-width: 768px) {
  .viewer-header {
    flex-direction: column;
    gap: 1rem;
    align-items: flex-start;
  }

  .controls {
    width: 100%;
    justify-content: flex-start;
  }

  .diagram-details {
    grid-template-columns: 1fr;
  }

  .interactive-diagram {
    height: 400px;
  }
}
```

## SVG Quality Assurance

### Validation Function

```tsx
export function validateSvgContent(svgContent: string): {
  valid: boolean;
  errors: string[];
} {
  const errors: string[] = [];

  if (!svgContent) {
    errors.push('SVG content is empty');
  }

  if (!svgContent.includes('<svg')) {
    errors.push('SVG content missing <svg> tag');
  }

  if (!svgContent.includes('xmlns')) {
    errors.push('SVG missing xmlns attribute');
  }

  try {
    const parser = new DOMParser();
    const doc = parser.parseFromString(svgContent, 'image/svg+xml');
    if (doc.getElementsByTagName('parsererror').length > 0) {
      errors.push('SVG parsing failed: malformed XML');
    }
  } catch (error) {
    errors.push(`SVG parsing error: ${error}`);
  }

  return {
    valid: errors.length === 0,
    errors,
  };
}
```

### Usage

```tsx
const validation = validateSvgContent(response.svg_content);
if (!validation.valid) {
  console.error('SVG validation errors:', validation.errors);
  // Handle error gracefully
}
```

## Installation Instructions for react-svg

### Option 1: With npm/yarn/pnpm

```bash
# Install main dependency
npm install react-svg

# Optional: for zoom/pan support
npm install svg-pan-zoom

# Optional: for SVG optimization
npm install svgo
```

### Option 2: In Next.js

```bash
npm install react-svg svg-pan-zoom
```

In `next.config.js`:

```js
/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // SVG handling (if using @svgr/webpack)
  webpack(config) {
    config.module.rules.push({
      test: /\.svg$/i,
      issuer: /\.[jt]sx?$/,
      use: ['@svgr/webpack'],
    });
    return config;
  },
};

module.exports = nextConfig;
```

### Option 3: In Vite

```bash
npm install react-svg svg-pan-zoom
```

In `vite.config.ts`:

```ts
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
});
```

## Testing

```tsx
// DiagramViewer.test.tsx
import { render, screen } from '@testing-library/react';
import { DiagramViewer } from './DiagramViewer';

const mockData = {
  svg_content: '<svg xmlns="http://www.w3.org/2000/svg"><circle r="50"/></svg>',
  svg_filename: 'test.svg',
  xml_filename: 'test.xml',
  review_score: 95,
  iterations: 1,
  total_time_seconds: 10,
  plan: {
    concept: 'Test Diagram',
    diagram_type: 'flowchart',
    components: ['A', 'B'],
    relationships: [{ from: 'A', to: 'B', label: 'connects' }],
  },
};

test('renders diagram viewer with SVG content', () => {
  render(<DiagramViewer data={mockData} />);
  expect(screen.getByText('Test Diagram')).toBeInTheDocument();
});
```

## Performance Tips

1. **Debounce zoom/pan interactions** to prevent excessive re-renders
2. **Lazy load DiagramViewer** if it's not immediately visible
3. **Use React.memo** to prevent unnecessary re-renders
4. **Optimize SVG on backend** before sending (consider adding SVGO post-processing in next-ai-draw-io)
5. **Cache SVG responses** using browser cache or React Query

## Browser Support

`react-svg` works on:
- Chrome 60+
- Firefox 55+
- Safari 12+
- Edge 79+
- All modern mobile browsers

## Troubleshooting

### SVG Not Displaying

```tsx
// Debug helper
function DebugDiagram({ svgContent }) {
  console.log('SVG Content:', svgContent);
  console.log('SVG Size:', svgContent.length);

  return (
    <>
      <details>
        <summary>View SVG Source</summary>
        <pre style={{ fontSize: '0.75rem', overflow: 'auto' }}>
          {svgContent}
        </pre>
      </details>
      <DiagramViewer data={{ svg_content: svgContent }} />
    </>
  );
}
```

### CORS Issues with Data URLs

If using external URLs for SVG:

```tsx
// Solution: Use data URL with base64 encoding
const svgDataUrl = `data:image/svg+xml;base64,${btoa(svgContent)}`;
```

### SVG Styling Not Applied

```tsx
beforeInjection={(svg) => {
  // Add custom styles to SVG
  svg.querySelectorAll('rect').forEach(rect => {
    rect.setAttribute('fill-opacity', '0.9');
  });
}}
```

## References

- [react-svg NPM](https://www.npmjs.com/package/react-svg)
- [svg-pan-zoom NPM](https://www.npmjs.com/package/svg-pan-zoom)
- [SVGO NPM](https://www.npmjs.com/package/svgo)
- [MDN SVG Documentation](https://developer.mozilla.org/en-US/docs/Web/SVG)
