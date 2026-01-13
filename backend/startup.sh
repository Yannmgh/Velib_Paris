#!/bin/bash

# Initialiser la base de données si elle n'existe pas
if [ ! -f velib.db ]; then
    python database.py
fi

# Lancer l'application avec Gunicorn
# Utilise $PORT fourni par Render (au lieu de 8000 en dur)
gunicorn --bind=0.0.0.0:$PORT --timeout 600 app:app