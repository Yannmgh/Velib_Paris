#!/bin/bash

# Script de démarrage pour Azure App Service - Vélib Backend

set -e

echo "🚀 Vélib Backend - Démarrage sur Azure App Service"
echo "=================================================="

# Afficher les infos
echo "📍 Répertoire courant: $(pwd)"
echo "📂 Contenu du répertoire:"
ls -la

# Aller dans le répertoire backend
if [ -d "backend" ]; then
    echo "✅ Dossier 'backend' trouvé"
    cd backend
else
    echo "⚠️ Dossier 'backend' non trouvé"
    echo "Vérification si nous sommes déjà dans backend..."
    if [ -f "app.py" ]; then
        echo "✅ app.py trouvé dans le répertoire courant"
    else
        echo "❌ app.py non trouvé!"
        exit 1
    fi
fi

echo ""
echo "📍 Répertoire de travail: $(pwd)"
echo "📂 Fichiers présents:"
ls -la | head -20

# Initialiser la base de données si elle n'existe pas
echo ""
echo "🗄️ Vérification de la base de données..."
if [ ! -f "velib.db" ]; then
    echo "📦 Création de la base de données..."
    python database.py
else
    echo "✅ Base de données existante trouvée"
fi

# Vérifier les dépendances
echo ""
echo "📚 Vérification des dépendances..."
if python -c "import flask; import flask_jwt_extended" 2>/dev/null; then
    echo "✅ Dépendances Flask installées"
else
    echo "⚠️ Installation des dépendances..."
    pip install -r requirements.txt
fi

# Démarrer Gunicorn
echo ""
echo "⚙️ Démarrage de Gunicorn..."
echo "🌐 Serveur disponible à: http://0.0.0.0:8000"
echo ""

exec gunicorn \
    --bind=0.0.0.0:8000 \
    --workers=4 \
    --worker-class=sync \
    --timeout=600 \
    --access-logfile=- \
    --error-logfile=- \
    app:app
