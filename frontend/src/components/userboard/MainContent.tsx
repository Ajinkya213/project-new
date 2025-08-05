// components/userboard/MainContent.tsx
import React from "react";
import { ChatTab } from "./ChatTab";
import { FileLibraryTab } from "./FileLibraryTab";
import { DocumentAgentTab } from "./DocumentAgentTab";
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

interface UploadedDocument {
  id: string;
  name: string;
  size: number;
  type: string;
  uploadDate: string;
  status: 'uploading' | 'processing' | 'completed' | 'failed';
  progress?: number;
  pages?: number;
  error?: string;
}

export function MainContent({
  currentSession
}: MainContentProps) {
  const { addMessage, addSession, currentSession: session } = useChat();

  // Use the session from context
  const activeSession = session;
  const activeMessages = activeSession?.messages || [];
  const [uploadedFiles, setUploadedFiles] = React.useState<UploadedFile[]>([]);
  const [uploadedDocuments, setUploadedDocuments] = React.useState<UploadedDocument[]>([]);
  const [isSendingMessage, setIsSendingMessage] = React.useState(false);
  const [activeTab, setActiveTab] = React.useState<"chat" | "files" | "documents">("chat");

  // Check if documents are available for context
  const hasAvailableDocuments = uploadedDocuments.length > 0 && uploadedDocuments.some(doc => doc.status === 'completed');

  // Enhanced AI response using automatic agent selection with document context
  const generateAIResponse = async (userMessage: string): Promise<{ response: string; agentInfo?: any }> => {
    try {
      const { AgentService } = await import('../../lib/agentService');

      // Check if this is a document query
      if (userMessage.startsWith('[Document Query]')) {
        // Use document agent for document-specific queries
        const { DocumentAgentService } = await import('../../lib/documentAgentService');
        const documentQuery = userMessage.replace('[Document Query] ', '');

        const response = await DocumentAgentService.queryDocumentAgent(documentQuery);

        if (response.success) {
          return {
            response: response.response || 'I processed your document query but got an empty response.',
            agentInfo: {
              selectedAgent: 'document',
              confidence: 1.0,
              documentsUsed: response.document_matches?.map((doc: any) => doc.filename) || [],
              sources: response.sources || [],
              searchResults: response.documents_found || 0
            }
          };
        } else {
          return {
            response: `Document query failed: ${response.error}. Please try again.`,
            agentInfo: { selectedAgent: 'document', confidence: 0.0 }
          };
        }
      }

      // Check if this is an image processing query
      if (userMessage.startsWith('[Image Processing]')) {
        // Use multimodal agent for image processing
        const imageQuery = userMessage.replace('[Image Processing] ', '');

        const response = await AgentService.queryAgent({
          query: imageQuery,
          agent_type: 'multimodal'
        });

        if (response.success) {
          return {
            response: response.response || 'I processed your image but got an empty response.',
            agentInfo: {
              selectedAgent: 'multimodal',
              confidence: 1.0,
              sources: ['image_processing'],
              searchResults: 1
            }
          };
        } else {
          return {
            response: `Image processing failed: ${response.error}. Please try again.`,
            agentInfo: { selectedAgent: 'multimodal', confidence: 0.0 }
          };
        }
      }

      // Check if we have uploaded documents and should use document context
      const hasUploadedDocuments = uploadedDocuments.length > 0 && uploadedDocuments.some(doc => doc.status === 'completed');

      if (hasUploadedDocuments) {
        // Use document agent for queries when documents are available
        console.log('Documents available, using document agent for context');
        const { DocumentAgentService } = await import('../../lib/documentAgentService');

        const response = await DocumentAgentService.queryDocumentAgent(userMessage);

        if (response.success) {
          return {
            response: response.response || 'I processed your query with document context but got an empty response.',
            agentInfo: {
              selectedAgent: 'document',
              confidence: 1.0,
              documentsUsed: response.document_matches?.map((doc: any) => doc.filename) || [],
              sources: response.sources || ['uploaded_documents'],
              searchResults: response.documents_found || 0
            }
          };
        } else {
          console.log('Document agent failed, falling back to regular agent');
        }
      }

      // Use automatic agent selection for regular queries (fallback or no documents)
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
          agentInfo: {
            ...response.agent_selection,
            sources: (response as any).sources || ['general_knowledge'],
            searchResults: (response as any).search_results_count || 0
          }
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
      // Fallback to simple response when backend is not available
      return {
        response: `I understand you said: "${userMessage}". This is a fallback response while the agent service is unavailable. You can still chat and your messages will be saved locally.`,
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
          await addMessage(newSession.id, messageText, true, undefined, uploadedDocuments.length > 0 ? uploadedDocuments.map(doc => ({
            filename: doc.name,
            pages: doc.pages,
            status: doc.status
          })) : undefined);

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
      await addMessage(activeSession.id, messageText, true, undefined, uploadedDocuments.length > 0 ? uploadedDocuments.map(doc => ({
        filename: doc.name,
        pages: doc.pages,
        status: doc.status
      })) : undefined);

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
              onClick={() => setActiveTab("documents")}
              className={`px-4 py-2 text-sm font-medium ${activeTab === "documents"
                ? "border-b-2 border-primary text-primary"
                : "text-muted-foreground hover:text-foreground"
                }`}
            >
              Document Agent
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
      <div className="flex-1 overflow-y-auto w-full">
        {activeTab === "chat" ? (
          <ChatTab
            currentChatMessages={activeMessages}
            onSendMessage={handleSendMessage}
            isSending={isSendingMessage}
            uploadedDocuments={uploadedDocuments}
          />
        ) : activeTab === "documents" ? (
          <DocumentAgentTab
            onSendMessage={handleSendMessage}
            onSwitchToChat={() => setActiveTab("chat")}
            uploadedDocuments={uploadedDocuments}
            setUploadedDocuments={setUploadedDocuments}
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