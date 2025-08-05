// Backend health check utility

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface BackendHealth {
    isAvailable: boolean;
    status: 'healthy' | 'unhealthy' | 'unavailable';
    message: string;
}

export async function checkBackendHealth(): Promise<BackendHealth> {
    try {
        const response = await fetch(`${API_BASE}/health`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            },
            // Add timeout to prevent hanging
            signal: AbortSignal.timeout(5000)
        });

        if (response.ok) {
            const data = await response.json();
            return {
                isAvailable: true,
                status: 'healthy',
                message: data.message || 'Backend is running'
            };
        } else {
            return {
                isAvailable: false,
                status: 'unhealthy',
                message: `Backend responded with status ${response.status}`
            };
        }
    } catch (error) {
        console.log('Backend health check failed:', error);
        return {
            isAvailable: false,
            status: 'unavailable',
            message: 'Backend server is not available. Using local storage mode.'
        };
    }
}

export function isBackendAvailable(): Promise<boolean> {
    return checkBackendHealth().then(health => health.isAvailable);
}

// Cache the health status
let healthCache: BackendHealth | null = null;
let cacheTimestamp = 0;
const CACHE_DURATION = 30000; // 30 seconds

export async function getBackendHealth(): Promise<BackendHealth> {
    const now = Date.now();

    // Return cached result if still valid
    if (healthCache && (now - cacheTimestamp) < CACHE_DURATION) {
        return healthCache;
    }

    // Check health and cache result
    healthCache = await checkBackendHealth();
    cacheTimestamp = now;

    return healthCache;
} 