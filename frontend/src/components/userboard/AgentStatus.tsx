// components/userboard/AgentStatus.tsx
import React, { useState, useEffect } from 'react';
import { AgentService } from '../../lib/agentService';

interface AgentStatusProps {
    className?: string;
    showDetails?: boolean;
}

interface AgentStats {
    status: string;
    total_queries: number;
    successful_queries: number;
    failed_queries: number;
    success_rate: number;
    average_response_time: number;
    last_activity: string | null;
}

export function AgentStatus({ className = '', showDetails = false }: AgentStatusProps) {
    const [status, setStatus] = useState<'online' | 'offline' | 'checking'>('checking');
    const [lastChecked, setLastChecked] = useState<Date | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [agentStats, setAgentStats] = useState<AgentStats | null>(null);
    const [isExpanded, setIsExpanded] = useState(false);

    const checkAgentStatus = async () => {
        try {
            setStatus('checking');
            setError(null);

            const health = await AgentService.getAgentHealth();

            if (health.status === 'healthy' || health.status === 'degraded') {
                setStatus('online');
                setLastChecked(new Date());

                // Get detailed stats if available
                if (health.agent_statuses) {
                    const lightweightStats = health.agent_statuses.lightweight;
                    if (lightweightStats) {
                        setAgentStats(lightweightStats);
                    }
                }
            } else {
                setStatus('offline');
                setError(health.error || 'Agent is not responding');
            }
        } catch (err) {
            setStatus('offline');
            setError(err instanceof Error ? err.message : 'Failed to check agent status');
        }
    };

    useEffect(() => {
        checkAgentStatus();

        // Check status every 30 seconds
        const interval = setInterval(checkAgentStatus, 30000);

        return () => clearInterval(interval);
    }, []);

    const getStatusColor = () => {
        switch (status) {
            case 'online':
                return 'text-green-500';
            case 'offline':
                return 'text-red-500';
            case 'checking':
                return 'text-yellow-500';
            default:
                return 'text-gray-500';
        }
    };

    const getStatusIcon = () => {
        switch (status) {
            case 'online':
                return '🟢';
            case 'offline':
                return '🔴';
            case 'checking':
                return '🟡';
            default:
                return '⚪';
        }
    };

    const getStatusText = () => {
        switch (status) {
            case 'online':
                return 'Agent Online';
            case 'offline':
                return 'Agent Offline';
            case 'checking':
                return 'Checking Status...';
            default:
                return 'Unknown Status';
        }
    };

    return (
        <div className={`p-2 rounded-md bg-gray-50 dark:bg-gray-800 ${className}`}>
            <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                    <span className="text-sm">{getStatusIcon()}</span>
                    <span className={`text-sm font-medium ${getStatusColor()}`}>
                        {getStatusText()}
                    </span>
                </div>

                <div className="flex items-center space-x-2">
                    {lastChecked && (
                        <span className="text-xs text-gray-500">
                            {lastChecked.toLocaleTimeString()}
                        </span>
                    )}

                    {showDetails && (
                        <button
                            onClick={() => setIsExpanded(!isExpanded)}
                            className="text-xs text-blue-500 hover:text-blue-700 underline"
                        >
                            {isExpanded ? 'Hide' : 'Details'}
                        </button>
                    )}

                    <button
                        onClick={checkAgentStatus}
                        className="text-xs text-blue-500 hover:text-blue-700 underline"
                        disabled={status === 'checking'}
                    >
                        Refresh
                    </button>
                </div>
            </div>

            {error && (
                <div className="mt-2 text-xs text-red-500">
                    {error}
                </div>
            )}

            {showDetails && isExpanded && agentStats && (
                <div className="mt-3 pt-3 border-t border-gray-200 dark:border-gray-700">
                    <div className="grid grid-cols-2 gap-2 text-xs">
                        <div>
                            <span className="text-gray-500">Total Queries:</span>
                            <span className="ml-1 font-medium">{agentStats.total_queries}</span>
                        </div>
                        <div>
                            <span className="text-gray-500">Success Rate:</span>
                            <span className="ml-1 font-medium">{agentStats.success_rate}%</span>
                        </div>
                        <div>
                            <span className="text-gray-500">Avg Response:</span>
                            <span className="ml-1 font-medium">{agentStats.average_response_time}s</span>
                        </div>
                        <div>
                            <span className="text-gray-500">Successful:</span>
                            <span className="ml-1 font-medium">{agentStats.successful_queries}</span>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
} 