// components/userboard/UserboardNavbar.tsx
import * as React from "react";
import { Link } from "react-router-dom";
import { Brain, Menu } from "lucide-react";
import { Button } from "../ui/button";
import { Sheet, SheetContent, SheetTrigger } from "../ui/sheet";
import { AgentStatus } from "./AgentStatus";

export function UserboardNavbar() {
    const [isMenuOpen, setIsMenuOpen] = React.useState(false);

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
                                </div>
                            </SheetContent>
                        </Sheet>
                    </div>
                </div>
            </div>
        </nav>
    );
} 