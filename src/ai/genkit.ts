import {genkit} from 'genkit';
import {googleAI} from '@genkit-ai/google-genai';

// Initialize Genkit with Google AI plugin using GEMINI_API_KEY from .env
// Note: Using gemini-2.5-pro instead of gemini-3-pro-preview due to free tier quota limits
export const ai = genkit({
  plugins: [
    googleAI({
      apiKey: process.env.GEMINI_API_KEY,
    }),
  ],
  model: 'googleai/gemini-3-preview',
});
