#!/bin/bash

# Script pour configurer les variables d'environnement Azure App Service pour le backend Vélib

# À PERSONNALISER AVANT DE LANCER
RESOURCE_GROUP="Vélib-Bornes-backend"
APP_NAME="Vélib-Bornes-backend"

# Générer des secrets sécurisés (à remplacer par des valeurs réelles)
SECRET_KEY=$(openssl rand -hex 32)
JWT_SECRET_KEY=$(openssl rand -hex 32)

echo "🔧 Configuration des variables d'environnement Azure App Service..."
echo "Ressource Group: $RESOURCE_GROUP"
echo "App Name: $APP_NAME"
echo ""

# Configurer les variables d'environnement
az webapp config appsettings set \
  --resource-group "$RESOURCE_GROUP" \
  --name "$APP_NAME" \
  --settings \
    SECRET_KEY="$SECRET_KEY" \
    JWT_SECRET_KEY="$JWT_SECRET_KEY" \
    DATABASE_PATH="velib.db" \
    FRONTEND_URL="https://your-frontend-domain.com" \
    FLASK_ENV="production"

echo "✅ Variables d'environnement configurées!"
echo ""
echo "⚠️ IMPORTANT: Mettez à jour les valeurs suivantes dans le Azure Portal:"
echo "  1. FRONTEND_URL - URL du frontend Azure Static Web Apps"
echo "  2. SECRET_KEY - Clé secrète sécurisée"
echo "  3. JWT_SECRET_KEY - Clé JWT sécurisée"
