import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';
const DEMO_AUTH_TOKEN = process.env.REACT_APP_DEMO_AUTH_TOKEN || '';
const DEMO_ORG_ID = process.env.REACT_APP_ORG_ID || '';

if (DEMO_AUTH_TOKEN && !localStorage.getItem('authToken')) {
  localStorage.setItem('authToken', DEMO_AUTH_TOKEN);
}

if (DEMO_ORG_ID && !localStorage.getItem('orgId')) {
  localStorage.setItem('orgId', DEMO_ORG_ID);
}

const ORG_ID = localStorage.getItem('orgId') || '';

const client = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'X-Organization-ID': ORG_ID,
    'Content-Type': 'application/json',
  },
});

client.interceptors.request.use((config) => {
  const token = localStorage.getItem('authToken');
  if (token) {
    config.headers.Authorization = `Token ${token}`;
  }
  config.headers['X-Organization-ID'] = localStorage.getItem('orgId') || '';
  return config;
});

export default client;
