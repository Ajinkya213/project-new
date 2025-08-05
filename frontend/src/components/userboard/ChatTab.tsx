// components/userboard/ChatTab.tsx
import * as React from "react";
import { PaperPlaneIcon } from "@radix-ui/react-icons";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { ChatMessage } from "./ChatMessage";
import { type ChatMessage as ChatMessageType } from "@/contexts/ChatContext";
import { Image, FileText, Search, BarChart3 } from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

interface ChatTabProps {
  currentChatMessages: ChatMessageType[];
  onSendMessage: (message: string) => Promise<void>;
  isSending?: boolean;
  uploadedDocuments?: any[];
}

export function ChatTab({ currentChatMessages, onSendMessage, isSending = false, uploadedDocuments = [] }: ChatTabProps) {
  const [inputMessage, setInputMessage] = React.useState("");
  const messagesEndRef = React.useRef<HTMLDivElement>(null);

  const handleSendMessage = async () => {
    if (inputMessage.trim() && !isSending) {
      try {
        await onSendMessage(inputMessage.trim());
        setInputMessage("");
      } catch (error) {
        console.error('Failed to send message:', error);
      }
    }
  };

  const handleKeyDown = (event: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === "Enter" && !event.shiftKey && !isSending) {
      event.preventDefault(); // Prevent new line
      handleSendMessage();
    }
  };

  React.useEffect(() => {
    // Scroll to the bottom of the chat view when messages change
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [currentChatMessages]);

  // Convert ChatMessageType to the format expected by ChatMessage component
  const formatMessageForDisplay = (msg: ChatMessageType) => ({
    id: msg.id,
    text: msg.text,  // Changed from msg.content to msg.text
    sender: msg.sender as "user" | "ai",  // Changed from is_user_message to sender
    timestamp: new Date(msg.timestamp).toLocaleTimeString([], {  // Changed from created_at to timestamp
      hour: '2-digit',
      minute: '2-digit'
    }),
    agentInfo: msg.agent_info,
    documentAttachments: msg.document_attachments
  });

  return (
    <div className="flex flex-col h-full">
      {/* Auto Agent Selection indicator */}
      <div className="border-b p-3 bg-muted/50">
        <div className="flex items-center justify-between">
          <span className="text-sm font-medium">Agent Selection:</span>
          <div className="flex items-center gap-2">
            <span className="text-sm text-muted-foreground">
              Automatic
            </span>
            {uploadedDocuments.length > 0 && uploadedDocuments.some(doc => doc.status === 'completed') && (
              <div className="flex items-center gap-1 text-xs text-green-600 bg-green-50 px-2 py-1 rounded">
                <FileText className="w-3 h-3" />
                <span>Documents Available</span>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Messages area - removed ScrollArea */}
      <div className="flex-1 overflow-y-auto p-4">
        <div className="space-y-4">
          {currentChatMessages.length === 0 ? (
            <div className="text-center text-muted-foreground pt-10">
              Start a new conversation!
            </div>
          ) : (
            currentChatMessages.map((msg) => (
              <ChatMessage key={msg.id} message={formatMessageForDisplay(msg)} />
            ))
          )}
          <div ref={messagesEndRef} /> {/* Dummy div to scroll to */}
        </div>
      </div>

      <div className="border-t p-4">
        {/* Quick Actions */}
        <div className="flex items-center gap-2 mb-3">
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline" size="sm">
                <Image className="h-4 w-4 mr-2" />
                Image Processing
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent>
              <DropdownMenuItem onClick={() => onSendMessage("[Image Processing] Analyze this image and describe what you see")}>
                <Image className="h-4 w-4 mr-2" />
                Analyze Image
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => onSendMessage("[Image Processing] Extract text from this image")}>
                <FileText className="h-4 w-4 mr-2" />
                Extract Text
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => onSendMessage("[Image Processing] Identify objects and people in this image")}>
                <Search className="h-4 w-4 mr-2" />
                Object Detection
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => onSendMessage("[Image Processing] Generate a detailed description of this image")}>
                <BarChart3 className="h-4 w-4 mr-2" />
                Detailed Description
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>

        {/* Message Input */}
        <div className="flex items-center gap-2">
          <Textarea
            placeholder={
              isSending
                ? "Sending message..."
                : uploadedDocuments.length > 0 && uploadedDocuments.some(doc => doc.status === 'completed')
                  ? "Type your message here... (Documents available for context)"
                  : "Type your message here..."
            }
            className="flex-1 resize-none"
            rows={1}
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={isSending}
          />
          <Button
            size="icon"
            onClick={handleSendMessage}
            disabled={isSending || !inputMessage.trim()}
          >
            {isSending ? (
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
            ) : (
              <PaperPlaneIcon className="h-4 w-4" />
            )}
          </Button>
        </div>

        {/* Document Context Indicator */}
        {uploadedDocuments.length > 0 && uploadedDocuments.some(doc => doc.status === 'completed') && (
          <div className="mt-2 text-xs text-muted-foreground flex items-center gap-1">
            <FileText className="w-3 h-3" />
            <span>Your queries will be processed with uploaded document context</span>
          </div>
        )}
      </div>
    </div>
  );
}