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
      // Don't redirect automatically, let components handle it
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  login: async (username, password) => {
    try {
      const formData = new FormData();
      formData.append('username', username);
      formData.append('password', password);
      
      console.log('🔐 Login attempt:', username);
      
      const response = await axios.post(
      `${API_BASE_URL}${API_ENDPOINTS.AUTH.LOGIN}`,
      {
        username,
        password
      }, 
      {
        headers: {
          'Content-Type': 'application/json',
        },
      }
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

// Chat API - FIXED VERSION
export const chatAPI = {
  sendMessage: async (text, token = null) => {
    try {
      console.log('💬 Sending message:', text.substring(0, 50) + '...');
      
      const headers = {
        'Content-Type': 'application/json',
      };
      
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      const response = await axios.post(
        `${API_BASE_URL}${API_ENDPOINTS.CHAT}`,
        { text },
        { 
          headers,
          timeout: 60000, // 60 seconds for chat responses
        }
      );
      
      console.log('✅ Chat response received:', response.data);
      return response.data;
    } catch (error) {
      console.error('❌ Chat error:', error.response?.data || error.message);
      
      // Re-throw with better error info
      if (error.response?.status === 401) {
        const authError = new Error('Authentication required');
        authError.response = error.response;
        throw authError;
      }
      
      throw error;
    }
  },
};

// Budget API
export const budgetAPI = {
  predictBudget: async (files, income, savingsAmount) => {
    try {
      console.log('📊 Predicting budget:', { files: files.length, income, savingsAmount });
      
      const token = localStorage.getItem(STORAGE_KEYS.TOKEN);
      const formData = new FormData();
      files.forEach(file => formData.append('files', file));
      formData.append('income', income);
      formData.append('saving_amt', savingsAmount);

      const response = await api.post(API_ENDPOINTS.BUDGET.PREDICT, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
          'Authorization': `Bearer ${token}`,
        },
        timeout: 120000, // 2 minutes for budget processing
      });
      
      console.log('✅ Budget prediction received');
      return response.data;
    } catch (error) {
      console.error('❌ Budget prediction failed:', error.response?.data);
      throw error;
    }
  },

  downloadClassification: async () => {
    try {
      console.log('⬇️ Downloading classification...');
      
      const response = await api.post(
        API_ENDPOINTS.BUDGET.DOWNLOAD_CLASSIFICATION,
        {},
        { responseType: 'blob' }
      );
      
      console.log('✅ Classification downloaded');
      return response.data;
    } catch (error) {
      console.error('❌ Classification download failed:', error.response?.data);
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