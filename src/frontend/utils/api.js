import axios from 'axios';
import { API_BASE_URL } from '../config/appConfig';
import { supabase } from './supabase';

export const api = axios.create({
    baseURL: `${API_BASE_URL}/api`,
});

api.interceptors.request.use(async (config) => {
    const { data: { session } } = await supabase.auth.getSession();
    if (session?.access_token) {
        config.headers.Authorization = `Bearer ${session.access_token}`;
    }

    const userId = localStorage.getItem('user_id');
    if (userId) {
        config.headers['X-User-ID'] = userId;
    }

    return config;
});

api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response) {
            const { status } = error.response;
            if (status === 404) {
                console.warn('Resource not found:', error.config.url);
            }
            if (status >= 500) {
                console.error('Server error:', error.message);
            }
        }
        return Promise.reject(error);
    }
);

export const uploadVideo = async (file, onProgress) => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await api.post('/upload/', formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
            if (onProgress) {
                const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
                onProgress(percentCompleted);
            }
        },
    });
    return response.data;
};

export const processSession = async (sessionId) => {
    const response = await api.post(`/process/${sessionId}`);
    return response.data;
};

export const checkStatus = async (sessionId) => {
    const response = await api.get(`/status/${sessionId}`);
    return response.data;
};

export const restartSession = async (sessionId) => {
    const response = await api.post(`/restart/${sessionId}`);
    return response.data;
};

export const getResults = async (sessionId) => {
    const response = await api.get(`/results/${sessionId}`);
    return response.data;
};

export const getSessions = async () => {
    const response = await api.get(`/sessions/list`);
    return response.data;
};
