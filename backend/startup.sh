#!/bin/bash

# Initialiser la base de données si elle n'existe pas
if [ ! -f velib.db ]; then
    python database.py
fi

# Lancer l'application avec Gunicorn
gunicorn --bind=0.0.0.0 --timeout 600 app:app