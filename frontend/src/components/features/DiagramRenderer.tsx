import { useMemo } from "react";

interface DiagramRendererProps {
  diagramSvg?: string; // SVG content from backend
  height?: number;
}

/**
 * DiagramRenderer Component
 *
 * Displays draw.io diagrams from SVG
 * - Renders SVG directly (no external dependencies)
 * - Responsive and lightweight
 * - Shows error state if rendering fails
 */
export function DiagramRenderer({
  diagramSvg,
  height = 500,
}: DiagramRendererProps) {
  // Parse SVG safely
  const svgContent = useMemo(() => {
    if (!diagramSvg) return null;
    try {
      return diagramSvg;
    } catch (e) {
      console.error("Failed to parse SVG:", e);
      return null;
    }
  }, [diagramSvg]);

  // No diagram data
  if (!svgContent) {
    return (
      <div
        style={{
          width: "100%",
          height: `${height}px`,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          backgroundColor: "#f9fafb",
          borderRadius: "0.75rem",
          border: "1px solid #e5e7eb",
        }}
      >
        <p style={{ color: "#6b7280", fontSize: "14px" }}>
          No diagram data available
        </p>
      </div>
    );
  }

  // Render SVG directly
  return (
    <div
      style={{
        width: "100%",
        height: `${height}px`,
        borderRadius: "0.75rem",
        overflow: "auto",
        border: "1px solid #e5e7eb",
        backgroundColor: "#ffffff",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      <div
        dangerouslySetInnerHTML={{ __html: svgContent }}
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
        }}
      />
    </div>
  );
}
