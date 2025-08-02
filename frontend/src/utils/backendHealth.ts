// utils/backendHealth.ts

const API_BASE = 'http://localhost:8000';

export interface BackendHealthStatus {
    isHealthy: boolean;
    isAuthenticated: boolean;
    error?: string;
}

export class BackendHealthChecker {
    static async checkHealth(): Promise<BackendHealthStatus> {
        try {
            // Check basic health
            const healthResponse = await fetch(`${API_BASE}/health`);
            if (!healthResponse.ok) {
                return {
                    isHealthy: false,
                    isAuthenticated: false,
                    error: `Backend health check failed: ${healthResponse.status}`
                };
            }

            // Check authentication status
            const token = localStorage.getItem('access_token');
            if (!token) {
                return {
                    isHealthy: true,
                    isAuthenticated: false,
                    error: 'No authentication token found'
                };
            }

            const authResponse = await fetch(`${API_BASE}/auth/verify`, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (authResponse.ok) {
                return {
                    isHealthy: true,
                    isAuthenticated: true
                };
            } else {
                return {
                    isHealthy: true,
                    isAuthenticated: false,
                    error: 'Authentication token is invalid'
                };
            }
        } catch (error) {
            return {
                isHealthy: false,
                isAuthenticated: false,
                error: `Connection error: ${error instanceof Error ? error.message : 'Unknown error'}`
            };
        }
    }

    static async checkAgentHealth(): Promise<any> {
        try {
            const response = await fetch(`${API_BASE}/agent/health`);
            if (!response.ok) {
                throw new Error(`Agent health check failed: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error('Agent health check error:', error);
            throw error;
        }
    }

    static logAuthStatus(): void {
        const token = localStorage.getItem('access_token');
        const refreshToken = localStorage.getItem('refresh_token');

        console.log('=== Authentication Status ===');
        console.log('Access Token:', token ? 'Present' : 'Missing');
        console.log('Refresh Token:', refreshToken ? 'Present' : 'Missing');
        console.log('===========================');
    }
} 