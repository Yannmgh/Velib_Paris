import axios from 'axios';

// URL de base de l'API - en production, utilise Render
const API_URL = process.env.REACT_APP_API_URL || 'https://velib-paris.onrender.com';

// Instance axios avec configuration de base
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Intercepteur pour ajouter le token JWT à chaque requête
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Intercepteur pour gérer les erreurs de réponse
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expiré ou invalide
      localStorage.removeItem('token');
      window.location.href = '/';
    }
    return Promise.reject(error);
  }
);

// ============== AUTHENTIFICATION ==============

export const login = async (username, password) => {
  // CORRECTION : Ajout du préfixe /api
  const response = await axios.post(`${API_URL}/api/login`, { 
    username, 
    password 
  });
  return response.data;
};

// ============== STATIONS ==============

// Récupérer les stations autour d'une position
export const getStations = async (lat, lon, radius = 2) => {
  const response = await api.get('/api/stations', {
    params: { lat, lon, radius },
  });
  return response.data;
};

// Récupérer une station spécifique
export const getStation = async (id) => {
  const response = await api.get(`/api/stations/${id}`);
  return response.data;
};

// Créer une station
export const createStation = async (stationData) => {
  const response = await api.post('/api/stations', stationData);
  return response.data;
};

// Modifier une station
export const updateStation = async (id, stationData) => {
  const response = await api.put(`/api/stations/${id}`, stationData);
  return response.data;
};

// Supprimer une station
export const deleteStation = async (id) => {
  const response = await api.delete(`/api/stations/${id}`);
  return response.data;
};

// Health check
export const checkHealth = async () => {
  const response = await axios.get(`${API_URL}/api/health`);
  return response.data;
};

export default api;