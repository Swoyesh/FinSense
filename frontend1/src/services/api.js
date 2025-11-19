import axios from 'axios';
import { API_BASE_URL, API_ENDPOINTS, STORAGE_KEYS } from '../utils/constants';

// Create axios instance with better configuration
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 seconds timeout
});

// Request interceptor to add token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem(STORAGE_KEYS.TOKEN);
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    console.log('📤 API Request:', config.method?.toUpperCase(), config.url);
    return config;
  },
  (error) => {
    console.error('❌ Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    console.log('✅ API Response:', response.config.url, response.status);
    return response;
  },
  (error) => {
    console.error('❌ API Error:', error.response?.status, error.response?.data);
    if (error.response?.status === 401) {
      localStorage.removeItem(STORAGE_KEYS.TOKEN);
      localStorage.removeItem(STORAGE_KEYS.USER);
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  login: async (username, password) => {
    try {
      const response = await axios.post(
        `${API_BASE_URL}${API_ENDPOINTS.AUTH.LOGIN}`,
        { username, password },
        { headers: { 'Content-Type': 'application/json' } }
      );
      console.log('✅ Login successful');
      return response.data;
    } catch (error) {
      console.error('❌ Login failed:', error.response?.data);
      throw error;
    }
  },

  register: async (email, username, fullName, password) => {
    try {
      console.log('📝 Register attempt:', username);
      const response = await api.post(API_ENDPOINTS.AUTH.REGISTER, {
        email,
        username,
        full_name: fullName,
        password,
      });
      console.log('✅ Registration successful');
      return response.data;
    } catch (error) {
      console.error('❌ Registration failed:', error.response?.data);
      throw error;
    }
  },

  getProfile: async () => {
    try {
      const response = await api.get(API_ENDPOINTS.AUTH.PROFILE);
      console.log('✅ Profile fetched');
      return response.data;
    } catch (error) {
      console.error('❌ Profile fetch failed:', error.response?.data);
      throw error;
    }
  },
};

// Chat API
export const chatAPI = {
  sendMessage: async (text, token = null) => {
    try {
      console.log('💬 Sending message:', text.substring(0, 50) + '...');
      const headers = { 'Content-Type': 'application/json' };
      if (token) headers['Authorization'] = `Bearer ${token}`;

      const response = await axios.post(
        `${API_BASE_URL}${API_ENDPOINTS.CHAT}`,
        { text },
        { headers, timeout: 60000 }
      );

      console.log('✅ Chat response received:', response.data);
      return response.data;
    } catch (error) {
      console.error('❌ Chat error:', error.response?.data || error.message);
      if (error.response?.status === 401) {
        const authError = new Error('Authentication required');
        authError.response = error.response;
        throw authError;
      }
      throw error;
    }
  },
};

// Classification API (newly added)
export const classificationAPI = {
  predictAccuracy: async (files) => {
    try {
      console.log('📈 Predicting (Accuracy Mode)...');
      const token = localStorage.getItem(STORAGE_KEYS.TOKEN);
      const formData = new FormData();
      files.forEach(file => formData.append('files', file));

      const response = await api.post(
        API_ENDPOINTS.CLASSIFICATION.PREDICT_ACCURACY,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
            'Authorization': `Bearer ${token}`,
          },
          timeout: 180000, // 3 minutes for accuracy mode
        }
      );

      console.log('✅ Accuracy classification done');
      return response.data;
    } catch (error) {
      console.error('❌ Accuracy classification failed:', error.response?.data);
      throw error;
    }
  },

  predictSpeed: async (files) => {
    try {
      console.log('⚡ Predicting (Speed Mode)...');
      const token = localStorage.getItem(STORAGE_KEYS.TOKEN);
      const formData = new FormData();
      files.forEach(file => formData.append('files', file));

      const response = await api.post(
        API_ENDPOINTS.CLASSIFICATION.PREDICT_SPEED,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
            'Authorization': `Bearer ${token}`,
          },
          timeout: 90000, // 1.5 minutes for speed mode
        }
      );

      console.log('✅ Speed classification done');
      return response.data;
    } catch (error) {
      console.error('❌ Speed classification failed:', error.response?.data);
      throw error;
    }
  },

  downloadAccuracyResult: async () => {
    try {
      console.log('⬇️ Downloading accurate classification...');
      const response = await api.post(
        API_ENDPOINTS.CLASSIFICATION.DOWNLOAD_ACCURACY,
        {},
        { responseType: 'blob' }
      );
      console.log('✅ Accurate classification downloaded');
      return response.data;
    } catch (error) {
      console.error('❌ Accuracy download failed:', error.response?.data);
      throw error;
    }
  },

  downloadSpeedResult: async () => {
    try {
      console.log('⬇️ Downloading speed classification...');
      const response = await api.post(
        API_ENDPOINTS.CLASSIFICATION.DOWNLOAD_SPEED,
        {},
        { responseType: 'blob' }
      );
      console.log('✅ Speed classification downloaded');
      return response.data;
    } catch (error) {
      console.error('❌ Speed download failed:', error.response?.data);
      throw error;
    }
  },
};

// Budget API
export const budgetAPI = {
  generateBudget: async (files, income, savingsAmount) => {
    try {
      console.log('📊 Generating budget:', { files: files.length, income, savingsAmount });
      const token = localStorage.getItem(STORAGE_KEYS.TOKEN);
      const formData = new FormData();
      files.forEach(file => formData.append('files', file));
      formData.append('income', income);
      formData.append('saving_amt', savingsAmount);

      const response = await api.post(API_ENDPOINTS.BUDGET.GENERATE, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
          'Authorization': `Bearer ${token}`,
        },
        timeout: 120000, // 2 minutes
      });

      console.log('✅ Budget generated');
      return response.data;
    } catch (error) {
      console.error('❌ Budget generation failed:', error.response?.data);
      throw error;
    }
  },

  downloadBudget: async () => {
    try {
      console.log('⬇️ Downloading budget...');
      const response = await api.post(
        API_ENDPOINTS.BUDGET.DOWNLOAD_BUDGET,
        {},
        { responseType: 'blob' }
      );
      console.log('✅ Budget downloaded');
      return response.data;
    } catch (error) {
      console.error('❌ Budget download failed:', error.response?.data);
      throw error;
    }
  },
};

export default api;