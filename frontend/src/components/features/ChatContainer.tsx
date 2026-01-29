import { useRef, useEffect } from "react";
import { ScrollArea } from "@/components/ui/scroll-area";
import { MessageBubble, type Message } from "./MessageBubble";
import { ProcessingIndicator, type ProcessingStep } from "./ProcessingIndicator";

interface ChatContainerProps {
  messages: Message[];
  isLoading?: boolean;
  currentStep?: ProcessingStep;
}

export function ChatContainer({ messages, isLoading, currentStep = 'analyzing' }: ChatContainerProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (bottomRef.current) {
      bottomRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages, isLoading]);

  return (
    <ScrollArea className="flex-1 px-4">
      <div className="mx-auto flex max-w-3xl flex-col gap-4 py-6">
        {messages.map((msg) => (
          <MessageBubble key={msg.id} message={msg} />
        ))}
        {isLoading && (
          <div className="flex w-full gap-3">
             <div className="flex-1">
                <ProcessingIndicator currentStep={currentStep} />
             </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>
    </ScrollArea>
  );
}
