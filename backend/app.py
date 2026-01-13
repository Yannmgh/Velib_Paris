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

# ============== CONFIGURATION CORS CORRIGÉE ==============
allowed_origins = [
    'https://gray-pebble-0bfc84a03.1.azurestaticapps.net',
    'http://localhost:3000',
    'http://localhost:5173',
    'http://127.0.0.1:3000'
]

CORS(app, 
     origins=allowed_origins,
     supports_credentials=True,
     allow_headers=["Content-Type", "Authorization"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])

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

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calcule la distance en km entre deux coordonnées GPS (formule de Haversine)"""
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) \
        * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

# ============== ROUTES D'AUTHENTIFICATION ==============

@app.route('/api/login', methods=['POST'])
def login():
    """Authentification utilisateur"""
    data = request.get_json()
    
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'error': 'Username et password requis'}), 400
    
    username = data['username']
    password = data['password']
    
    conn = get_db_connection()
    user = conn.execute(
        'SELECT * FROM users WHERE username = ? AND password = ?',
        (username, password)
    ).fetchone()
    conn.close()
    
    if user:
        access_token = create_access_token(identity=username)
        print(f"✅ Login réussi pour {username}")
        return jsonify({'access_token': access_token, 'username': username}), 200
    else:
        print(f"❌ Login échoué pour {username}")
        return jsonify({'error': 'Identifiants invalides'}), 401

# ============== ROUTES POUR LES STATIONS ==============

@app.route('/api/stations', methods=['GET'])
@jwt_required()
def get_stations():
    """Récupère les stations autour d'une position"""
    lat = request.args.get('lat', type=float)
    lon = request.args.get('lon', type=float)
    radius = request.args.get('radius', default=2.0, type=float)
    
    print(f"🔍 GET /api/stations - lat={lat}, lon={lon}, radius={radius}km")
    
    if lat is None or lon is None:
        return jsonify({'error': 'Paramètres lat et lon requis'}), 400
    
    conn = get_db_connection()
    stations = conn.execute('SELECT * FROM stations').fetchall()
    conn.close()
    
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
    
    nearby_stations.sort(key=lambda x: x['distance'])
    print(f"✅ {len(nearby_stations)} stations trouvées dans un rayon de {radius}km")
    
    return jsonify(nearby_stations), 200

@app.route('/api/stations/<int:station_id>', methods=['GET'])
@jwt_required()
def get_station(station_id):
    """Récupère une station spécifique"""
    print(f"🔍 GET /api/stations/{station_id}")
    
    conn = get_db_connection()
    station = conn.execute('SELECT * FROM stations WHERE id = ?', (station_id,)).fetchone()
    conn.close()
    
    if station is None:
        print(f"❌ Station {station_id} non trouvée")
        return jsonify({'error': 'Station non trouvée'}), 404
    
    print(f"✅ Station {station_id} trouvée: {station['name']}")
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
    """Crée une nouvelle station"""
    data = request.get_json()
    print(f"🔍 POST /api/stations - Data: {data}")
    
    required_fields = ['name', 'latitude', 'longitude']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Champs requis : name, latitude, longitude'}), 400
    
    try:
        conn = get_db_connection()
        
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
        
        print(f"✅ Station créée: ID={new_id}, name={data['name']}")
        return jsonify({'message': 'Station créée', 'id': new_id, 'station_id': station_id}), 201
    except Exception as e:
        print(f"❌ Erreur création station: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        if 'conn' in locals():
            conn.close()

@app.route('/api/stations/<int:station_id>', methods=['PUT'])
@jwt_required()
def update_station(station_id):
    """Met à jour une station existante"""
    data = request.get_json()
    
    # 🔍 LOGS DE DEBUG
    print(f"🔍 PUT /api/stations/{station_id}")
    print(f"📦 Data reçue: {data}")
    
    try:
        conn = get_db_connection()
        
        # Vérifier si la station existe AVANT de modifier
        existing = conn.execute('SELECT * FROM stations WHERE id = ?', (station_id,)).fetchone()
        
        if existing:
            print(f"✅ Station trouvée: {dict(existing)}")
        else:
            print(f"❌ Station {station_id} NOT FOUND en base de données")
            # Lister toutes les stations pour debug
            all_stations = conn.execute('SELECT id, name FROM stations LIMIT 10').fetchall()
            print(f"📋 Premières stations en DB: {[dict(s) for s in all_stations]}")
            conn.close()
            return jsonify({'error': f'Station {station_id} non trouvée en base'}), 404
        
        # Mise à jour
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
        
        print(f"✅ Station {station_id} mise à jour avec succès")
        return jsonify({'message': 'Station mise à jour'}), 200
    except Exception as e:
        print(f"❌ Erreur lors de la mise à jour: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
    finally:
        if 'conn' in locals():
            conn.close()

@app.route('/api/stations/<int:station_id>', methods=['DELETE'])
@jwt_required()
def delete_station(station_id):
    """Supprime une station"""
    
    # 🔍 LOGS DE DEBUG
    print(f"🔍 DELETE /api/stations/{station_id}")
    
    try:
        conn = get_db_connection()
        
        # Vérifier si la station existe AVANT de supprimer
        existing = conn.execute('SELECT * FROM stations WHERE id = ?', (station_id,)).fetchone()
        
        if existing:
            print(f"✅ Station trouvée: {dict(existing)}")
        else:
            print(f"❌ Station {station_id} NOT FOUND en base de données")
            # Lister toutes les stations pour debug
            all_stations = conn.execute('SELECT id, name FROM stations LIMIT 10').fetchall()
            print(f"📋 Premières stations en DB: {[dict(s) for s in all_stations]}")
            conn.close()
            return jsonify({'error': f'Station {station_id} non trouvée en base'}), 404
        
        # Suppression
        conn.execute('DELETE FROM stations WHERE id = ?', (station_id,))
        conn.commit()
        
        print(f"✅ Station {station_id} supprimée avec succès")
        return jsonify({'message': 'Station supprimée'}), 200
    except Exception as e:
        print(f"❌ Erreur lors de la suppression: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
    finally:
        if 'conn' in locals():
            conn.close()

# ============== ROUTES DE TEST ==============

@app.route('/')
def index():
    """Page d'accueil"""
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
    """Vérification de l'état de l'API"""
    return jsonify({'status': 'OK', 'message': 'API Vélib opérationnelle'}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)