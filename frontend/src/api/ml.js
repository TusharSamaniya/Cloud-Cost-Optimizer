import client from './client';

export const runPipeline = async () => (await client.post('/api/ml/run')).data;
export const getClusters = async () => (await client.get('/api/ml/clusters')).data;
export const getForecast = async () => (await client.get('/api/ml/forecast')).data;