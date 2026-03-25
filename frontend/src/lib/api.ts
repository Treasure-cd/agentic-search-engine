// API Configuration for different environments
const API_URL = import.meta.env.VITE_API_URL || 'https://api.ase.penivera.me/api';

export const apiConfig = {
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
};

export default API_URL;
