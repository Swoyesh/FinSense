export const API_BASE_URL = 'http://localhost:8000';

export const API_ENDPOINTS = {
    AUTH: {
        LOGIN: '/auth/login',
        REGISTER: '/auth/register',
        PROFILE: '/auth/profile',
        TOKEN: '/auth/token'
    },
    CHAT: '/chat',
    CLASSIFICATION: {
        PREDICT_ACCURACY: '/predict_accuracy',
        PREDICT_SPEED: '/predict_speed',
        DOWNLOAD_ACCURACY: '/download/accurate_classification',
        DOWNLOAD_SPEED: '/download/speed_classification',
    },
    BUDGET: {
        GENERATE: '/budget',
        DOWNLOAD_BUDGET: '/download/budget',
    }
};

export const STORAGE_KEYS = {
  TOKEN: 'finsense_token',
  USER: 'finsense_user',
};