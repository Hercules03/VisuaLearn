import { useState, useRef, type KeyboardEvent } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { SendHorizonal, Sparkles } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

interface InputAreaProps {
  onSendMessage: (message: string) => void;
  isLoading?: boolean;
}

const SUGGESTIONS = [
  "Explain Photosynthesis",
  "How does a CPU work?",
  "Water Cycle diagram",
  "Structure of an Atom"
];

export function InputArea({ onSendMessage, isLoading }: InputAreaProps) {
  const [input, setInput] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSend = () => {
    if (input.trim() && !isLoading) {
      onSendMessage(input.trim());
      setInput("");
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="relative z-10 w-full bg-gradient-to-t from-background via-background to-transparent pb-4 pt-10">
      <div className="mx-auto max-w-3xl px-4">
        {/* Suggestion Chips */}
        <AnimatePresence>
          {!input.trim() && !isLoading && (
            <motion.div 
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 10 }}
              className="mb-4 flex flex-wrap gap-2 justify-center sm:justify-start"
            >
              {SUGGESTIONS.map((suggestion, index) => (
                <motion.button
                  key={suggestion}
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: index * 0.05 }}
                  onClick={() => onSendMessage(suggestion)}
                  disabled={isLoading}
                  className="group flex items-center gap-1.5 rounded-full border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-600 shadow-sm transition-all hover:-translate-y-0.5 hover:border-blue-200 hover:bg-blue-50/50 hover:text-blue-600 hover:shadow-md disabled:opacity-50"
                >
                  <Sparkles className="h-3.5 w-3.5 text-blue-400 group-hover:text-blue-600" />
                  {suggestion}
                </motion.button>
              ))}
            </motion.div>
          )}
        </AnimatePresence>

        <div className="relative rounded-2xl bg-white shadow-xl shadow-slate-200/40 ring-1 ring-slate-200 transition-all focus-within:ring-2 focus-within:ring-blue-500/20 focus-within:shadow-2xl focus-within:shadow-blue-500/10">
          <Textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask anything you want to learn..."
            className="min-h-[60px] w-full resize-none border-0 bg-transparent p-4 pr-14 text-base placeholder:text-slate-400 focus-visible:ring-0"
            disabled={isLoading}
            rows={1}
            style={{ maxHeight: '200px' }}
          />
          <div className="absolute bottom-2 right-2">
            <Button
              size="icon"
              onClick={handleSend}
              disabled={!input.trim() || isLoading}
              className={`h-9 w-9 rounded-xl transition-all ${
                input.trim() 
                  ? "bg-blue-600 text-white shadow-lg shadow-blue-600/20 hover:bg-blue-700 hover:scale-105 active:scale-95" 
                  : "bg-slate-100 text-slate-400 hover:bg-slate-200"
              }`}
            >
              <SendHorizonal className="h-5 w-5" />
              <span className="sr-only">Send</span>
            </Button>
          </div>
        </div>
        
        <p className="mt-3 text-center text-xs font-medium text-slate-400">
          AI can make mistakes. Please verify important information.
        </p>
      </div>
    </div>
  );
}