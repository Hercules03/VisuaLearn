'use client';

import React, { useEffect, useRef, useState } from 'react';
import Image from 'next/image';
import { Card, CardContent } from '@/components/ui/card';
import { PlaceHolderImages } from '@/lib/placeholder-images';
import type { DiagramContent, DiagramComponent } from '@/ai/flows/generate-interactive-diagram';
import { ComponentInspectorPanel } from './component-inspector-panel';
import { ScenarioTester } from './scenario-tester';
import { ComplexityToggle } from './complexity-toggle';

interface DiagramDisplayProps {
  svgContent: string | null;
  diagramData: DiagramContent | null;
  isLoading: boolean;
  currentStep: number;
  isSimulating: boolean;
}

export function DiagramDisplay({
  svgContent,
  diagramData,
  isLoading,
  currentStep,
  isSimulating,
}: DiagramDisplayProps) {
  const svgContainerRef = useRef<HTMLDivElement>(null);
  const [hoveredComponent, setHoveredComponent] = useState<string | null>(null);
  const [selectedComponent, setSelectedComponent] = useState<DiagramComponent | null>(null);
  const [activeScenario, setActiveScenario] = useState<string | null>(null);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const placeholder = PlaceHolderImages.find(
    (p) => p.id === 'visualearn-placeholder'
  );

  // Apply visual highlights and interactivity based on current step and hover state
  useEffect(() => {
    const container = svgContainerRef.current;
    if (!container || !diagramData) return;

    // Render SVG content if it changed
    if (svgContent && container.innerHTML !== svgContent) {
      container.innerHTML = svgContent;
      const svg = container.querySelector('svg');
      if (svg) {
        svg.setAttribute('width', '100%');
        svg.setAttribute('height', '100%');
        svg.style.maxWidth = '100%';
        svg.style.height = 'auto';
      }
    }

    // Apply complexity layer visibility
    const advancedElements = container.querySelectorAll('[data-layer="advanced"]');
    advancedElements.forEach((el) => {
      if (showAdvanced) {
        (el as HTMLElement).style.display = '';
      } else {
        (el as HTMLElement).style.display = 'none';
      }
    });

    // Apply scenario visualization
    if (activeScenario) {
      const scenario = diagramData.scenarios?.find(s => s.scenarioName === activeScenario);
      if (scenario) {
        // Highlight impacted components
        scenario.visualization.highlightComponents.forEach(componentId => {
          const component = diagramData.components.find(c => c.id === componentId);
          if (component) {
            const elements = container.querySelectorAll(component.svgSelector);
            elements.forEach(el => {
              el.classList.add(`scenario-${scenario.visualization.animationType}`);
            });
          }
        });
        // Dim specified components
        scenario.visualization.dimComponents.forEach(componentId => {
          const component = diagramData.components.find(c => c.id === componentId);
          if (component) {
            const elements = container.querySelectorAll(component.svgSelector);
            elements.forEach(el => {
              el.classList.add('scenario-dim');
            });
          }
        });
      }
    } else {
      // Clear scenario classes
      container.querySelectorAll('[class*="scenario-"]').forEach(el => {
        el.classList.remove('scenario-overload', 'scenario-failure', 'scenario-slow', 'scenario-bottleneck', 'scenario-dim');
      });
    }

    if (!svgContent) {
      container.innerHTML = '';
      return;
    }

    // Update step highlighting
    container.querySelectorAll('[data-step-active="true"]').forEach((el) => {
      el.setAttribute('data-step-active', 'false');
    });

    if (currentStep >= 0 && diagramData.steps[currentStep]) {
      const step = diagramData.steps[currentStep];

      // Highlight components active in this step
      if (step.activeComponentIds && step.activeComponentIds.length > 0) {
        step.activeComponentIds.forEach((componentId) => {
          const component = diagramData.components.find(c => c.id === componentId);
          if (component) {
            try {
              const element = container.querySelector(component.svgSelector);
              if (element) {
                element.setAttribute('data-step-active', 'true');
              }
            } catch (e) {
              console.warn(`Invalid selector "${component.svgSelector}" for component ${componentId}`);
            }
          }
        });
      }

      // Also try highlighting by step ID (legacy support)
      const stepElement = container.querySelector(`#step-${currentStep}`);
      if (stepElement) {
        stepElement.classList.add('highlighted');
      }
    }

    // Handle hover component highlighting
    if (hoveredComponent) {
      const component = diagramData.components.find(c => c.id === hoveredComponent);
      if (component) {
        try {
          const element = container.querySelector(component.svgSelector);
          if (element) {
            element.setAttribute('data-component-hover', 'true');
          }
        } catch (e) {
          console.warn(`Invalid selector for component ${hoveredComponent}`);
        }
      }
    } else {
      // Clear all hover states
      container.querySelectorAll('[data-component-hover="true"]').forEach((el) => {
        el.setAttribute('data-component-hover', 'false');
      });
    }
  }, [svgContent, diagramData, currentStep, hoveredComponent, isLoading, showAdvanced, activeScenario]);

  // Setup component hover tooltips and click handlers
  useEffect(() => {
    const container = svgContainerRef.current;
    if (!container || !diagramData || !svgContent) return;

    // Store event handler references for cleanup
    const listenerMap = new Map<
      Element,
      { enter: EventListener; leave: EventListener; click: EventListener }
    >();

    // Attach hover listeners to each component
    diagramData.components.forEach((component) => {
      try {
        const elements = container.querySelectorAll(component.svgSelector);
        elements.forEach((element) => {
          const enterHandler = () => {
            setHoveredComponent(component.id);
          };
          const leaveHandler = () => {
            setHoveredComponent(null);
          };
          const clickHandler = () => {
            setSelectedComponent(component);
          };

          element.addEventListener('mouseenter', enterHandler);
          element.addEventListener('mouseleave', leaveHandler);
          element.addEventListener('click', clickHandler);
          (element as HTMLElement).style.cursor = 'pointer';
          listenerMap.set(element, { enter: enterHandler, leave: leaveHandler, click: clickHandler });
        });
      } catch (e) {
        // Selector parsing error - log but continue
        console.warn(`Could not attach listeners to selector "${component.svgSelector}"`);
      }
    });

    return () => {
      // Cleanup listeners with correct references
      listenerMap.forEach((handlers, element) => {
        element.removeEventListener('mouseenter', handlers.enter);
        element.removeEventListener('mouseleave', handlers.leave);
        element.removeEventListener('click', handlers.click);
      });
    };
  }, [diagramData, svgContent]);

  return (
    <div className="flex-1 w-full h-full flex flex-col overflow-hidden">
      {/* Main diagram area with toolbar */}
      <Card className="flex-1 w-full flex flex-col overflow-hidden">
        {/* Toolbar */}
        {svgContent && diagramData && !isLoading && (
          <div className="border-b border-gray-200 bg-gray-50 p-3 flex items-center justify-between gap-4 flex-wrap">
            <ComplexityToggle showAdvanced={showAdvanced} onToggle={setShowAdvanced} />
            {diagramData.timeEstimates && (
              <div className="text-xs text-gray-600">
                ⏱️ Quick view: {diagramData.timeEstimates.quickView}m |{' '}
                Deep: {diagramData.timeEstimates.deepUnderstanding}m
              </div>
            )}
          </div>
        )}

        <CardContent className="flex-1 p-4 md:p-6 flex flex-col items-center justify-center relative overflow-auto">
          {isLoading ? (
            <div className="w-full h-full flex items-center justify-center">
              <svg
                className="animate-spin h-12 w-12 text-primary"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                ></circle>
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                ></path>
              </svg>
            </div>
          ) : svgContent && diagramData ? (
            <>
              {/* SVG Container */}
              <div ref={svgContainerRef} className="w-full h-full flex-1" />

              {/* Hover Tooltip - appears when hovering components */}
              {hoveredComponent && (
                <div className="absolute bottom-4 left-4 right-4 bg-black/80 text-white p-3 rounded-lg shadow-lg z-40 max-w-xs">
                  {diagramData.components.find(c => c.id === hoveredComponent) && (
                    <>
                      <h4 className="font-semibold text-sm">
                        {diagramData.components.find(c => c.id === hoveredComponent)?.label}
                      </h4>
                      <p className="text-xs text-gray-200 mt-1">
                        {diagramData.components.find(c => c.id === hoveredComponent)?.description}
                      </p>
                      <p className="text-xs text-gray-300 mt-2">Click to inspect</p>
                    </>
                  )}
                </div>
              )}
            </>
          ) : (
            <div className="text-center text-muted-foreground flex flex-col items-center gap-4 animate-in fade-in">
              {placeholder && (
                <Image
                  src={placeholder.imageUrl}
                  alt={placeholder.description}
                  width={400}
                  height={300}
                  className="rounded-lg object-cover shadow-md"
                  data-ai-hint={placeholder.imageHint}
                  priority
                />
              )}
              <h3 className="text-lg font-semibold font-headline text-foreground">
                Welcome to VisuaLearn
              </h3>
              <p className="max-w-md">
                Enter a concept you want to learn about, and we'll generate an
                interactive diagram to explain it.
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Interactive controls panel below diagram */}
      {svgContent && diagramData && !isLoading && (
        <div className="bg-white border-t border-gray-200 overflow-y-auto max-h-64">
          {/* Scenario Tester */}
          {diagramData.scenarios && diagramData.scenarios.length > 0 && (
            <ScenarioTester
              scenarios={diagramData.scenarios}
              onScenarioSelect={setActiveScenario}
            />
          )}
        </div>
      )}

      {/* Component Inspector Panel (right sidebar) */}
      <ComponentInspectorPanel
        component={selectedComponent}
        onClose={() => setSelectedComponent(null)}
      />
    </div>
  );
}
