// components/userboard/AgentSelector.tsx
import React, { useState, useEffect } from 'react';
import { AgentService } from '../../lib/agentService';

interface AgentSelectorProps {
    onAgentChange: (agentType: string) => void;
    selectedAgent?: string;
    className?: string;
}

interface Agent {
    name: string;
    description: string;
    status: string;
}

export function AgentSelector({ onAgentChange, selectedAgent = 'lightweight', className = '' }: AgentSelectorProps) {
    const [agents, setAgents] = useState<Record<string, string>>({});
    const [agentStatuses, setAgentStatuses] = useState<Record<string, any>>({});
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        loadAgents();
        loadAgentStatuses();
    }, []);

    const loadAgents = async () => {
        try {
            setLoading(true);
            const response = await AgentService.getAgentHealth();
            if (response.available_agents) {
                const agentDescriptions: Record<string, string> = {};
                response.available_agents.forEach((agent: string) => {
                    agentDescriptions[agent] = getAgentDescription(agent);
                });
                setAgents(agentDescriptions);
            } else {
                // Fallback: show all agents even if health check fails
                const fallbackAgents = {
                    'multimodal': getAgentDescription('multimodal'),
                    'chat': getAgentDescription('chat'),
                    'document': getAgentDescription('document'),
                    'research': getAgentDescription('research'),
                    'lightweight': getAgentDescription('lightweight')
                };
                setAgents(fallbackAgents);
            }
        } catch (err) {
            console.error('Error loading agents:', err);
            // Fallback: show all agents even if health check fails
            const fallbackAgents = {
                'multimodal': getAgentDescription('multimodal'),
                'chat': getAgentDescription('chat'),
                'document': getAgentDescription('document'),
                'research': getAgentDescription('research'),
                'lightweight': getAgentDescription('lightweight')
            };
            setAgents(fallbackAgents);
        } finally {
            setLoading(false);
        }
    };

    const loadAgentStatuses = async () => {
        try {
            const statusResponse = await AgentService.getAgentStatus();
            if (statusResponse.success && statusResponse.status) {
                setAgentStatuses(statusResponse.status);
            } else {
                // Fallback: set default statuses
                const defaultStatuses = {
                    'multimodal': { status: 'offline' },
                    'chat': { status: 'offline' },
                    'document': { status: 'offline' },
                    'research': { status: 'offline' },
                    'lightweight': { status: 'online' }
                };
                setAgentStatuses(defaultStatuses);
            }
        } catch (err) {
            console.error('Error loading agent statuses:', err);
            // Fallback: set default statuses
            const defaultStatuses = {
                'multimodal': { status: 'offline' },
                'chat': { status: 'offline' },
                'document': { status: 'offline' },
                'research': { status: 'offline' },
                'lightweight': { status: 'online' }
            };
            setAgentStatuses(defaultStatuses);
        }
    };

    const getAgentDescription = (agentType: string): string => {
        const descriptions: Record<string, string> = {
            'multimodal': 'Multimodal Retrieval Agent - Handles documents and web search',
            'chat': 'Chat Assistant - General conversation and help',
            'document': 'Document Analyst - Analyzes and extracts insights from documents',
            'research': 'Research Assistant - Conducts comprehensive research',
            'lightweight': 'Lightweight Assistant - Quick and simple responses'
        };
        return descriptions[agentType] || 'Unknown agent type';
    };

    const getStatusColor = (status: string) => {
        switch (status) {
            case 'online':
                return 'text-green-500';
            case 'processing':
                return 'text-yellow-500';
            case 'offline':
                return 'text-red-500';
            default:
                return 'text-gray-500';
        }
    };

    const getStatusIcon = (status: string) => {
        switch (status) {
            case 'online':
                return '🟢';
            case 'processing':
                return '🟡';
            case 'offline':
                return '🔴';
            default:
                return '⚪';
        }
    };

    if (loading) {
        return (
            <div className={`p-4 ${className}`}>
                <div className="animate-pulse">
                    <div className="h-4 bg-gray-200 rounded w-1/4 mb-2"></div>
                    <div className="h-8 bg-gray-200 rounded w-full"></div>
                </div>
            </div>
        );
    }

    return (
        <div className={`p-4 ${className}`}>
            <div className="mb-3">
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Select Agent
                </label>
                {error && (
                    <div className="text-sm text-red-500 mb-2">{error}</div>
                )}
            </div>

            <div className="space-y-2">
                {Object.entries(agents).map(([agentType, description]) => {
                    const status = agentStatuses[agentType]?.status || 'unknown';
                    const isSelected = agentType === selectedAgent;

                    return (
                        <div
                            key={agentType}
                            className={`p-3 rounded-lg border cursor-pointer transition-colors ${isSelected
                                ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                                : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
                                }`}
                            onClick={() => onAgentChange(agentType)}
                        >
                            <div className="flex items-center justify-between">
                                <div className="flex items-center space-x-3">
                                    <span className="text-sm">{getStatusIcon(status)}</span>
                                    <div>
                                        <div className="font-medium text-sm capitalize">
                                            {agentType.replace('_', ' ')}
                                        </div>
                                        <div className="text-xs text-gray-500 dark:text-gray-400">
                                            {description}
                                        </div>
                                    </div>
                                </div>

                                <div className="flex items-center space-x-2">
                                    <span className={`text-xs ${getStatusColor(status)}`}>
                                        {status}
                                    </span>
                                    {isSelected && (
                                        <span className="text-blue-500">✓</span>
                                    )}
                                </div>
                            </div>

                            {agentStatuses[agentType] && (
                                <div className="mt-2 pt-2 border-t border-gray-200 dark:border-gray-700">
                                    <div className="grid grid-cols-3 gap-2 text-xs text-gray-500">
                                        <div>
                                            <span>Queries: </span>
                                            <span className="font-medium">{agentStatuses[agentType].total_queries || 0}</span>
                                        </div>
                                        <div>
                                            <span>Success: </span>
                                            <span className="font-medium">{agentStatuses[agentType].success_rate || 0}%</span>
                                        </div>
                                        <div>
                                            <span>Avg: </span>
                                            <span className="font-medium">{agentStatuses[agentType].average_response_time || 0}s</span>
                                        </div>
                                    </div>
                                </div>
                            )}
                        </div>
                    );
                })}
            </div>
        </div>
    );
} 