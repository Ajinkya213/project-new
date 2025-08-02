// components/userboard/ChatMessage.tsx
import * as React from "react";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { Brain, User, Bot, Search, FileText, MessageSquare, Zap } from "lucide-react";

interface Message {
  id: string;
  text: string;
  sender: "user" | "ai";
  timestamp: string;
  agentInfo?: {
    selectedAgent?: string;
    confidence?: number;
  };
}

interface ChatMessageProps {
  message: Message;
}

const getAgentIcon = (agentType?: string) => {
  switch (agentType) {
    case 'multimodal':
      return <Search className="w-4 h-4" />;
    case 'research':
      return <Search className="w-4 h-4" />;
    case 'document':
      return <FileText className="w-4 h-4" />;
    case 'chat':
      return <MessageSquare className="w-4 h-4" />;
    case 'lightweight':
      return <Zap className="w-4 h-4" />;
    default:
      return <Brain className="w-4 h-4" />;
  }
};

const getAgentColor = (agentType?: string) => {
  switch (agentType) {
    case 'multimodal':
      return 'bg-blue-100 text-blue-800 border-blue-200';
    case 'research':
      return 'bg-green-100 text-green-800 border-green-200';
    case 'document':
      return 'bg-purple-100 text-purple-800 border-purple-200';
    case 'chat':
      return 'bg-orange-100 text-orange-800 border-orange-200';
    case 'lightweight':
      return 'bg-gray-100 text-gray-800 border-gray-200';
    default:
      return 'bg-gray-100 text-gray-800 border-gray-200';
  }
};

const getAgentDisplayName = (agentType?: string) => {
  switch (agentType) {
    case 'multimodal':
      return 'Multimodal';
    case 'research':
      return 'Research';
    case 'document':
      return 'Document';
    case 'chat':
      return 'Chat';
    case 'lightweight':
      return 'Lightweight';
    default:
      return 'Auto';
  }
};

export function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.sender === "user";
  const agentInfo = message.agentInfo;

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"} mb-4`}>
      <div className={`flex ${isUser ? "flex-row-reverse" : "flex-row"} items-start gap-3 max-w-[80%]`}>
        {/* Avatar */}
        <Avatar className={`w-8 h-8 ${isUser ? "order-2" : "order-1"}`}>
          {isUser ? (
            <AvatarImage src="/user-avatar.png" />
          ) : (
            <AvatarImage src="/ai-avatar.png" />
          )}
          <AvatarFallback className={isUser ? "bg-primary text-primary-foreground" : "bg-secondary text-secondary-foreground"}>
            {isUser ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
          </AvatarFallback>
        </Avatar>

        {/* Message Content */}
        <div className={`flex flex-col ${isUser ? "items-end" : "items-start"} space-y-2`}>
          {/* Agent Badge for AI messages */}
          {!isUser && agentInfo?.selectedAgent && (
            <div className="flex items-center gap-2">
              <Badge
                variant="outline"
                className={`${getAgentColor(agentInfo.selectedAgent)} text-xs font-medium`}
              >
                {getAgentIcon(agentInfo.selectedAgent)}
                <span className="ml-1">{getAgentDisplayName(agentInfo.selectedAgent)}</span>
                {agentInfo.confidence && (
                  <span className="ml-1 text-xs opacity-75">
                    ({Math.round(agentInfo.confidence * 100)}%)
                  </span>
                )}
              </Badge>
            </div>
          )}

          {/* Message Bubble */}
          <div
            className={`px-4 py-3 rounded-2xl max-w-full ${isUser
                ? "bg-primary text-primary-foreground"
                : "bg-muted text-foreground border border-border"
              }`}
          >
            <div className="whitespace-pre-wrap break-words">
              {message.text}
            </div>
          </div>

          {/* Timestamp */}
          <span className="text-xs text-muted-foreground">
            {message.timestamp}
          </span>
        </div>
      </div>
    </div>
  );
}