import { Dialog, DialogContent, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import { TransformWrapper, TransformComponent } from "react-zoom-pan-pinch";
import { X, ZoomIn, ZoomOut, RotateCcw } from "lucide-react";
import { Button } from "@/components/ui/button";

interface DiagramDialogProps {
  isOpen: boolean;
  onClose: () => void;
  imageUrl: string;
}

export function DiagramDialog({ isOpen, onClose, imageUrl }: DiagramDialogProps) {
  return (
    <Dialog open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="max-w-[95vw] h-[90vh] p-0 overflow-hidden bg-slate-50 border-0">
        {/* Hidden accessible title */}
        <DialogTitle className="sr-only">Diagram View</DialogTitle>
        <DialogDescription className="sr-only">
          Interactive view of the generated diagram. Use controls to zoom and pan.
        </DialogDescription>

        <TransformWrapper
          initialScale={1}
          minScale={0.5}
          maxScale={4}
          centerOnInit
        >
          {({ zoomIn, zoomOut, resetTransform }) => (
            <div className="relative flex h-full w-full flex-col">
              {/* Toolbar */}
              <div className="absolute top-4 right-4 z-50 flex gap-2">
                <div className="flex rounded-md bg-white/90 shadow-sm border backdrop-blur-sm">
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => zoomIn()}
                    className="h-9 w-9 rounded-none first:rounded-l-md border-r hover:bg-slate-100"
                  >
                    <ZoomIn className="h-4 w-4" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => zoomOut()}
                    className="h-9 w-9 rounded-none border-r hover:bg-slate-100"
                  >
                    <ZoomOut className="h-4 w-4" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => resetTransform()}
                    className="h-9 w-9 rounded-none last:rounded-r-md hover:bg-slate-100"
                  >
                    <RotateCcw className="h-4 w-4" />
                  </Button>
                </div>
                
                <Button
                  variant="outline"
                  size="icon"
                  onClick={onClose}
                  className="h-9 w-9 rounded-full bg-white/90 shadow-sm hover:bg-slate-100 backdrop-blur-sm"
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>

              {/* Viewer */}
              <div className="flex-1 overflow-hidden bg-slate-100/50 cursor-move">
                <TransformComponent
                  wrapperClass="!w-full !h-full"
                  contentClass="!w-full !h-full flex items-center justify-center"
                >
                  <img
                    src={imageUrl}
                    alt="Diagram Fullscreen"
                    className="max-h-full max-w-full object-contain"
                  />
                </TransformComponent>
              </div>
            </div>
          )}
        </TransformWrapper>
      </DialogContent>
    </Dialog>
  );
}
