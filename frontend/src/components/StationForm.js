import React, { useState, useEffect } from 'react';
import { createStation, updateStation } from '../services/api';
import './StationForm.css';

function StationForm({ station, onClose, onSuccess }) {
  const [formData, setFormData] = useState({
    name: '',
    latitude: '',
    longitude: '',
    capacity: '',
    address: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (station) {
      setFormData({
        name: station.name || '',
        latitude: station.latitude || '',
        longitude: station.longitude || '',
        capacity: station.capacity || '',
        address: station.address || '',
      });
    }
  }, [station]);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const data = {
        name: formData.name,
        latitude: parseFloat(formData.latitude),
        longitude: parseFloat(formData.longitude),
        capacity: parseInt(formData.capacity) || 0,
        address: formData.address,
      };

      if (station && station.id) {
        // Mode édition
        await updateStation(station.id, data);
        alert('Station modifiée avec succès !');
      } else {
        // Mode création
        await createStation(data);
        alert('Station créée avec succès !');
      }

      onSuccess();
      onClose();
    } catch (err) {
      setError('Erreur lors de la sauvegarde. Veuillez réessayer.');
      console.error('Erreur:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>{station?.id ? '✏️ Modifier la station' : '➕ Nouvelle station'}</h2>
          <button className="close-button" onClick={onClose}>×</button>
        </div>

        {error && <div className="error-message">{error}</div>}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="name">Nom de la station *</label>
            <input
              type="text"
              id="name"
              name="name"
              value={formData.name}
              onChange={handleChange}
              required
              placeholder="Ex: Station Tour Eiffel"
            />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="latitude">Latitude *</label>
              <input
                type="number"
                step="any"
                id="latitude"
                name="latitude"
                value={formData.latitude}
                onChange={handleChange}
                required
                placeholder="48.8566"
              />
            </div>

            <div className="form-group">
              <label htmlFor="longitude">Longitude *</label>
              <input
                type="number"
                step="any"
                id="longitude"
                name="longitude"
                value={formData.longitude}
                onChange={handleChange}
                required
                placeholder="2.3522"
              />
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="capacity">Capacité</label>
            <input
              type="number"
              id="capacity"
              name="capacity"
              value={formData.capacity}
              onChange={handleChange}
              placeholder="20"
            />
          </div>

          <div className="form-group">
            <label htmlFor="address">Adresse</label>
            <input
              type="text"
              id="address"
              name="address"
              value={formData.address}
              onChange={handleChange}
              placeholder="Ex: 1 rue de Rivoli, Paris"
            />
          </div>

          <div className="form-actions">
            <button type="button" onClick={onClose} className="cancel-button">
              Annuler
            </button>
            <button type="submit" disabled={loading} className="submit-button">
              {loading ? 'Enregistrement...' : 'Enregistrer'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default StationForm;