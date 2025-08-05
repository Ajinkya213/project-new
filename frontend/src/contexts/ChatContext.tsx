import React, { createContext, useContext, useState, useEffect } from 'react';
import type { ReactNode } from 'react';
import { auth } from '../config/firebase';
import { apiService } from '../services/api';

export interface ChatMessage {
    id: string;
    text: string;
    sender: string; // 'user' or 'ai'
    timestamp: string;
    session_id: string;
    agent_info?: {
        selectedAgent?: string;
        confidence?: number;
        documentsUsed?: string[];
        sources?: string[];
        searchResults?: number;
    };
    document_attachments?: {
        filename: string;
        pages?: number;
        status: 'uploading' | 'processing' | 'completed' | 'failed';
    }[];
}

export interface ChatSession {
    id: string;
    title: string;
    created_at: string;
    updated_at: string;
    user_id: string;
    messages: ChatMessage[];
}

interface ChatContextType {
    sessions: ChatSession[];
    currentSession: ChatSession | null;
    isLoading: boolean;
    error: string | null;
    addSession: (title?: string) => Promise<ChatSession>;
    updateSession: (sessionId: string, updates: Partial<ChatSession>) => Promise<void>;
    deleteSession: (sessionId: string) => Promise<void>;
    setCurrentSession: (sessionId: string) => void;
    addMessage: (sessionId: string, content: string, isUserMessage: boolean, agentInfo?: any, documentAttachments?: any[]) => Promise<void>;
    updateMessage: (sessionId: string, messageId: string, content: string) => Promise<void>;
    deleteMessage: (sessionId: string, messageId: string) => Promise<void>;
    clearSession: (sessionId: string) => Promise<void>;
    exportSession: (sessionId: string) => string;
    importSession: (sessionData: string) => Promise<void>;
    loadSessions: () => Promise<void>;
    loadMessages: (sessionId: string) => Promise<void>;
    refreshCurrentSession: () => Promise<void>;
    clearAllSessions: () => void;
    reloadSessions: () => Promise<void>;
}

const ChatContext = createContext<ChatContextType | undefined>(undefined);

export const useChat = (): ChatContextType => {
    const context = useContext(ChatContext);
    if (context === undefined) {
        throw new Error('useChat must be used within a ChatProvider');
    }
    return context;
};

interface ChatProviderProps {
    children: ReactNode;
}

// Add local storage utilities
const STORAGE_KEY = 'chat_sessions';

const getStoredSessions = (): ChatSession[] => {
    try {
        const stored = localStorage.getItem(STORAGE_KEY);
        const sessions = stored ? JSON.parse(stored) : [];

        // Ensure all sessions have the proper structure
        return sessions.map((session: any) => ({
            id: session.id || '',
            title: session.title || 'New Chat',
            created_at: session.created_at || '',
            updated_at: session.updated_at || '',
            user_id: session.user_id || '',
            messages: Array.isArray(session.messages) ? session.messages : []
        }));
    } catch (error) {
        console.error('Failed to load sessions from localStorage:', error);
        return [];
    }
};

const setStoredSessions = (sessions: ChatSession[]) => {
    try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(sessions));
    } catch (error) {
        console.error('Failed to save sessions to localStorage:', error);
    }
};

export const ChatProvider: React.FC<ChatProviderProps> = ({ children }) => {
    const [sessions, setSessions] = useState<ChatSession[]>([]);
    const [currentSession, setCurrentSessionState] = useState<ChatSession | null>(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const API_BASE = 'http://127.0.0.1:8000';

    // Helper function to get auth headers
    const getAuthHeaders = () => {
        try {
            // Get current user from Firebase Auth
            const currentUser = auth.currentUser;
            if (!currentUser) {
                return {
                    'Content-Type': 'application/json'
                };
            }

            // For now, return headers without token until we fix the async issue
            return {
                'Content-Type': 'application/json'
            };
        } catch (error) {
            console.error('Failed to get auth token:', error);
            return {
                'Content-Type': 'application/json'
            };
        }
    };

    // Save sessions to localStorage whenever they change
    useEffect(() => {
        setStoredSessions(sessions);
    }, [sessions]);

    // Load sessions on mount
    useEffect(() => {
        loadSessions();
    }, []);

    const loadSessions = async () => {
        setIsLoading(true);
        setError(null);

        try {
            // Try to load from backend first
            const response = await apiService.getChatSessions();
            const backendSessions = response.sessions || [];

            // Load messages for each session
            const sessionsWithMessages = await Promise.all(
                backendSessions.map(async (session: ChatSession) => {
                    try {
                        const sessionResponse = await apiService.getChatSession(session.id);
                        return {
                            ...session,
                            messages: Array.isArray(sessionResponse.session?.messages) ? sessionResponse.session.messages : []
                        };
                    } catch (err) {
                        console.error(`Failed to load messages for session ${session.id}:`, err);
                        return { ...session, messages: [] };
                    }
                })
            );

            setSessions(sessionsWithMessages);
        } catch (err) {
            console.log('Backend not available, using local storage');
            // If backend fails, use local storage
            const localSessions = getStoredSessions();
            setSessions(localSessions);
        } finally {
            setIsLoading(false);
        }
    };

    const loadMessages = async (sessionId: string) => {
        try {
            const response = await apiService.getChatSession(sessionId);
            const session = response.session;
            const messages = Array.isArray(session?.messages) ? session.messages : [];

            // Update sessions with messages
            setSessions(prev => prev.map(session => {
                if (session.id.toString() === sessionId.toString()) {
                    return { ...session, messages };
                }
                return session;
            }));

            // Update current session if it's the one we're loading
            if (currentSession?.id.toString() === sessionId.toString()) {
                setCurrentSessionState(prev => prev ? { ...prev, messages } : null);
            }

            // Return the updated session with messages
            return { ...session, messages };
        } catch (err) {
            console.log('Backend not available for loading messages');
            // Return local session data
            const localSession = sessions.find(s => s.id.toString() === sessionId.toString());
            return localSession || null;
        }
    };

    const setCurrentSession = (sessionId: string) => {
        const session = sessions.find(s => s.id.toString() === sessionId.toString());
        if (session) {
            // Ensure the session has the proper structure
            const safeSession: ChatSession = {
                ...session,
                messages: Array.isArray(session.messages) ? session.messages : []
            };
            setCurrentSessionState(safeSession);
        }
    };

    const addSession = async (title?: string): Promise<ChatSession> => {
        try {
            const response = await apiService.createChatSession(title || 'New Chat');
            const newSession = response.session;
            setSessions(prev => [newSession, ...prev]);
            return newSession;
        } catch (err) {
            console.log('Backend not available, creating local session');
            // Create local session if backend is not available
            const newSession: ChatSession = {
                id: `local_${Date.now()}`,
                title: title || 'New Chat',
                created_at: new Date().toISOString(),
                updated_at: new Date().toISOString(),
                user_id: 'local_user',
                messages: []
            };
            setSessions(prev => [newSession, ...prev]);
            return newSession;
        }
    };

    const updateSession = async (sessionId: string, updates: Partial<ChatSession>): Promise<void> => {
        try {
            await apiService.updateChatSession(sessionId, updates.title || '');

            setSessions(prev => prev.map(session => {
                if (session.id.toString() === sessionId.toString()) {
                    return { ...session, ...updates, updated_at: new Date().toISOString() };
                }
                return session;
            }));

            if (currentSession?.id.toString() === sessionId.toString()) {
                setCurrentSessionState(prev => prev ? { ...prev, ...updates, updated_at: new Date().toISOString() } : null);
            }
        } catch (err) {
            console.log('Backend not available, updating local session');
            // Update local session
            setSessions(prev => prev.map(session => {
                if (session.id.toString() === sessionId.toString()) {
                    return { ...session, ...updates, updated_at: new Date().toISOString() };
                }
                return session;
            }));

            if (currentSession?.id.toString() === sessionId.toString()) {
                setCurrentSessionState(prev => prev ? { ...prev, ...updates, updated_at: new Date().toISOString() } : null);
            }
        }
    };

    const deleteSession = async (sessionId: string): Promise<void> => {
        try {
            await apiService.deleteChatSession(sessionId);

            setSessions(prev => prev.filter(session => session.id.toString() !== sessionId.toString()));

            if (currentSession?.id.toString() === sessionId.toString()) {
                setCurrentSessionState(null);
            }
        } catch (err) {
            console.log('Backend not available, deleting local session');
            // Delete local session
            setSessions(prev => prev.filter(session => session.id.toString() !== sessionId.toString()));

            if (currentSession?.id.toString() === sessionId.toString()) {
                setCurrentSessionState(null);
            }
        }
    };

    const addMessage = async (sessionId: string, content: string, isUserMessage: boolean, agentInfo?: any, documentAttachments?: any[]): Promise<void> => {
        try {
            const newMessage: ChatMessage = {
                id: `msg_${Date.now()}_${Math.random()}`,
                text: content,
                sender: isUserMessage ? 'user' : 'ai',
                timestamp: new Date().toISOString(),
                session_id: sessionId,
                agent_info: agentInfo,
                document_attachments: documentAttachments
            };

            // Try to save to backend first
            try {
                await apiService.addMessage(sessionId, content, isUserMessage ? 'user' : 'ai');
            } catch (err) {
                console.log('Backend not available, saving message locally');
            }

            // Update sessions with new message
            setSessions(prev => prev.map(session => {
                if (session.id.toString() === sessionId.toString()) {
                    return {
                        ...session,
                        messages: [...(session.messages || []), newMessage],
                        updated_at: new Date().toISOString()
                    };
                }
                return session;
            }));

            // Update current session if it's the one we're adding to
            if (currentSession?.id.toString() === sessionId.toString()) {
                setCurrentSessionState(prev => prev ? {
                    ...prev,
                    messages: [...(prev.messages || []), newMessage],
                    updated_at: new Date().toISOString()
                } : null);
            }
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to add message');
            throw err;
        }
    };

    const updateMessage = async (sessionId: string, messageId: string, content: string): Promise<void> => {
        try {
            const response = await apiService.updateMessage(messageId, content);

            setSessions(prev => prev.map(session => {
                if (session.id.toString() === sessionId.toString()) {
                    return {
                        ...session,
                        messages: (session.messages || []).map(msg =>
                            msg.id.toString() === messageId.toString() ? { ...msg, text: content } : msg
                        )
                    };
                }
                return session;
            }));

            if (currentSession?.id.toString() === sessionId.toString()) {
                setCurrentSessionState(prev => prev ? {
                    ...prev,
                    messages: (prev.messages || []).map(msg =>
                        msg.id.toString() === messageId.toString() ? { ...msg, text: content } : msg
                    )
                } : null);
            }
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to update message');
            throw err;
        }
    };

    const deleteMessage = async (sessionId: string, messageId: string): Promise<void> => {
        try {
            const response = await apiService.deleteMessage(messageId);

            setSessions(prev => prev.map(session => {
                if (session.id.toString() === sessionId.toString()) {
                    return {
                        ...session,
                        messages: (session.messages || []).filter(msg => msg.id.toString() !== messageId.toString())
                    };
                }
                return session;
            }));

            if (currentSession?.id.toString() === sessionId.toString()) {
                setCurrentSessionState(prev => prev ? {
                    ...prev,
                    messages: (prev.messages || []).filter(msg => msg.id.toString() !== messageId.toString())
                } : null);
            }
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to delete message');
            throw err;
        }
    };

    const clearSession = async (sessionId: string): Promise<void> => {
        try {
            const response = await fetch(`${API_BASE}/chat/sessions/${sessionId}/messages`, {
                method: 'DELETE',
                headers: getAuthHeaders()
            });

            if (!response.ok) {
                throw new Error(`Failed to clear session: ${response.status}`);
            }

            setSessions(prev => prev.map(session => {
                if (session.id.toString() === sessionId.toString()) {
                    return { ...session, messages: [] };
                }
                return session;
            }));

            if (currentSession?.id.toString() === sessionId.toString()) {
                setCurrentSessionState(prev => prev ? { ...prev, messages: [] } : null);
            }
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to clear session');
            throw err;
        }
    };

    const exportSession = (sessionId: string): string => {
        const session = sessions.find(s => s.id.toString() === sessionId.toString());
        if (!session) return '';
        return JSON.stringify(session, null, 2);
    };

    const importSession = async (sessionData: string): Promise<void> => {
        try {
            const session = JSON.parse(sessionData);
            // Note: This would need backend support for importing sessions
            console.log('Import session:', session);
        } catch (err) {
            setError('Failed to import session');
        }
    };

    const clearAllSessions = () => {
        setSessions([]);
        setCurrentSessionState(null);
    };

    const reloadSessions = async () => {
        await loadSessions();
    };

    const refreshCurrentSession = async () => {
        if (currentSession) {
            await loadMessages(currentSession.id);
        }
    };

    const value: ChatContextType = {
        sessions,
        currentSession,
        isLoading,
        error,
        addSession,
        updateSession,
        deleteSession,
        setCurrentSession,
        addMessage,
        updateMessage,
        deleteMessage,
        clearSession,
        exportSession,
        importSession,
        loadSessions,
        loadMessages,
        refreshCurrentSession,
        clearAllSessions,
        reloadSessions
    };

    return (
        <ChatContext.Provider value={value}>
            {children}
        </ChatContext.Provider>
    );
}; 