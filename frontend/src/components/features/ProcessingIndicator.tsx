import { cn } from "@/lib/utils";
import { Check, Loader2 } from "lucide-react";
import { motion } from "framer-motion";

export type ProcessingStep = 'analyzing' | 'planning' | 'generating' | 'reviewing' | 'completed';

interface ProcessingIndicatorProps {
  currentStep: ProcessingStep;
}

const STEPS = [
  { id: 'analyzing', label: 'Analyzing Concept' },
  { id: 'planning', label: 'Planning Structure' },
  { id: 'generating', label: 'Creating Visual' },
  { id: 'reviewing', label: 'Reviewing Quality' },
];

export function ProcessingIndicator({ currentStep }: ProcessingIndicatorProps) {
  const getStepStatus = (stepId: string) => {
    const stepIndex = STEPS.findIndex(s => s.id === stepId);
    const currentIndex = STEPS.findIndex(s => s.id === currentStep);
    
    if (currentStep === 'completed') return 'completed';
    if (stepIndex < currentIndex) return 'completed';
    if (stepIndex === currentIndex) return 'active';
    return 'pending';
  };

  return (
    <motion.div 
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="flex w-full flex-col gap-6 rounded-2xl border border-slate-200 bg-white/80 p-6 shadow-sm backdrop-blur-sm"
    >
      <div className="flex items-center gap-4">
        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-50 text-blue-600 shadow-sm ring-1 ring-blue-100">
          <Loader2 className="h-5 w-5 animate-spin" />
        </div>
        <div className="flex flex-col gap-0.5">
          <span className="font-semibold text-slate-900">Processing your request</span>
          <span className="text-xs text-slate-500">Generating the best educational diagram for you...</span>
        </div>
      </div>

      <div className="relative pl-5">
        {/* Connecting Line */}
        <div className="absolute left-[19px] top-2 h-[calc(100%-16px)] w-0.5 bg-slate-100" />

        <div className="space-y-6">
          {STEPS.map((step) => {
            const status = getStepStatus(step.id);
            return (
              <div key={step.id} className="relative flex items-center gap-4">
                <div className={cn(
                  "relative z-10 flex h-6 w-6 items-center justify-center rounded-full border-2 transition-all duration-300",
                  status === 'completed' ? "border-emerald-500 bg-emerald-500 text-white shadow-emerald-200" : 
                  status === 'active' ? "border-blue-500 bg-white text-blue-500 shadow-blue-200 scale-110" : 
                  "border-slate-200 bg-white text-slate-300"
                )}>
                  {status === 'completed' ? <Check className="h-3 w-3" /> : 
                   status === 'active' ? <div className="h-2 w-2 rounded-full bg-blue-500 animate-pulse" /> :
                   <div className="h-1.5 w-1.5 rounded-full bg-slate-200" />
                  }
                </div>
                <span className={cn(
                  "text-sm font-medium transition-colors duration-300",
                  status === 'completed' ? "text-emerald-700" : 
                  status === 'active' ? "text-blue-700" : 
                  "text-slate-400"
                )}>
                  {step.label}
                </span>
              </div>
            );
          })}
        </div>
      </div>
    </motion.div>
  );
}