/**
 * Axios instance pre-configured with:
 * - Base URL from environment
 * - Automatic Firebase ID token injection in Authorization header
 *
 * Every API call automatically includes the current user's token,
 * so routes/components don't need to manage auth headers manually.
 */

import axios from 'axios';
import { auth } from '../firebase';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor — injects Firebase ID token
api.interceptors.request.use(
  async (config) => {
    const user = auth.currentUser;
    if (user) {
      const token = await user.getIdToken();
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor — handle common errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      const { status, data } = error.response;
      if (status === 401) {
        console.error('Authentication error:', data.detail);
      } else if (status === 403) {
        console.error('Authorization error:', data.detail);
      }
    }
    return Promise.reject(error);
  }
);

export default api;