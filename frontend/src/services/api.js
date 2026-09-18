import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api/v1';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Attach Authorization header if token exists
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Intercept responses for global 401 handling and uniform error extraction
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      // If 401 Unauthorized, purge token and redirect to login
      if (error.response.status === 401) {
        localStorage.removeItem('token');
        localStorage.removeItem('user_id');
        localStorage.removeItem('user_name');
        localStorage.removeItem('user_email');
        if (!window.location.pathname.includes('/login') && !window.location.pathname.includes('/signup')) {
          window.location.href = '/login?expired=1';
        }
      }

      // Extract standardized error message
      const errorData = error.response.data?.error;
      const message = errorData?.message || error.response.data?.detail || 'An unexpected error occurred';
      const code = errorData?.code || 'UNKNOWN_ERROR';

      const customError = new Error(message);
      customError.code = code;
      customError.status = error.response.status;
      customError.raw = error.response.data;
      return Promise.reject(customError);
    }
    return Promise.reject(new Error('Network error. Please verify backend server is running.'));
  }
);

// Auth endpoints
export const authApi = {
  signup: async (userData) => {
    const response = await api.post('/auth/signup', userData);
    return response.data;
  },
  login: async (credentials) => {
    const response = await api.post('/auth/login', credentials);
    return response.data;
  },
  getMe: async () => {
    const response = await api.get('/auth/me');
    return response.data;
  },
};

// Applications endpoints
export const applicationsApi = {
  list: async (params = {}) => {
    const response = await api.get('/applications', { params });
    return response.data;
  },
  get: async (id) => {
    const response = await api.get(`/applications/${id}`);
    return response.data;
  },
  create: async (data) => {
    const response = await api.post('/applications', data);
    return response.data;
  },
  update: async (id, data) => {
    const response = await api.put(`/applications/${id}`, data);
    return response.data;
  },
  delete: async (id) => {
    await api.delete(`/applications/${id}`);
  },
};

// Resumes endpoints
export const resumesApi = {
  list: async () => {
    const response = await api.get('/resumes');
    return response.data;
  },
  upload: async (formData) => {
    const response = await api.post('/resumes', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
  getDownloadUrl: async (id) => {
    const response = await api.get(`/resumes/${id}/download-url`);
    return response.data;
  },
  delete: async (id) => {
    await api.delete(`/resumes/${id}`);
  },
};
