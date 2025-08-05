import { auth } from '../config/firebase';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

class ApiService {
    private async getAuthHeaders(): Promise<HeadersInit> {
        const user = auth.currentUser;
        if (!user) {
            throw new Error('User not authenticated');
        }

        const idToken = await user.getIdToken();
        return {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${idToken}`
        };
    }

    private async makeRequest(endpoint: string, options: RequestInit = {}): Promise<any> {
        try {
            const headers = await this.getAuthHeaders();
            const response = await fetch(`${API_BASE_URL}${endpoint}`, {
                ...options,
                headers: {
                    ...headers,
                    ...options.headers
                }
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || `HTTP ${response.status}: ${response.statusText}`);
            }

            return data;
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    }

    // Chat API methods
    async getChatSessions() {
        return this.makeRequest('/chat/sessions');
    }

    async createChatSession(title: string) {
        return this.makeRequest('/chat/sessions', {
            method: 'POST',
            body: JSON.stringify({ title })
        });
    }

    async getChatSession(sessionId: string) {
        return this.makeRequest(`/chat/sessions/${sessionId}`);
    }

    async updateChatSession(sessionId: string, title: string) {
        return this.makeRequest(`/chat/sessions/${sessionId}`, {
            method: 'PUT',
            body: JSON.stringify({ title })
        });
    }

    async deleteChatSession(sessionId: string) {
        return this.makeRequest(`/chat/sessions/${sessionId}`, {
            method: 'DELETE'
        });
    }

    async addMessage(sessionId: string, text: string, sender: 'user' | 'ai') {
        return this.makeRequest(`/chat/sessions/${sessionId}/messages`, {
            method: 'POST',
            body: JSON.stringify({ text, sender })
        });
    }

    async updateMessage(messageId: string, text: string) {
        return this.makeRequest(`/chat/messages/${messageId}`, {
            method: 'PUT',
            body: JSON.stringify({ text })
        });
    }

    async deleteMessage(messageId: string) {
        return this.makeRequest(`/chat/messages/${messageId}`, {
            method: 'DELETE'
        });
    }

    // Auth API methods
    async verifyToken(idToken: string) {
        return this.makeRequest('/auth/verify-token', {
            method: 'POST',
            body: JSON.stringify({ idToken })
        });
    }

    async getProfile() {
        return this.makeRequest('/auth/profile');
    }

    async updateProfile(name: string) {
        return this.makeRequest('/auth/profile', {
            method: 'PUT',
            body: JSON.stringify({ name })
        });
    }

    async deleteAccount() {
        return this.makeRequest('/auth/delete-account', {
            method: 'DELETE'
        });
    }

    // Agent API methods
    async processQuery(query: string, agentType?: string, sessionId?: string, context?: any) {
        return this.makeRequest('/agent/query', {
            method: 'POST',
            body: JSON.stringify({
                query,
                agent_type: agentType,
                session_id: sessionId,
                context
            })
        });
    }

    async getAvailableAgents() {
        return this.makeRequest('/agent/agents');
    }

    async getAgentStatus(agentType?: string) {
        if (agentType) {
            return this.makeRequest(`/agent/agents/${agentType}/status`);
        } else {
            return this.makeRequest('/agent/agents/status');
        }
    }

    async getUserAgentHistory(limit: number = 10) {
        return this.makeRequest(`/agent/history?limit=${limit}`);
    }

    async getAgentAnalytics() {
        return this.makeRequest('/agent/analytics');
    }

    async processChatQuery(sessionId: string, query: string, agentType: string = 'chat') {
        return this.makeRequest(`/agent/chat/${sessionId}/query`, {
            method: 'POST',
            body: JSON.stringify({
                query,
                agent_type: agentType
            })
        });
    }

    async autoSelectAgent(query: string) {
        return this.makeRequest('/agent/auto-select', {
            method: 'POST',
            body: JSON.stringify({ query })
        });
    }

    async getAgentHealth() {
        return this.makeRequest('/agent/health');
    }

    // API Key management methods
    async getUserApiKeys() {
        return this.makeRequest('/api-keys/keys');
    }

    async getUserKeyStatus() {
        return this.makeRequest('/api-keys/keys/status');
    }

    async getAvailableApiKeys() {
        return this.makeRequest('/api-keys/keys/available');
    }

    async storeApiKey(keyName: string, apiKey: string, validate: boolean = true) {
        return this.makeRequest('/api-keys/keys', {
            method: 'POST',
            body: JSON.stringify({
                key_name: keyName,
                api_key: apiKey,
                validate
            })
        });
    }

    async deleteApiKey(keyName: string) {
        return this.makeRequest(`/api-keys/keys/${keyName}`, {
            method: 'DELETE'
        });
    }

    async validateApiKey(keyName: string, apiKey: string) {
        return this.makeRequest(`/api-keys/keys/${keyName}/validate`, {
            method: 'POST',
            body: JSON.stringify({ api_key: apiKey })
        });
    }

    async testApiKey(keyName: string, apiKey: string) {
        return this.makeRequest('/api-keys/keys/test', {
            method: 'POST',
            body: JSON.stringify({
                key_name: keyName,
                api_key: apiKey
            })
        });
    }

    // File upload method
    async uploadFile(file: File) {
        const user = auth.currentUser;
        if (!user) {
            throw new Error('User not authenticated');
        }

        const formData = new FormData();
        formData.append('file', file);

        const idToken = await user.getIdToken();

        const response = await fetch(`${API_BASE_URL}/api/upload`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${idToken}`
            },
            body: formData
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Upload failed');
        }

        return response.json();
    }

    // File download method
    async downloadFile(documentId: string) {
        const user = auth.currentUser;
        if (!user) {
            throw new Error('User not authenticated');
        }

        const idToken = await user.getIdToken();

        const response = await fetch(`${API_BASE_URL}/api/documents/${documentId}/download`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${idToken}`
            }
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Download failed');
        }

        // Create blob and download
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = documentId; // You might want to get the original filename from the response
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
    }

    // Get file URL for display (if needed)
    getFileUrl(userId: string, filename: string): string {
        return `${API_BASE_URL}/api/uploads/${userId}/${filename}`;
    }

    // Health check
    async healthCheck() {
        try {
            const response = await fetch(`${API_BASE_URL}/health`);
            return response.json();
        } catch (error) {
            console.error('Health check failed:', error);
            throw error;
        }
    }
}

export const apiService = new ApiService(); 