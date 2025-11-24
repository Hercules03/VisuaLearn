#!/usr/bin/env node
/**
 * Test Google Generative AI API connectivity and key validity
 */

require('dotenv').config();

const apiKey = process.env.GEMINI_API_KEY;

if (!apiKey) {
  console.error('❌ GEMINI_API_KEY not found in environment variables');
  process.exit(1);
}

console.log('🔍 Testing API Key Validity...\n');
console.log(`API Key: ${apiKey.slice(0, 10)}...${apiKey.slice(-10)}`);
console.log('Testing model: gemini-3-pro-preview\n');

const testPayload = {
  contents: [
    {
      parts: [
        {
          text: 'Say "API test successful" in exactly 3 words.'
        }
      ]
    }
  ]
};

fetch('https://generativelanguage.googleapis.com/v1beta/models/gemini-3-pro-preview:generateContent?key=' + apiKey, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify(testPayload),
  timeout: 30000,
})
  .then(async (response) => {
    console.log(`📊 HTTP Status: ${response.status} ${response.statusText}`);

    const data = await response.json();

    if (response.ok) {
      console.log('\n✅ API KEY IS VALID!\n');
      console.log('Response:', JSON.stringify(data, null, 2));

      if (data.candidates && data.candidates[0]?.content?.parts?.[0]?.text) {
        console.log('\n✅ Model is working correctly!');
        console.log('Model response:', data.candidates[0].content.parts[0].text);
      }
      process.exit(0);
    } else {
      console.log('\n❌ API ERROR\n');
      console.log('Response:', JSON.stringify(data, null, 2));

      if (data.error?.message) {
        console.log('\nError message:', data.error.message);

        if (data.error.message.includes('quota')) {
          console.log('💡 Hint: Your API quota may be exceeded. Check Google Cloud console.');
        }
        if (data.error.message.includes('permission')) {
          console.log('💡 Hint: API key may not have permission for this model.');
        }
        if (data.error.message.includes('not found')) {
          console.log('💡 Hint: Model "gemini-3-pro-preview" may not exist. Try "gemini-2.0-pro" or "gemini-1.5-pro"');
        }
      }
      process.exit(1);
    }
  })
  .catch((error) => {
    console.error('\n❌ NETWORK ERROR\n');
    console.error('Error:', error.message);

    if (error.code === 'ENOTFOUND') {
      console.log('💡 Hint: Cannot reach generativelanguage.googleapis.com. Check your internet connection.');
    } else if (error.code === 'ECONNRESET') {
      console.log('💡 Hint: Connection was reset by the server. API may be having issues.');
    } else if (error.code === 'ETIMEDOUT') {
      console.log('💡 Hint: Request timed out. Check your network or try again later.');
    }

    console.error('\nFull error:', error);
    process.exit(1);
  });
