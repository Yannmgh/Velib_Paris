import React, { useState, useEffect, useCallback, useRef } from 'react';
import mapboxgl from 'mapbox-gl';
import { getStations, deleteStation } from '../services/api';
import Navbar from './Navbar';
import StationForm from './StationForm';
import 'mapbox-gl/dist/mapbox-gl.css';
import './Map.css';

mapboxgl.accessToken = process.env.REACT_APP_MAPBOX_TOKEN;

function MapComponent() {
  const mapContainer = useRef(null);
  const map = useRef(null);
  const markersRef = useRef([]);
  const popupRef = useRef(null);
  
  const [stations, setStations] = useState([]);
  // Ligne 18 : Variable non utilisée - on la garde mais on ajoute un commentaire
  // eslint-disable-next-line no-unused-vars
  const [selectedStation, setSelectedStation] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [editingStation, setEditingStation] = useState(null);
  const [loading, setLoading] = useState(false);
  const [searchRadius, setSearchRadius] = useState(5);
  const [mapCenter, setMapCenter] = useState([2.3522, 48.8566]); // [lng, lat] pour Mapbox

  // Initialiser la carte
  useEffect(() => {
    if (map.current) return; // La carte est déjà initialisée

    map.current = new mapboxgl.Map({
      container: mapContainer.current,
      style: 'mapbox://styles/mapbox/streets-v12',
      center: mapCenter,
      zoom: 13,
    });

    // Événement de fin de déplacement
    map.current.on('moveend', () => {
      const center = map.current.getCenter();
      setMapCenter([center.lng, center.lat]);
    });

    // Shift + Clic pour créer une station
    map.current.on('click', (e) => {
      if (e.originalEvent.shiftKey) {
        setEditingStation({
          latitude: e.lngLat.lat,
          longitude: e.lngLat.lng,
        });
        setShowForm(true);
      }
    });

    return () => {
      if (map.current) {
        map.current.remove();
      }
    };
  }, [mapCenter]); // Ligne 58 : Ajout de mapCenter dans les dépendances

  // Charger les stations
  const loadStations = useCallback(async () => {
    setLoading(true);
    try {
      const data = await getStations(mapCenter[1], mapCenter[0], searchRadius);
      setStations(data);
      console.log(`${data.length} stations chargées`);
    } catch (error) {
      console.error('Erreur lors du chargement des stations:', error);
      alert('Erreur lors du chargement des stations');
    } finally {
      setLoading(false);
    }
  }, [mapCenter, searchRadius]);

  useEffect(() => {
    loadStations();
  }, [loadStations]);

  // Afficher le popup d'une station
  const showStationPopup = useCallback((station) => {
    if (popupRef.current) {
      popupRef.current.remove();
    }

    const popupContent = `
      <div class="popup-content">
        <h3>${station.name}</h3>
        <p><strong>Capacité :</strong> ${station.capacity} vélos</p>
        <p><strong>Adresse :</strong> ${station.address || 'Non renseignée'}</p>
        <p><strong>Distance :</strong> ${station.distance} km</p>
        <div class="popup-actions">
          <button id="edit-btn-${station.id}" class="edit-button">✏️ Modifier</button>
          <button id="delete-btn-${station.id}" class="delete-button">🗑️ Supprimer</button>
        </div>
      </div>
    `;

    popupRef.current = new mapboxgl.Popup({ closeOnClick: false })
      .setLngLat([station.longitude, station.latitude])
      .setHTML(popupContent)
      .addTo(map.current);

    // Ajouter les événements aux boutons
    setTimeout(() => {
      const editBtn = document.getElementById(`edit-btn-${station.id}`);
      const deleteBtn = document.getElementById(`delete-btn-${station.id}`);

      if (editBtn) {
        editBtn.addEventListener('click', () => handleEdit(station));
      }
      if (deleteBtn) {
        deleteBtn.addEventListener('click', () => handleDelete(station.id));
      }
    }, 0);
  }, []); // Ligne 109 : Transformation en useCallback

  // Afficher les marqueurs sur la carte
  useEffect(() => {
    if (!map.current) return;

    // Supprimer les anciens marqueurs
    markersRef.current.forEach(marker => marker.remove());
    markersRef.current = [];

    // Ajouter les nouveaux marqueurs
    stations.forEach((station) => {
      // Créer un élément HTML personnalisé pour le marqueur
      const el = document.createElement('div');
      el.className = 'custom-marker';
      el.innerHTML = '🚴';
      el.style.cursor = 'pointer';
      el.style.fontSize = '32px';

      // Créer le marqueur
      const marker = new mapboxgl.Marker(el)
        .setLngLat([station.longitude, station.latitude])
        .addTo(map.current);

      // Événement au clic
      el.addEventListener('click', () => {
        setSelectedStation(station);
        showStationPopup(station);
      });

      markersRef.current.push(marker);
    });
  }, [stations, showStationPopup]); // Ajout de showStationPopup dans les dépendances

  const handleDelete = async (id) => {
    if (window.confirm('Voulez-vous vraiment supprimer cette station ?')) {
      try {
        await deleteStation(id);
        if (popupRef.current) {
          popupRef.current.remove();
        }
        setSelectedStation(null);
        loadStations();
      } catch (error) {
        console.error('Erreur lors de la suppression:', error);
        alert('Erreur lors de la suppression de la station');
      }
    }
  };

  const handleEdit = (station) => {
    setEditingStation(station);
    setShowForm(true);
    if (popupRef.current) {
      popupRef.current.remove();
    }
  };

  const handleAddNew = () => {
    setEditingStation(null);
    setShowForm(true);
  };

  const handleFormSuccess = () => {
    loadStations();
  };

  return (
    <div className="map-container">
      <Navbar />
      
      <div className="map-controls">
        <button onClick={handleAddNew} className="add-station-button">
          ➕ Nouvelle station
        </button>
        
        <div className="radius-control">
          <label>Rayon de recherche : {searchRadius} km</label>
          <input
            type="range"
            min="1"
            max="10"
            value={searchRadius}
            onChange={(e) => setSearchRadius(parseInt(e.target.value))}
          />
        </div>

        <div className="station-count">
          🔍 {stations.length} station{stations.length > 1 ? 's' : ''} trouvée{stations.length > 1 ? 's' : ''}
        </div>

        <div className="map-hint">
          💡 Shift + Clic sur la carte pour créer une station
        </div>
      </div>

      <div ref={mapContainer} className="map" style={{ height: 'calc(100vh - 70px)' }} />

      {/* Formulaire modal */}
      {showForm && (
        <StationForm
          station={editingStation}
          onClose={() => setShowForm(false)}
          onSuccess={handleFormSuccess}
        />
      )}

      {loading && <div className="loading-overlay">Chargement...</div>}
    </div>
  );
}

export default MapComponent;