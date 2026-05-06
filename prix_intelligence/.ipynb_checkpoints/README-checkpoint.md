# 📊 Prix Intelligence Platform

<div align="center">

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)
![Pandas](https://img.shields.io/badge/Pandas-2.2-green?logo=pandas)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110-teal?logo=fastapi)
![Streamlit](https://img.shields.io/badge/Streamlit-1.3-red?logo=streamlit)
![Sklearn](https://img.shields.io/badge/Sklearn-1.4-orange?logo=scikitlearn)
![Docker](https://img.shields.io/badge/Docker-ready-blue?logo=docker)
![Tests](https://img.shields.io/badge/Tests-78%2F78%20✅-brightgreen)
![License](https://img.shields.io/badge/License-MIT-yellow)

**Plateforme d'analyse des prix e-commerce en temps réel**  
*Meubles & Maison — Kitea · Jumia · Ikea — Maroc*

[📊 Dashboard](#-dashboard-streamlit) · [🔌 API](#-api-fastapi) · [📄 Rapport PDF](#-rapport-pdf) · [🤖 ML](#-machine-learning) · [🚀 Quick Start](#-quick-start)

</div>

---

## 🎯 Vue d'ensemble

> Pipeline de données **hybride batch + streaming** pour surveiller et analyser les prix de meubles sur 3 plateformes e-commerce marocaines en temps réel.

```
Scraping (Scrapy)
      ↓
Google Cloud Bigtable (stockage temps-réel)
      ↓
Apache Airflow (orchestration quotidienne)
      ↓
┌─────────────────────────────────────────────┐
│           COUCHE DATA ANALYST               │
│  Notebook Jupyter (39 analyses statist.)    │
│  Machine Learning (Random Forest)           │
│  Rapport PDF auto-généré (7 pages)          │
│  Dashboard Streamlit (6 onglets)            │
│  API FastAPI (17 endpoints)                 │
└─────────────────────────────────────────────┘
      ↓
Fullstack Dashboard Web
      ↓
Utilisateurs finaux
```

---

## 📈 Résultats clés

| Métrique | Valeur |
|----------|--------|
| Produits analysés | **2 647** |
| Sites comparés | **3** (Ikea, Jumia, Kitea) |
| Catégories | **5** (Salon, Chambre, Rangement, etc.) |
| Historique | **30 jours** · 106 650 observations |
| En promotion | **55%** des produits |
| Prix moyen Ikea | **4 230 MAD** |
| Prix moyen Kitea | **3 190 MAD** |
| Prix moyen Jumia | **1 306 MAD** |
| R² régression | **0.19** |
| MAE prédiction ML | **± 150 MAD** |
| Tests pytest | **78 / 78 ✅** |

---

## 🏗️ Architecture technique

```
┌────────────────────────────────────────────────────────────┐
│                    INFRASTRUCTURE                          │
│                                                            │
│  Scrapy + BeautifulSoup → Apache NiFi → Bigtable          │
│         ↓ (streaming)              ↓ (stockage)           │
│  Apache Airflow ──────────────────→ DAGs quotidiens       │
└────────────────────────────────────────────────────────────┘
         ↓
┌────────────────────────────────────────────────────────────┐
│                  COUCHE ANALYSE (Data Analyst)             │
│                                                            │
│  Étape 1  : Chargement (Bigtable / CSV)                   │
│  Étape 2  : Nettoyage (IQR, dedup, normalisation)        │
│  Étape 3  : Stats descriptives                            │
│  Étape 4  : Tests statistiques (Shapiro, Kruskal, MW)     │
│  Étape 5  : Évolution temporelle                          │
│  Étape 6  : Export JSON                                   │
│  Étape 7  : Intervalles de confiance 95%                  │
│  Étape 8  : Power Analysis (Cohen's d)                    │
│  Étape 9  : Matrice de corrélation Spearman               │
│  Étape 10 : Distribution KDE                              │
│  Étape 11 : Price Velocity (tendance 30j)                 │
│  Étape 12 : Alertes intelligentes (3 types)               │
│  Étape 13 : Segmentation par gamme de prix                │
│  Étape 14 : Export final enrichi                          │
│  Étape 15 : Machine Learning (Random Forest)              │
└────────────────────────────────────────────────────────────┘
         ↓
┌────────────────────────────────────────────────────────────┐
│                    LIVRABLES                               │
│                                                            │
│  📄 Rapport PDF   7 pages auto-générées                   │
│  🎨 Dashboard     6 onglets Streamlit interactifs         │
│  🔌 API           17 endpoints FastAPI                    │
│  🤖 ML            Prédiction prix (Random Forest)         │
│  🐳 Docker        Image de production                     │
└────────────────────────────────────────────────────────────┘
```

---

## 📁 Structure du projet

```
prix_intelligence/
│
├── 📊 data/
│   ├── raw/
│   │   ├── raw_prices.csv          # 3555 produits bruts
│   │   └── historique_prices.csv   # 106 650 lignes (30 jours)
│   └── clean/
│       └── clean_prices.csv        # 2647 produits nettoyés
│
├── 📓 notebooks/
│   └── analyse_prix_intelligence.ipynb   # 39 cellules, 15 étapes
│
├── 🔌 api/
│   └── main.py                     # FastAPI 17 endpoints
│
├── 🎨 dashboard/
│   ├── app.py                      # Streamlit 6 onglets
│   └── .streamlit/config.toml      # Configuration thème
│
├── 🧪 tests/
│   ├── conftest.py                 # Fixtures partagées
│   ├── test_data.py                # 46 tests qualité données
│   └── test_api.py                 # 32 tests structure & API
│
├── 📤 outputs/
│   ├── analyse_results.json        # Tous les résultats
│   ├── rapport_prix_intelligence.pdf  # Rapport 7 pages
│   ├── alertes.json                # Alertes intelligentes
│   ├── ml_results.json             # Résultats ML
│   └── fig_*.json                  # 10 graphiques Plotly
│
├── generer_rapport.py              # Script PDF automatique
├── lancer_dashboard.bat            # Lanceur Windows
├── Dockerfile                      # Image production
├── requirements.txt                # Dépendances
└── README.md                       # Ce fichier
```

---

## 🚀 Quick Start

### Prérequis
```bash
Python >= 3.12
conda ou pip
```

### Installation

```bash
# 1. Cloner le repository
git clone https://github.com/votre-equipe/prix-intelligence.git
cd prix-intelligence

# 2. Créer l'environnement
conda create -n prix_ecommerce python=3.12
conda activate prix_ecommerce

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Vérifier l'installation
python -m pytest tests/ -v
# → 78/78 tests passent ✅
```

### Lancer l'application

```bash
# Terminal 1 — API FastAPI
cd prix_intelligence/api
python main.py
# → http://localhost:8000

# Terminal 2 — Dashboard Streamlit
cd prix_intelligence
streamlit run dashboard/app.py
# → http://localhost:8501

# Terminal 3 — Générer le rapport PDF
python generer_rapport.py
# → outputs/rapport_prix_intelligence.pdf (30 sec)
```

### Docker

```bash
# Build
docker build -t prix-intelligence:2.0 .

# Run
docker run -p 8000:8000 prix-intelligence:2.0
# → API disponible sur http://localhost:8000
```

---

## 📊 Dashboard Streamlit

Application web interactive avec **6 onglets** :

| Onglet | Contenu |
|--------|---------|
| 📊 Vue Générale | Boxplot, prix moyen, stats par site, KDE |
| 📈 Évolution des Prix | Ligne 30 jours, price velocity, évolution par catégorie |
| 🔬 Tests Statistiques | IC 95%, Shapiro-Wilk, Kruskal-Wallis, Power Analysis, OLS |
| 🎯 Segmentation | Gamme de prix, tableau croisé, corrélation Spearman |
| 🚨 Alertes | Baisses fortes (-15%), hausses (+10%), anomalies (3σ) |
| 🔍 Explorateur | Recherche produits, filtres, export CSV |

**Filtres sidebar :**
- Sites (Ikea, Jumia, Kitea)
- Catégories (5 types de meubles)
- Gamme de prix (slider MAD)
- Promotions uniquement

```bash
streamlit run dashboard/app.py
# → http://localhost:8501
```

---

## 🔌 API FastAPI

**17 endpoints disponibles :**

```bash
# Stats générales
GET /stats                    # Stats par site (moy, med, std, min, max)
GET /stats/categories         # Stats par catégorie
GET /stats/sites              # Croisement site × catégorie

# Analyses statistiques
GET /tests                    # Shapiro + Kruskal + Mann-Whitney
GET /regression               # OLS : R², coefficients, p-values
GET /intervalles-confiance    # IC 95% par site
GET /power-analysis           # Cohen's d, puissance, n requis

# Évolution temporelle
GET /evolution                # Prix moyen sur 30 jours
GET /velocity                 # Tendance (pente, R², variation %)
GET /anomalies                # Variations > 20% en 1 jour

# Alertes & ML
GET /alertes                  # Alertes intelligentes (3 types)
GET /segmentation             # Gamme de prix (Entrée → Luxe)
GET /correlation              # Corrélation Spearman

# Graphiques interactifs (Plotly JSON)
GET /figure/boxplot           # Distribution prix
GET /figure/barchart          # Prix moyen par catégorie
GET /figure/evolution         # Ligne temporelle
GET /figure/scatter           # Prix vs ancien prix
GET /figure/kde               # Distribution KDE
GET /figure/ic                # Intervalles de confiance
GET /figure/correlation       # Heatmap corrélation
GET /figure/velocity          # Price velocity
GET /figure/segmentation      # Gamme de prix
```

**Exemple :**
```javascript
// JavaScript (Fullstack)
const stats = await fetch('http://localhost:8000/stats').then(r => r.json())

// Afficher un graphique Plotly
const fig = await fetch('http://localhost:8000/figure/boxplot').then(r => r.json())
Plotly.newPlot('div-chart', fig.data, fig.layout)
```

---

## 📄 Rapport PDF

Rapport professionnel de **7 pages** auto-généré en **30 secondes** :

```
Page 1 : Couverture + KPIs (2647 produits, 55% en promo...)
Page 2 : Stats descriptives + Boxplot + Bar chart
Page 3 : Intervalles de confiance + Tests normalité
Page 4 : Power Analysis + Régression linéaire
Page 5 : Distribution KDE + Analyse promotions
Page 6 : Évolution 30j + Price Velocity + Segmentation
Page 7 : Corrélation Spearman + Conclusions
```

```bash
# Générer le rapport
python generer_rapport.py

# Avec nom personnalisé
python generer_rapport.py --output rapport_semaine_1.pdf
```

**Usage Airflow :** Ce script est conçu pour être déclenché automatiquement chaque semaine par Apache Airflow, ce qui correspond au *"weekly statistical report"* demandé dans le projet.

---

## 🤖 Machine Learning

**Prédiction du prix demain** avec Random Forest :

### Modèles

| Modèle | MAE | RMSE | R² |
|--------|-----|------|-----|
| **Random Forest** (100 arbres) | **± 150 MAD** | ± 180 MAD | **0.41** |
| Linear Regression (baseline) | ± 200 MAD | ± 240 MAD | 0.32 |

### Features utilisées

| Feature | Importance |
|---------|-----------|
| ancien_prix | 28% |
| prix_log | 21% |
| ratio_prix | 18% |
| remise_pct | 14% |
| categorie | 9% |
| jour_semaine | 4% |
| site | 4% |

### Utilisation

```python
from ml_prediction_module import MLPredictor

# Entraîner
predictor = MLPredictor(n_estimators=100)
predictor.train(df_clean)

# Prédire
pred = predictor.predict(
    site='kitea',
    categorie='Salon Et Sejour',
    remise_pct=15,
    ancien_prix=4200
)
# {'prix_predit': 3420, 'marge_erreur': 150, 'intervalle': [3270, 3570]}
```

---

## 🔬 Analyses statistiques

**15 étapes d'analyse complètes :**

### Statistiques descriptives
- Moyenne, médiane, écart-type, min, max par site & catégorie
- Coefficient de variation (volatilité)
- Taux et remise moyenne par promotion

### Tests inférentiels
| Test | Résultat |
|------|---------|
| Shapiro-Wilk | Non-normal (p ≈ 0) → justifie tests non-param. |
| Kruskal-Wallis (catégories) | H=55.38, **p<0.001** → différences significatives |
| Kruskal-Wallis (sites) | H=515.07, **p<0.001** → différences significatives |
| Mann-Whitney U | Toutes paires significatives (p<0.05) |

### Modélisation
- **OLS Regression** : prix ~ site + catégorie + promotion
  - R² ajusté = 0.19, F=89.15, p<0.001
  - Jumia = -2799 MAD vs Ikea (référence)

### Analyses avancées
- Intervalles de confiance 95% par site
- **Power Analysis** : Cohen's d, puissance statistique
- Matrice de corrélation Spearman
- Distribution KDE avec histogramme
- Price Velocity (tendance linéaire 30 jours)
- Détection d'anomalies (variation > 20%)
- Alertes intelligentes (3 types)
- Segmentation Entrée/Économique/Milieu/Premium/Luxe

---

## 🧪 Tests

```bash
# Lancer tous les tests
python -m pytest tests/ -v

# Avec couverture de code
python -m pytest tests/ --cov=. --cov-report=html

# Résultat attendu
# 78 passed in 10.01s ✅
```

### Structure des tests

```
tests/
├── conftest.py              # Fixtures (df_clean, results_json...)
├── test_data.py (46 tests)
│   ├── TestFichiersExistent    # Fichiers existent
│   ├── TestTailleDonnees       # Nb lignes minimum
│   ├── TestColonnesRequises    # Colonnes présentes
│   ├── TestQualitePrix         # Prix positifs, remises valides
│   ├── TestDoublons            # Pas de doublons
│   ├── TestDistributions       # Cohérence statistique
│   └── TestJsonResultats       # Structure JSON
│
└── test_api.py (32 tests)
    ├── TestOutputsFichiers     # Fichiers outputs
    ├── TestStructureJson       # Structure résultats
    ├── TestValeursStatistiques # Valeurs cohérentes
    ├── TestRapportPdf          # PDF généré
    ├── TestFichiersApplication # API, Dashboard, Docker
    └── TestImports             # Dépendances installées
```

---

## 🔄 Workflow de production (Bigtable + Airflow)

```python
# En production : remplacer pd.read_csv() par Bigtable
# Seul ce bloc change — tout le reste est identique !

from google.cloud import bigtable

client   = bigtable.Client(project='prix-intelligence-prod')
instance = client.instance('prix-prod-instance')
table    = instance.table('prix-maison')

rows = table.read_rows()
df_raw = pd.DataFrame([
    {
        'product_id': row.key.decode(),
        'prix': float(row.cells[b'price_cf'][b'prix'][-1].value),
        'date': row.cells[b'price_cf'][b'prix'][-1].timestamp,
    }
    for row in rows
])

# → Tout le reste du notebook fonctionne identiquement ✅
```

**DAG Airflow quotidien :**
```
2:00 AM → Data Engineer scrape les 3 sites → stocke dans Bigtable
3:00 AM → Airflow DAG déclenche :
          ├─ python generer_rapport.py     (PDF du jour)
          ├─ jupyter nbconvert --execute  (15 étapes analyse)
          └─ python -m pytest tests/      (validation)
4:00 AM → Dashboard actualisé, API prête, alertes calculées
```

---

## 🐳 Docker

```bash
# Build image production
docker build -t prix-intelligence:2.0 .

# Run container
docker run -p 8000:8000 prix-intelligence:2.0
# → ✅ API running on http://0.0.0.0:8000

# Avec volume pour données
docker run -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/outputs:/app/outputs \
  prix-intelligence:2.0
```

---

## 🛠️ Stack technique

| Couche | Technologie |
|--------|------------|
| Scraping | Scrapy, BeautifulSoup, Selenium |
| Streaming | Apache NiFi |
| Orchestration | Apache Airflow |
| Stockage | Google Cloud Bigtable |
| Transformation | dbt (SQL models) |
| Analyse | Python, Pandas, SciPy, statsmodels |
| ML | scikit-learn (Random Forest) |
| Visualisation | Plotly, Streamlit |
| API | FastAPI, Uvicorn |
| Tests | pytest, pytest-cov |
| Containerisation | Docker |
| Cloud | Google Cloud Platform |

---

## 👥 Équipe

| Rôle | Responsabilité |
|------|---------------|
| **Data Engineer** | Scrapers, NiFi, Airflow DAGs, Bigtable |
| **Data Analyst** | Analyses, API, Dashboard, ML, Rapport PDF |
| **Fullstack** | Dashboard web consommant l'API |
| **DevOps** | Docker, CI/CD, déploiement GKE |
| **DevSec** | Sécurité API, authentification |

---

## 📚 Documentation

- [LIVRAISON_FULLSTACK.md](./LIVRAISON_FULLSTACK.md) — Guide API pour le Fullstack
- [GUIDE_MACHINE_LEARNING.md](./GUIDE_MACHINE_LEARNING.md) — Explication du ML
- [EXPLICATION_COMPLETE_PROJET.md](./EXPLICATION_COMPLETE_PROJET.md) — Architecture complète

---

## 📄 Licence

MIT License — Projet académique Data Engineering & Analytics  
Prof. Elaachak — 2025-2026
