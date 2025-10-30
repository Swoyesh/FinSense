export const API_BASE_URL = 'http://localhost:8000';

export const API_ENDPOINTS = {
    AUTH: {
        LOGIN: '/auth/login',
        REGISTER: '/auth/register',
        PROFILE: '/auth/profile',
        TOKEN: '/auth/token'
    },
    CHAT: '/chat',
    BUDGET: {
        PREDICT: '/predict_budget',
        DOWNLOAD_CLASSIFICATION: '/download/classification',
        DOWNLOAD_BUDGET: '/download/budget',
    }
}

export const STORAGE_KEYS = {
  TOKEN: 'finsense_token',
  USER: 'finsense_user',
};