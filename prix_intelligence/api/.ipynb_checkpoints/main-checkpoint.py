"""
API FastAPI — Price Intelligence (Kitea + Jumia + Ikea)
Data Analyst : livraison des résultats au Fullstack
"""
import json, os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Prix Intelligence API",
    description="Analyse des prix Kitea, Jumia et Ikea — Maroc",
    version="2.0.0"
)

app.add_middleware(CORSMiddleware, allow_origins=["*"],
    allow_methods=["*"], allow_headers=["*"])

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'outputs')

def load_results():
    path = os.path.join(OUTPUT_DIR, 'analyse_results.json')
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

try:
    RESULTS = load_results()
    print("✅ Résultats chargés avec succès")
except Exception as e:
    print(f"❌ Erreur chargement: {e}")
    RESULTS = {}

@app.get("/")
def root():
    return {
        "api": "Prix Intelligence — Kitea + Jumia + Ikea",
        "version": "2.0.0",
        "endpoints": ["/stats", "/stats/categories", "/stats/sites",
                      "/tests", "/regression", "/promotions",
                      "/evolution", "/anomalies", "/figure/{nom}"]
    }

@app.get("/stats")
def get_stats():
    return {
        "meta": RESULTS.get("meta", {}),
        "stats_par_site": RESULTS.get("stats_par_site", {}),
    }

@app.get("/stats/categories")
def get_stats_cat():
    return RESULTS.get("stats_par_categorie", {})

@app.get("/stats/sites")
def get_stats_sites():
    return RESULTS.get("stats_site_categorie", {})

@app.get("/tests")
def get_tests():
    return {
        "shapiro": RESULTS.get("shapiro", {}),
        "kruskal_categories": RESULTS.get("kruskal_categories", {}),
        "kruskal_sites": RESULTS.get("kruskal_sites", {}),
        "mann_whitney": RESULTS.get("mann_whitney", {}),
    }

@app.get("/regression")
def get_regression():
    return RESULTS.get("regression", {})

@app.get("/promotions")
def get_promotions():
    return RESULTS.get("promotions", {})

@app.get("/evolution")
def get_evolution():
    return RESULTS.get("evolution_prix", [])

@app.get("/anomalies")
def get_anomalies():
    return RESULTS.get("anomalies", [])

@app.get("/figure/{nom}")
def get_figure(nom: str):
    valid = ["boxplot","barchart","scatter","promotions","evolution"]
    if nom not in valid:
        raise HTTPException(404, f"Figure '{nom}' non trouvée. Valides: {valid}")
    path = os.path.join(OUTPUT_DIR, f"fig_{nom}.json")
    if not os.path.exists(path):
        raise HTTPException(404, f"Fichier fig_{nom}.json pas encore généré")
    with open(path, 'r') as f:
        return json.load(f)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
