import React, { createContext, useContext, useState, useEffect } from 'react';
import type { ReactNode } from 'react';
import {
    signInWithEmailAndPassword,
    createUserWithEmailAndPassword,
    signOut,
    onAuthStateChanged,
    updateProfile
} from 'firebase/auth';
import { auth } from '../config/firebase';

// Define Firebase User type to avoid import issues
interface FirebaseUser {
    uid: string;
    email: string | null;
    displayName: string | null;
    getIdToken(): Promise<string>;
}

interface User {
    uid: string;
    email: string;
    name?: string;
}

interface AuthContextType {
    user: User | null;
    isAuthenticated: boolean;
    login: (email: string, password: string) => Promise<void>;
    signup: (email: string, password: string, name?: string) => Promise<void>;
    logout: () => Promise<void>;
    loading: boolean;
    error: string | null;
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
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        // Listen for Firebase auth state changes
        const unsubscribe = onAuthStateChanged(auth, (firebaseUser: FirebaseUser | null) => {
            if (firebaseUser) {
                // User is signed in
                const userData: User = {
                    uid: firebaseUser.uid,
                    email: firebaseUser.email || '',
                    name: firebaseUser.displayName || undefined
                };
                setUser(userData);
            } else {
                // User is signed out
                setUser(null);
            }
            setLoading(false);
        });

        // Cleanup subscription on unmount
        return () => unsubscribe();
    }, []);

    const login = async (email: string, password: string) => {
        try {
            setLoading(true);
            setError(null);

            // Sign in with Firebase
            const userCredential = await signInWithEmailAndPassword(auth, email, password);
            const firebaseUser = userCredential.user;

            // Update user state (this will be handled by onAuthStateChanged)
            const userData: User = {
                uid: firebaseUser.uid,
                email: firebaseUser.email || '',
                name: firebaseUser.displayName || undefined
            };
            setUser(userData);

        } catch (error: any) {
            const errorMessage = error.code === 'auth/user-not-found' || error.code === 'auth/wrong-password'
                ? 'Invalid email or password'
                : error.code === 'auth/too-many-requests'
                    ? 'Too many failed attempts. Please try again later.'
                    : 'Login failed. Please try again.';

            setError(errorMessage);
            console.error('Login error:', error);
            throw new Error(errorMessage);
        } finally {
            setLoading(false);
        }
    };

    const signup = async (email: string, password: string, name?: string) => {
        try {
            setLoading(true);
            setError(null);

            // Create user with Firebase
            const userCredential = await createUserWithEmailAndPassword(auth, email, password);
            const firebaseUser = userCredential.user;

            // Update profile with display name if provided
            if (name) {
                await updateProfile(firebaseUser, {
                    displayName: name
                });
            }

            // Update user state (this will be handled by onAuthStateChanged)
            const userData: User = {
                uid: firebaseUser.uid,
                email: firebaseUser.email || '',
                name: name || firebaseUser.displayName || undefined
            };
            setUser(userData);

        } catch (error: any) {
            const errorMessage = error.code === 'auth/email-already-in-use'
                ? 'Email is already registered. Please use a different email or try logging in.'
                : error.code === 'auth/weak-password'
                    ? 'Password is too weak. Please use a stronger password.'
                    : error.code === 'auth/invalid-email'
                        ? 'Invalid email address.'
                        : 'Signup failed. Please try again.';

            setError(errorMessage);
            console.error('Signup error:', error);
            throw new Error(errorMessage);
        } finally {
            setLoading(false);
        }
    };

    const logout = async () => {
        try {
            await signOut(auth);
            setUser(null);
            setError(null);
        } catch (error) {
            console.error('Logout error:', error);
            setError('Logout failed. Please try again.');
        }
    };

    const clearError = () => {
        setError(null);
    };

    const value: AuthContextType = {
        user,
        isAuthenticated: !!user,
        login,
        signup,
        logout,
        loading,
        error,
        clearError,
    };

    return (
        <AuthContext.Provider value={value}>
            {children}
        </AuthContext.Provider>
    );
}; 