# 🚀 Configuration Azure App Service - Guide Manuel

## Étape 1: Aller à Azure Portal

1. Va sur https://portal.azure.com
2. Recherche et clique sur **Vélib-Bornes-backend** (Application Web)

## Étape 2: Configurer les Variables d'Environnement

1. Clique sur **Configuration** (menu de gauche) → **Paramètres de l'application**
2. Clique sur **+ Ajouter un paramètre**
3. Ajoute les variables suivantes:

| Nom | Valeur | Notes |
|-----|--------|-------|
| `SECRET_KEY` | `your-secret-key-XXXX` | Génère une clé sécurisée |
| `JWT_SECRET_KEY` | `your-jwt-secret-XXXX` | Génère une clé sécurisée |
| `DATABASE_PATH` | `velib.db` | Chemin de la BD |
| `FRONTEND_URL` | `https://ton-frontend.com` | URL du frontend Azure |
| `FLASK_ENV` | `production` | Mode production |

4. Clique **Enregistrer**

## Étape 3: Configurer la Pile d'Exécution

1. Clique sur **Configuration** (menu de gauche) → **Paramètres généraux**
2. Assure-toi que:
   - **Stack**: Python
   - **Version Python**: 3.11

## Étape 4: Configurer la Commande de Démarrage

⚠️ **C'EST L'ÉTAPE CRITIQUE!**

1. Toujours dans **Configuration** → **Paramètres généraux**
2. Trouve le champ **Commande de démarrage**
3. **Remplace complètement** par:
```bash
bash /home/site/wwwroot/run.sh
```

4. Clique **Enregistrer**

## Étape 5: Redémarrer l'App Service

1. Retourne à la page principale de **Vélib-Bornes-backend**
2. Clique sur le bouton **Redémarrer** (en haut)
3. Confirme le redémarrage

## Étape 6: Vérifier que ça Marche

1. Attends 30-60 secondes le redémarrage
2. Va sur: `https://velib-bornes-backend.azurewebsites.net/api/health`
3. Tu devrais voir:
```json
{
  "status": "OK",
  "message": "API Vélib opérationnelle"
}
```

---

## 🆘 Si ça ne marche toujours pas:

### Vérifier les logs:
1. Clique sur **Journal d'activité** (menu de gauche)
2. Regarde les erreurs récentes

### Ou:
1. Clique sur **Outils avancés** → **Go** (Kudu Console)
2. Va dans le dossier `D:\home\site\wwwroot`
3. Exécute manuellement: `python backend\app.py`

### Ou redéployer via Git:
```bash
cd c:\Users\Public\Documents\velib-project
git push origin main
```

---

## ✅ Checklist Final

- [ ] Variables d'environnement configurées
- [ ] Python 3.11 sélectionné
- [ ] Commande de démarrage = `bash /home/site/wwwroot/run.sh`
- [ ] App Service redémarrée
- [ ] `/api/health` retourne OK

Fais-moi signe quand c'est fait! 🎯
