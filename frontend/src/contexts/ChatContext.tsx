import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import type { ReactNode } from 'react';

export interface ChatMessage {
    id: string;
    text: string;
    sender: string; // 'user' or 'ai'
    timestamp: string;
    session_id: string;
    agent_info?: {
        selectedAgent?: string;
        confidence?: number;
    };
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
    addMessage: (sessionId: string, content: string, isUserMessage: boolean, agentInfo?: any) => Promise<void>;
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

export const useChat = () => {
    const context = useContext(ChatContext);
    if (context === undefined) {
        throw new Error('useChat must be used within a ChatProvider');
    }
    return context;
};

interface ChatProviderProps {
    children: ReactNode;
}

export const ChatProvider: React.FC<ChatProviderProps> = ({ children }) => {
    const [sessions, setSessions] = useState<ChatSession[]>([]);
    const [currentSession, setCurrentSessionState] = useState<ChatSession | null>(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const getAuthToken = () => localStorage.getItem('access_token');
    const API_BASE = 'http://localhost:8000';

    // Clear sessions when authentication token is removed
    useEffect(() => {
        const handleStorageChange = () => {
            const token = getAuthToken();
            if (!token) {
                console.log('DEBUG: No auth token found, clearing chat sessions');
                setSessions([]);
                setCurrentSessionState(null);
                setError(null);
            }
        };

        const handleLogout = () => {
            console.log('DEBUG: Logout event received, clearing chat sessions');
            setSessions([]);
            setCurrentSessionState(null);
            setError(null);
        };

        // Check on mount
        handleStorageChange();

        // Listen for storage changes
        window.addEventListener('storage', handleStorageChange);

        // Listen for logout events
        window.addEventListener('userLogout', handleLogout);

        return () => {
            window.removeEventListener('storage', handleStorageChange);
            window.removeEventListener('userLogout', handleLogout);
        };
    }, []);

    // Load sessions on mount and when token becomes available
    useEffect(() => {
        const token = getAuthToken();
        if (token) {
            loadSessions();
        }
    }, []);

    // Listen for login events to reload sessions
    useEffect(() => {
        const handleLogin = () => {
            console.log('DEBUG: Login event received, reloading sessions');
            const token = getAuthToken();
            if (token) {
                loadSessions();
            }
        };

        // Listen for login events
        window.addEventListener('userLogin', handleLogin);

        return () => {
            window.removeEventListener('userLogin', handleLogin);
        };
    }, []);

    // Auto-refresh current session messages every 30 seconds (disabled to prevent message clearing)
    // useEffect(() => {
    //     if (!currentSession) return;

    //     const interval = setInterval(() => {
    //         refreshCurrentSession();
    //     }, 30000);

    //     return () => clearInterval(interval);
    // }, [currentSession?.id]);

    const loadSessions = async () => {
        setIsLoading(true);
        setError(null);

        try {
            const token = getAuthToken();
            console.log('DEBUG: Loading sessions, token exists:', !!token);

            if (!token) {
                console.log('DEBUG: No authentication token, setting empty sessions');
                setSessions([]);
                setCurrentSessionState(null);
                return;
            }

            console.log('DEBUG: Making API call to load sessions');
            const response = await fetch(`${API_BASE}/chat/sessions`, {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });

            console.log('DEBUG: Load sessions response status:', response.status);

            if (!response.ok) {
                if (response.status === 401) {
                    // Token expired or invalid
                    localStorage.removeItem('access_token');
                    setSessions([]);
                    setCurrentSessionState(null);
                    return;
                }
                throw new Error(`Failed to load sessions: ${response.status}`);
            }

            const data = await response.json();
            const sessionsData = data.sessions || [];
            console.log('DEBUG: Received sessions data:', sessionsData);

            // Convert to ChatSession format with empty messages array initially
            const sessionsWithEmptyMessages = sessionsData.map((session: any) => ({
                ...session,
                messages: []
            }));

            console.log('DEBUG: Setting sessions with empty messages initially');
            setSessions(sessionsWithEmptyMessages);

            if (sessionsWithEmptyMessages.length > 0) {
                setCurrentSessionState(sessionsWithEmptyMessages[0]);

                // Load messages for all sessions
                console.log('DEBUG: Loading messages for all sessions');
                for (const session of sessionsWithEmptyMessages) {
                    console.log('DEBUG: Loading messages for session ID:', session.id, 'type:', typeof session.id);
                    await loadMessages(session.id.toString());
                }
            }
        } catch (err) {
            console.error('DEBUG: Error loading sessions:', err);
            setError(err instanceof Error ? err.message : 'Failed to load sessions');
        } finally {
            setIsLoading(false);
        }
    };

    const loadMessages = async (sessionId: string) => {
        try {
            const token = getAuthToken();
            if (!token) {
                throw new Error('No authentication token');
            }

            console.log('DEBUG: Loading messages for session:', sessionId);
            const response = await fetch(`${API_BASE}/chat/sessions/${sessionId}/messages`, {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                if (response.status === 401) {
                    localStorage.removeItem('access_token');
                    throw new Error('Authentication expired');
                }
                throw new Error(`Failed to load messages: ${response.status}`);
            }

            const data = await response.json();
            const messages = data.messages || [];
            console.log('DEBUG: Loaded messages for session', sessionId, ':', messages.length, 'messages');

            // Update sessions with messages
            console.log('DEBUG: Updating sessions with messages for sessionId:', sessionId);
            setSessions(prev => {
                const updated = prev.map(session => {
                    if (session.id.toString() === sessionId.toString()) {
                        console.log('DEBUG: Found matching session, updating with', messages.length, 'messages');
                        return { ...session, messages };
                    }
                    return session;
                });
                console.log('DEBUG: Updated sessions:', updated.map(s => ({ id: s.id, messageCount: s.messages.length })));
                return updated;
            });

            // Update current session if it's the one we're loading
            if (currentSession?.id.toString() === sessionId.toString()) {
                console.log('DEBUG: Updating current session with messages');
                setCurrentSessionState(prev => prev ? { ...prev, messages } : null);
            }
        } catch (err) {
            console.error('DEBUG: Error loading messages:', err);
            setError(err instanceof Error ? err.message : 'Failed to load messages');
            throw err;
        }
    };

    const refreshCurrentSession = useCallback(async () => {
        if (currentSession) {
            try {
                await loadMessages(currentSession.id);
            } catch (error) {
                console.error('Failed to refresh current session:', error);
            }
        }
    }, [currentSession]);

    const setCurrentSession = (sessionId: string) => {
        const session = sessions.find(s => s.id.toString() === sessionId.toString());
        if (session) {
            setCurrentSessionState(session);
            // Load messages if not already loaded
            if (session.messages.length === 0) {
                loadMessages(sessionId).catch(console.error);
            }
        }
    };

    const addSession = async (title?: string): Promise<ChatSession> => {
        try {
            const token = getAuthToken();
            if (!token) {
                throw new Error('No authentication token');
            }

            const sessionTitle = title || 'New Chat';
            const response = await fetch(`${API_BASE}/chat/sessions`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ title: sessionTitle })
            });

            if (!response.ok) {
                throw new Error(`Failed to create session: ${response.status}`);
            }

            const data = await response.json();
            const newSession = data.session;
            const sessionWithMessages = { ...newSession, messages: [] };

            setSessions(prev => [sessionWithMessages, ...prev]);
            setCurrentSessionState(sessionWithMessages);

            return sessionWithMessages;
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to create session');
            throw err;
        }
    };

    const updateSession = async (sessionId: string, updates: Partial<ChatSession>): Promise<void> => {
        try {
            const token = getAuthToken();
            if (!token) {
                throw new Error('No authentication token');
            }

            const response = await fetch(`${API_BASE}/chat/sessions/${sessionId}`, {
                method: 'PUT',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(updates)
            });

            if (!response.ok) {
                throw new Error(`Failed to update session: ${response.status}`);
            }

            setSessions(prev => prev.map(session => {
                if (session.id.toString() === sessionId.toString()) {
                    return { ...session, ...updates };
                }
                return session;
            }));

            if (currentSession?.id.toString() === sessionId.toString()) {
                setCurrentSessionState(prev => prev ? { ...prev, ...updates } : null);
            }
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to update session');
            throw err;
        }
    };

    const deleteSession = async (sessionId: string): Promise<void> => {
        try {
            const token = getAuthToken();
            if (!token) {
                throw new Error('No authentication token');
            }

            const response = await fetch(`${API_BASE}/chat/sessions/${sessionId}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error(`Failed to delete session: ${response.status}`);
            }

            setSessions(prev => prev.filter(session => session.id.toString() !== sessionId.toString()));

            // If we deleted the current session, switch to another one
            if (currentSession?.id.toString() === sessionId.toString()) {
                const remainingSessions = sessions.filter(session => session.id.toString() !== sessionId.toString());
                if (remainingSessions.length > 0) {
                    setCurrentSessionState(remainingSessions[0]);
                } else {
                    setCurrentSessionState(null);
                }
            }
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to delete session');
            throw err;
        }
    };

    const addMessage = async (sessionId: string, content: string, isUserMessage: boolean, agentInfo?: any): Promise<void> => {
        try {
            const token = getAuthToken();
            if (!token) {
                throw new Error('No authentication token');
            }

            // Ensure content is a string
            const contentString = typeof content === 'string' ? content : String(content);

            console.log('[DEBUG] Adding message:', { sessionId, content: contentString.substring(0, 100), isUserMessage, agentInfo }); // Debug log

            const response = await fetch(`${API_BASE}/chat/sessions/${sessionId}/messages`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    text: contentString,
                    sender: isUserMessage ? 'user' : 'ai',
                    agent_info: agentInfo
                })
            });

            if (!response.ok) {
                const errorText = await response.text();
                console.error('[DEBUG] Response error:', response.status, errorText); // Debug log

                // Handle specific error cases
                if (response.status === 400) {
                    try {
                        const errorData = JSON.parse(errorText);
                        if (errorData.error && errorData.error.includes('cannot exceed')) {
                            throw new Error('Response too long. Please try a shorter query.');
                        }
                    } catch (parseError) {
                        // If we can't parse the error, use the original error
                    }
                }

                throw new Error(`Failed to add message: ${response.status}`);
            }

            const data = await response.json();
            const newMessage = data.message_data;

            // Update sessions with new message
            setSessions(prev => prev.map(session => {
                if (session.id.toString() === sessionId.toString()) {
                    return {
                        ...session,
                        messages: [...session.messages, newMessage],
                        updated_at: new Date().toISOString()
                    };
                }
                return session;
            }));

            // Update current session if it's the one we're adding to
            if (currentSession?.id.toString() === sessionId.toString()) {
                setCurrentSessionState(prev => prev ? {
                    ...prev,
                    messages: [...prev.messages, newMessage],
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
            const token = getAuthToken();
            if (!token) {
                throw new Error('No authentication token');
            }

            const response = await fetch(`${API_BASE}/chat/sessions/${sessionId}/messages/${messageId}`, {
                method: 'PUT',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ text: content })
            });

            if (!response.ok) {
                throw new Error(`Failed to update message: ${response.status}`);
            }

            setSessions(prev => prev.map(session => {
                if (session.id.toString() === sessionId.toString()) {
                    return {
                        ...session,
                        messages: session.messages.map(msg =>
                            msg.id.toString() === messageId.toString() ? { ...msg, text: content } : msg
                        )
                    };
                }
                return session;
            }));

            if (currentSession?.id.toString() === sessionId.toString()) {
                setCurrentSessionState(prev => prev ? {
                    ...prev,
                    messages: prev.messages.map(msg =>
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
            const token = getAuthToken();
            if (!token) {
                throw new Error('No authentication token');
            }

            const response = await fetch(`${API_BASE}/chat/sessions/${sessionId}/messages/${messageId}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error(`Failed to delete message: ${response.status}`);
            }

            setSessions(prev => prev.map(session => {
                if (session.id.toString() === sessionId.toString()) {
                    return {
                        ...session,
                        messages: session.messages.filter(msg => msg.id.toString() !== messageId.toString())
                    };
                }
                return session;
            }));

            if (currentSession?.id.toString() === sessionId.toString()) {
                setCurrentSessionState(prev => prev ? {
                    ...prev,
                    messages: prev.messages.filter(msg => msg.id.toString() !== messageId.toString())
                } : null);
            }
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to delete message');
            throw err;
        }
    };

    const clearSession = async (sessionId: string): Promise<void> => {
        try {
            const token = getAuthToken();
            if (!token) {
                throw new Error('No authentication token');
            }

            const response = await fetch(`${API_BASE}/chat/sessions/${sessionId}/messages`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
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
        const session = sessions.find(s => s.id === sessionId);
        if (!session) {
            throw new Error('Session not found');
        }
        return JSON.stringify(session, null, 2);
    };

    const importSession = async (sessionData: string): Promise<void> => {
        try {
            const session = JSON.parse(sessionData);
            // Validate session structure
            if (!session.title || !session.messages) {
                throw new Error('Invalid session data format');
            }

            // Create new session with imported data
            const newSession = await addSession(session.title);

            // Add all messages from imported session
            for (const message of session.messages) {
                await addMessage(newSession.id, message.text, message.sender === 'user');
            }
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to import session');
            throw err;
        }
    };

    const clearAllSessions = () => {
        console.log('DEBUG: Clearing all chat sessions');
        setSessions([]);
        setCurrentSessionState(null);
        setError(null);
    };

    const reloadSessions = async () => {
        console.log('DEBUG: Manually reloading sessions');
        const token = getAuthToken();
        if (token) {
            await loadSessions();
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