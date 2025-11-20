/**
 * Diagram validation utilities - server-side only
 * This runs on the server during diagram generation, not on the client
 */

import { z } from 'zod';
import type {
  DiagramContent,
  DiagramComponent,
  DiagramStep,
  DataFlow,
  Scenario,
  Connection
} from '@/ai/flows/generate-interactive-diagram';

/**
 * Validates diagram schema and returns detailed error messages
 * Raises errors via return object (no exceptions)
 */
export function validateDiagramSchema(diagramData: DiagramContent): { valid: boolean; error?: string } {
  try {
    // Check components exist
    if (!diagramData.components || diagramData.components.length === 0) {
      return { valid: false, error: 'Diagram must have at least one component defined.' };
    }

    // Check steps exist
    if (!diagramData.steps || diagramData.steps.length === 0) {
      return { valid: false, error: 'Diagram must have at least one step defined.' };
    }

    // Validate component IDs are unique
    const componentIds = new Set<string>();
    for (const component of diagramData.components) {
      if (!component.id) {
        return { valid: false, error: 'All components must have an id field.' };
      }
      if (componentIds.has(component.id)) {
        return { valid: false, error: `Component ID "${component.id}" is not unique.` };
      }
      componentIds.add(component.id);

      // Validate required component fields
      if (!component.label) {
        return { valid: false, error: `Component "${component.id}" must have a label.` };
      }
      if (!component.description) {
        return { valid: false, error: `Component "${component.id}" must have a description.` };
      }
      if (!component.svgSelector) {
        return { valid: false, error: `Component "${component.id}" must have an svgSelector.` };
      }
    }

    // Validate steps
    const stepIds = new Set<string>();
    for (let i = 0; i < diagramData.steps.length; i++) {
      const step = diagramData.steps[i];

      if (!step.id) {
        return { valid: false, error: `Step at index ${i} must have an id field.` };
      }

      if (stepIds.has(step.id)) {
        return { valid: false, error: `Step ID "${step.id}" is not unique.` };
      }
      stepIds.add(step.id);

      if (!step.title) {
        return { valid: false, error: `Step "${step.id}" must have a title.` };
      }

      if (!step.description) {
        return { valid: false, error: `Step "${step.id}" must have a description.` };
      }

      // Validate activeComponentIds reference existing components
      if (step.activeComponentIds && step.activeComponentIds.length > 0) {
        for (const componentId of step.activeComponentIds) {
          if (!componentIds.has(componentId)) {
            return {
              valid: false,
              error: `Step "${step.id}" references non-existent component "${componentId}".`,
            };
          }
        }
      }

      // Validate animation timing if present
      if (step.animationTiming) {
        if (step.animationTiming.duration < 100 || step.animationTiming.duration > 5000) {
          return {
            valid: false,
            error: `Step "${step.id}" animation duration must be between 100-5000ms.`,
          };
        }
      }
    }

    // Validate metadata
    if (!diagramData.metadata) {
      return { valid: false, error: 'Diagram must have metadata.' };
    }

    if (!diagramData.metadata.conceptName) {
      return { valid: false, error: 'Metadata must have a conceptName.' };
    }

    if (typeof diagramData.metadata.totalDuration !== 'number' || diagramData.metadata.totalDuration <= 0) {
      return { valid: false, error: 'Metadata must have a valid totalDuration (> 0).' };
    }

    // Validate data flows if present
    if (diagramData.steps) {
      for (const step of diagramData.steps) {
        if (step.dataFlows && step.dataFlows.length > 0) {
          for (const flow of step.dataFlows) {
            if (!componentIds.has(flow.fromComponent)) {
              return {
                valid: false,
                error: `Step "${step.id}" data flow references non-existent source component "${flow.fromComponent}".`,
              };
            }
            if (!componentIds.has(flow.toComponent)) {
              return {
                valid: false,
                error: `Step "${step.id}" data flow references non-existent destination component "${flow.toComponent}".`,
              };
            }
          }
        }
      }
    }

    // Validate scenarios if present
    if (diagramData.scenarios && diagramData.scenarios.length > 0) {
      for (const scenario of diagramData.scenarios) {
        if (!scenario.scenarioName) {
          return { valid: false, error: 'Scenario must have a scenarioName.' };
        }
        if (!scenario.description) {
          return { valid: false, error: `Scenario "${scenario.scenarioName}" must have a description.` };
        }
        if (!scenario.visualization || !scenario.visualization.animationType) {
          return { valid: false, error: `Scenario "${scenario.scenarioName}" must have a visualization with animationType.` };
        }

        // Validate scenario component references
        if (scenario.impactedComponents) {
          for (const componentId of scenario.impactedComponents) {
            if (!componentIds.has(componentId)) {
              return {
                valid: false,
                error: `Scenario "${scenario.scenarioName}" references non-existent component "${componentId}".`,
              };
            }
          }
        }
        if (scenario.visualization.highlightComponents) {
          for (const componentId of scenario.visualization.highlightComponents) {
            if (!componentIds.has(componentId)) {
              return {
                valid: false,
                error: `Scenario "${scenario.scenarioName}" highlight references non-existent component "${componentId}".`,
              };
            }
          }
        }
        if (scenario.visualization.dimComponents) {
          for (const componentId of scenario.visualization.dimComponents) {
            if (!componentIds.has(componentId)) {
              return {
                valid: false,
                error: `Scenario "${scenario.scenarioName}" dim references non-existent component "${componentId}".`,
              };
            }
          }
        }
      }
    }

    // Validate connections if present
    if (diagramData.connections && diagramData.connections.length > 0) {
      for (const connection of diagramData.connections) {
        if (!componentIds.has(connection.fromComponent)) {
          return {
            valid: false,
            error: `Connection references non-existent source component "${connection.fromComponent}".`,
          };
        }
        if (!componentIds.has(connection.toComponent)) {
          return {
            valid: false,
            error: `Connection references non-existent destination component "${connection.toComponent}".`,
          };
        }
      }
    }

    // Validate time estimates if present
    if (diagramData.timeEstimates) {
      if (diagramData.timeEstimates.quickView && (diagramData.timeEstimates.quickView < 1 || diagramData.timeEstimates.quickView > 60)) {
        return {
          valid: false,
          error: 'Time estimate for quickView must be between 1-60 minutes.',
        };
      }
      if (diagramData.timeEstimates.deepUnderstanding && (diagramData.timeEstimates.deepUnderstanding < 1 || diagramData.timeEstimates.deepUnderstanding > 60)) {
        return {
          valid: false,
          error: 'Time estimate for deepUnderstanding must be between 1-60 minutes.',
        };
      }
      if (diagramData.timeEstimates.masteryChallenges && (diagramData.timeEstimates.masteryChallenges < 1 || diagramData.timeEstimates.masteryChallenges > 120)) {
        return {
          valid: false,
          error: 'Time estimate for masteryChallenges must be between 1-120 minutes.',
        };
      }
    }

    // Validate concept difficulty if present
    if (diagramData.conceptDifficulty && (diagramData.conceptDifficulty < 1 || diagramData.conceptDifficulty > 10)) {
      return {
        valid: false,
        error: 'Concept difficulty must be between 1-10.',
      };
    }

    // Validate quality score if present
    if (diagramData.qualityScore && (diagramData.qualityScore < 0 || diagramData.qualityScore > 100)) {
      return {
        valid: false,
        error: 'Quality score must be between 0-100.',
      };
    }

    // SVG content
    if (!diagramData.svgContent || diagramData.svgContent.trim().length === 0) {
      return { valid: false, error: 'Diagram must have SVG content.' };
    }

    if (!diagramData.svgContent.includes('<svg')) {
      return { valid: false, error: 'SVG content is invalid or malformed.' };
    }

    // Optional: Validate that SVG contains expected element IDs
    // This helps catch AI generation errors early
    try {
      // Check if components' SVG selectors appear in the SVG content
      const svgLower = diagramData.svgContent.toLowerCase();

      // Check for step IDs (id="step-0", id="step-1", etc.)
      const stepIdPattern = /#"?step-\d+/gi;
      const stepsInSvg = (diagramData.svgContent.match(/id\s*=\s*["']?step-\d+/gi) || []).length;

      if (stepsInSvg === 0 && diagramData.steps.length > 0) {
        // Steps exist but no step elements found in SVG
        // This is a warning but not a fatal error (SVG might use classes instead)
        console.warn('Warning: No step elements (id="step-N") found in SVG. Visual step highlighting may not work.');
      }
    } catch (e) {
      // Silently continue; SVG validation is best-effort
      console.warn('Could not validate SVG element IDs:', e);
    }

    return { valid: true };
  } catch (e) {
    const message = e instanceof Error ? e.message : 'Unknown validation error';
    return { valid: false, error: `Validation error: ${message}` };
  }
}

/**
 * Generates a user-friendly error message from a validation error
 */
export function getUserFacingErrorMessage(error?: string): string {
  if (!error) {
    return 'Diagram structure error. Please try generating again.';
  }

  // Friendly messages for common errors
  if (error.includes('references non-existent component')) {
    return 'The diagram has a structural issue with missing components. Please regenerate.';
  }

  if (error.includes('not unique')) {
    return 'The diagram has duplicate IDs. Please regenerate.';
  }

  if (error.includes('must have')) {
    return 'The diagram is missing required information. Please regenerate.';
  }

  // Fallback to the original error message
  return `Diagram Error: ${error}`;
}
