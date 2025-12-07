import axios from 'axios';
import { config } from '../config/env';

export const apiClient = axios.create({
  baseURL: config.apiBaseUrl,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    // Add mock user ID based on user type for authorization
    const userType = localStorage.getItem('userType') || 'ko';
    let userId: string;

    // Map user types to IDs based on fixtures/users.json
    switch (userType) {
      case 'kierownictwo':
        userId = '1'; // Anna Kowalska
        break;
      case 'bbf':
        userId = '1'; // Jan Nowak
        break;
      case 'ko':
      default:
        userId = '2'; // Piotr Wiśniewski (komorka_organizacyjna_id: 1)
        break;
    }

    config.headers.Authorization = userId;

    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);
