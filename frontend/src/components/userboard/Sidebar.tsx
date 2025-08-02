// components/userboard/Sidebar.tsx
import * as React from "react";
import { useLocation } from "react-router-dom";
import { ChevronRightIcon, PlusIcon, GearIcon, ExitIcon, TrashIcon, PersonIcon } from "@radix-ui/react-icons";

import { cn } from "../../lib/utils";
import { Button } from "../ui/button";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "../ui/collapsible";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "../ui/dropdown-menu";
import { useChat, type ChatSession } from "../../contexts/ChatContext";
import { ThemeToggle } from "../ThemeToggle";

interface User {
  id: string;
  username: string;
  email: string;
  created_at: string;
  updated_at: string;
  is_active: boolean;
  is_verified: boolean;
}

interface SidebarProps {
  sessions: ChatSession[];
  currentSession: ChatSession | null;
  onNewQuery: () => void;
  onSessionSelect: (sessionId: string) => void;
  onLogout: () => void;
  user: User | null;
}

export function Sidebar({ sessions, currentSession, onNewQuery, onSessionSelect, onLogout, user }: SidebarProps) {
  const [isOpen, setIsOpen] = React.useState(true);
  const { deleteSession, updateSession } = useChat();
  const location = useLocation();

  // Determine current session ID from URL
  const currentSessionId = new URLSearchParams(location.search).get("query");

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

  // Get initials for circular avatar
  const getInitials = (text: string) => {
    return text
      .split(' ')
      .map(word => word.charAt(0))
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  return (
    <Collapsible
      open={isOpen}
      onOpenChange={setIsOpen}
      className="h-full border-r bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 flex flex-col transition-all duration-300 ease-in-out flex-shrink-0 shadow-sm"
      style={{ width: isOpen ? "320px" : "88px" }}
    >
      {/* Header Section */}
      <div className="flex items-center justify-between p-4 border-b border-border/50">
        {isOpen && (
          <div className="flex items-center space-x-3">
            {user && (
              <div className="flex items-center space-x-3">
                <div className="relative">
                  <div className="w-10 h-10 bg-primary rounded-full flex items-center justify-center text-primary-foreground font-semibold text-sm shadow-sm">
                    {getInitials(user.username)}
                  </div>
                  <div className="absolute -bottom-0.5 -right-0.5 w-3 h-3 bg-green-500 rounded-full border-2 border-background"></div>
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-semibold text-foreground truncate">{user.username}</p>
                  <p className="text-xs text-muted-foreground truncate">{user.email}</p>
                </div>
              </div>
            )}
          </div>
        )}
        <div className="flex items-center gap-2">
          {isOpen && <ThemeToggle size="sm" />}
          <CollapsibleTrigger asChild>
            <Button
              variant="ghost"
              size="icon"
              className="h-9 w-9 rounded-lg hover:bg-accent transition-colors"
            >
              <ChevronRightIcon className={cn("h-4 w-4 transition-transform duration-200", !isOpen && "rotate-180")} />
              <span className="sr-only">Toggle Sidebar</span>
            </Button>
          </CollapsibleTrigger>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-hidden p-4 space-y-6">
        {/* New Chat Button */}
        <div className="space-y-2">
          <Button
            className={cn(
              "transition-all duration-300 font-medium",
              isOpen
                ? "w-full h-11 justify-start gap-3 rounded-lg bg-primary hover:bg-primary/90 text-primary-foreground shadow-sm"
                : "w-12 h-12 p-0 rounded-xl bg-primary hover:bg-primary/90 text-primary-foreground shadow-sm"
            )}
            onClick={onNewQuery}
            title={isOpen ? "Start a new conversation" : "New Chat"}
          >
            <PlusIcon className="h-4 w-4" />
            {isOpen && "New Chat"}
          </Button>
        </div>

        {/* Chat Sessions */}
        <div className="space-y-3">
          {isOpen && (
            <div className="flex items-center justify-between">
              <h2 className="text-sm font-semibold text-foreground">Recent Chats</h2>
              <span className="text-xs text-muted-foreground bg-muted px-2 py-1 rounded-full">
                {sessions.length}
              </span>
            </div>
          )}

          <div className={cn(
            "overflow-y-auto",
            isOpen ? "h-[calc(100vh-300px)]" : "h-[calc(100vh-150px)]"
          )}>
            <div className="space-y-1">
              {sessions.length === 0 ? (
                <div className={cn(
                  "text-center py-8",
                  isOpen ? "px-4" : "px-2"
                )}>
                  {isOpen ? (
                    <div className="space-y-2">
                      <div className="w-12 h-12 bg-muted rounded-full flex items-center justify-center mx-auto">
                        <PersonIcon className="h-6 w-6 text-muted-foreground" />
                      </div>
                      <p className="text-sm text-muted-foreground">No conversations yet</p>
                      <p className="text-xs text-muted-foreground">Start your first chat!</p>
                    </div>
                  ) : (
                    <div className="w-8 h-8 bg-muted rounded-full flex items-center justify-center mx-auto">
                      <PersonIcon className="h-4 w-4 text-muted-foreground" />
                    </div>
                  )}
                </div>
              ) : (
                sessions.map((session) => (
                  <div
                    key={session.id}
                    className={cn(
                      "group relative transition-all duration-200 cursor-pointer",
                      isOpen
                        ? "rounded-lg hover:bg-accent/50"
                        : "rounded-xl hover:bg-accent/50"
                    )}
                    onClick={() => onSessionSelect(session.id)}
                    title={isOpen ? session.title : session.title}
                  >
                    {isOpen ? (
                      <div className={cn(
                        "flex items-center space-x-3 p-3 rounded-lg transition-colors",
                        currentSession?.id === session.id
                          ? "bg-primary/10 border border-primary/20"
                          : "hover:bg-accent/50"
                      )}>
                        <div className={cn(
                          "w-8 h-8 rounded-lg flex items-center justify-center text-sm font-medium transition-colors",
                          currentSession?.id === session.id
                            ? "bg-primary text-primary-foreground"
                            : "bg-muted text-muted-foreground"
                        )}>
                          {getInitials(session.title)}
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center justify-between">
                            <span className="text-sm font-medium text-foreground truncate">
                              {session.title}
                            </span>
                            <DropdownMenu>
                              <DropdownMenuTrigger asChild>
                                <Button
                                  variant="ghost"
                                  size="icon"
                                  className="h-6 w-6 opacity-0 group-hover:opacity-100 transition-opacity rounded-md"
                                  onClick={(e) => e.stopPropagation()}
                                >
                                  <GearIcon className="h-3 w-3" />
                                </Button>
                              </DropdownMenuTrigger>
                              <DropdownMenuContent align="end" className="w-48">
                                <DropdownMenuItem onClick={() => handleRenameSession(session)}>
                                  <GearIcon className="h-4 w-4 mr-2" />
                                  Rename
                                </DropdownMenuItem>
                                <DropdownMenuItem
                                  onClick={(e) => handleDeleteSession(session.id, e)}
                                  className="text-destructive focus:text-destructive"
                                >
                                  <TrashIcon className="h-4 w-4 mr-2" />
                                  Delete
                                </DropdownMenuItem>
                              </DropdownMenuContent>
                            </DropdownMenu>
                          </div>
                          <div className="text-xs text-muted-foreground">
                            {formatDate(session.updated_at)}
                          </div>
                        </div>
                      </div>
                    ) : (
                      // Collapsed view - circular icon
                      <div className="w-full flex justify-center p-2">
                        <div className={cn(
                          "w-10 h-10 rounded-xl flex items-center justify-center text-sm font-medium transition-all duration-200 shadow-sm",
                          currentSession?.id === session.id
                            ? "bg-primary text-primary-foreground ring-2 ring-primary/20"
                            : "bg-muted text-muted-foreground hover:bg-accent hover:text-accent-foreground"
                        )}>
                          {getInitials(session.title)}
                        </div>
                      </div>
                    )}
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>
    </Collapsible>
  );
}