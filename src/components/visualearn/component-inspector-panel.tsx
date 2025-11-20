'use client';

import { useState } from 'react';
import { DiagramComponent, RealWorldExample } from '@/ai/flows/generate-interactive-diagram';
import { X, ExternalLink } from 'lucide-react';

interface ComponentInspectorPanelProps {
  component: DiagramComponent | null;
  onClose: () => void;
}

type TabType = 'overview' | 'howItWorks' | 'realWorld' | 'failures';

export function ComponentInspectorPanel({
  component,
  onClose,
}: ComponentInspectorPanelProps) {
  const [activeTab, setActiveTab] = useState<TabType>('overview');

  if (!component) {
    return null;
  }

  const tabs: { id: TabType; label: string; icon: string }[] = [
    { id: 'overview', label: 'Overview', icon: 'ℹ️' },
    { id: 'howItWorks', label: 'How It Works', icon: '⚙️' },
    { id: 'realWorld', label: 'Real-World', icon: '🌍' },
    { id: 'failures', label: 'Failures', icon: '⚠️' },
  ];

  const getCategoryColor = (category: string) => {
    const colors: Record<string, string> = {
      control: 'bg-blue-100 text-blue-800',
      input: 'bg-green-100 text-green-800',
      output: 'bg-purple-100 text-purple-800',
      process: 'bg-orange-100 text-orange-800',
      sensor: 'bg-red-100 text-red-800',
    };
    return colors[category] || 'bg-gray-100 text-gray-800';
  };

  const renderOverview = () => (
    <div className="space-y-4">
      <div>
        <h3 className="text-sm font-semibold text-gray-600 mb-2">Description</h3>
        <p className="text-gray-700">{component.description}</p>
      </div>

      <div>
        <h3 className="text-sm font-semibold text-gray-600 mb-2">Category</h3>
        <span className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${getCategoryColor(component.category)}`}>
          {component.category.charAt(0).toUpperCase() + component.category.slice(1)}
        </span>
      </div>

      {component.metrics && (
        <div className="bg-gray-50 p-3 rounded-lg space-y-2">
          <h3 className="text-sm font-semibold text-gray-600">Performance Metrics</h3>
          {component.metrics.throughput && (
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Throughput:</span>
              <span className="font-medium text-gray-900">{component.metrics.throughput}</span>
            </div>
          )}
          {component.metrics.latency && (
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Latency:</span>
              <span className="font-medium text-gray-900">{component.metrics.latency}</span>
            </div>
          )}
          {component.metrics.criticality && (
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Criticality:</span>
              <span className={`font-medium ${
                component.metrics.criticality === 'essential' ? 'text-red-600' :
                component.metrics.criticality === 'important' ? 'text-orange-600' :
                'text-blue-600'
              }`}>
                {component.metrics.criticality.charAt(0).toUpperCase() + component.metrics.criticality.slice(1)}
              </span>
            </div>
          )}
        </div>
      )}
    </div>
  );

  const renderHowItWorks = () => (
    <div className="space-y-4">
      {component.detailedExplanation && (
        <div>
          <h3 className="text-sm font-semibold text-gray-600 mb-2">How It Works</h3>
          <p className="text-gray-700 leading-relaxed">{component.detailedExplanation}</p>
        </div>
      )}

      {component.inputs && component.inputs.length > 0 && (
        <div>
          <h3 className="text-sm font-semibold text-gray-600 mb-2 flex items-center gap-1">
            <span>📥</span> Inputs
          </h3>
          <ul className="space-y-1">
            {component.inputs.map((input, idx) => (
              <li key={idx} className="text-sm text-gray-700 flex items-start gap-2">
                <span className="text-gray-400 mt-0.5">•</span>
                <span>{input}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {component.outputs && component.outputs.length > 0 && (
        <div>
          <h3 className="text-sm font-semibold text-gray-600 mb-2 flex items-center gap-1">
            <span>📤</span> Outputs
          </h3>
          <ul className="space-y-1">
            {component.outputs.map((output, idx) => (
              <li key={idx} className="text-sm text-gray-700 flex items-start gap-2">
                <span className="text-gray-400 mt-0.5">•</span>
                <span>{output}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );

  const renderRealWorld = () => (
    <div className="space-y-3">
      {component.realWorldExamples && component.realWorldExamples.length > 0 ? (
        component.realWorldExamples.map((example, idx) => (
          <div key={idx} className="border border-gray-200 rounded-lg p-3 hover:border-gray-300 transition">
            <div className="flex items-start justify-between">
              <div>
                <h4 className="font-semibold text-gray-900 text-sm">{example.name}</h4>
                <p className="text-xs text-gray-600 mt-1">{example.technology}</p>
              </div>
              {example.link && (
                <a
                  href={example.link}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:text-blue-800 flex-shrink-0"
                  title="View documentation"
                >
                  <ExternalLink size={16} />
                </a>
              )}
            </div>
          </div>
        ))
      ) : (
        <p className="text-sm text-gray-500">No real-world examples available</p>
      )}
    </div>
  );

  const renderFailures = () => (
    <div className="space-y-4">
      {component.failureMode && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-3">
          <h3 className="text-sm font-semibold text-red-900 mb-2">Failure Mode</h3>
          <p className="text-sm text-red-800">{component.failureMode}</p>
        </div>
      )}

      {component.failureRecovery && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-3">
          <h3 className="text-sm font-semibold text-green-900 mb-2">Recovery Strategy</h3>
          <p className="text-sm text-green-800">{component.failureRecovery}</p>
        </div>
      )}

      {!component.failureMode && !component.failureRecovery && (
        <p className="text-sm text-gray-500">No failure information available</p>
      )}
    </div>
  );

  const renderTabContent = () => {
    switch (activeTab) {
      case 'overview':
        return renderOverview();
      case 'howItWorks':
        return renderHowItWorks();
      case 'realWorld':
        return renderRealWorld();
      case 'failures':
        return renderFailures();
      default:
        return null;
    }
  };

  return (
    <div className="fixed inset-y-0 right-0 w-full sm:w-96 bg-white border-l border-gray-200 shadow-lg z-50 flex flex-col overflow-hidden">
      {/* Header */}
      <div className="flex-shrink-0 border-b border-gray-200 bg-gray-50 px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-bold text-gray-900">{component.label}</h2>
            <p className="text-xs text-gray-500 mt-1 font-mono">{component.id}</p>
          </div>
          <button
            onClick={onClose}
            className="p-1 hover:bg-gray-200 rounded transition"
            aria-label="Close inspector"
          >
            <X size={20} className="text-gray-600" />
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex-shrink-0 border-b border-gray-200 px-6 mt-4">
        <div className="flex gap-2 -mb-px">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`text-sm font-medium px-3 py-2 border-b-2 transition ${
                activeTab === tab.id
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-600 hover:text-gray-900'
              }`}
              title={tab.label}
            >
              <span>{tab.icon}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto px-6 py-4">{renderTabContent()}</div>
    </div>
  );
}
