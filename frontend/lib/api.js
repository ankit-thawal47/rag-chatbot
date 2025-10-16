import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Create axios instance with base configuration
const apiClient = axios.create({
  baseURL: API_URL,
  timeout: 30000, // 30 seconds timeout
});

// Add request interceptor to include JWT token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('access_token');
      localStorage.removeItem('user_id');
      localStorage.removeItem('user_email');
      window.location.href = '/';
    }
    return Promise.reject(error);
  }
);

// Authentication API
export const authenticateUser = async (firebaseToken) => {
  try {
    const response = await axios.post(`${API_URL}/auth`, {
      firebase_token: firebaseToken
    });
    return response.data;
  } catch (error) {
    console.error('Authentication error:', error);
    throw error;
  }
};

// File upload API
export const uploadFile = async (file, onProgress = null) => {
  try {
    const formData = new FormData();
    formData.append('file', file);
    
    const config = {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      timeout: 60000, // 60 seconds for file upload
    };
    
    if (onProgress) {
      config.onUploadProgress = (progressEvent) => {
        const percentCompleted = Math.round(
          (progressEvent.loaded * 100) / progressEvent.total
        );
        onProgress(percentCompleted);
      };
    }
    
    const response = await apiClient.post('/upload', formData, config);
    return response.data;
  } catch (error) {
    console.error('Upload error:', error);
    throw error;
  }
};

// Get user files API
export const getFiles = async () => {
  try {
    const response = await apiClient.get('/files');
    return response.data;
  } catch (error) {
    console.error('Get files error:', error);
    throw error;
  }
};

// Chat query API
export const chatQuery = async (query) => {
  try {
    const response = await apiClient.post('/chat', { query });
    return response.data;
  } catch (error) {
    console.error('Chat error:', error);
    throw error;
  }
};

// Get user statistics API
export const getStats = async () => {
  try {
    const response = await apiClient.get('/stats');
    return response.data;
  } catch (error) {
    console.error('Stats error:', error);
    throw error;
  }
};

// Delete document API (placeholder)
export const deleteDocument = async (docId) => {
  try {
    const response = await apiClient.delete(`/documents/${docId}`);
    return response.data;
  } catch (error) {
    console.error('Delete error:', error);
    throw error;
  }
};