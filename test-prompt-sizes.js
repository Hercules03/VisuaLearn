#!/usr/bin/env node
/**
 * Test different prompt sizes to identify payload limits
 */

require('dotenv').config();

const apiKey = process.env.GEMINI_API_KEY;

if (!apiKey) {
  console.error('❌ GEMINI_API_KEY not found');
  process.exit(1);
}

const tests = [
  {
    name: 'Minimal',
    size: 'small',
    prompt: 'Say "test" in one word.'
  },
  {
    name: 'Small',
    size: 'medium',
    prompt: 'Create a detailed explanation (3-5 paragraphs) about how a load balancer works in a distributed system.'
  },
  {
    name: 'Medium',
    size: 'large',
    prompt: `You are an expert educational technologist. Create a comprehensive educational diagram explanation for: Load Balancing

Generate:
1. Simple explanation (2-3 sentences)
2. How it works (5 sentences)
3. Components involved (list 4-5)
4. Real-world examples (3 examples)
5. Common failure scenarios (2 scenarios)
6. Best practices (3 practices)
7. Difficulty assessment (1-10)
8. Time estimate for learning (minutes)`
  },
  {
    name: 'Large',
    size: 'xlarge',
    prompt: `You are an expert SVG animator and educational technologist. Create an interactive diagram for: Load Balancing

CRITICAL REQUIREMENTS:
1. Generate SVG with animations
2. Create detailed component metadata
3. Define step-by-step process
4. Include data flow visualization
5. Add debugging metadata for each component
6. Real-world implementation examples
7. Failure scenarios and recovery strategies
8. Time estimates and difficulty levels
9. Quality assessment and scoring
10. Complexity layers (core vs advanced)

For each component, provide:
- Detailed explanation
- Inputs and outputs
- Failure modes
- Recovery strategies
- Real-world technologies (AWS, Kubernetes, etc.)
- Performance metrics

Generate comprehensive metadata for at least 8 steps.
Include 5+ scenarios for testing.
Provide quality scoring (0-100).`
  }
];

async function runTest(test) {
  const payloadSize = JSON.stringify({
    contents: [{
      parts: [{
        text: test.prompt
      }]
    }]
  }).length;

  console.log(`\n📊 Testing: ${test.name} (${payloadSize} bytes)`);
  console.log('─'.repeat(60));

  try {
    const startTime = Date.now();
    const response = await fetch(
      `https://generativelanguage.googleapis.com/v1beta/models/gemini-3-pro-preview:generateContent?key=${apiKey}`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          contents: [{
            parts: [{
              text: test.prompt
            }]
          }]
        }),
        timeout: 60000,
      }
    );

    const duration = Date.now() - startTime;
    const data = await response.json();

    if (response.ok) {
      console.log(`✅ SUCCESS (${duration}ms)`);
      console.log(`Response tokens: ${data.usageMetadata?.totalTokenCount || 'N/A'}`);
    } else {
      console.log(`❌ FAILED with status ${response.status}`);
      console.log(`Error: ${data.error?.message || 'Unknown error'}`);
    }
  } catch (error) {
    console.log(`❌ ERROR (${error.message})`);
    if (error.code === 'UND_ERR_SOCKET') {
      console.log('💡 Socket closed - request likely too large or network issue');
    }
  }

  // Wait between tests to avoid rate limiting
  await new Promise(resolve => setTimeout(resolve, 2000));
}

async function main() {
  console.log('🧪 Testing Different Prompt Sizes\n');
  console.log('This will help identify if large prompts cause socket closure\n');

  for (const test of tests) {
    await runTest(test);
  }

  console.log('\n' + '='.repeat(60));
  console.log('📈 Analysis:');
  console.log('- If small tests pass but large fail: payload size is the issue');
  console.log('- If all fail: network or quota issue');
  console.log('- Note request size in bytes and response in the output above');
}

main().catch(console.error);
