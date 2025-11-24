import {genkit} from 'genkit';
import {googleAI} from '@genkit-ai/google-genai';

// Initialize Genkit with Google AI plugin using GEMINI_API_KEY from .env
// Using gemini-2.5-pro (tested and working) instead of gemini-3-pro-preview (requires quota)
export const ai = genkit({
  plugins: [
    googleAI({
      apiKey: process.env.GEMINI_API_KEY,
    }),
  ],
  model: 'googleai/gemini-2.5-pro',
});
