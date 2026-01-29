import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Download, ExternalLink, Maximize2, FileCode } from "lucide-react";
import { DiagramDialog } from "./DiagramDialog";
import { downloadFile } from "@/lib/api";

interface DiagramCardProps {
  image: string;
  exportUrls: {
    png: string;
    svg: string;
    xml: string;
  };
}

export function DiagramCard({ image, exportUrls }: DiagramCardProps) {
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [isDownloading, setIsDownloading] = useState(false);
  const [downloadError, setDownloadError] = useState<string | null>(null);

  const handleDownload = async (url: string, format: 'png' | 'svg' | 'xml') => {
    setIsDownloading(true);
    setDownloadError(null);

    try {
      // Extract filename from URL (e.g., "/api/export/uuid.png" → "uuid.png")
      const filename = url.split('/').pop();
      if (!filename) {
        throw new Error('Invalid export URL');
      }

      // Call the downloadFile function from API
      const blob = await downloadFile(filename);

      // Create download link
      const downloadUrl = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = downloadUrl;
      link.download = `diagram.${format}`;

      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(downloadUrl);
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : 'Download failed';
      setDownloadError(errorMsg);
      console.error('Download error:', error);
    } finally {
      setIsDownloading(false);
    }
  };

  return (
    <>
      <Card className="mt-6 overflow-hidden border border-slate-200 bg-white shadow-lg shadow-slate-200/50 rounded-xl transition-all hover:shadow-xl hover:shadow-slate-300/40">
        <div 
          className="group relative aspect-video w-full cursor-zoom-in bg-slate-50/50"
          onClick={() => setIsDialogOpen(true)}
        >
          {/* Subtle grid pattern background */}
          <div className="absolute inset-0 bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:24px_24px]"></div>
          
          <img
            src={image}
            alt="Educational Diagram"
            className="relative z-10 h-full w-full object-contain p-6 transition-transform duration-300 group-hover:scale-[1.02]"
          />
          
          <div className="absolute inset-0 z-20 flex items-center justify-center bg-black/5 opacity-0 backdrop-blur-[1px] transition-opacity duration-200 group-hover:opacity-100">
            <Button size="sm" variant="secondary" className="shadow-lg font-medium bg-white/90 text-slate-700 hover:bg-white">
              <Maximize2 className="mr-2 h-4 w-4" />
              Click to Expand
            </Button>
          </div>
        </div>
        
        <div className="flex flex-col gap-3 border-t border-slate-100 bg-slate-50/30 p-4 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex items-center gap-2 text-xs font-semibold text-slate-500 uppercase tracking-wider">
             <div className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse"></div>
             Generated Diagram
          </div>
          <div className="flex flex-wrap gap-2">
            <Button
              variant="outline"
              size="sm"
              disabled={isDownloading}
              className="h-8 border-slate-200 bg-white px-3 text-xs font-medium text-slate-600 hover:border-blue-200 hover:bg-blue-50 hover:text-blue-700 shadow-sm disabled:opacity-50 disabled:cursor-not-allowed"
              onClick={() => handleDownload(exportUrls.png, 'png')}
            >
              <Download className="mr-1.5 h-3.5 w-3.5" />
              PNG
            </Button>
            <Button
              variant="outline"
              size="sm"
              disabled={isDownloading}
              className="h-8 border-slate-200 bg-white px-3 text-xs font-medium text-slate-600 hover:border-blue-200 hover:bg-blue-50 hover:text-blue-700 shadow-sm disabled:opacity-50 disabled:cursor-not-allowed"
              onClick={() => handleDownload(exportUrls.svg, 'svg')}
            >
              <FileCode className="mr-1.5 h-3.5 w-3.5" />
              SVG
            </Button>
            <Button
              variant="outline"
              size="sm"
              disabled={isDownloading}
              className="h-8 border-slate-200 bg-white px-3 text-xs font-medium text-slate-600 hover:border-blue-200 hover:bg-blue-50 hover:text-blue-700 shadow-sm disabled:opacity-50 disabled:cursor-not-allowed"
              onClick={() => handleDownload(exportUrls.xml, 'xml')}
            >
              <ExternalLink className="mr-1.5 h-3.5 w-3.5" />
              XML
            </Button>
          </div>
          {downloadError && (
            <div className="mt-2 text-xs text-red-600 bg-red-50 p-2 rounded border border-red-200">
              {downloadError}
            </div>
          )}
        </div>
      </Card>

      <DiagramDialog 
        isOpen={isDialogOpen} 
        onClose={() => setIsDialogOpen(false)} 
        imageUrl={image} 
      />
    </>
  );
}