import client from './client';

export const getResources = async () => (await client.get('/api/aws/resources')).data;
export const syncResources = async () => (await client.post('/api/sync/aws')).data;
export const getRecommendations = async () => (await client.get('/api/recommendations')).data;
export const updateRecommendation = async (id, status) => 
  (await client.put(`/api/recommendations/${id}`, { status })).data;
export const getAnomalies = async () => (await client.get('/api/anomalies')).data;
export const getDashboardSummary = async () => (await client.get('/api/dashboard/summary')).data;