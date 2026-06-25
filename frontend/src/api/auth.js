import client from './client';

export const login = async (username, password) => {
  // FastAPI OAuth2 requires form data, not JSON
  const formData = new URLSearchParams();
  formData.append('username', username);
  formData.append('password', password);
  
  const response = await client.post('/api/auth/login', formData);
  return response.data;
};

export const register = async (email, password) => {
  const response = await client.post('/api/auth/register', { email, password });
  return response.data;
};