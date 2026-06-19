import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api',
});

// Configure Axios with JWT token interceptor
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('medpredict_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('medpredict_token');
      localStorage.removeItem('medpredict_user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;
