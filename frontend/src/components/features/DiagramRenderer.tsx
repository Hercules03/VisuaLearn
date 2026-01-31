import { useRef, useEffect } from "react";

interface DiagramRendererProps {
  xmlContent: string;
  height?: number;
}

export function DiagramRenderer({ xmlContent, height = 400 }: DiagramRendererProps) {
  const iframeRef = useRef<HTMLIFrameElement>(null);

  useEffect(() => {
    if (!iframeRef.current || !xmlContent) return;

    // Encode XML for URL
    const encodedXml = encodeURIComponent(xmlContent);

    // Create draw.io viewer URL with read-only parameters
    // noSaveBtn=1: hide save button
    // saveAndExit=0: disable save on exit
    // noExitBtn=1: hide exit button
    // embed=1: embedding mode
    // lightbox=1: lightbox mode (no UI clutter)
    const viewerUrl = `https://viewer.diagrams.net/?lightbox=1&embed=1&noSaveBtn=1&saveAndExit=0&noExitBtn=1#R${encodedXml}`;

    iframeRef.current.src = viewerUrl;
  }, [xmlContent]);

  return (
    <iframe
      ref={iframeRef}
      title="Educational Diagram"
      style={{
        width: "100%",
        height: `${height}px`,
        border: "none",
        borderRadius: "0.75rem",
        background: "white",
      }}
      allowFullScreen
      sandbox="allow-same-origin allow-popups"
    />
  );
}
