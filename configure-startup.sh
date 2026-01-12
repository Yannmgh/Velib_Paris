#!/bin/bash
# Script pour configurer le startup command sur Azure

RESOURCE_GROUP="Vélib-Bornes-backend_group"
APP_NAME="Vélib-Bornes-backend"
STARTUP_CMD="bash /home/site/wwwroot/run.sh"

echo "🔧 Configuration du démarrage Azure App Service..."
echo "Ressource Group: $RESOURCE_GROUP"
echo "App Name: $APP_NAME"
echo "Commande: $STARTUP_CMD"
echo ""

az webapp config set \
  --resource-group "$RESOURCE_GROUP" \
  --name "$APP_NAME" \
  --startup-file "$STARTUP_CMD"

echo ""
echo "✅ Commande configurée!"
echo "🔄 Redémarrage de l'application..."

az webapp restart --resource-group "$RESOURCE_GROUP" --name "$APP_NAME"

echo ""
echo "🎉 App Service redémarrée!"
