/**
 * InputValidator Service
 * Validates user concept input according to specification requirements
 */

import type { ValidationResult, ValidationField } from '@/types/index';

// Blocklist of security-sensitive keywords
const BLOCKLIST_KEYWORDS = new Set([
  'bomb',
  'exploit',
  'attack method',
  'malware',
  'hack',
  'inject',
  'backdoor',
  'ransomware',
  'trojan',
  'worm',
  'virus',
  'weaponized',
  'detonate',
  'explosive',
  'chemical weapons',
  'biological weapons',
  'nuclear weapons',
]);

// Constants for validation
const MIN_WORDS = 2;
const MAX_CONCEPT_LENGTH = 200;
const MIN_CONCEPT_LENGTH = 3;

/**
 * Validates a concept input string
 * @param concept - The concept to validate
 * @returns ValidationResult with any errors found
 */
export function validateConcept(concept: string): ValidationResult {
  const errors: ValidationField[] = [];

  // Check if concept is empty or only whitespace
  if (!concept || !concept.trim()) {
    errors.push({
      field: 'concept',
      message: 'Concept cannot be empty',
    });
    return { valid: false, errors };
  }

  // Check minimum length
  if (concept.length < MIN_CONCEPT_LENGTH) {
    errors.push({
      field: 'concept',
      message: `Concept must be at least ${MIN_CONCEPT_LENGTH} characters long`,
    });
  }

  // Check maximum length
  if (concept.length > MAX_CONCEPT_LENGTH) {
    errors.push({
      field: 'concept',
      message: `Concept cannot exceed ${MAX_CONCEPT_LENGTH} characters (current: ${concept.length})`,
    });
  }

  // Check word count (at least 2 words)
  const wordCount = concept.trim().split(/\s+/).length;
  if (wordCount < MIN_WORDS) {
    errors.push({
      field: 'concept',
      message: `Concept must contain at least ${MIN_WORDS} words (current: ${wordCount})`,
    });
  }

  // Check for single-character tokens
  const tokens = concept.trim().split(/\s+/);
  const singleCharTokens = tokens.filter((token) => token.length === 1);
  if (singleCharTokens.length > 0) {
    errors.push({
      field: 'concept',
      message: `Concept cannot contain single-character tokens: ${singleCharTokens.join(', ')}`,
    });
  }

  // Check for blocklist keywords (case-insensitive)
  const lowerConcept = concept.toLowerCase();
  for (const keyword of BLOCKLIST_KEYWORDS) {
    if (lowerConcept.includes(keyword.toLowerCase())) {
      errors.push({
        field: 'concept',
        message: `Concept contains restricted keyword. Please avoid security-sensitive terms.`,
      });
      break; // Only show one error message for blocklist
    }
  }

  return {
    valid: errors.length === 0,
    errors,
  };
}

/**
 * Gets a user-friendly error message for validation failures
 * @param errors - Array of validation errors
 * @returns Formatted error message
 */
export function formatValidationErrors(errors: ValidationField[]): string {
  if (errors.length === 0) {
    return '';
  }

  if (errors.length === 1) {
    return errors[0]!.message;
  }

  return `${errors.length} validation errors:\n${errors.map((e) => `• ${e.message}`).join('\n')}`;
}

/**
 * Validates all required input fields for concept generation
 * @param concept - The concept string
 * @param depth - The depth level
 * @param language - The language code
 * @returns ValidationResult with any errors
 */
export function validateConceptGenerationInput(
  concept?: string,
  depth?: string,
  language?: string
): ValidationResult {
  const errors: ValidationField[] = [];

  // Check concept
  if (!concept) {
    errors.push({
      field: 'concept',
      message: 'Concept is required',
    });
  } else {
    const conceptValidation = validateConcept(concept);
    if (!conceptValidation.valid) {
      errors.push(...conceptValidation.errors);
    }
  }

  // Check depth
  if (!depth) {
    errors.push({
      field: 'depth',
      message: 'Depth level is required',
    });
  } else if (!['intro', 'intermediate', 'advanced'].includes(depth)) {
    errors.push({
      field: 'depth',
      message: `Depth must be 'intro', 'intermediate', or 'advanced' (current: ${depth})`,
    });
  }

  // Check language
  if (!language) {
    errors.push({
      field: 'language',
      message: 'Language is required',
    });
  } else if (!['en', 'ja'].includes(language)) {
    errors.push({
      field: 'language',
      message: `Language must be 'en' or 'ja' (current: ${language})`,
    });
  }

  return {
    valid: errors.length === 0,
    errors,
  };
}

/**
 * Sanitizes user input to prevent injection attacks
 * @param input - The input to sanitize
 * @returns Sanitized input
 */
export function sanitizeInput(input: string): string {
  // Remove leading/trailing whitespace
  let sanitized = input.trim();

  // Normalize whitespace (collapse multiple spaces)
  sanitized = sanitized.replace(/\s+/g, ' ');

  // Ensure no null bytes
  sanitized = sanitized.replace(/\0/g, '');

  return sanitized;
}
