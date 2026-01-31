import { useState } from 'react';
import { Layout } from '@/components/layout/Layout';
import { ChatContainer } from '@/components/features/ChatContainer';
import { InputArea } from '@/components/features/InputArea';
import type { Message } from '@/components/features/MessageBubble';
import type { ProcessingStep } from '@/components/features/ProcessingIndicator';
import { v4 as uuidv4 } from 'uuid';
import { useDiagram } from '@/hooks/useDiagram';
import { APIError } from '@/lib/api';

function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const { generateDiagram, state } = useDiagram();

  const mapProgressToStep = (progress: number): ProcessingStep => {
    if (progress < 20) return 'analyzing';
    if (progress < 40) return 'planning';
    if (progress < 70) return 'generating';
    if (progress < 100) return 'reviewing';
    return 'completed';
  };

  const handleSendMessage = async (content: string) => {
    // Validate input
    const trimmed = content.trim();
    if (!trimmed) {
      setErrorMessage('Please enter a concept to learn about');
      return;
    }

    if (trimmed.length > 1000) {
      setErrorMessage('Please keep your question under 1000 characters');
      return;
    }

    setErrorMessage(null);

    // Add user message
    const userMsg: Message = {
      id: uuidv4(),
      role: 'user',
      content: trimmed,
      timestamp: Date.now(),
    };
    setMessages((prev) => [...prev, userMsg]);

    try {
      // Call the real API
      const response = await generateDiagram({
        concept: trimmed,
        educational_level: '11-13', // Default to ages 11-13 (intermediate)
      });

      // Convert SVG content to data URL for inline display
      const imageUrl = `data:image/svg+xml;base64,${btoa(response.svg_content)}`;

      // Add bot response with diagram
      const botMsg: Message = {
        id: uuidv4(),
        role: 'assistant',
        content: `I've created a diagram for "${trimmed}". This visual representation shows the key components and their relationships.\n\n⚠️ This diagram is AI-generated. Please verify with your teacher or textbook for accuracy.`,
        timestamp: Date.now(),
        diagram: {
          image: imageUrl,
          svg_content: response.svg_content,
          xml: response.xml_content,
          export_urls: {
            png: `/api/export/${response.svg_filename}`,
            svg: `/api/export/${response.svg_filename}`,
            xml: `/api/export/${response.xml_filename}`,
          },
          svgFilename: response.svg_filename,
          metadata: {
            score: response.review_score,
            iterations: response.iterations,
            totalTime: response.total_time_seconds,
          },
        },
      };

      setMessages((prev) => [...prev, botMsg]);
    } catch (error) {
      const errorMsg =
        error instanceof APIError
          ? error.message
          : error instanceof Error
            ? error.message
            : 'An unexpected error occurred while generating the diagram';

      setErrorMessage(errorMsg);

      // Add error message to chat
      const errorBotMsg: Message = {
        id: uuidv4(),
        role: 'assistant',
        content: `I encountered an error: ${errorMsg}`,
        timestamp: Date.now(),
      };
      setMessages((prev) => [...prev, errorBotMsg]);
    }
  };

  const handleReset = () => {
    setMessages([]);
    setErrorMessage(null);
  };

  return (
    <Layout onReset={handleReset}>
      {messages.length === 0 ? (
        <div className="flex flex-1 flex-col items-center justify-center p-4">
          <div className="text-center space-y-4 max-w-md">
            <h2 className="text-2xl font-bold tracking-tight">What do you want to learn?</h2>
            <p className="text-muted-foreground">
              Ask me to explain any complex concept, and I'll create a diagram to help you understand.
            </p>
            {errorMessage && (
              <div className="mt-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
                {errorMessage}
              </div>
            )}
          </div>
        </div>
      ) : (
        <>
          {errorMessage && (
            <div className="px-4 py-3 bg-red-100 border-l-4 border-red-500 text-red-700 mb-4">
              {errorMessage}
            </div>
          )}
          <ChatContainer
            messages={messages}
            isLoading={state.isLoading}
            currentStep={mapProgressToStep(state.progress)}
          />
        </>
      )}
      <InputArea onSendMessage={handleSendMessage} isLoading={state.isLoading} />
    </Layout>
  );
}

export default App;
