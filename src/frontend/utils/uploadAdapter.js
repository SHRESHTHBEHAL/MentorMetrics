import { api } from './api';
import { MAX_VIDEO_SIZE_MB, SUPPORTED_VIDEO_TYPES } from '../config/appConfig';

const MAX_SIZE_BYTES = MAX_VIDEO_SIZE_MB * 1024 * 1024;
const ALLOWED_TYPES = SUPPORTED_VIDEO_TYPES;

const CONFIG = {
    MAX_RETRIES: 3,
    RETRY_DELAY: 1000, // 1 second
};

class UploadError extends Error {
    constructor(message, code) {
        super(message);
        this.name = 'UploadError';
        this.code = code;
    }
}

const validateFile = (file) => {
    if (!file) {
        throw new UploadError('No file selected', 'NO_FILE');
    }

    if (!ALLOWED_TYPES.includes(file.type)) {
        throw new UploadError(
            'Invalid file type. Please upload MP4, MOV, or WEBM.',
            'INVALID_TYPE'
        );
    }

    if (file.size > MAX_SIZE_BYTES) {
        throw new UploadError(
            `File size exceeds limit of ${MAX_VIDEO_SIZE_MB}MB`,
            'INVALID_SIZE'
        );
    }
};

const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

export const uploadVideo = async (file, onProgress) => {
    try {
        validateFile(file);

        const formData = new FormData();
        formData.append('file', file);

        let lastError;
        for (let attempt = 0; attempt < CONFIG.MAX_RETRIES; attempt++) {
            try {
                const response = await api.post('/upload/', formData, {
                    headers: {
                        'Content-Type': 'multipart/form-data',
                    },
                    onUploadProgress: (progressEvent) => {
                        if (onProgress) {
                            const percentCompleted = Math.round(
                                (progressEvent.loaded * 100) / progressEvent.total
                            );
                            onProgress(percentCompleted);
                        }
                    },
                });

                return response.data;
            } catch (error) {
                lastError = error;
                if (error.response && error.response.status >= 400 && error.response.status < 500) {
                    throw error;
                }

                if (attempt < CONFIG.MAX_RETRIES - 1) {
                    await sleep(CONFIG.RETRY_DELAY * (attempt + 1)); // Exponential backoff-ish
                }
            }
        }

        throw lastError;

    } catch (error) {
        if (error instanceof UploadError) {
            throw error;
        }
        throw new UploadError(
            error.response?.data?.detail || 'Upload failed. Please check your connection and try again.',
            'UPLOAD_FAILED'
        );
    }
};
