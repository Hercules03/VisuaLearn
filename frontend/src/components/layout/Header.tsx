import { Button } from "@/components/ui/button";
import { RefreshCw, Sparkles } from "lucide-react";

interface HeaderProps {
  onReset: () => void;
}

export function Header({ onReset }: HeaderProps) {
  return (
    <header className="sticky top-0 z-50 w-full border-b border-white/40 bg-white/60 px-4 backdrop-blur-xl supports-[backdrop-filter]:bg-white/40 md:px-6 shadow-sm shadow-slate-200/20 transition-all">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between">
        <div className="flex items-center gap-2.5 group cursor-default">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-blue-600 to-indigo-600 shadow-lg shadow-blue-500/20 transition-transform group-hover:scale-105 group-hover:rotate-3">
            <Sparkles className="h-5 w-5 text-white" />
          </div>
          <h1 className="text-xl font-bold tracking-tight text-slate-900 group-hover:text-blue-700 transition-colors">
            Visua<span className="text-blue-600">Learn</span>
          </h1>
        </div>
        <Button 
          variant="outline" 
          size="sm" 
          onClick={onReset} 
          className="gap-2 border-slate-200 bg-white/50 text-slate-600 hover:bg-white hover:text-blue-600 hover:border-blue-200 shadow-sm transition-all"
        >
          <RefreshCw className="h-4 w-4" />
          <span className="hidden sm:inline">New Chat</span>
        </Button>
      </div>
    </header>
  );
}