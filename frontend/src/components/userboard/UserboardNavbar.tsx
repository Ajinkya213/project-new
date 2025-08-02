// components/userboard/UserboardNavbar.tsx
import React, { useState } from 'react';
import { Brain, Menu, LogOut } from 'lucide-react';
import { Button } from "@/components/ui/button";
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet";
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { AgentStatus } from './AgentStatus';

interface UserboardNavbarProps {
    user: any;
    onLogout: () => void;
}

export function UserboardNavbar({
    user,
    onLogout
}: UserboardNavbarProps) {
    const [isMenuOpen, setIsMenuOpen] = useState(false);
    const navigate = useNavigate();

    // Close dropdowns when clicking outside
    React.useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            const target = event.target as Element;
            if (!target.closest('.dropdown-container')) {
                // setShowUserMenu(false); // This state was removed
            }
        };

        document.addEventListener('mousedown', handleClickOutside);
        return () => {
            document.removeEventListener('mousedown', handleClickOutside);
        };
    }, []);

    // Removed theme-related useEffects

    // Removed toggleTheme function

    // Get initials for user avatar
    const getInitials = (text: string) => {
        return text
            .split(' ')
            .map(word => word.charAt(0))
            .join('')
            .toUpperCase()
            .slice(0, 2);
    };

    return (
        <nav className="fixed w-full z-50 bg-background/80 backdrop-blur-lg border-b border-border">
            <div className="w-full px-4 sm:px-6 lg:px-8">
                <div className="flex justify-between items-center py-4 w-full">
                    {/* Left side - Logo */}
                    <div className="flex items-center space-x-4">
                        <Link to="/userboard" className="flex items-center space-x-2">
                            <div className="w-10 h-10 bg-primary text-primary-foreground rounded-lg flex items-center justify-center">
                                <Brain className="w-6 h-6" />
                            </div>
                            <span className="text-2xl font-bold text-foreground">
                                AIM
                            </span>
                        </Link>
                    </div>

                    {/* Right side - Agent Status and Mobile Menu */}
                    <div className="flex items-center space-x-4">
                        {/* Agent Status */}
                        <div className="hidden md:flex items-center space-x-2">
                            <div className="flex items-center space-x-2 text-sm text-muted-foreground">
                                <Brain className="w-4 h-4" />
                                <span>Auto Agent Selection</span>
                            </div>
                            <div className="hidden lg:block">
                                <AgentStatus showDetails={false} />
                            </div>
                        </div>

                        {/* Mobile Menu Button */}
                        <Sheet open={isMenuOpen} onOpenChange={setIsMenuOpen}>
                            <SheetTrigger asChild>
                                <Button variant="ghost" size="icon" className="md:hidden w-8 h-8 rounded-lg">
                                    <Menu className="h-4 w-4" />
                                </Button>
                            </SheetTrigger>
                            <SheetContent side="right">
                                <div className="flex flex-col space-y-6">
                                    <div className="flex items-center space-x-2">
                                        <div className="w-8 h-8 bg-primary text-primary-foreground rounded-lg flex items-center justify-center">
                                            <Brain className="w-5 h-5" />
                                        </div>
                                        <span className="text-lg font-bold">AIM</span>
                                    </div>

                                    <div className="space-y-2">
                                        <p className="text-sm font-medium text-muted-foreground">Auto Agent Selection</p>
                                        <p className="text-xs text-muted-foreground">
                                            Agents are automatically selected based on your query content.
                                        </p>
                                    </div>

                                    <div className="space-y-2">
                                        <p className="text-sm font-medium text-muted-foreground">Agent Status</p>
                                        <AgentStatus showDetails={true} />
                                    </div>

                                    <div className="border-t pt-4">
                                        <div className="flex items-center space-x-3 mb-4">
                                            <div className="w-8 h-8 bg-primary rounded-full flex items-center justify-center text-primary-foreground text-xs font-semibold">
                                                {getInitials(user?.username || 'User')}
                                            </div>
                                            <div>
                                                <p className="text-sm font-semibold">{user?.username || 'User'}</p>
                                                <p className="text-xs text-muted-foreground">{user?.email || 'user@example.com'}</p>
                                            </div>
                                        </div>
                                        <Button
                                            onClick={onLogout}
                                            variant="ghost"
                                            className="w-full justify-start text-destructive"
                                        >
                                            <LogOut className="h-4 w-4 mr-2" />
                                            Sign Out
                                        </Button>
                                    </div>
                                </div>
                            </SheetContent>
                        </Sheet>
                    </div>
                </div>
            </div>
        </nav>
    );
} 