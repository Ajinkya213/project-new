// components/userboard/SessionList.tsx
import React from 'react';
import { Plus, MessageSquare } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useChat, type ChatSession } from '@/contexts/ChatContext';

interface SessionListProps {
    sessions: ChatSession[];
    currentSession: ChatSession | null;
    onSessionSelect: (sessionId: string) => void;
    onNewQuery: () => void;
    className?: string;
}

export function SessionList({
    sessions,
    currentSession,
    onSessionSelect,
    onNewQuery,
    className = ''
}: SessionListProps) {
    const { deleteSession, updateSession } = useChat();

    const handleDeleteSession = async (sessionId: string, e: React.MouseEvent) => {
        e.preventDefault();
        e.stopPropagation();
        if (confirm("Are you sure you want to delete this chat session?")) {
            try {
                await deleteSession(sessionId);
            } catch (error) {
                console.error('Failed to delete session:', error);
                alert('Failed to delete session. Please try again.');
            }
        }
    };

    const handleRenameSession = async (session: ChatSession) => {
        const newTitle = prompt("Enter new title:", session.title);
        if (newTitle && newTitle.trim()) {
            try {
                await updateSession(session.id, { title: newTitle.trim() });
            } catch (error) {
                console.error('Failed to rename session:', error);
                alert('Failed to rename session. Please try again.');
            }
        }
    };

    const formatDate = (dateString: string) => {
        const date = new Date(dateString);
        const now = new Date();
        const diffInHours = (now.getTime() - date.getTime()) / (1000 * 60 * 60);

        if (diffInHours < 1) {
            return 'Just now';
        } else if (diffInHours < 24) {
            return `${Math.floor(diffInHours)}h ago`;
        } else {
            return date.toLocaleDateString();
        }
    };

    return (
        <div className={`space-y-2 ${className}`}>
            <Button
                onClick={onNewQuery}
                variant="outline"
                size="sm"
                className="w-full justify-start"
            >
                <Plus className="w-4 h-4 mr-2" />
                New Chat
            </Button>

            <div className="space-y-1">
                {sessions.map((session) => (
                    <div
                        key={session.id}
                        className={`group relative flex items-center space-x-2 rounded-lg px-3 py-2 text-sm font-medium hover:bg-accent hover:text-accent-foreground cursor-pointer transition-colors ${currentSession?.id === session.id ? "bg-accent text-accent-foreground" : ""
                            }`}
                        onClick={() => onSessionSelect(session.id)}
                    >
                        <MessageSquare className="w-4 h-4" />
                        <div className="flex-1 min-w-0">
                            <div className="flex items-center justify-between">
                                <span className="truncate">{session.title}</span>
                                <div className="flex items-center space-x-1 opacity-0 group-hover:opacity-100 transition-opacity">
                                    <Button
                                        variant="ghost"
                                        size="icon"
                                        className="h-6 w-6"
                                        onClick={(e) => {
                                            e.stopPropagation();
                                            handleRenameSession(session);
                                        }}
                                    >
                                        <span className="text-xs">✏️</span>
                                    </Button>
                                    <Button
                                        variant="ghost"
                                        size="icon"
                                        className="h-6 w-6 text-red-500 hover:text-red-700"
                                        onClick={(e) => handleDeleteSession(session.id, e)}
                                    >
                                        <span className="text-xs">🗑️</span>
                                    </Button>
                                </div>
                            </div>
                            <div className="text-xs text-muted-foreground">
                                {formatDate(session.updated_at)}
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
} 