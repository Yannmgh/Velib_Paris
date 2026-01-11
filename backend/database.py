import sqlite3
import pandas as pd
from config import Config

def get_db_connection():
    """Crée une connexion à la base de données SQLite"""
    conn = sqlite3.connect(Config.DATABASE_PATH, timeout=10.0, check_same_thread=False)
    conn.row_factory = sqlite3.Row  # Permet d'accéder aux colonnes par nom
    # Active le mode Write-Ahead Logging pour améliorer la concurrence
    conn.execute('PRAGMA journal_mode=WAL')
    return conn

def init_db():
    """Initialise la base de données avec les tables nécessaires"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Table des utilisateurs
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    
    # Table des bornes Vélib
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            station_id TEXT,
            name TEXT NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            capacity INTEGER,
            address TEXT
        )
    ''')
    
    # Crée un utilisateur de test (mot de passe : admin123)
    # Note : en production, il faut hasher le mot de passe !
    cursor.execute('''
        INSERT OR IGNORE INTO users (username, password) 
        VALUES (?, ?)
    ''', ('admin', 'admin123'))
    
    conn.commit()
    conn.close()
    print("Base de données initialisée avec succès !")

def import_csv(csv_file_path):
    """Importe les données du fichier CSV dans la base de données"""
    try:
        # Lit le fichier CSV avec point-virgule comme séparateur
        df = pd.read_csv(csv_file_path, sep=';', encoding='utf-8')
        
        print(f"Colonnes trouvées: {df.columns.tolist()}")
        
        conn = get_db_connection()
        imported_count = 0
        
        # Nettoie les données et les insère
        for _, row in df.iterrows():
            try:
                # Récupère le code de la station
                station_code = str(row.get('Code de la station', ''))
                
                # Récupère le nom de la station
                station_name = str(row.get('Nom de la station', 'Sans nom'))
                
                # Parse les coordonnées GPS depuis la colonne 'geo'
                geo = str(row.get('geo', ''))
                if ',' in geo:
                    coords = geo.split(',')
                    latitude = float(coords[0])
                    longitude = float(coords[1])
                else:
                    print(f"Coordonnées invalides pour {station_name}")
                    continue
                
                # Récupère la capacité
                capacity = int(row.get('Nombres de bornes en station', 0)) if pd.notna(row.get('Nombres de bornes en station')) else 0
                
                # Adresse (on n'a pas cette info dans le CSV, on laisse vide)
                address = ''
                
                conn.execute('''
                    INSERT OR REPLACE INTO stations 
                    (station_id, name, latitude, longitude, capacity, address)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    station_code,
                    station_name,
                    latitude,
                    longitude,
                    capacity,
                    address
                ))
                imported_count += 1
                
            except Exception as e:
                print(f"Erreur lors de l'insertion d'une ligne : {e}")
                print(f"Données de la ligne : {row.to_dict()}")
                continue
        
        conn.commit()
        conn.close()
        print(f"Import réussi : {imported_count} stations importées !")
        
    except Exception as e:
        print(f"Erreur lors de l'import du CSV : {e}")

if __name__ == '__main__':
    # Initialise la base de données
    init_db()
    
    # Importe le fichier CSV (adapte le nom si nécessaire)
    import_csv('velib-pos (1).csv')