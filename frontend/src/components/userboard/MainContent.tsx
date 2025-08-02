// components/userboard/MainContent.tsx
import React from "react";
import { ChatTab } from "./ChatTab";
import { FileLibraryTab } from "./FileLibraryTab";
import { useChat } from "../../contexts/ChatContext";
import type { ChatMessage } from "../../contexts/ChatContext";
import { truncateResponse, getResponseInfo } from "../../utils/responseTruncator";

interface MainContentProps {
  currentSession?: any;
}

interface UploadedFile {
  id: string;
  name: string;
  size: number;
  type: string;
  uploadDate: string;
  status: "pending" | "uploading" | "completed" | "failed";
  progress?: number; // 0-100
}

export function MainContent({
  currentSession
}: MainContentProps) {
  const { addMessage, addSession, currentSession: session } = useChat();

  // Use the session from context
  const activeSession = session;
  const activeMessages = activeSession?.messages || [];
  const [uploadedFiles, setUploadedFiles] = React.useState<UploadedFile[]>([]);
  const [isSendingMessage, setIsSendingMessage] = React.useState(false);
  const [activeTab, setActiveTab] = React.useState<"chat" | "files">("chat");

  // Enhanced AI response using automatic agent selection
  const generateAIResponse = async (userMessage: string): Promise<{ response: string; agentInfo?: any }> => {
    try {
      const { AgentService } = await import('../../lib/agentService');

      // Use automatic agent selection
      const response = await AgentService.autoQueryAgent({
        query: userMessage
      });

      if (response.success) {
        // Log the selected agent for debugging
        if (response.agent_selection) {
          console.log('Auto-selected agent:', response.agent_selection.selected_agent);
          console.log('Confidence:', response.agent_selection.confidence);
        }

        return {
          response: response.response || 'I processed your message but got an empty response.',
          agentInfo: response.agent_selection
        };
      } else {
        console.error('Agent query failed:', response.error);

        // Try lightweight agent as fallback
        console.log('Trying lightweight agent as fallback...');
        const fallbackResponse = await AgentService.queryAgent({
          query: userMessage,
          agent_type: 'lightweight'
        });

        if (fallbackResponse.success) {
          return {
            response: `[Fallback Response] ${fallbackResponse.response}`,
            agentInfo: { selectedAgent: 'lightweight', confidence: 1.0 }
          };
        }

        return {
          response: `I encountered an error: ${response.error}. Please try again.`,
          agentInfo: { selectedAgent: 'lightweight', confidence: 0.0 }
        };
      }
    } catch (error) {
      console.error('Failed to query agent:', error);
      // Fallback to simple response
      return {
        response: `I understand you said: "${userMessage}". This is a fallback response while the agent service is unavailable.`,
        agentInfo: { selectedAgent: 'lightweight', confidence: 0.0 }
      };
    }
  };

  // Enhanced message sending with better error handling
  const handleSendMessage = async (messageText: string) => {
    if (!activeSession) {
      console.error('No active session');
      // Try to create a new session if none exists
      try {
        const newSession = await addSession();
        if (newSession) {
          // Add user message to new session
          await addMessage(newSession.id, messageText, true);

          // Generate AI response using agent service
          setTimeout(async () => {
            try {
              const aiResponseData = await generateAIResponse(messageText);

              // Use intelligent truncation for long responses
              const responseInfo = getResponseInfo(aiResponseData.response);
              let responseText = aiResponseData.response;
              if (responseInfo.isTooLong) {
                console.log(`Response too long (${responseInfo.length} chars), truncating intelligently`);
                responseText = truncateResponse(aiResponseData.response);
              }

              await addMessage(newSession.id, responseText, false, aiResponseData.agentInfo);
            } catch (error) {
              console.error('Failed to add AI response:', error);
              // Show user-friendly error
              await addMessage(newSession.id, "Sorry, I encountered an error processing your message. Please try again.", false);
            }
          }, 1000 + Math.random() * 2000); // Random delay between 1-3 seconds for realism
        }
      } catch (error) {
        console.error('Failed to create session or send message:', error);
      }
      return;
    }

    setIsSendingMessage(true);
    try {
      // Add user message
      await addMessage(activeSession.id, messageText, true);

      // Generate AI response using agent service
      setTimeout(async () => {
        try {
          const aiResponseData = await generateAIResponse(messageText);
          console.log('AI Response Data:', aiResponseData); // Debug log
          console.log('AI Response:', aiResponseData.response); // Debug log
          console.log('AI Response length:', aiResponseData.response.length); // Debug log
          console.log('AI Response type:', typeof aiResponseData.response); // Debug log
          console.log('Session ID:', activeSession.id, 'Type:', typeof activeSession.id); // Debug log

          // Use intelligent truncation for long responses
          const responseInfo = getResponseInfo(aiResponseData.response);
          console.log('Response info:', responseInfo);

          let responseText = aiResponseData.response;
          if (responseInfo.isTooLong) {
            console.log(`Response too long (${responseInfo.length} chars), truncating intelligently`);
            responseText = truncateResponse(aiResponseData.response);
          }

          await addMessage(activeSession.id, responseText, false, aiResponseData.agentInfo);
        } catch (error) {
          console.error('Failed to add AI response:', error);
          // Show user-friendly error
          await addMessage(activeSession.id, "Sorry, I encountered an error processing your message. Please try again.", false);
        }
      }, 1000 + Math.random() * 2000); // Random delay between 1-3 seconds for realism
    } catch (error) {
      console.error('Failed to send message:', error);
      // Could show a toast notification here
    } finally {
      setIsSendingMessage(false);
    }
  };

  // Enhanced file upload simulation
  const handleFileUpload = (file: File) => {
    const newFile: UploadedFile = {
      id: Date.now().toString(),
      name: file.name,
      size: file.size,
      type: file.type,
      uploadDate: new Date().toISOString().split('T')[0],
      status: "uploading",
      progress: 0
    };

    setUploadedFiles(prev => [...prev, newFile]);

    // Simulate upload progress
    const interval = setInterval(() => {
      setUploadedFiles(prev => prev.map(f => {
        if (f.id === newFile.id) {
          const newProgress = Math.min(f.progress! + 10, 100);
          return { ...f, progress: newProgress };
        }
        return f;
      }));
    }, 100);

    // Clear interval when upload is complete
    setTimeout(() => {
      clearInterval(interval);
      setUploadedFiles(prev => prev.map(f => {
        if (f.id === newFile.id) {
          return { ...f, status: "completed", progress: 100 };
        }
        return f;
      }));
    }, 1000);
  };

  // Handle file deletion
  const handleFileDelete = (fileId: string) => {
    setUploadedFiles(prev => prev.filter(file => file.id !== fileId));
  };

  return (
    <div className="flex-1 flex flex-col h-full w-full">
      {/* Tab Navigation */}
      <div className="border-b">
        <div className="flex items-center px-4">
          <div className="flex">
            <button
              onClick={() => setActiveTab("chat")}
              className={`px-4 py-2 text-sm font-medium ${activeTab === "chat"
                ? "border-b-2 border-primary text-primary"
                : "text-muted-foreground hover:text-foreground"
                }`}
            >
              Chat
            </button>
            <button
              onClick={() => setActiveTab("files")}
              className={`px-4 py-2 text-sm font-medium ${activeTab === "files"
                ? "border-b-2 border-primary text-primary"
                : "text-muted-foreground hover:text-foreground"
                }`}
            >
              Files
            </button>
          </div>
        </div>
      </div>

      {/* Tab Content */}
      <div className="flex-1 overflow-hidden w-full">
        {activeTab === "chat" ? (
          <ChatTab
            currentChatMessages={activeMessages}
            onSendMessage={handleSendMessage}
            isSending={isSendingMessage}
          />
        ) : (
          <FileLibraryTab
            uploadedFiles={uploadedFiles}
            onFileUpload={handleFileUpload}
            onFileDelete={handleFileDelete}
          />
        )}
      </div>
    </div>
  );
}