export const config = {
  apiBaseUrl: 'http://localhost:8000/api',
  isDevelopment: import.meta.env.DEV,
  isProduction: import.meta.env.PROD,
} as const;
