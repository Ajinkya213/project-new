// utils/sessionStorage.ts

export interface SessionData {
    lastActivity: number;
    currentSessionId?: string;
    unsavedChanges?: any;
}

export class SessionStorage {
    private static readonly SESSION_KEY = 'chat_session_data';
    private static readonly ACTIVITY_KEY = 'last_activity';

    static saveSessionData(data: Partial<SessionData>): void {
        try {
            const existing = this.getSessionData();
            const updated = { ...existing, ...data };
            sessionStorage.setItem(this.SESSION_KEY, JSON.stringify(updated));
        } catch (error) {
            console.error('Failed to save session data:', error);
        }
    }

    static getSessionData(): SessionData {
        try {
            const data = sessionStorage.getItem(this.SESSION_KEY);
            return data ? JSON.parse(data) : { lastActivity: Date.now() };
        } catch (error) {
            console.error('Failed to get session data:', error);
            return { lastActivity: Date.now() };
        }
    }

    static updateActivity(): void {
        try {
            const data = this.getSessionData();
            data.lastActivity = Date.now();
            this.saveSessionData(data);
        } catch (error) {
            console.error('Failed to update activity:', error);
        }
    }

    static getLastActivity(): number {
        try {
            const data = this.getSessionData();
            return data.lastActivity || Date.now();
        } catch (error) {
            console.error('Failed to get last activity:', error);
            return Date.now();
        }
    }

    static clearSessionData(): void {
        try {
            sessionStorage.removeItem(this.SESSION_KEY);
        } catch (error) {
            console.error('Failed to clear session data:', error);
        }
    }

    static isSessionActive(maxInactiveMinutes: number = 30): boolean {
        const lastActivity = this.getLastActivity();
        const now = Date.now();
        const inactiveTime = now - lastActivity;
        const maxInactiveTime = maxInactiveMinutes * 60 * 1000;

        return inactiveTime < maxInactiveTime;
    }
} 