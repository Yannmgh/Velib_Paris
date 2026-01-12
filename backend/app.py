import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flasgger import Swagger, swag_from
from config import Config
from database import get_db_connection
import math
import uuid

app = Flask(__name__)
app.config.from_object(Config)

# Active CORS pour permettre au frontend de communiquer avec le backend
# En production, remplacer par l'URL du frontend déployé
allowed_origins = os.getenv('FRONTEND_URL', 'http://localhost:3000')
CORS(app, resources={r"/api/*": {"origins": allowed_origins.split(',')}})

# Initialise JWT pour l'authentification
jwt = JWTManager(app)

# Configuration Swagger
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'apispec',
            "route": '/apispec.json',
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/api/docs"
}

swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "API Vélib - Gestion des bornes",
        "description": "API REST pour gérer les bornes Vélib à Paris",
        "version": "1.0.0",
        "contact": {
            "name": "Votre nom",
            "email": "votre.email@example.com"
        }
    },
    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "JWT Authorization header. Format: 'Bearer {token}'"
        }
    },
    "security": [{"Bearer": []}]
}

swagger = Swagger(app, config=swagger_config, template=swagger_template)

# Fonction utilitaire pour calculer la distance entre deux points GPS
def calculate_distance(lat1, lon1, lat2, lon2):
    """Calcule la distance en km entre deux coordonnées GPS (formule de Haversine)"""
    R = 6371  # Rayon de la Terre en km
    
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    
    a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) \
        * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    return R * c

# ============== ROUTES D'AUTHENTIFICATION ==============

@app.route('/api/login', methods=['POST'])
def login():
    """
    Authentification utilisateur
    ---
    tags:
      - Authentification
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - username
            - password
          properties:
            username:
              type: string
              example: admin
            password:
              type: string
              example: admin123
    responses:
      200:
        description: Connexion réussie
        schema:
          type: object
          properties:
            access_token:
              type: string
              description: Token JWT pour les requêtes authentifiées
            username:
              type: string
      400:
        description: Paramètres manquants
      401:
        description: Identifiants invalides
    """
    data = request.get_json()
    
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'error': 'Username et password requis'}), 400
    
    username = data['username']
    password = data['password']
    
    # Vérifie les identifiants
    conn = get_db_connection()
    user = conn.execute(
        'SELECT * FROM users WHERE username = ? AND password = ?',
        (username, password)
    ).fetchone()
    conn.close()
    
    if user:
        # Crée un token JWT
        access_token = create_access_token(identity=username)
        return jsonify({'access_token': access_token, 'username': username}), 200
    else:
        return jsonify({'error': 'Identifiants invalides'}), 401

# ============== ROUTES POUR LES STATIONS ==============

@app.route('/api/stations', methods=['GET'])
@jwt_required()
def get_stations():
    """
    Récupère les stations autour d'une position
    ---
    tags:
      - Stations
    security:
      - Bearer: []
    parameters:
      - name: lat
        in: query
        type: number
        required: true
        description: Latitude de la position
        example: 48.8566
      - name: lon
        in: query
        type: number
        required: true
        description: Longitude de la position
        example: 2.3522
      - name: radius
        in: query
        type: number
        required: false
        default: 2.0
        description: Rayon de recherche en km
    responses:
      200:
        description: Liste des stations à proximité
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
              station_id:
                type: string
              name:
                type: string
              latitude:
                type: number
              longitude:
                type: number
              capacity:
                type: integer
              address:
                type: string
              distance:
                type: number
      400:
        description: Paramètres manquants
      401:
        description: Non authentifié
    """
    # Récupère les paramètres de la requête
    lat = request.args.get('lat', type=float)
    lon = request.args.get('lon', type=float)
    radius = request.args.get('radius', default=2.0, type=float)  # Rayon en km
    
    if lat is None or lon is None:
        return jsonify({'error': 'Paramètres lat et lon requis'}), 400
    
    conn = get_db_connection()
    stations = conn.execute('SELECT * FROM stations').fetchall()
    conn.close()
    
    # Filtre les stations dans le rayon spécifié
    nearby_stations = []
    for station in stations:
        distance = calculate_distance(lat, lon, station['latitude'], station['longitude'])
        if distance <= radius:
            nearby_stations.append({
                'id': station['id'],
                'station_id': station['station_id'],
                'name': station['name'],
                'latitude': station['latitude'],
                'longitude': station['longitude'],
                'capacity': station['capacity'],
                'address': station['address'],
                'distance': round(distance, 2)
            })
    
    # Trie par distance
    nearby_stations.sort(key=lambda x: x['distance'])
    
    return jsonify(nearby_stations), 200

@app.route('/api/stations/<int:station_id>', methods=['GET'])
@jwt_required()
def get_station(station_id):
    """
    Récupère une station spécifique
    ---
    tags:
      - Stations
    security:
      - Bearer: []
    parameters:
      - name: station_id
        in: path
        type: integer
        required: true
        description: ID de la station
    responses:
      200:
        description: Détails de la station
      404:
        description: Station non trouvée
      401:
        description: Non authentifié
    """
    conn = get_db_connection()
    station = conn.execute('SELECT * FROM stations WHERE id = ?', (station_id,)).fetchone()
    conn.close()
    
    if station is None:
        return jsonify({'error': 'Station non trouvée'}), 404
    
    return jsonify({
        'id': station['id'],
        'station_id': station['station_id'],
        'name': station['name'],
        'latitude': station['latitude'],
        'longitude': station['longitude'],
        'capacity': station['capacity'],
        'address': station['address']
    }), 200

@app.route('/api/stations', methods=['POST'])
@jwt_required()
def create_station():
    """
    Crée une nouvelle station
    ---
    tags:
      - Stations
    security:
      - Bearer: []
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - name
            - latitude
            - longitude
          properties:
            station_id:
              type: string
            name:
              type: string
              example: Nouvelle station Vélib
            latitude:
              type: number
              example: 48.8566
            longitude:
              type: number
              example: 2.3522
            capacity:
              type: integer
              example: 20
            address:
              type: string
              example: 1 rue de Rivoli, Paris
    responses:
      201:
        description: Station créée avec succès
      400:
        description: Champs requis manquants
      401:
        description: Non authentifié
      500:
        description: Erreur serveur
    """
    data = request.get_json()
    
    required_fields = ['name', 'latitude', 'longitude']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Champs requis : name, latitude, longitude'}), 400
    
    try:
        conn = get_db_connection()
        
        # Génère un station_id unique si non fourni
        station_id = data.get('station_id')
        if not station_id:
            station_id = f"STATION-{str(uuid.uuid4())[:8].upper()}"
        
        cursor = conn.execute('''
            INSERT INTO stations (station_id, name, latitude, longitude, capacity, address)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            station_id,
            data['name'],
            float(data['latitude']),
            float(data['longitude']),
            data.get('capacity', 0),
            data.get('address', '')
        ))
        conn.commit()
        new_id = cursor.lastrowid
        
        return jsonify({'message': 'Station créée', 'id': new_id, 'station_id': station_id}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if 'conn' in locals():
            conn.close()

@app.route('/api/stations/<int:station_id>', methods=['PUT'])
@jwt_required()
def update_station(station_id):
    """
    Met à jour une station existante
    ---
    tags:
      - Stations
    security:
      - Bearer: []
    parameters:
      - name: station_id
        in: path
        type: integer
        required: true
        description: ID de la station à modifier
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            name:
              type: string
            latitude:
              type: number
            longitude:
              type: number
            capacity:
              type: integer
            address:
              type: string
    responses:
      200:
        description: Station mise à jour
      404:
        description: Station non trouvée
      401:
        description: Non authentifié
      500:
        description: Erreur serveur
    """
    data = request.get_json()
    
    try:
        conn = get_db_connection()
        conn.execute('''
            UPDATE stations
            SET name = ?, latitude = ?, longitude = ?, capacity = ?, address = ?
            WHERE id = ?
        ''', (
            data.get('name'),
            float(data.get('latitude')),
            float(data.get('longitude')),
            data.get('capacity', 0),
            data.get('address', ''),
            station_id
        ))
        conn.commit()
        
        if conn.total_changes == 0:
            return jsonify({'error': 'Station non trouvée'}), 404
        
        return jsonify({'message': 'Station mise à jour'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if 'conn' in locals():
            conn.close()

@app.route('/api/stations/<int:station_id>', methods=['DELETE'])
@jwt_required()
def delete_station(station_id):
    """
    Supprime une station
    ---
    tags:
      - Stations
    security:
      - Bearer: []
    parameters:
      - name: station_id
        in: path
        type: integer
        required: true
        description: ID de la station à supprimer
    responses:
      200:
        description: Station supprimée
      404:
        description: Station non trouvée
      401:
        description: Non authentifié
      500:
        description: Erreur serveur
    """
    try:
        conn = get_db_connection()
        conn.execute('DELETE FROM stations WHERE id = ?', (station_id,))
        conn.commit()
        
        if conn.total_changes == 0:
            return jsonify({'error': 'Station non trouvée'}), 404
        
        return jsonify({'message': 'Station supprimée'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if 'conn' in locals():
            conn.close()

# ============== ROUTE DE TEST ==============

@app.route('/')
def index():
    """
    Page d'accueil - Redirige vers la documentation
    ---
    tags:
      - Accueil
    responses:
      200:
        description: Informations sur l'API
    """
    return jsonify({
        'message': 'Bienvenue sur l\'API Vélib',
        'documentation': '/api/docs',
        'version': '1.0.0',
        'endpoints': {
            'health': '/api/health',
            'login': '/api/login',
            'stations': '/api/stations'
        }
    }), 200

@app.route('/api/health', methods=['GET'])
def health():
    """
    Vérification de l'état de l'API
    ---
    tags:
      - Santé
    responses:
      200:
        description: API opérationnelle
        schema:
          type: object
          properties:
            status:
              type: string
              example: OK
            message:
              type: string
              example: API Vélib opérationnelle
    """
    return jsonify({'status': 'OK', 'message': 'API Vélib opérationnelle'}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)