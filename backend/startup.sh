#!/bin/bash

set -e

echo "🚀 Starting Vélib API..."

# Initialiser la base de données si elle n'existe pas
if [ ! -f velib.db ]; then
    echo "📦 Initializing database..."
    python database.py
fi

# Lancer l'application avec Gunicorn
echo "⚙️ Starting Gunicorn server..."
gunicorn --bind=0.0.0.0 --timeout 600 --workers 4 --worker-class sync app:app
