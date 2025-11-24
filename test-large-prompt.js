#!/usr/bin/env node
/**
 * Test with a prompt similar in size to the diagram generation prompt
 */

require('dotenv').config();

const apiKey = process.env.GEMINI_API_KEY;

if (!apiKey) {
  console.error('❌ GEMINI_API_KEY not found');
  process.exit(1);
}

// Create a large prompt similar to diagram generation prompt
const largePrompt = `You are an expert educational technologist and SVG/CSS animation specialist. Your mission is to create a self-contained, interactive, and animated educational diagram.

**Critical Requirements:**
- Generate comprehensive SVG with embedded animations
- Create detailed component metadata structure
- Define step-by-step process breakdown
- Include data flow visualization
- Add comprehensive debugging information
- Real-world implementation examples
- Failure scenarios and recovery strategies

${Array(30).fill(0).map((_, i) => `
**Requirement ${i + 1}:**
Generate detailed explanation of component behavior
- How it processes inputs
- What transformations occur
- What outputs are produced
- When and how it fails
- How the system recovers from failures
- Real-world products that implement this
- Performance characteristics
- Criticality level assessment
`).join('\n')}

**Metadata Structure:**
The output must include:
- Component definitions with unique IDs
- Step-by-step tutorial with animation timings
- Data flow specifications between components
- Failure mode documentation
- Real-world implementation mapping
- Scenario-based testing cases
- Time estimates for learning
- Difficulty assessment (1-10)
- Quality score (0-100)
- Prerequisites for understanding
- Key insights and takeaways

**SVG Animation Requirements:**
- Components must move between zones
- Messages must flow between components
- State transformations must be animated
- Hover effects must show interactive elements
- Each step must have distinct visual changes
- Animations must be smooth with proper timing
- All animations must have educational purpose

**Code Examples and Patterns:**
Include detailed examples for:
- Animation timing specifications
- Component selector patterns
- Data attribute usage
- CSS animation definitions
- Keyframe animations
- Transition timings
- Hover interactions
- Click handling

**Quality Assurance:**
Before returning, verify:
- All component IDs are unique
- All step references are valid
- All data flows reference existing components
- All failure modes are realistic
- All real-world examples are accurate
- Time estimates are reasonable
- Quality score is justified
- SVG is self-contained

Format your response as JSON with:
- diagramData.svgContent: Full SVG with embedded styles
- diagramData.explanation: Comprehensive concept explanation
- diagramData.components: Array of component definitions
- diagramData.steps: Array of sequential steps
- diagramData.metadata: Diagram metadata
- diagramData.scenarios: What-if testing scenarios
- diagramData.timeEstimates: Learning time by depth
- diagramData.qualityScore: Self-assessment score
`;

console.log(`\n📊 Testing Large Prompt (${largePrompt.length} chars, ${Buffer.byteLength(largePrompt, 'utf8')} bytes)\n`);

const testPayload = {
  contents: [
    {
      parts: [
        {
          text: largePrompt
        }
      ]
    }
  ]
};

const payloadSize = Buffer.byteLength(JSON.stringify(testPayload), 'utf8');
console.log(`💾 Payload Size: ${payloadSize} bytes (${(payloadSize / 1024).toFixed(2)} KB)\n`);

fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-3-pro-preview:generateContent?key=${apiKey}`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify(testPayload),
  timeout: 120000,
})
  .then(async (response) => {
    console.log(`📊 Response Status: ${response.status} ${response.statusText}`);

    const data = await response.json();

    if (response.ok) {
      console.log('\n✅ SUCCESS - Large prompt handled correctly!\n');
      console.log('Response stats:');
      console.log(`  Prompt tokens: ${data.usageMetadata?.promptTokenCount || 'N/A'}`);
      console.log(`  Response tokens: ${data.usageMetadata?.candidatesTokenCount || 'N/A'}`);
      console.log(`  Total tokens: ${data.usageMetadata?.totalTokenCount || 'N/A'}`);
    } else {
      console.log('\n❌ Failed\n');
      console.log('Error:', JSON.stringify(data.error, null, 2));
    }
  })
  .catch((error) => {
    console.error('\n❌ Network Error\n');
    console.error('Error:', error.message);
    if (error.code === 'UND_ERR_SOCKET') {
      console.log('\n💡 Socket was closed - this confirms large prompts cause the issue');
      console.log('   Solution: Reduce prompt complexity or split into smaller requests');
    }
  });
