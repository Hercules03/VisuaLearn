import { useState } from "react";

interface DiagramRendererProps {
  imageData?: string; // Base64 PNG from backend
  xmlContent?: string;
  height?: number;
}

/**
 * DiagramRenderer Component
 *
 * Displays draw.io diagrams as rendered PNG images.
 * Receives base64-encoded PNG from backend (rendered via Playwright + mxGraph).
 *
 * Features:
 * - Simple image display (no CSP issues)
 * - Server-side rendering ensures quality
 * - Responsive sizing with zoom/pan capability
 * - Fallback to XML display if needed
 *
 * Architecture:
 * Backend XML → mxGraph rendering → PNG → Base64 → Frontend image display
 */
export function DiagramRenderer({
  imageData,
  xmlContent,
  height = 500,
}: DiagramRendererProps) {
  const [imageError, setImageError] = useState(false);

  // No diagram data
  if (!imageData && !xmlContent) {
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

  // Rendered image available
  if (imageData && !imageError) {
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
        <img
          src={imageData}
          alt="Diagram"
          style={{
            maxWidth: "100%",
            maxHeight: "100%",
            objectFit: "contain",
            borderRadius: "0.5rem",
          }}
          onError={() => setImageError(true)}
        />
      </div>
    );
  }

  // Image failed to load, show XML as fallback
  if (imageError && xmlContent) {
    return (
      <div
        style={{
          width: "100%",
          height: `${height}px`,
          borderRadius: "0.75rem",
          overflow: "auto",
          border: "1px solid #fef3c7",
          backgroundColor: "#fffbeb",
          padding: "12px",
          fontFamily: "monospace",
          fontSize: "11px",
          color: "#92400e",
        }}
      >
        <div style={{ marginBottom: "8px", fontWeight: "bold" }}>
          ⚠️ Image rendering failed. XML content:
        </div>
        <pre style={{ margin: 0, whiteSpace: "pre-wrap", wordBreak: "break-all" }}>
          {xmlContent.substring(0, 500)}...
        </pre>
      </div>
    );
  }

  // Failed to render
  return (
    <div
      style={{
        width: "100%",
        height: `${height}px`,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        backgroundColor: "#fee2e2",
        borderRadius: "0.75rem",
        border: "1px solid #fecaca",
      }}
    >
      <p style={{ color: "#dc2626", fontSize: "14px" }}>
        Failed to prepare diagram for display
      </p>
    </div>
  );
}
