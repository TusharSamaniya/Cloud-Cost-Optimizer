import axios from 'axios';

// Step 1: Create the base instance
const client = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
});

// Step 2: Request Interceptor (Attaches the token)
client.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Step 3: Response Interceptor (Handles expired tokens)
client.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login'; // Redirect to login
    }
    return Promise.reject(error);
  }
);

export default client;