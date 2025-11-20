'use client';

import { DiagramStep } from '@/ai/flows/generate-interactive-diagram';
import { ChevronLeft, ChevronRight } from 'lucide-react';

interface TimelineControlProps {
  steps: DiagramStep[];
  currentStep: number;
  onStepChange: (stepIndex: number) => void;
}

export function TimelineControl({ steps, currentStep, onStepChange }: TimelineControlProps) {
  if (!steps || steps.length === 0) {
    return null;
  }

  const handlePrevious = () => {
    if (currentStep > 0) {
      onStepChange(currentStep - 1);
    }
  };

  const handleNext = () => {
    if (currentStep < steps.length - 1) {
      onStepChange(currentStep + 1);
    }
  };

  const handleSliderChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onStepChange(parseInt(e.target.value, 10));
  };

  const handleStepClick = (index: number) => {
    onStepChange(index);
  };

  const currentStepData = steps[currentStep];
  const progress = ((currentStep + 1) / steps.length) * 100;

  return (
    <div className="bg-white border-t border-gray-200 p-4 space-y-4">
      {/* Step Info */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900">
            {currentStepData?.title || 'Step'}
          </h3>
          <p className="text-xs text-gray-600 mt-1">
            Step {currentStep + 1} of {steps.length}
          </p>
        </div>
        <div className="text-xs font-medium text-gray-600 bg-gray-100 px-2 py-1 rounded">
          {Math.round(progress)}%
        </div>
      </div>

      {/* Slider */}
      <div className="space-y-2">
        <input
          type="range"
          min="0"
          max={steps.length - 1}
          value={currentStep}
          onChange={handleSliderChange}
          className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
          aria-label="Timeline scrubber"
        />
        <div className="flex justify-between text-xs text-gray-500 px-1">
          <span>Start</span>
          <span>End</span>
        </div>
      </div>

      {/* Step Description */}
      {currentStepData?.description && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
          <p className="text-sm text-blue-900">{currentStepData.description}</p>
        </div>
      )}

      {/* Mini Timeline / Step Navigation */}
      <div className="space-y-2">
        <h4 className="text-xs font-semibold text-gray-600 uppercase tracking-wide">Steps</h4>
        <div className="flex gap-1 overflow-x-auto pb-2">
          {steps.map((step, index) => (
            <button
              key={step.id}
              onClick={() => handleStepClick(index)}
              className={`
                flex-shrink-0 w-8 h-8 rounded-lg flex items-center justify-center font-medium text-xs transition
                ${
                  index === currentStep
                    ? 'bg-blue-600 text-white shadow-md'
                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }
                ${index < currentStep ? 'bg-opacity-50' : ''}
              `}
              title={step.title}
              aria-label={`Step ${index + 1}: ${step.title}`}
            >
              {index + 1}
            </button>
          ))}
        </div>
      </div>

      {/* Navigation Buttons */}
      <div className="flex gap-2">
        <button
          onClick={handlePrevious}
          disabled={currentStep === 0}
          className="flex-1 flex items-center justify-center gap-1 px-3 py-2 text-sm font-medium rounded-lg border border-gray-300 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition"
          aria-label="Previous step"
        >
          <ChevronLeft size={16} />
          <span className="hidden sm:inline">Previous</span>
        </button>
        <button
          onClick={handleNext}
          disabled={currentStep === steps.length - 1}
          className="flex-1 flex items-center justify-center gap-1 px-3 py-2 text-sm font-medium rounded-lg bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition"
          aria-label="Next step"
        >
          <span className="hidden sm:inline">Next</span>
          <ChevronRight size={16} />
        </button>
      </div>

      {/* Progress Bar */}
      <div className="w-full h-1 bg-gray-200 rounded-full overflow-hidden">
        <div
          className="h-full bg-blue-600 transition-all duration-300"
          style={{ width: `${progress}%` }}
        />
      </div>
    </div>
  );
}
