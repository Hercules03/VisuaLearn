# Contributing to visuaLearn

Thank you for contributing to visuaLearn! This document provides guidelines for development, code style, and pull request process.

---

## Development Setup

### Prerequisites
- Node.js 18+
- npm 9+
- Git

### Initial Setup

```bash
# Clone the repository
git clone <repository-url>
cd visuaLearn

# Install dependencies
npm install

# Create environment files
cp frontend/.env.example frontend/.env.local
cp backend/.env.example backend/.env.local

# Edit .env.local files with your API keys
nano frontend/.env.local
nano backend/.env.local
```

### Running the Development Server

```bash
# Terminal 1: Start both frontend and backend
npm run dev

# Or run separately:
npm run dev -w frontend  # Frontend on http://localhost:5173
npm run dev -w backend   # Backend on http://localhost:3000
```

---

## Branch Naming Convention

Follow this pattern for branch names:

```
<type>/<description>
```

### Types
- `feature/` - New features (e.g., `feature/p1-student-learns`)
- `bugfix/` - Bug fixes (e.g., `bugfix/fix-animation-controls`)
- `refactor/` - Refactoring (e.g., `refactor/simplify-cache-manager`)
- `docs/` - Documentation updates (e.g., `docs/add-api-reference`)
- `test/` - Test additions (e.g., `test/add-export-tests`)
- `chore/` - Maintenance tasks (e.g., `chore/update-dependencies`)

### Examples
- ✅ `feature/p1-concept-input-form`
- ✅ `bugfix/fix-webgl-detection`
- ✅ `refactor/improve-error-handling`
- ❌ `my-branch`
- ❌ `T101`

---

## Commit Message Format

Use the following format for commit messages:

```
[T###] Brief description (imperative mood)

Detailed explanation of changes if needed.
This can span multiple lines.

Closes #issue-number
```

### Guidelines
1. **Start with task ID** in brackets: `[T101]`
2. **Use imperative mood**: "Add feature" not "Added feature"
3. **Capitalize** the first letter
4. **No period** at the end of subject line
5. **Max 50 characters** for subject line
6. **Blank line** between subject and body
7. **Wrap body** at 72 characters
8. **Reference issues** with `Closes #123` or `Fixes #456`

### Examples

```
[T101] Initialize frontend project with Vite + React 18

Set up the React frontend with TypeScript strict mode and Vite.
Configured tsconfig.json for maximum type safety and ESLint/Prettier
for consistent code formatting.

Closes #1
```

```
[T201] Implement InputValidator service

Created backend service for concept input validation.
Validates concept length (>2 words), checks blocklist keywords,
and enforces max 200 character limit.

Tests added for valid/invalid inputs and edge cases.
```

---

## Code Style

### TypeScript

1. **Strict Mode**: All code uses TypeScript strict mode
   ```json
   {
     "compilerOptions": {
       "strict": true,
       "noImplicitAny": true,
       "strictNullChecks": true
     }
   }
   ```

2. **No `any` Types**: Avoid `any` unless absolutely necessary
   ```typescript
   // ❌ Bad
   const data: any = response.data;

   // ✅ Good
   const data: ConceptResponse = response.data;
   ```

3. **Explicit Return Types**: All functions must have explicit return types
   ```typescript
   // ❌ Bad
   export function validateConcept(concept) {
     return concept.length > 2;
   }

   // ✅ Good
   export function validateConcept(concept: string): boolean {
     return concept.length > 2;
   }
   ```

4. **Error Handling**: No silent failures; always handle errors
   ```typescript
   // ❌ Bad
   try {
     const data = await generateConcept(concept);
   } catch (error) {
     // Silently ignored
   }

   // ✅ Good
   try {
     const data = await generateConcept(concept);
   } catch (error) {
     logger.error('Generation failed', { error, concept });
     throw new GenerationError('Failed to generate visualization');
   }
   ```

### File Organization

```typescript
// 1. Imports (grouped: external, internal, types)
import express, { Request, Response } from 'express';
import { validateConcept } from '@/services/InputValidator';
import type { ConceptRequest } from '@/types';

// 2. Type definitions/interfaces (if file-specific)
interface RequestWithContext extends Request {
  context: RequestContext;
}

// 3. Constants
const CACHE_TTL = 3600;

// 4. Main exports (classes, functions)
export class ConceptService { ... }

// 5. Helper functions (if any)
function formatCachKey(concept: string): string { ... }
```

### Naming Conventions

| Type | Convention | Example |
|------|-----------|---------|
| **Classes** | PascalCase | `ConceptService`, `InputValidator` |
| **Functions** | camelCase | `validateConcept`, `generateAnimation` |
| **Constants** | UPPER_SNAKE_CASE | `CACHE_TTL`, `MAX_CONCEPT_LENGTH` |
| **Variables** | camelCase | `cacheManager`, `isLoading` |
| **Types/Interfaces** | PascalCase | `ConceptRequest`, `AnimationSpec` |
| **Files** | kebab-case or PascalCase | `input-validator.ts`, `InputValidator.ts` |
| **Directories** | kebab-case | `services/`, `controllers/`, `ui-components/` |

### Code Formatting

**Prettier** automatically formats code. Config in `.prettierrc`:
```json
{
  "semi": true,
  "trailingComma": "es5",
  "singleQuote": true,
  "printWidth": 100,
  "tabWidth": 2,
  "useTabs": false
}
```

**Always run before committing:**
```bash
npm run format
```

### ESLint

**ESLint** enforces code quality. Config in `.eslintrc.json`:

**Always fix issues before committing:**
```bash
npm run lint:fix
```

---

## Testing

### Unit Tests

1. **Location**: Co-located with source files
   ```
   src/services/InputValidator.ts
   src/services/InputValidator.test.ts
   ```

2. **Naming**: `*.test.ts` or `*.spec.ts`

3. **Run Tests**:
   ```bash
   npm run test                  # All tests
   npm run test:coverage         # With coverage report
   npm run test -- --watch       # Watch mode
   ```

4. **Coverage Target**: ≥80% for critical services

### Integration Tests

Located in `tests/integration/`:
```bash
npm run test:integration -w backend
```

### E2E Tests

Located in `tests/e2e/`, use Playwright:
```bash
npm run test:e2e
```

### Writing Tests

Use Vitest + React Testing Library:

```typescript
import { describe, it, expect, beforeEach } from 'vitest';
import { validateConcept } from '@/services/InputValidator';

describe('InputValidator', () => {
  describe('validateConcept', () => {
    it('should accept concepts with 2+ words', () => {
      expect(validateConcept('DNA replication')).toBe(true);
    });

    it('should reject single-word concepts', () => {
      expect(validateConcept('photosynthesis')).toBe(false);
    });

    it('should reject blocklist keywords', () => {
      expect(validateConcept('how to make a bomb')).toBe(false);
    });
  });
});
```

---

## Pull Request Process

### Before Creating a PR

1. **Update your branch**:
   ```bash
   git fetch origin
   git rebase origin/develop
   ```

2. **Run checks locally**:
   ```bash
   npm run type-check
   npm run lint
   npm run test
   npm run build
   ```

3. **Ensure all checks pass** before pushing

### Creating a PR

1. **Push your branch**:
   ```bash
   git push -u origin your-branch-name
   ```

2. **Open PR on GitHub** with this template:
   ```markdown
   ## Description
   Brief description of changes.

   ## Type of Change
   - [ ] Bug fix
   - [ ] New feature
   - [ ] Breaking change
   - [ ] Documentation

   ## Related Issues
   Closes #123

   ## Testing
   - [ ] Unit tests added/updated
   - [ ] Integration tests added/updated
   - [ ] Manual testing completed

   ## Checklist
   - [ ] Code follows style guidelines
   - [ ] `npm run lint` passes
   - [ ] `npm run type-check` passes
   - [ ] Tests added/updated
   - [ ] Documentation updated
   - [ ] No new warnings generated
   ```

3. **Require Approval**: At least 1 approval before merging

4. **CI/CD Must Pass**: All GitHub Actions workflows must pass

### PR Review Guidelines

Reviewers should check:
- ✅ Code follows style guidelines
- ✅ No `any` types or type violations
- ✅ Tests are comprehensive
- ✅ No console.log left in code
- ✅ Error handling is proper
- ✅ Performance impact assessed
- ✅ Accessibility considered

---

## Performance Considerations

### Frontend
- ✅ Use `React.memo` for expensive components
- ✅ Lazy load non-critical components
- ✅ Minimize bundle size
- ✅ Target <3s interactive render time

### Backend
- ✅ Implement caching for repeated calls
- ✅ Use connection pooling
- ✅ Monitor response times
- ✅ Target <500ms p95 latency

---

## Documentation

### Inline Comments

Use sparingly - code should be self-documenting:
```typescript
// ✅ Good: Explains WHY not WHAT
export function filterValidConcepts(concepts: string[]): string[] {
  // Gemini performs better with 2+ word inputs;
  // single words risk hallucination
  return concepts.filter((c) => c.split(' ').length >= 2);
}

// ❌ Bad: Explains WHAT (obvious from code)
export function filterValidConcepts(concepts: string[]): string[] {
  // Filter concepts by length
  return concepts.filter((c) => c.split(' ').length >= 2);
}
```

### JSDoc for Public APIs

```typescript
/**
 * Validates and processes a user concept input.
 *
 * @param concept - The concept to validate (max 200 chars)
 * @param depth - The explanation depth level
 * @returns Validated concept or throws ValidationError
 *
 * @throws {ValidationError} If concept is invalid
 * @example
 * const result = await generateConcept('photosynthesis', 'intro');
 */
export async function generateConcept(
  concept: string,
  depth: 'intro' | 'intermediate' | 'advanced'
): Promise<ConceptGenerationResponse> {
  // implementation
}
```

### README Updates

When adding significant features, update relevant documentation:
- Frontend components → Update README with new UI descriptions
- Backend services → Update API documentation
- New dependencies → Update setup instructions

---

## Common Issues & Solutions

### Issue: `npm install` fails with peer dependency warnings

**Solution**: Add `--legacy-peer-deps` flag if needed (not recommended long-term):
```bash
npm install --legacy-peer-deps
```

### Issue: TypeScript errors after changes

**Solution**: Ensure strict mode compliance:
```bash
npm run type-check
npm run lint:fix
```

### Issue: Tests fail locally but pass in CI

**Solution**: Ensure environment matches:
```bash
npm ci  # Clean install (CI behavior)
npm run test
```

---

## Getting Help

- 📖 **Documentation**: See [specs/](./specs/001-interactive-viz/)
- 🔗 **Architecture**: See [plan.md](./specs/001-interactive-viz/plan.md)
- ❓ **Questions**: Open a GitHub discussion

---

## Code of Conduct

Be respectful, inclusive, and constructive in all interactions.

---

**Thank you for contributing!** 🙏
