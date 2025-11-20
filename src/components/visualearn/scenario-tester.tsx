'use client';

import { useState } from 'react';
import { Scenario } from '@/ai/flows/generate-interactive-diagram';

interface ScenarioTesterProps {
  scenarios: Scenario[];
  onScenarioSelect: (scenarioName: string | null) => void;
}

export function ScenarioTester({ scenarios, onScenarioSelect }: ScenarioTesterProps) {
  const [selectedScenario, setSelectedScenario] = useState<string | null>(null);
  const [showDetails, setShowDetails] = useState(false);

  if (!scenarios || scenarios.length === 0) {
    return null;
  }

  const handleScenarioSelect = (scenarioName: string) => {
    if (selectedScenario === scenarioName) {
      // Deselect if clicking the same scenario
      setSelectedScenario(null);
      onScenarioSelect(null);
    } else {
      // Select new scenario
      setSelectedScenario(scenarioName);
      onScenarioSelect(scenarioName);
      setShowDetails(true);
    }
  };

  const getAnimationTypeIcon = (type: string) => {
    const icons: Record<string, string> = {
      overload: '🔥',
      failure: '💥',
      slow: '🐌',
      bottleneck: '⚠️',
    };
    return icons[type] || '📋';
  };

  const getAnimationTypeColor = (type: string) => {
    const colors: Record<string, string> = {
      overload: 'bg-red-100 text-red-800 hover:bg-red-200',
      failure: 'bg-rose-100 text-rose-800 hover:bg-rose-200',
      slow: 'bg-yellow-100 text-yellow-800 hover:bg-yellow-200',
      bottleneck: 'bg-orange-100 text-orange-800 hover:bg-orange-200',
    };
    return colors[type] || 'bg-gray-100 text-gray-800 hover:bg-gray-200';
  };

  const currentScenario = scenarios.find((s) => s.scenarioName === selectedScenario);

  return (
    <div className="bg-white border-t border-gray-200 p-4">
      {/* Title */}
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900">Test Scenarios</h3>
        <p className="text-xs text-gray-600 mt-1">Explore how the system responds to different conditions</p>
      </div>

      {/* Scenarios Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 mb-4">
        {scenarios.map((scenario) => (
          <button
            key={scenario.scenarioName}
            onClick={() => handleScenarioSelect(scenario.scenarioName)}
            className={`
              relative p-3 rounded-lg border-2 transition text-left
              ${
                selectedScenario === scenario.scenarioName
                  ? `border-blue-500 ${getAnimationTypeColor(scenario.visualization.animationType)}`
                  : 'border-gray-200 bg-white hover:border-gray-300'
              }
            `}
            title={scenario.description}
          >
            <div className="flex items-start gap-2">
              <span className="text-lg flex-shrink-0">
                {getAnimationTypeIcon(scenario.visualization.animationType)}
              </span>
              <div className="flex-1 min-w-0">
                <h4 className="text-sm font-medium text-gray-900 truncate">
                  {scenario.scenarioName}
                </h4>
                <p className="text-xs text-gray-600 line-clamp-1 mt-0.5">
                  {scenario.description}
                </p>
              </div>
            </div>
            {selectedScenario === scenario.scenarioName && (
              <div className="absolute top-2 right-2 w-2 h-2 bg-blue-600 rounded-full" />
            )}
          </button>
        ))}
      </div>

      {/* Details Panel */}
      {currentScenario && showDetails && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 mt-4">
          <div className="flex items-start justify-between mb-3">
            <div>
              <h4 className="font-semibold text-blue-900">
                {getAnimationTypeIcon(currentScenario.visualization.animationType)}{' '}
                {currentScenario.scenarioName}
              </h4>
              <p className="text-sm text-blue-800 mt-1">{currentScenario.description}</p>
            </div>
            <button
              onClick={() => setShowDetails(false)}
              className="text-blue-600 hover:text-blue-800 text-lg leading-none flex-shrink-0"
              aria-label="Close details"
            >
              ✕
            </button>
          </div>

          <div className="border-t border-blue-200 pt-3 space-y-2">
            <div>
              <h5 className="text-xs font-semibold text-blue-900 uppercase tracking-wide mb-1">
                What You'll Learn
              </h5>
              <p className="text-sm text-blue-800">{currentScenario.lessonLearned}</p>
            </div>

            {(currentScenario.visualization.highlightComponents.length > 0 ||
              currentScenario.visualization.dimComponents.length > 0) && (
              <div>
                <h5 className="text-xs font-semibold text-blue-900 uppercase tracking-wide mb-1">
                  Affected Components
                </h5>
                <div className="flex flex-wrap gap-1">
                  {currentScenario.visualization.highlightComponents.map((compId) => (
                    <span key={compId} className="px-2 py-1 bg-blue-200 text-blue-900 rounded text-xs font-medium">
                      {compId} (↑)
                    </span>
                  ))}
                  {currentScenario.visualization.dimComponents.map((compId) => (
                    <span key={compId} className="px-2 py-1 bg-blue-100 text-blue-700 rounded text-xs">
                      {compId} (↓)
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Reset Button */}
      {selectedScenario && (
        <div className="mt-3 flex gap-2">
          <button
            onClick={() => {
              setSelectedScenario(null);
              onScenarioSelect(null);
              setShowDetails(false);
            }}
            className="flex-1 px-3 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded transition"
          >
            Reset Scenario
          </button>
        </div>
      )}
    </div>
  );
}
