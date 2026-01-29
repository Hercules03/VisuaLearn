import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { cn } from "@/lib/utils";
import { User, Bot } from "lucide-react";
import { DiagramCard } from "./DiagramCard";
import { motion } from "framer-motion";

export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: number;
  diagram?: {
    image: string;
    xml: string;
    export_urls: {
      png: string;
      svg: string;
      xml: string;
    };
    pngFilename?: string;
    svgFilename?: string;
    metadata?: {
      score: number;
      iterations: number;
      totalTime: number;
    };
  };
}

interface MessageBubbleProps {
  message: Message;
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === "user";

  return (
    <motion.div
      initial={{ opacity: 0, y: 15, scale: 0.98 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ duration: 0.3, ease: "easeOut" }}
      className={cn(
        "flex w-full gap-4 p-2 md:p-4",
        isUser ? "flex-row-reverse" : "flex-row"
      )}
    >
      <Avatar className={cn(
        "h-9 w-9 border-2 shadow-sm transition-transform hover:scale-105",
        isUser ? "border-blue-100" : "border-emerald-100"
      )}>
        {isUser ? (
          <>
            <AvatarImage src="/user-avatar.png" alt="User" />
            <AvatarFallback className="bg-gradient-to-br from-blue-500 to-blue-600 text-white">
              <User className="h-5 w-5" />
            </AvatarFallback>
          </>
        ) : (
          <>
            <AvatarImage src="/bot-avatar.png" alt="AI" />
            <AvatarFallback className="bg-gradient-to-br from-emerald-400 to-emerald-600 text-white">
              <Bot className="h-5 w-5" />
            </AvatarFallback>
          </>
        )}
      </Avatar>

      <div
        className={cn(
          "flex max-w-[85%] flex-col gap-2 rounded-2xl px-5 py-4 text-base shadow-sm",
          isUser
            ? "bg-blue-600 text-white shadow-blue-600/10 rounded-tr-sm"
            : "bg-white border border-slate-100 text-slate-700 shadow-slate-200/40 rounded-tl-sm"
        )}
      >
        <div className={cn(
          "whitespace-pre-wrap leading-relaxed tracking-wide",
          isUser ? "font-medium" : "font-normal"
        )}>
          {message.content}
        </div>
        {!isUser && message.diagram && (
          <DiagramCard 
            image={message.diagram.image} 
            exportUrls={message.diagram.export_urls} 
          />
        )}
      </div>
    </motion.div>
  );
}