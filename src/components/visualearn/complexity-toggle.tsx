'use client';

import { useEffect, useState } from 'react';
import { Eye, EyeOff } from 'lucide-react';

interface ComplexityToggleProps {
  showAdvanced: boolean;
  onToggle: (show: boolean) => void;
}

export function ComplexityToggle({ showAdvanced, onToggle }: ComplexityToggleProps) {
  const [isInitialized, setIsInitialized] = useState(false);

  useEffect(() => {
    // Load preference from localStorage on mount
    if (typeof window !== 'undefined') {
      const saved = localStorage.getItem('diagram-show-advanced');
      if (saved !== null) {
        const shouldShow = saved === 'true';
        onToggle(shouldShow);
      }
      setIsInitialized(true);
    }
  }, [onToggle]);

  const handleToggle = () => {
    const newValue = !showAdvanced;
    onToggle(newValue);

    // Save preference to localStorage
    if (typeof window !== 'undefined') {
      localStorage.setItem('diagram-show-advanced', String(newValue));
    }
  };

  if (!isInitialized) {
    return null;
  }

  return (
    <div className="inline-flex items-center gap-2 bg-white border border-gray-300 rounded-lg p-2">
      <button
        onClick={handleToggle}
        className={`flex items-center gap-2 px-3 py-1.5 rounded transition font-medium text-sm ${
          showAdvanced
            ? 'bg-blue-100 text-blue-700 hover:bg-blue-200'
            : 'text-gray-700 hover:bg-gray-100'
        }`}
        title={showAdvanced ? 'Hide advanced components' : 'Show advanced components'}
      >
        {showAdvanced ? <Eye size={16} /> : <EyeOff size={16} />}
        <span>
          {showAdvanced ? 'Advanced On' : 'Advanced Off'}
        </span>
      </button>
      <div className="w-0.5 h-4 bg-gray-300" />
      <span className="text-xs text-gray-600 px-2">
        {showAdvanced ? 'Showing all details' : 'Core components only'}
      </span>
    </div>
  );
}
