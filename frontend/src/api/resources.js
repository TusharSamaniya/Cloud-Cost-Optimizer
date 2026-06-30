import client from './client';

// BUG FIXED: was '/api/aws/resources' → correct URL is '/api/sync/resources'
export const getResources = async () => (await client.get('/api/sync/resources')).data;

// BUG FIXED: was '/api/sync/aws' → correct URL is '/api/sync/'
export const syncResources = async () => (await client.post('/api/sync/')).data;

export const getRecommendations = async () => (await client.get('/api/recommendations/')).data;

// BUG FIXED: was PUT → correct method is PATCH, matches your backend route
export const updateRecommendation = async (id, status) =>
  (await client.patch(`/api/recommendations/${id}`, { status })).data;

export const getAnomalies = async () => (await client.get('/api/anomalies/')).data;
export const getDashboardSummary = async () => (await client.get('/api/dashboard/summary')).data;
