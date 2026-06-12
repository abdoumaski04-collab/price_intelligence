# ================================================
# Dockerfile — Price Intelligence API
# Kitea + Jumia + Ikea — Data Analyst
# Compatible Cloud Run (PORT dynamique)
# ================================================

FROM python:3.11-slim

LABEL maintainer="Data Analyst - Prix Intelligence"
LABEL version="2.0"
LABEL description="API FastAPI - Analyse prix Kitea, Jumia, Ikea"

WORKDIR /app

# Copier requirements en premier (optimise le cache Docker)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier tout le projet (code + outputs/ générés par run_analysis.py + data/clean/)
COPY . .

# Créer les dossiers nécessaires s'ils n'existent pas
RUN mkdir -p outputs data/raw data/clean

# Cloud Run fournit la variable PORT (8080 par défaut)
ENV PORT=8080
EXPOSE 8080

# Démarrage avec uvicorn, port dynamique
CMD exec uvicorn api.main:app --host 0.0.0.0 --port ${PORT}
