# ================================================
# Dockerfile — Price Intelligence API
# Kitea + Jumia + Ikea — Data Analyst
# ================================================

# Image de base Python 3.11 légère
FROM python:3.11-slim

# Métadonnées
LABEL maintainer="Data Analyst - Prix Intelligence"
LABEL version="2.0"
LABEL description="API FastAPI - Analyse prix Kitea, Jumia, Ikea"

# Dossier de travail dans le conteneur
WORKDIR /app

# Copier requirements en premier (optimise le cache Docker)
COPY requirements.txt .

# Installer les librairies
RUN pip install --no-cache-dir -r requirements.txt

# Copier tout le projet
COPY . .

# Créer les dossiers nécessaires s'ils n'existent pas
RUN mkdir -p outputs data/raw data/clean

# Port exposé
EXPOSE 8000

# Commande de démarrage
CMD ["python", "api/main.py"]
