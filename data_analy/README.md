# 📊 Prix Intelligence Platform

<div align="center">

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)
![Pandas](https://img.shields.io/badge/Pandas-2.2-green?logo=pandas)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110-teal?logo=fastapi)
![Streamlit](https://img.shields.io/badge/Streamlit-1.3-red?logo=streamlit)
![Sklearn](https://img.shields.io/badge/Sklearn-1.4-orange?logo=scikitlearn)
![Docker](https://img.shields.io/badge/Docker-ready-blue?logo=docker)
![Tests](https://img.shields.io/badge/Tests-78%2F78%20✅-brightgreen)
![BigQuery](https://img.shields.io/badge/BigQuery-GCP-4285F4?logo=googlecloud)
![License](https://img.shields.io/badge/License-MIT-yellow)

**Plateforme d'analyse des prix e-commerce — hybride batch + streaming**  
*Meubles & Maison — Kitea · Jumia · Ikea — Maroc*

[📊 Dashboard](#-dashboard-streamlit) · [🔌 API](#-api-fastapi) · [📄 Rapport PDF](#-rapport-pdf) · [🤖 ML](#-machine-learning) · [🚀 Quick Start](#-quick-start)

</div>

---

## 🎯 Vue d'ensemble

> Pipeline de données **hybride batch + streaming** pour surveiller et analyser les prix de meubles sur 3 plateformes e-commerce marocaines. Les données sont collectées via Scrapy, ingérées en temps réel par Apache NiFi, stockées dans Google Cloud Bigtable, transformées par dbt, et analysées dans ce module Data Analyst.

```
Scrapy (3 spiders)
      ↓
Kafka (topics : prix-jumia / prix-ikea / prix-kitea)
      ↓
Apache NiFi (streaming → ingestion temps réel)
      ↓
Google Cloud Bigtable (stockage time-series)
      ↓
Apache Airflow (orchestration : DAGs quotidiens 6h/7h/8h)
      ↓
dbt (transformations SQL : staging → cleaned → aggregations)
      ↓
┌─────────────────────────────────────────────────────────┐
│              COUCHE DATA ANALYST (ce module)            │
│                                                         │
│  Notebook Jupyter — 15 étapes d'analyse complètes      │
│  Machine Learning — Random Forest (sans data leakage)  │
│  Rapport PDF — 7 pages auto-générées en 30 sec         │
│  Dashboard Streamlit — 6 onglets interactifs           │
│  API FastAPI — 21 endpoints (données + figures)        │
└─────────────────────────────────────────────────────────┘
      ↓
Fullstack Dashboard Web
      ↓
Utilisateurs finaux
```

---

## 📈 Résultats clés

| Métrique | Valeur |
|----------|--------|
| Produits analysés | **2 647** (après nettoyage IQR + normalisation) |
| Produits bruts scrapés | **3 555** (raw_prices.csv) |
| Sites comparés | **3** — Ikea · Jumia · Kitea |
| Catégories | **5** — Salon, Chambre, Salle à Manger, Rangement, Mobilier Pro |
| Historique | **30 jours** · 106 650 observations |
| En promotion | **55%** des produits |
| Prix moyen Ikea | **4 230 MAD** |
| Prix moyen Kitea | **3 190 MAD** |
| Prix moyen Jumia | **1 306 MAD** |
| R² régression OLS | **0.19** (prix ~ site + catégorie + promotion) |
| R² ML Random Forest | **0.48** (sans data leakage) |
| MAE prédiction ML | **± 1 032 MAD** |
| Alertes actives | **100** (52 baisses + 48 hausses) |
| Anomalies détectées | **50** (variation > 20% en 1 jour) |
| Tests pytest | **78 / 78 ✅** |
| Mode BigQuery | **177 655 produits** depuis GCP (`DATA_MODE=bigquery`) |

---

## 🏗️ Architecture technique

```
┌──────────────────────────────────────────────────────────────┐
│                    DATA ENGINEERING                          │
│                                                              │
│  Scrapy ──→ Kafka ──→ NiFi ──→ Bigtable                    │
│    ↑             (streaming)        ↓                        │
│  3 spiders                    Airflow DAGs                   │
│  (6h/7h/8h)                   (quotidiens)                   │
│                                    ↓                         │
│                               dbt models                     │
│                    (staging → cleaned → aggregations)        │
└──────────────────────────────────────────────────────────────┘
         ↓  DATA_MODE = bigquery | csv | json
┌──────────────────────────────────────────────────────────────┐
│                  COUCHE ANALYSE (Data Analyst)               │
│                                                              │
│  Étape 1  : Chargement (BigQuery / Bigtable / CSV)          │
│  Étape 2  : Nettoyage (IQR, dedup, normalisation catégories)│
│  Étape 3  : Statistiques descriptives                        │
│  Étape 4  : Tests statistiques (Shapiro, Kruskal, MW)       │
│  Étape 5  : Évolution temporelle (30 jours)                 │
│  Étape 6  : Export JSON intermédiaire                        │
│  Étape 7  : Intervalles de confiance 95%                     │
│  Étape 8  : Power Analysis (Cohen's d)                       │
│  Étape 9  : Matrice de corrélation Spearman                 │
│  Étape 10 : Distribution KDE                                 │
│  Étape 11 : Price Velocity (tendance linéaire 30j)          │
│  Étape 12 : Alertes intelligentes (BAISSE / HAUSSE / STAT)  │
│  Étape 13 : Segmentation par gamme de prix                  │
│  Étape 14 : Export final enrichi (analyse_results.json)     │
│  Étape 15 : Machine Learning (Random Forest sans leakage)   │
└──────────────────────────────────────────────────────────────┘
         ↓
┌──────────────────────────────────────────────────────────────┐
│                    LIVRABLES                                 │
│                                                              │
│  📄 Rapport PDF     7 pages auto-générées                   │
│  🎨 Dashboard       6 onglets Streamlit interactifs         │
│  🔌 API             21 endpoints FastAPI                    │
│  🤖 ML              Prédiction prix (Random Forest)         │
│  🐳 Docker          Image de production                     │
└──────────────────────────────────────────────────────────────┘
```

---

## 📁 Structure du projet

```
prix_intelligence/
│
├── 📊 data/
│   ├── raw/
│   │   ├── raw_prices.csv              # 3 555 produits bruts (3 sites)
│   │   ├── historique_prices.csv       # 106 650 lignes (30 jours)
│   │   ├── json_jumia.json             # Export JSON Data Engineer
│   │   ├── json_ikea.json
│   │   └── json_kitea.json
│   └── clean/
│       └── clean_prices.csv            # 2 647 produits nettoyés (5 catégories)
│
├── 📓 notebooks/
│   └── analyse_prix_intelligence.ipynb # 58 cellules, 15 étapes complètes
│
├── 🔌 api/
│   └── main.py                         # FastAPI 21 endpoints, reload dynamique
│
├── 🎨 dashboard/
│   └── app.py                          # Streamlit 6 onglets (1 013 lignes)
│
├── 🧪 tests/
│   ├── conftest.py                     # Fixtures + DATA_MODE (csv/bigquery/json)
│   ├── test_data.py                    # 46 tests qualité données
│   └── test_api.py                     # 32 tests structure & API
│
├── 📤 outputs/
│   ├── analyse_results.json            # 21 sections — tous les résultats
│   ├── rapport_prix_intelligence.pdf   # Rapport 7 pages
│   ├── ml_results.json                 # Résultats ML (v2 — sans data leakage)
│   ├── alertes.json                    # 100 alertes baisses/hausses
│   └── fig_*.json                      # 12 graphiques Plotly interactifs
│
├── generer_rapport.py                  # Script PDF automatique (30 sec)
├── lancer_dashboard.bat                # Lanceur Windows
├── Dockerfile                          # Image production Python 3.11-slim
├── requirements.txt                    # Dépendances production
└── README.md                           # Ce fichier
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
# → http://localhost:8000/docs  (Swagger UI interactif)

# Terminal 2 — Dashboard Streamlit
cd prix_intelligence
streamlit run dashboard/app.py
# → http://localhost:8501

# Terminal 3 — Générer le rapport PDF
python generer_rapport.py
# → outputs/rapport_prix_intelligence.pdf (30 sec)
```

### Mode BigQuery (données production GCP)

```bash
# Lire 177 655 produits depuis Google Cloud BigQuery
set DATA_MODE=bigquery          # Windows
export DATA_MODE=bigquery       # Linux/Mac

# Puis ouvrir et exécuter le notebook normalement
# Toutes les analyses s'adaptent automatiquement au volume BigQuery
jupyter notebook notebooks/analyse_prix_intelligence.ipynb
```

### Docker

```bash
# Build
docker build -t prix-intelligence:2.0 .

# Run
docker run -p 8000:8000 prix-intelligence:2.0
# → API disponible sur http://localhost:8000

# Avec volumes pour données
docker run -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/outputs:/app/outputs \
  prix-intelligence:2.0
```

---

## 📊 Dashboard Streamlit

Application web interactive avec **6 onglets** :

| Onglet | Contenu |
|--------|---------|
| 📊 Vue Générale | Boxplot, prix moyen par site, KDE, stats |
| 📈 Évolution des Prix | Courbe 30 jours, price velocity, tendance |
| 🔬 Tests Statistiques | IC 95%, Shapiro-Wilk, Kruskal-Wallis, Power Analysis, OLS |
| 🎯 Segmentation | Gammes de prix, tableau croisé, corrélation Spearman |
| 🚨 Alertes | 100 alertes (baisses ≤ -2%, hausses ≥ +2%) |
| 🔍 Explorateur | Recherche produits, filtres, export CSV |

**Filtres sidebar :**
- Sites (Ikea · Jumia · Kitea)
- Catégories (5 types de meubles)
- Gamme de prix (slider MAD)
- Promotions uniquement

```bash
streamlit run dashboard/app.py
# → http://localhost:8501
```

---

## 🔌 API FastAPI

**21 endpoints disponibles** — reload dynamique à chaque requête :

```bash
# ── Statistiques ─────────────────────────────────────────
GET /stats                        # Stats globales par site (moy, med, std, min, max)
GET /stats/categories             # Stats par catégorie
GET /stats/sites                  # Croisement site × catégorie (3 sites × 5 catégories)

# ── Analyses statistiques ────────────────────────────────
GET /tests                        # Shapiro-Wilk + Kruskal-Wallis + Mann-Whitney
GET /regression                   # OLS : R²=0.19, coefficients, p-values
GET /intervalles-confiance        # IC 95% par site ET par catégorie
GET /intervalles-confiance/categories  # IC 95% par catégorie uniquement
GET /power-analysis               # Cohen's d, puissance statistique, n requis
GET /correlation                  # Matrice de corrélation Spearman

# ── Évolution temporelle ─────────────────────────────────
GET /evolution                    # Prix moyen 30 jours par site
GET /velocity                     # Tendance (pente, R², variation MAD/jour)
GET /anomalies                    # 50 anomalies (variation > 20% en 1 jour)

# ── Alertes & Segmentation ───────────────────────────────
GET /alertes                      # 100 alertes intelligentes
GET /alertes?priorite=HAUTE       # Filtrer par priorité (HAUTE/MOYENNE/BASSE)
GET /alertes?site=ikea            # Filtrer par site
GET /alertes?type_alerte=BAISSE_FORTE  # Filtrer par type
GET /segmentation                 # Gammes Entrée/Économique/Milieu/Premium/Luxe

# ── Graphiques Plotly (JSON prêt à afficher) ─────────────
GET /figures                      # Liste toutes les figures + statut disponible
GET /figure/boxplot               # Distribution prix par site
GET /figure/barchart              # Prix moyen par catégorie
GET /figure/evolution             # Courbe temporelle 30 jours
GET /figure/scatter               # Prix vs ancien prix
GET /figure/kde                   # Distribution KDE par site
GET /figure/ic                    # Intervalles de confiance
GET /figure/correlation           # Heatmap corrélation Spearman
GET /figure/velocity              # Price velocity (tendance)
GET /figure/segmentation          # Gammes de prix
GET /figure/feature_importance    # Importance des features ML
GET /figure/ml_predictions        # Prix réel vs prédit
```

**Exemple d'intégration Fullstack :**
```javascript
// Récupérer les stats
const stats = await fetch('http://localhost:8000/stats').then(r => r.json())

// Afficher un graphique Plotly directement
const fig = await fetch('http://localhost:8000/figure/boxplot').then(r => r.json())
Plotly.newPlot('div-chart', fig.data, fig.layout)

// Récupérer les alertes HAUTE priorité
const alertes = await fetch('http://localhost:8000/alertes?priorite=HAUTE').then(r => r.json())
console.log(`${alertes.total} alertes critiques`)

// Intervalles de confiance 95%
const ic = await fetch('http://localhost:8000/intervalles-confiance').then(r => r.json())
```

**Documentation interactive :**
```bash
http://localhost:8000/docs   # Swagger UI — tester tous les endpoints
http://localhost:8000/redoc  # ReDoc — documentation complète
```

---

## 📄 Rapport PDF

Rapport professionnel de **7 pages** auto-généré en **30 secondes** :

```
Page 1 : Couverture + KPIs (2 647 produits, 55% en promo, 100 alertes)
Page 2 : Stats descriptives + Boxplot + Bar chart
Page 3 : Intervalles de confiance 95% + Tests normalité (Shapiro-Wilk)
Page 4 : Power Analysis (Cohen's d) + Régression linéaire (R²=0.19)
Page 5 : Distribution KDE + Analyse promotions
Page 6 : Évolution 30j + Price Velocity + Segmentation gammes
Page 7 : Corrélation Spearman + Machine Learning + Conclusions
```

```bash
# Générer le rapport
python generer_rapport.py

# Avec nom personnalisé
python generer_rapport.py --output rapport_semaine_1.pdf
```

> **Usage Airflow :** Ce script est déclenché automatiquement chaque dimanche à 10h par le DAG `weekly_report_pipeline` d'Apache Airflow — c'est le *"weekly statistical report"* demandé dans le projet.

---

## 🤖 Machine Learning

**Prédiction du prix** avec Random Forest — **sans data leakage** (v2) :

### Modèles comparés

| Modèle | MAE | RMSE | R² | Note |
|--------|-----|------|----|------|
| **Random Forest** (200 arbres) | **± 1 032 MAD** | ± 2 100 MAD | **0.48** | ✅ Meilleur modèle |
| Linear Regression (baseline) | ± 1 344 MAD | ± 2 600 MAD | 0.32 | Référence |

> **Note v2 — Correction data leakage :** La version précédente utilisait `prix_log` et `ratio_prix` comme features, qui sont des transformations directes du prix cible → R²=0.9997 artificiel. Ces features ont été supprimées. Le R²=0.48 actuel est honnête et réaliste.

### Features utilisées (sans leakage)

| Feature | Importance | Justification |
|---------|-----------|---------------|
| `ancien_prix` | **34.3%** | Prix barré connu avant la prédiction ✅ |
| `ancien_prix_log` | **33.0%** | Version log pour normaliser la distribution ✅ |
| `site_enc` | **13.2%** | Ikea > Kitea > Jumia en termes de prix ✅ |
| `cat_enc` | **12.2%** | Catégorie du produit ✅ |
| `remise_pct` | **7.2%** | Pourcentage de remise annoncé ✅ |
| `en_promo` | **0.1%** | Flag binaire promotion ✅ |
| `jour_semaine` | **0.0%** | Jour de la semaine ✅ |

### Utilisation

```python
# predict_price() disponible après exécution de la cellule ML (Cell 38)

pred = predict_price(
    site='kitea',
    categorie='Salon Et Sejour',
    remise_pct=15,
    ancien_prix=4200
)
# {'prix_predit': 3420.0, 'marge_erreur': 1032.0,
#  'intervalle': [2388.0, 4452.0], 'confiance': 'BASSE', 'r2': 0.4779}
```

---

## 🔬 Analyses statistiques

**15 étapes d'analyse complètes :**

### Statistiques descriptives
- Moyenne, médiane, écart-type, min, max par site & catégorie
- Coefficient de variation (volatilité des prix)
- Taux et remise moyenne des promotions par site

### Tests inférentiels

| Test | Résultat | Interprétation |
|------|---------|----------------|
| Shapiro-Wilk | Non-normal (p ≈ 0) | Justifie l'utilisation de tests non-paramétriques |
| Kruskal-Wallis (catégories) | H=55.38, **p<0.001** | Différences significatives entre catégories |
| Kruskal-Wallis (sites) | H=515.07, **p<0.001** | Différences significatives entre sites |
| Mann-Whitney U | Toutes paires significatives | Chaque paire de sites est statistiquement différente |

### Modélisation
- **OLS Regression** : `prix ~ C(site) + C(categorie) + en_promo`
  - R² ajusté = **0.19**, F=89.15, p<0.001
  - Jumia ≈ -2 799 MAD vs Ikea (référence)

### Analyses avancées
- **Intervalles de confiance 95%** par site et par catégorie (t-distribution)
- **Power Analysis** : Cohen's d, puissance statistique, taille d'échantillon minimum
- **Corrélation Spearman** (données non-normales)
- **Distribution KDE** avec histogramme par site
- **Price Velocity** : tendance linéaire sur 30 jours (pente, R²)
- **Alertes intelligentes** : 100 alertes (baisses ≤ -2%, hausses ≥ +2%)
- **Anomalies** : 50 produits avec variation > 20% en une journée
- **Segmentation** : Entrée / Économique / Milieu / Premium / Luxe

---

## 🧪 Tests

```bash
# Lancer tous les tests
python -m pytest tests/ -v
# → 78/78 passed ✅

# Avec couverture de code
python -m pytest tests/ --cov=. --cov-report=html

# En mode BigQuery (les tests s'adaptent automatiquement)
set DATA_MODE=bigquery
python -m pytest tests/ -v
# → 78/78 passed ✅  (nb_produits comparé au JSON, pas au CSV local)
```

### Structure des tests

```
tests/
├── conftest.py                  # Fixtures session-scope + DATA_MODE
│   ├── df_clean                 # CSV nettoyé
│   ├── df_hist                  # Historique 30 jours
│   ├── results_json             # analyse_results.json
│   ├── nb_produits_attendu      # Adapté selon DATA_MODE
│   └── data_mode                # 'csv' | 'bigquery' | 'json'
│
├── test_data.py  (46 tests)
│   ├── TestFichiersExistent     # Tous les fichiers existent
│   ├── TestTailleDonnees        # Minimum 1 000 produits, 25 jours
│   ├── TestColonnesRequises     # Colonnes obligatoires présentes
│   ├── TestQualitePrix          # Prix positifs, remises [0–100]
│   ├── TestDoublons             # Pas de product_id dupliqués
│   ├── TestDistributions        # Taux promo [10–90%], Ikea > Jumia
│   └── TestJsonResultats        # Structure et cohérence du JSON
│
└── test_api.py   (32 tests)
    ├── TestOutputsFichiers      # Fichiers outputs générés
    ├── TestStructureJson        # Toutes les sections présentes
    ├── TestValeursStatistiques  # R², p-values, prix cohérents
    ├── TestRapportPdf           # PDF généré et lisible
    ├── TestFichiersApplication  # API, Dashboard, Dockerfile
    └── TestImports              # Dépendances installées
```

---

## 🔄 Workflow de production (Bigtable + Airflow)

```python
# DATA_MODE contrôle la source de données — tout le reste du notebook est identique

# Mode CSV (développement local)
export DATA_MODE=csv
# → lit data/raw/raw_prices.csv (2 647 produits)

# Mode JSON (données Data Engineer exportées)
export DATA_MODE=json
# → lit data/raw/json_jumia.json + json_ikea.json + json_kitea.json

# Mode BigQuery (production GCP)
export DATA_MODE=bigquery
# → lit depuis diesel-patrol-491520-j8.jumia_price_intelligence
# → 177 655 produits depuis Google Cloud BigQuery
```

**DAG Airflow — planning quotidien :**
```
06:00 → jumia_pipeline  : scrapy crawl jumia → Kafka → NiFi → Bigtable → dbt
07:00 → ikea_pipeline   : scrapy crawl ikea  → Kafka → NiFi → Bigtable → dbt
08:00 → kitea_pipeline  : scrapy crawl kitea → Kafka → NiFi → Bigtable → dbt
       (toutes les 6h)
       → bigtable_pipeline : Bigtable → BigQuery → dbt run → dbt test

Dimanche 10:00 → weekly_report_pipeline :
    (attend les 3 pipelines via ExternalTaskSensor)
    ├─ dbt run --all
    ├─ jupyter nbconvert --execute (15 étapes analyse)
    ├─ python generer_rapport.py   (PDF du rapport)
    └─ python -m pytest tests/     (validation 78/78)
```

---

## 🐳 Docker

```bash
# Build image production
docker build -t prix-intelligence:2.0 .

# Run container
docker run -p 8000:8000 prix-intelligence:2.0
# → ✅ API running on http://0.0.0.0:8000

# Avec volumes pour données persistantes
docker run -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/outputs:/app/outputs \
  prix-intelligence:2.0

# Variables d'environnement
docker run -p 8000:8000 \
  -e DATA_MODE=bigquery \
  -e GOOGLE_APPLICATION_CREDENTIALS=/app/credentials/service_account.json \
  -v $(pwd)/credentials:/app/credentials \
  prix-intelligence:2.0
```

---

## 🛠️ Stack technique

| Couche | Technologie | Rôle |
|--------|------------|------|
| Scraping | Scrapy + BeautifulSoup | 3 spiders (Jumia/Ikea/Kitea) |
| Streaming | Apache Kafka | Topics par site |
| Ingestion | Apache NiFi | GetKafka → Transform → PutBigtable |
| Orchestration | Apache Airflow | 5 DAGs (3 quotidiens + 1 toutes 6h + 1 hebdo) |
| Stockage | Google Cloud Bigtable | Time-series `product_id#timestamp` |
| Transformation | dbt (BigQuery) | staging → cleaned → aggregations |
| Entrepôt | Google Cloud BigQuery | `diesel-patrol-491520-j8` |
| Analyse | Python, Pandas, SciPy, statsmodels | 15 étapes notebook |
| ML | scikit-learn (Random Forest) | Prédiction sans data leakage |
| Visualisation | Plotly, Streamlit | 12 figures + dashboard 6 onglets |
| API | FastAPI, Uvicorn | 21 endpoints, reload dynamique |
| Tests | pytest, pytest-cov | 78/78 tests, DATA_MODE aware |
| Containerisation | Docker | Python 3.11-slim |
| Cloud | Google Cloud Platform | Bigtable + BigQuery |

---

## 👥 Équipe

| Rôle | Responsabilité |
|------|---------------|
| **Data Engineer** | Scrapy spiders, Kafka, NiFi flows, Airflow DAGs, Bigtable, dbt |
| **Data Analyst** | Analyses statistiques, ML, API, Dashboard, Rapport PDF |
| **Fullstack** | Dashboard web consommant l'API FastAPI |
| **DevOps** | Docker, CI/CD GitHub Actions, déploiement GKE |

---

## 📚 Documentation complémentaire

- [`LIVRAISON_FULLSTACK.md`](./LIVRAISON_FULLSTACK.md) — Guide d'intégration API pour le Fullstack
- [`notebooks/analyse_prix_intelligence.ipynb`](./notebooks/analyse_prix_intelligence.ipynb) — Notebook complet 15 étapes

---

## 📄 Licence

MIT License — Projet académique Data Engineering & Analytics  
Prof. Elaachak — 2025-2026
