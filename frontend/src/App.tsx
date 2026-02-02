import { useState, useEffect } from 'react';
import { Layout } from '@/components/layout/Layout';
import { ChatContainer } from '@/components/features/ChatContainer';
import { InputArea } from '@/components/features/InputArea';
import type { Message } from '@/components/features/MessageBubble';
import type { ProcessingStep } from '@/components/features/ProcessingIndicator';
import { v4 as uuidv4 } from 'uuid';
import { useDiagram } from '@/hooks/useDiagram';
import { APIError } from '@/lib/api';

// Sample diagram XML for demo mode
const DEMO_DIAGRAMS: Record<string, string> = {
  photosynthesis: `<mxfile host="app.diagrams.net" modified="2025-01-28T00:00:00.000Z" agent="VisuaLearn" version="1.0" type="device">
  <diagram id="default" name="Photosynthesis">
    <mxGraphModel dx="0" dy="0" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1200" pageHeight="800" math="0" shadow="0">
      <root>
        <mxCell id="0" value="" parent="" vertex="1" />
        <mxCell id="1" value="" parent="0" vertex="1" />
        <mxCell id="2" value="Photosynthesis" style="rounded=1;whiteSpace=wrap;html=1;fontSize=16;fontStyle=1" vertex="1" parent="1">
          <mxGeometry x="500" y="50" width="200" height="60" as="geometry" />
        </mxCell>
        <mxCell id="3" value="Inputs" style="rounded=1;whiteSpace=wrap;html=1;fontSize=14;fontStyle=1;fillColor=#e1d5e7" vertex="1" parent="1">
          <mxGeometry x="100" y="200" width="120" height="60" as="geometry" />
        </mxCell>
        <mxCell id="4" value="Sunlight" style="ellipse;whiteSpace=wrap;html=1;" vertex="1" parent="1">
          <mxGeometry x="50" y="300" width="80" height="60" as="geometry" />
        </mxCell>
        <mxCell id="5" value="Water" style="ellipse;whiteSpace=wrap;html=1;" vertex="1" parent="1">
          <mxGeometry x="150" y="300" width="80" height="60" as="geometry" />
        </mxCell>
        <mxCell id="6" value="CO₂" style="ellipse;whiteSpace=wrap;html=1;" vertex="1" parent="1">
          <mxGeometry x="250" y="300" width="80" height="60" as="geometry" />
        </mxCell>
        <mxCell id="7" value="Outputs" style="rounded=1;whiteSpace=wrap;html=1;fontSize=14;fontStyle=1;fillColor=#d5e8d4" vertex="1" parent="1">
          <mxGeometry x="900" y="200" width="120" height="60" as="geometry" />
        </mxCell>
        <mxCell id="8" value="Glucose" style="ellipse;whiteSpace=wrap;html=1;" vertex="1" parent="1">
          <mxGeometry x="850" y="300" width="80" height="60" as="geometry" />
        </mxCell>
        <mxCell id="9" value="Oxygen" style="ellipse;whiteSpace=wrap;html=1;" vertex="1" parent="1">
          <mxGeometry x="950" y="300" width="80" height="60" as="geometry" />
        </mxCell>
        <mxCell id="10" edge="1" parent="1" source="3" target="2">
          <mxGeometry width="50" height="50" relative="1" as="geometry">
            <mxPoint x="160" y="260" as="sourcePoint" />
            <mxPoint x="210" y="210" as="targetPoint" />
          </mxGeometry>
        </mxCell>
        <mxCell id="11" edge="1" parent="1" source="4" target="3">
          <mxGeometry width="50" height="50" relative="1" as="geometry">
            <mxPoint x="90" y="360" as="sourcePoint" />
            <mxPoint x="110" y="260" as="targetPoint" />
          </mxGeometry>
        </mxCell>
        <mxCell id="12" edge="1" parent="1" source="5" target="3">
          <mxGeometry width="50" height="50" relative="1" as="geometry">
            <mxPoint x="190" y="360" as="sourcePoint" />
            <mxPoint x="150" y="260" as="targetPoint" />
          </mxGeometry>
        </mxCell>
        <mxCell id="13" edge="1" parent="1" source="6" target="3">
          <mxGeometry width="50" height="50" relative="1" as="geometry">
            <mxPoint x="290" y="360" as="sourcePoint" />
            <mxPoint x="190" y="260" as="targetPoint" />
          </mxGeometry>
        </mxCell>
        <mxCell id="14" edge="1" parent="1" source="2" target="7">
          <mxGeometry width="50" height="50" relative="1" as="geometry">
            <mxPoint x="600" y="110" as="sourcePoint" />
            <mxPoint x="960" y="260" as="targetPoint" />
          </mxGeometry>
        </mxCell>
        <mxCell id="15" edge="1" parent="1" source="7" target="8">
          <mxGeometry width="50" height="50" relative="1" as="geometry">
            <mxPoint x="960" y="260" as="sourcePoint" />
            <mxPoint x="890" y="360" as="targetPoint" />
          </mxGeometry>
        </mxCell>
        <mxCell id="16" edge="1" parent="1" source="7" target="9">
          <mxGeometry width="50" height="50" relative="1" as="geometry">
            <mxPoint x="960" y="260" as="sourcePoint" />
            <mxPoint x="990" y="360" as="targetPoint" />
          </mxGeometry>
        </mxCell>
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>`,
};

function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isDemoMode, setIsDemoMode] = useState(false);
  const { generateDiagram, state } = useDiagram();

  // Check for demo mode on mount
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const demoParam = params.get('demo');
    if (demoParam && DEMO_DIAGRAMS[demoParam]) {
      setIsDemoMode(true);
      // Pre-load demo message
      const botMsg: Message = {
        id: uuidv4(),
        role: 'assistant',
        content: `📚 DEMO MODE: Showing sample diagram for "${demoParam}"\n\nThis is a pre-generated diagram for testing the frontend without consuming API tokens. In production, the system will generate diagrams based on your input.`,
        timestamp: Date.now(),
        diagram: {
          image: '',
          xml_content: DEMO_DIAGRAMS[demoParam],
          xml: DEMO_DIAGRAMS[demoParam],
          export_urls: {
            png: '',
            svg: '',
            xml: '',
          },
          xmlFilename: '',
          metadata: {
            score: 95,
            iterations: 1,
            totalTime: 0.5,
          },
        },
      };
      setMessages([botMsg]);
    }
  }, []);

  const mapProgressToStep = (progress: number): ProcessingStep => {
    if (progress < 20) return 'analyzing';
    if (progress < 40) return 'planning';
    if (progress < 70) return 'generating';
    if (progress < 100) return 'reviewing';
    return 'completed';
  };

  const handleSendMessage = async (content: string) => {
    // Check if in demo mode
    if (isDemoMode) {
      setErrorMessage(
        '📚 Demo Mode: To generate new diagrams, remove the ?demo= parameter from the URL and try again. This will allow the system to use the full API pipeline.'
      );
      return;
    }

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

      // Add bot response with diagram
      const botMsg: Message = {
        id: uuidv4(),
        role: 'assistant',
        content: `I've created a diagram for "${trimmed}". This visual representation shows the key components and their relationships.\n\n⚠️ This diagram is AI-generated. Please verify with your teacher or textbook for accuracy.`,
        timestamp: Date.now(),
        diagram: {
          image: '',
          diagram_svg: response.diagram_svg,
          xml_content: response.diagram_svg,
          xml: response.diagram_svg,
          export_urls: {
            png: `/api/export/${response.svg_filename}`,
            svg: `/api/export/${response.svg_filename}`,
            xml: `/api/export/${response.xml_filename}`,
          },
          xmlFilename: response.xml_filename,
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
