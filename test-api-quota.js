#!/usr/bin/env node

/**
 * Simple script to test Google Gemini API quota
 * Run with: node test-api-quota.js
 */

require('dotenv').config();

const apiKey = process.env.GEMINI_API_KEY;

if (!apiKey) {
  console.error('❌ ERROR: GEMINI_API_KEY not found in .env');
  process.exit(1);
}

console.log('🔍 Testing API key quota...');
console.log(`API Key: ${apiKey.substring(0, 20)}...${apiKey.substring(apiKey.length - 10)}`);
console.log('');

// First, list available models to see what's available
async function listModels() {
  console.log('📋 Listing available models...\n');
  try {
    const response = await fetch(
      'https://generativelanguage.googleapis.com/v1beta/models?key=' + apiKey
    );

    const data = await response.json();

    if (response.ok && data.models) {
      console.log('Available models:');
      data.models.forEach((model) => {
        console.log(`  - ${model.name}`);
      });
      console.log('');
      return data.models;
    } else {
      console.log('Could not list models:');
      console.log(JSON.stringify(data, null, 2));
      return [];
    }
  } catch (error) {
    console.error('Error listing models:', error.message);
    return [];
  }
}

// Test with gemini-2.0-flash (common model name)
const testPayload = {
  contents: [
    {
      parts: [
        {
          text: 'Say "Hello" in one word only.',
        },
      ],
    },
  ],
};

async function testAPI() {
  try {
    // Try gemini-2.0-flash first (most common/available)
    let modelName = 'gemini-2.0-flash';
    let response = await fetch(
      `https://generativelanguage.googleapis.com/v1beta/models/${modelName}:generateContent?key=${apiKey}`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(testPayload),
      }
    );

    const data = await response.json();

    console.log(`Status: ${response.status} ${response.statusText}`);
    console.log('');

    if (response.ok) {
      console.log(`✅ SUCCESS! API has quota and is working with model: ${modelName}`);
      console.log('');
      console.log('Response:');
      console.log(JSON.stringify(data, null, 2));
      process.exit(0);
    } else if (response.status === 429) {
      console.log('❌ QUOTA EXCEEDED on this API key');
      console.log('');
      console.log('Error Details:');
      console.log(JSON.stringify(data, null, 2));
      console.log('');
      console.log('Next steps:');
      console.log('1. Check if billing is enabled: https://console.cloud.google.com/billing');
      console.log('2. If not, enable billing on the Google Cloud project');
      console.log('3. If billing is enabled, wait 30+ seconds and retry');
      console.log('4. Or try a different API key');
      process.exit(1);
    } else if (response.status === 403) {
      console.log('❌ PERMISSION DENIED - API Key may be invalid or expired');
      console.log('');
      console.log('Error Details:');
      console.log(JSON.stringify(data, null, 2));
      process.exit(1);
    } else {
      console.log(`❌ ERROR with model ${modelName}`);
      console.log('');
      console.log('Error Details:');
      console.log(JSON.stringify(data, null, 2));
      process.exit(1);
    }
  } catch (error) {
    console.error('❌ Network Error:');
    console.error(error.message);
    process.exit(1);
  }
}

// Run tests
(async () => {
  await listModels();
  await testAPI();
})();
