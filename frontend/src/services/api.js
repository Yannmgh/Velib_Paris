import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'https://velib-bornes-backend.azurewebsites.net';

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

// Authentification
export const login = async (username, password) => {
  const response = await axios.post(`${API_URL}/login`, { username, password });
  return response.data;
};

// Récupérer les stations autour d'une position
export const getStations = async (lat, lon, radius = 2) => {
  const response = await api.get('/stations', {
    params: { lat, lon, radius },
  });
  return response.data;
};

// Récupérer une station spécifique
export const getStation = async (id) => {
  const response = await api.get(`/stations/${id}`);
  return response.data;
};

// Créer une station
export const createStation = async (stationData) => {
  const response = await api.post('/stations', stationData);
  return response.data;
};

// Modifier une station
export const updateStation = async (id, stationData) => {
  const response = await api.put(`/stations/${id}`, stationData);
  return response.data;
};

// Supprimer une station
export const deleteStation = async (id) => {
  const response = await api.delete(`/stations/${id}`);
  return response.data;
};

export default api;