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
  const [selectedStation, setSelectedStation] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [editingStation, setEditingStation] = useState(null);
  const [loading, setLoading] = useState(false);
  const [searchRadius, setSearchRadius] = useState(5);

  // ✅ Fonction de chargement définie EN PREMIER
  const loadStationsNow = useCallback(async () => {
    if (!map.current || !map.current.loaded()) return;
    
    setLoading(true);
    try {
      const center = map.current.getCenter();
      console.log(`🔍 Chargement stations: lat=${center.lat.toFixed(4)}, lon=${center.lng.toFixed(4)}, rayon=${searchRadius}km`);
      
      const data = await getStations(center.lat, center.lng, searchRadius);
      setStations(data);
      console.log(`✅ ${data.length} stations chargées`);
    } catch (error) {
      console.error('❌ Erreur chargement stations:', error);
      alert('Erreur lors du chargement des stations');
    } finally {
      setLoading(false);
    }
  }, [searchRadius]);

  // ✅ handleDelete utilise loadStationsNow
  const handleDelete = useCallback(async (id) => {
    if (window.confirm('Voulez-vous vraiment supprimer cette station ?')) {
      try {
        console.log(`🗑️ Suppression de la station ${id}...`);
        await deleteStation(id);
        
        if (popupRef.current) {
          popupRef.current.remove();
        }
        setSelectedStation(null);
        
        // ✅ Recharger immédiatement
        console.log('🔄 Rechargement des stations...');
        await loadStationsNow();
        alert('Station supprimée avec succès !');
      } catch (error) {
        console.error('❌ Erreur suppression:', error);
        alert('Erreur lors de la suppression de la station');
      }
    }
  }, [loadStationsNow]);

  const handleEdit = useCallback((station) => {
    setEditingStation(station);
    setShowForm(true);
    if (popupRef.current) {
      popupRef.current.remove();
    }
  }, []);

  // Popup avec les fonctions dans le bon ordre
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
  }, [handleEdit, handleDelete]);

  // Initialiser la carte UNE SEULE FOIS
  useEffect(() => {
    if (map.current) return;

    if (!mapboxgl.accessToken) {
      console.error('❌ Token Mapbox manquant !');
      alert('Erreur : Token Mapbox non configuré');
      return;
    }

    try {
      map.current = new mapboxgl.Map({
        container: mapContainer.current,
        style: 'mapbox://styles/mapbox/streets-v12',
        center: [2.3522, 48.8566],
        zoom: 13,
      });

      map.current.addControl(new mapboxgl.NavigationControl(), 'top-right');

      map.current.on('moveend', () => {
        if (map.current.loaded()) {
          loadStationsNow();
        }
      });

      map.current.on('click', (e) => {
        if (e.originalEvent.shiftKey) {
          setEditingStation({
            latitude: e.lngLat.lat,
            longitude: e.lngLat.lng,
            name: '',
            capacity: 20,
            address: ''
          });
          setShowForm(true);
        }
      });

      map.current.on('load', () => {
        console.log('✅ Carte initialisée');
        loadStationsNow();
      });

    } catch (error) {
      console.error('❌ Erreur init carte:', error);
    }

    return () => {
      if (map.current) {
        map.current.remove();
        map.current = null;
      }
    };
  }, [loadStationsNow]);

  // Recharger quand le rayon change
  useEffect(() => {
    if (map.current && map.current.loaded()) {
      const timeoutId = setTimeout(() => {
        loadStationsNow();
      }, 300);
      
      return () => clearTimeout(timeoutId);
    }
  }, [searchRadius, loadStationsNow]);

  // Afficher les marqueurs
  useEffect(() => {
    if (!map.current || !map.current.loaded()) return;

    markersRef.current.forEach(marker => marker.remove());
    markersRef.current = [];

    stations.forEach((station) => {
      const el = document.createElement('div');
      el.className = 'custom-marker';
      el.innerHTML = '🚴';
      el.style.cursor = 'pointer';
      el.style.fontSize = '32px';

      const marker = new mapboxgl.Marker(el)
        .setLngLat([station.longitude, station.latitude])
        .addTo(map.current);

      el.addEventListener('click', () => {
        setSelectedStation(station);
        showStationPopup(station);
      });

      markersRef.current.push(marker);
    });
  }, [stations, showStationPopup]);

  const handleAddNew = () => {
    const center = map.current.getCenter();
    setEditingStation({
      latitude: center.lat,
      longitude: center.lng,
      name: '',
      capacity: 20,
      address: ''
    });
    setShowForm(true);
  };

  const handleFormSuccess = async (newStationCoords) => {
    setShowForm(false);
    
    // Si c'est une nouvelle station (avec coordonnées), centrer la carte dessus
    if (newStationCoords && newStationCoords.latitude && newStationCoords.longitude) {
      console.log('🎯 Centrage sur la nouvelle station:', newStationCoords);
      map.current.flyTo({
        center: [newStationCoords.longitude, newStationCoords.latitude],
        zoom: 15,
        duration: 1500
      });
      
      // Attendre que l'animation se termine
      await new Promise(resolve => setTimeout(resolve, 1600));
    }
    
    console.log('🔄 Rechargement après création/modification...');
    await loadStationsNow();
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

        <button 
          onClick={loadStationsNow} 
          className="refresh-button"
          disabled={loading}
        >
          🔄 {loading ? 'Chargement...' : 'Recharger'}
        </button>

        <div className="station-count">
          📍 {stations.length} station{stations.length > 1 ? 's' : ''} trouvée{stations.length > 1 ? 's' : ''}
        </div>

        <div className="map-hint">
          💡 Shift + Clic sur la carte pour créer une station
        </div>
      </div>

      <div ref={mapContainer} className="map" style={{ height: 'calc(100vh - 70px)' }} />

      {showForm && (
        <StationForm
          station={editingStation}
          onClose={() => {
            setShowForm(false);
            setEditingStation(null);
          }}
          onSuccess={handleFormSuccess}
        />
      )}

      {loading && <div className="loading-overlay">Chargement...</div>}
    </div>
  );
}

export default MapComponent;