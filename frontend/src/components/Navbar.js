import React from 'react';
import { useNavigate } from 'react-router-dom';
import './Navbar.css';

function Navbar() {
  const navigate = useNavigate();
  const username = localStorage.getItem('username');

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('username');
    navigate('/');
  };

  return (
    <nav className="navbar">
      <div className="navbar-brand">
        <h1>🚴 Vélib Paris</h1>
      </div>
      <div className="navbar-user">
        <span className="username">👤 {username}</span>
        <button onClick={handleLogout} className="logout-button">
          Déconnexion
        </button>
      </div>
    </nav>
  );
}

export default Navbar;