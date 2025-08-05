import React from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { UserProfile } from './UserProfile';

export function UserProfileWrapper() {
    const { user, logout } = useAuth();

    return <UserProfile user={user} onLogout={logout} />;
} 