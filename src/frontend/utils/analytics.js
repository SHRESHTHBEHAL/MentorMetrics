import { api } from './api';

export const recordEvent = async (eventName, data = {}) => {
    try {
        const { session_id, ...metadata } = data;

        await api.post('/analytics/frontend', {
            event_name: eventName,
            session_id: session_id || null,
            metadata: metadata
        });
    } catch (error) {
        console.warn('[Analytics] Failed to record event:', eventName, error);
    }
};

