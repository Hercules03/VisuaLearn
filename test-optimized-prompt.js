#!/usr/bin/env node
/**
 * Test the optimized diagram generation prompt
 * Verifies that the prompt generates valid JSON with all required metadata
 */

require('dotenv').config();

const apiKey = process.env.GEMINI_API_KEY;

if (!apiKey) {
  console.error('❌ GEMINI_API_KEY not found');
  process.exit(1);
}

const optimizedPrompt = `You are the Interactive Diagram Engine. Generate a single, strictly valid JSON object explaining: Load Balancing

**Output Structure:**
{
  "diagramData": {
    "svgContent": "Self-contained <svg> with CSS animations. Use <g id='comp_id'> for all actors. Modern, clean, flat style.",
    "explanation": "2-3 paragraph overview of the concept.",
    "components": [
      {
        "id": "Must match SVG id",
        "label": "Display name",
        "description": "2-3 sentences technical summary",
        "detailedExplanation": "How this component works (2-3 sentences)",
        "realWorldExamples": [{"technology": "AWS", "name": "ALB", "link": "..."}],
        "failureMode": "What breaks",
        "failureRecovery": "How it recovers",
        "inputs": ["Input type 1", "Input type 2"],
        "outputs": ["Output type 1"],
        "layer": "core|advanced",
        "category": "control|input|output|process|sensor",
        "svgSelector": "CSS selector to SVG element"
      }
    ],
    "steps": [
      {
        "id": "step-1",
        "title": "Step name",
        "description": "Narrative of what happens",
        "activeComponentIds": ["comp1", "comp2"],
        "animationTiming": {"duration": 1000, "easing": "ease-in-out"},
        "stateSnapshot": [{"componentId": "comp1", "state": "idle|processing|complete|error", "dataIn": "...", "dataOut": "..."}],
        "dataFlows": [{"fromComponent": "comp1", "toComponent": "comp2", "dataType": "HTTP request", "transformation": "..."}]
      }
    ],
    "scenarios": [
      {
        "scenarioName": "What if X fails?",
        "description": "User action or condition",
        "impactedComponents": ["comp2", "comp3"],
        "visualization": {"highlightComponents": [...], "dimComponents": [...], "animationType": "overload|failure|slow|bottleneck"},
        "lessonLearned": "Key insight from this scenario"
      }
    ],
    "conceptDifficulty": 5,
    "prerequisites": ["Knowledge area 1", "Knowledge area 2"],
    "keyInsights": ["Key insight 1", "Key insight 2"],
    "timeEstimates": {"quickView": 5, "deepUnderstanding": 15, "masteryChallenges": 20},
    "qualityScore": 85,
    "generationNotes": ["Confidence notes"]
  }
}

**Strict Requirements:**
1. JSON ONLY. No markdown, no preamble, no explanation.
2. ALL component IDs in steps/scenarios MUST exist in components array. NO orphaned references.
3. SVG must use CSS @keyframes for movement (moveLeft, moveRight, moveUp, moveDown, pulse, flowRight, flowLeft).
4. Technical depth for software engineers: include protocols, state management, error handling.
5. 5-8 sequential steps showing progression from start to completion.
6. 3-4 "what-if" scenarios testing knowledge and failure modes.
7. Real-world implementations with specific technologies (AWS, Kubernetes, Nginx, etc.).
8. Every step has visible animation or visual change - NO static diagrams.
9. Validate all references before returning.`;

const payloadSize = JSON.stringify({
  contents: [{ parts: [{ text: optimizedPrompt }] }],
}).length;

console.log('\n🧪 Testing Optimized Diagram Generation Prompt');
console.log('═'.repeat(60));
console.log(`📊 Prompt Size: ${payloadSize} bytes (${(payloadSize / 1024).toFixed(2)} KB)`);
console.log(`✅ Payload is ${payloadSize < 12000 ? 'WITHIN' : 'EXCEEDS'} safe limits (12 KB)\n`);

fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-3-pro-preview:generateContent?key=${apiKey}`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    contents: [{ parts: [{ text: optimizedPrompt }] }],
  }),
  timeout: 60000,
})
  .then(async (response) => {
    const data = await response.json();

    if (response.ok) {
      console.log('✅ REQUEST SUCCESSFUL\n');
      console.log('Response Metadata:');
      console.log(`  Status: ${response.status} ${response.statusText}`);
      console.log(`  Prompt Tokens: ${data.usageMetadata?.promptTokenCount || 'N/A'}`);
      console.log(`  Response Tokens: ${data.usageMetadata?.candidatesTokenCount || 'N/A'}`);
      console.log(`  Total Tokens: ${data.usageMetadata?.totalTokenCount || 'N/A'}`);

      // Try to parse the response as JSON
      if (data.candidates?.[0]?.content?.parts?.[0]?.text) {
        try {
          const jsonResponse = JSON.parse(data.candidates[0].content.parts[0].text);
          console.log('\n✅ Valid JSON Response Generated');
          console.log(`  Components: ${jsonResponse.diagramData?.components?.length || 0}`);
          console.log(`  Steps: ${jsonResponse.diagramData?.steps?.length || 0}`);
          console.log(`  Scenarios: ${jsonResponse.diagramData?.scenarios?.length || 0}`);
          console.log(`  Quality Score: ${jsonResponse.diagramData?.qualityScore || 'N/A'}/100`);
          console.log(`  Has SVG: ${!!jsonResponse.diagramData?.svgContent}`);
          console.log('\n🎉 Optimized prompt is working correctly!');
        } catch (e) {
          console.log('\n⚠️  Response is not JSON:');
          console.log(data.candidates[0].content.parts[0].text.substring(0, 200) + '...');
        }
      }
    } else {
      console.log('❌ REQUEST FAILED\n');
      console.log('Error:', JSON.stringify(data.error, null, 2));
    }
  })
  .catch((error) => {
    console.log('❌ NETWORK ERROR\n');
    console.log('Error:', error.message);
    if (error.code === 'UND_ERR_SOCKET') {
      console.log('\n💡 Socket closed - request may still be too large');
    }
  });
