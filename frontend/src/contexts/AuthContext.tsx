import React, { createContext, useContext, useState, useEffect } from 'react';
import type { ReactNode } from 'react';

interface User {
    id: string;
    username: string;
    email: string;
    created_at: string;
    updated_at: string;
    is_active: boolean;
    is_verified: boolean;
}

interface AuthContextType {
    user: User | null;
    isAuthenticated: boolean;
    isLoading: boolean;
    error: string | null;
    login: (username: string, password: string) => Promise<void>;
    register: (username: string, email: string, password: string) => Promise<void>;
    logout: () => void;
    clearError: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
};

interface AuthProviderProps {
    children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
    const [user, setUser] = useState<User | null>(null);
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const API_BASE = 'http://localhost:8000';

    // Check authentication status on mount
    useEffect(() => {
        checkAuthStatus();
    }, []);

    // Periodic token refresh to prevent expiration during active use
    useEffect(() => {
        if (!isAuthenticated) return;

        const refreshInterval = setInterval(async () => {
            try {
                const refreshToken = localStorage.getItem('refresh_token');
                if (!refreshToken) return;

                const response = await fetch(`${API_BASE}/auth/refresh`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${refreshToken}`
                    }
                });

                if (response.ok) {
                    const data = await response.json();
                    localStorage.setItem('access_token', data.access_token);
                    console.log('Token refreshed successfully');
                }
            } catch (error) {
                console.error('Periodic token refresh failed:', error);
            }
        }, 14 * 60 * 1000); // Refresh every 14 minutes (assuming 15-minute token expiry)

        return () => clearInterval(refreshInterval);
    }, [isAuthenticated]);

    const checkAuthStatus = async () => {
        try {
            const token = localStorage.getItem('access_token');
            if (!token) {
                setIsAuthenticated(false);
                setUser(null);
                setIsLoading(false);
                return;
            }

            // Verify token with backend
            const response = await fetch(`${API_BASE}/auth/verify`, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                const userData = await response.json();
                setUser(userData.user);
                setIsAuthenticated(true);
            } else if (response.status === 401) {
                // Token expired, try to refresh
                const refreshToken = localStorage.getItem('refresh_token');
                if (refreshToken) {
                    try {
                        const refreshResponse = await fetch(`${API_BASE}/auth/refresh`, {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                                'Authorization': `Bearer ${refreshToken}`
                            }
                        });

                        if (refreshResponse.ok) {
                            const refreshData = await refreshResponse.json();
                            localStorage.setItem('access_token', refreshData.access_token);

                            // Verify the new token
                            const verifyResponse = await fetch(`${API_BASE}/auth/verify`, {
                                method: 'GET',
                                headers: {
                                    'Authorization': `Bearer ${refreshData.access_token}`,
                                    'Content-Type': 'application/json'
                                }
                            });

                            if (verifyResponse.ok) {
                                const userData = await verifyResponse.json();
                                setUser(userData.user);
                                setIsAuthenticated(true);
                            } else {
                                throw new Error('Token verification failed after refresh');
                            }
                        } else {
                            throw new Error('Token refresh failed');
                        }
                    } catch (refreshError) {
                        console.error('Token refresh failed:', refreshError);
                        localStorage.removeItem('access_token');
                        localStorage.removeItem('refresh_token');
                        setIsAuthenticated(false);
                        setUser(null);
                    }
                } else {
                    // No refresh token available
                    localStorage.removeItem('access_token');
                    setIsAuthenticated(false);
                    setUser(null);
                }
            } else {
                // Other error, clear tokens
                localStorage.removeItem('access_token');
                localStorage.removeItem('refresh_token');
                setIsAuthenticated(false);
                setUser(null);
            }
        } catch (error) {
            console.error('Auth check failed:', error);
            setIsAuthenticated(false);
            setUser(null);
        } finally {
            setIsLoading(false);
        }
    };

    const login = async (username: string, password: string) => {
        try {
            setIsLoading(true);
            setError(null);

            const response = await fetch(`${API_BASE}/auth/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ username, password })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Login failed');
            }

            // Store tokens
            const { tokens } = data;
            localStorage.setItem('access_token', tokens.access_token);
            localStorage.setItem('refresh_token', tokens.refresh_token);

            // Set user and authentication status
            setUser(data.user);
            setIsAuthenticated(true);
            setError(null);

            // Dispatch login event for other contexts to listen to
            window.dispatchEvent(new CustomEvent('userLogin'));

        } catch (error) {
            setError(error instanceof Error ? error.message : 'Login failed');
            throw error;
        } finally {
            setIsLoading(false);
        }
    };

    const register = async (username: string, email: string, password: string) => {
        try {
            setIsLoading(true);
            setError(null);

            const response = await fetch(`${API_BASE}/auth/register`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ username, email, password })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Registration failed');
            }

            // Store tokens
            const { tokens } = data;
            localStorage.setItem('access_token', tokens.access_token);
            localStorage.setItem('refresh_token', tokens.refresh_token);

            // Set user and authentication status
            setUser(data.user);
            setIsAuthenticated(true);
            setError(null);

            // Dispatch login event for other contexts to listen to
            window.dispatchEvent(new CustomEvent('userLogin'));

        } catch (error) {
            setError(error instanceof Error ? error.message : 'Registration failed');
            throw error;
        } finally {
            setIsLoading(false);
        }
    };

    const logout = async () => {
        try {
            const token = localStorage.getItem('access_token');
            if (token) {
                // Call logout endpoint
                await fetch(`${API_BASE}/auth/logout`, {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json'
                    }
                });
            }
        } catch (error) {
            console.error('Logout error:', error);
        } finally {
            // Clear local storage and state regardless of API call success
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            setUser(null);
            setIsAuthenticated(false);
            setError(null);

            // Dispatch logout event for other contexts to listen to
            window.dispatchEvent(new CustomEvent('userLogout'));
        }
    };

    const clearError = () => {
        setError(null);
    };

    const value: AuthContextType = {
        user,
        isAuthenticated,
        isLoading,
        error,
        login,
        register,
        logout,
        clearError
    };

    return (
        <AuthContext.Provider value={value}>
            {children}
        </AuthContext.Provider>
    );
}; 