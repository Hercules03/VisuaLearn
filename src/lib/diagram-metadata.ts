/**
 * Diagram metadata utilities for accessing and filtering enhanced metadata
 * These utilities help frontend components access specific metadata fields
 */

import type {
  DiagramContent,
  DiagramComponent,
  Scenario,
  Connection,
  ComparableConcept,
} from '@/ai/flows/generate-interactive-diagram';

/**
 * Extract components filtered by layer (core or advanced)
 * @param diagram The diagram content
 * @param layer The layer to filter by ('core' or 'advanced')
 * @returns Array of components in the specified layer
 */
export function extractComponentsByLayer(
  diagram: DiagramContent,
  layer: 'core' | 'advanced'
): DiagramComponent[] {
  return diagram.components.filter(
    (component) => (component.layer ?? 'core') === layer
  );
}

/**
 * Get detailed information for a specific component
 * @param diagram The diagram content
 * @param componentId The ID of the component
 * @returns The component with all metadata, or undefined if not found
 */
export function getComponentDetails(
  diagram: DiagramContent,
  componentId: string
): DiagramComponent | undefined {
  return diagram.components.find((c) => c.id === componentId);
}

/**
 * Get scenarios filtered by type
 * @param diagram The diagram content
 * @param type The animation type to filter by
 * @returns Array of scenarios of the specified type
 */
export function getScenariosByType(
  diagram: DiagramContent,
  type: 'overload' | 'failure' | 'slow' | 'bottleneck'
): Scenario[] {
  return (diagram.scenarios ?? []).filter(
    (scenario) => scenario.visualization.animationType === type
  );
}

/**
 * Calculate total learning time for the diagram
 * @param diagram The diagram content
 * @returns Total minutes across all learning depths
 */
export function calculateTotalLearningTime(diagram: DiagramContent): number {
  if (!diagram.timeEstimates) {
    return 0;
  }

  let total = 0;
  if (diagram.timeEstimates.quickView) {
    total += diagram.timeEstimates.quickView;
  }
  if (diagram.timeEstimates.deepUnderstanding) {
    total += diagram.timeEstimates.deepUnderstanding;
  }
  if (diagram.timeEstimates.masteryChallenges) {
    total += diagram.timeEstimates.masteryChallenges;
  }
  return total;
}

/**
 * Get all connections for a specific component
 * @param diagram The diagram content
 * @param componentId The component ID to get connections for
 * @returns Array of connections where this component is source or destination
 */
export function getComponentConnections(
  diagram: DiagramContent,
  componentId: string
): Connection[] {
  return (diagram.connections ?? []).filter(
    (conn) => conn.fromComponent === componentId || conn.toComponent === componentId
  );
}

/**
 * Get all incoming connections to a component
 * @param diagram The diagram content
 * @param componentId The component ID to get connections for
 * @returns Array of connections with this component as destination
 */
export function getIncomingConnections(
  diagram: DiagramContent,
  componentId: string
): Connection[] {
  return (diagram.connections ?? []).filter(
    (conn) => conn.toComponent === componentId
  );
}

/**
 * Get all outgoing connections from a component
 * @param diagram The diagram content
 * @param componentId The component ID to get connections for
 * @returns Array of connections with this component as source
 */
export function getOutgoingConnections(
  diagram: DiagramContent,
  componentId: string
): Connection[] {
  return (diagram.connections ?? []).filter(
    (conn) => conn.fromComponent === componentId
  );
}

/**
 * Get scenarios that impact a specific component
 * @param diagram The diagram content
 * @param componentId The component ID
 * @returns Array of scenarios that impact this component
 */
export function getScenariosForComponent(
  diagram: DiagramContent,
  componentId: string
): Scenario[] {
  return (diagram.scenarios ?? []).filter((scenario) =>
    scenario.impactedComponents.includes(componentId)
  );
}

/**
 * Check if a component is in advanced layer
 * @param component The component to check
 * @returns True if the component is in the advanced layer
 */
export function isAdvancedComponent(component: DiagramComponent): boolean {
  return component.layer === 'advanced';
}

/**
 * Get the learning difficulty label
 * @param difficulty The difficulty score (1-10)
 * @returns A human-readable difficulty label
 */
export function getDifficultyLabel(difficulty?: number): string {
  if (!difficulty) return 'Not specified';
  if (difficulty <= 2) return 'Beginner';
  if (difficulty <= 4) return 'Easy';
  if (difficulty <= 6) return 'Intermediate';
  if (difficulty <= 8) return 'Advanced';
  return 'Expert';
}

/**
 * Get quality score interpretation
 * @param score The quality score (0-100)
 * @returns A human-readable quality interpretation
 */
export function getQualityInterpretation(score?: number): string {
  if (!score) return 'Not assessed';
  if (score >= 90) return 'Excellent';
  if (score >= 75) return 'Good';
  if (score >= 60) return 'Acceptable';
  return 'Needs improvement';
}

/**
 * Get all critical path connections
 * @param diagram The diagram content
 * @returns Array of critical path connections
 */
export function getCriticalPathConnections(diagram: DiagramContent): Connection[] {
  return (diagram.connections ?? []).filter((conn) => conn.isRequired);
}

/**
 * Get comparable concepts for learning context
 * @param diagram The diagram content
 * @returns Array of comparable concepts
 */
export function getComparableConcepts(
  diagram: DiagramContent
): ComparableConcept[] {
  return diagram.comparableConcepts ?? [];
}

/**
 * Format time estimate for display
 * @param minutes The number of minutes
 * @returns A human-readable time string
 */
export function formatTimeEstimate(minutes: number): string {
  if (minutes < 1) return 'Less than 1 minute';
  if (minutes === 1) return '1 minute';
  if (minutes < 60) return `${minutes} minutes`;
  if (minutes === 60) return '1 hour';
  const hours = Math.floor(minutes / 60);
  const mins = minutes % 60;
  if (mins === 0) return `${hours} hour${hours > 1 ? 's' : ''}`;
  return `${hours} hour${hours > 1 ? 's' : ''} ${mins} minutes`;
}

/**
 * Check if diagram has complete metadata
 * @param diagram The diagram content
 * @returns True if all recommended metadata fields are present
 */
export function hasCompleteMetadata(diagram: DiagramContent): boolean {
  return !!(
    diagram.timeEstimates &&
    diagram.conceptDifficulty &&
    diagram.prerequisites &&
    diagram.keyInsights &&
    diagram.scenarios &&
    diagram.qualityScore
  );
}

/**
 * Get all components with a specific criticality level
 * @param diagram The diagram content
 * @param criticality The criticality level to filter by
 * @returns Array of components with the specified criticality
 */
export function getComponentsByCriticality(
  diagram: DiagramContent,
  criticality: 'essential' | 'important' | 'optional'
): DiagramComponent[] {
  return diagram.components.filter(
    (component) => component.metrics?.criticality === criticality
  );
}

/**
 * Get the most critical components
 * @param diagram The diagram content
 * @returns Array of essential components
 */
export function getEssentialComponents(diagram: DiagramContent): DiagramComponent[] {
  return getComponentsByCriticality(diagram, 'essential');
}
