# 🛋️ MobilierPrix - Price Intelligence Platform

Ce projet est une plateforme complète de **Data Engineering** et de **Price Intelligence** conçue pour collecter, analyser et visualiser les prix du mobilier des trois plus grands détaillants au Maroc : **Jumia**, **IKEA** et **Kitea**. 

La plateforme combine un pipeline de streaming en temps réel et de traitements batch, des analyses statistiques avancées (Machine Learning, tests d'hypothèses, détection d'anomalies), ainsi qu'une double interface de visualisation (un Dashboard d'analyse Streamlit et une application web Angular de production).

---

## 📌 Sommaire
1. [🛠️ Data Engineering](#️-data-engineering) __najlae najdi akel
2. [⚙️ Ops & Infrastructure](#️-ops--infrastructure)__Hafsa Elladam
3. [🛡️ Sécurité (DevSecOps)](#️-sécurité-devsecops) __abderrahmane Maski
4. [📈 Analyses Statistiques & Machine Learning](#-analyses-statistiques--machine-learning) __adnane Biyoud
5. [📊 Dashboards & Visualisation](#-fullstack--development)__ acher elhatimi
6. [🚀 Démarrage Rapide](#-démarrage-rapide)

---

## 🛠️ Data Engineering

Le flux de données suit une architecture hybride (batch et temps réel) pour ingérer et nettoyer les données e-commerce.

### 1. Ingestion & Streaming (Scrapy & Kafka)
*   **Scrapers (Spiders) :** Récupèrent les informations brutes des produits sur Jumia, IKEA et Kitea.
*   **Pipeline Kafka :** Nettoie les données scrapées en temps réel via [pipelines.py](file:///C:/Users/admin/Downloads/price_intelligence_FINAL/airflow/dags/jumia_scraper/pipelines.py), normalise la source, calcule le pourcentage de remise (`remise_pct`) et publie les messages sur 3 topics Kafka distincts :
    *   `prix-jumia`
    *   `prix-ikea`
    *   `prix-kitea`

### 2. Flux de Streaming & Stockage (Apache NiFi & Google Cloud Bigtable)
*   **Apache NiFi :** Consomme les messages depuis Kafka, extrait les attributs JSON via `EvaluateJsonPath` et exécute le script [write_bigtable.py](file:///C:/Users/admin/Downloads/price_intelligence_FINAL/nifi_scripts/write_bigtable.py).
*   **Google Cloud Bigtable :** Stocke l'historique temporel sous forme NoSQL.
    *   *Row Key structurée :* `source#hash(url)#timestamp`
    *   *Column Family :* `price_cf` (contenant nom, prix, ancien_prix, remise, url, image_url, source, categorie, date_scraping).

### 3. Entrepôt de Données & Transformations (Google BigQuery & dbt)
*   **Script de Transfert :** Le script [bigtable_to_bigquery.py](file:///C:/Users/admin/Downloads/price_intelligence_FINAL/airflow/dags/bigtable_to_bigquery.py) transfère les données de Bigtable vers Google BigQuery par lots.
*   **dbt (Data Build Tool) :** Modélise et transforme les données brutes via 9 modèles dbt en 3 couches (staging unifié, déduplication incrémentale, tables d'agrégations statistiques et calcul de la vélocité des prix). La configuration du profil utilise le fichier [profiles.yml](file:///C:/Users/admin/Downloads/price_intelligence_FINAL/airflow/jumia_dbt/profiles.yml).

---

## ⚙️ Ops & Infrastructure

L'infrastructure complète est conteneurisée et orchestrée automatiquement.

### 1. Orchestration avec Docker Compose
Le fichier [docker-compose.yml](file:///C:/Users/admin/Downloads/price_intelligence_FINAL/docker-compose.yml) orchestre **5 services essentiels** :
*   **Zookeeper & Kafka :** Gestion de la file d'attente et du streaming.
*   **Apache NiFi :** Ingestion et traitement de flux.
*   **Apache Airflow :** Planification et automatisation des workflows de données.
*   **Bigtable Emulator :** Émulateur local NoSQL pour le développement hors-cloud.

### 2. Automatisation des Pipelines (Airflow)
L'orchestration est découpée en **5 DAGs** planifiés dans Airflow :
*   [jumia_dag.py](file:///C:/Users/admin/Downloads/price_intelligence_FINAL/airflow/dags/jumia_dag.py) (06h00) : Vérifie Kafka, lance le scraper Jumia, attend la fin de NiFi et déclenche dbt.
*   [ikea_dag.py](file:///C:/Users/admin/Downloads/price_intelligence_FINAL/airflow/dags/ikea_dag.py) (07h00) : Idem pour IKEA.
*   [kitea_dag.py](file:///C:/Users/admin/Downloads/price_intelligence_FINAL/airflow/dags/kitea_dag.py) (08h00) : Idem pour Kitea.
*   [bigtable_pipeline_dag.py](file:///C:/Users/admin/Downloads/price_intelligence_FINAL/airflow/dags/bigtable_pipeline_dag.py) (12h00) : Exécute le pipeline complet de Bigtable vers BigQuery puis dbt.
*   [weekly_report_dag.py](file:///C:/Users/admin/Downloads/price_intelligence_FINAL/airflow/dags/weekly_report_dag.py) (Dimanche 10h00) : Génère un rapport statistique hebdomadaire.

---

## 🛡️ Sécurité (DevSecOps)

Une attention particulière a été portée sur la sécurisation de l'ensemble du pipeline.

### 1. Protection des Secrets & Identifiants
*   **Séparation des secrets :** Les clés de compte de service GCP (`.json`) et les identifiants de bases de données sont exclus de Git via `.gitignore`.
*   **Centralisation :** Utilisation d'un fichier `.env` pour toutes les variables d'environnement locales (avec un modèle [.env.example](file:///C:/Users/admin/Downloads/price_intelligence_FINAL/.env.example) fourni pour l'équipe).

### 2. Sécurisation de l'API (FastAPI)
*   **Restriction CORS :** Restriction stricte des requêtes CORS uniquement à l'origine du frontend Angular (`http://localhost:4200`) et limitation aux méthodes `GET`.
*   **Validation des Entrées :** L'endpoint de recherche valide strictement les paramètres (limitation de `q` à 100 caractères, `limit` de 1 à 200, sens de tri).
*   **Audit Logging :** Tracé systématique de chaque appel API (IP, méthode, URL, statut, durée) dans un fichier `audit.log`.

### 3. Sécurisation de l'Infrastructure
*   **Docker Volumes :** Clé GCP montée en lecture seule (`:ro`) dans le conteneur Airflow.
*   **Identifiants par défaut supprimés :** Remplacement des accès par défaut de NiFi et Airflow par des credentials sécurisés et uniques.
*   **dbt Credentials :** Configuration dynamique du fichier [profiles.yml](file:///C:/Users/admin/Downloads/price_intelligence_FINAL/airflow/jumia_dbt/profiles.yml) via la fonction `env_var()` pour ne pas écrire de chemins en dur.

---

## 📈 Analyses Statistiques & Machine Learning

Les données nettoyées et stockées dans [clean_prices.csv](file:///C:/Users/admin/Downloads/price_intelligence_FINAL/data_analy/data/clean/clean_prices.csv) (2 647 produits) font l'objet d'analyses statistiques et de modélisations poussées dans le notebook [analyse_prix_intelligence.ipynb](file:///C:/Users/admin/Downloads/price_intelligence_FINAL/data_analy/notebooks/analyse_prix_intelligence.ipynb).

### 1. Analyses Statistiques & Inférence (Notebook 15 étapes)
*   **Statistiques Descriptives :** Calcul des moyennes, médianes, écart-types et coefficients de variation des prix croisés par site et par catégorie de produits.
*   **Tests de Normalité :** Test de *Shapiro-Wilk* montrant des distributions non-normales (justifiant l'usage de tests non-paramétriques).
*   **Tests de Comparaison :** Application du test de *Kruskal-Wallis* et du test post-hoc de *Mann-Whitney U* pour confirmer des différences de prix statistiquement significatives entre les trois plateformes.
*   **Intervalles de Confiance :** Calcul d'intervalles de confiance à 95% pour estimer la valeur réelle des prix moyens par enseigne.
*   **Régression Linéaire OLS :** Modélisation OLS (`prix ~ site + categorie + en_promo`) avec un $R^2$ ajusté de 0.19.

### 2. Modélisation Prédictive (Machine Learning)
Entraînement d'un modèle **Random Forest Regressor** (200 estimateurs) après correction stricte du "data leakage" (fuite de données) :
*   **Performance :** $R^2 = 0.48$ et Erreur Moyenne Absolue (MAE) de $\pm 1032$ MAD.
*   **Importance des Features :**
    *   `ancien_prix` et son log : **67.3%**
    *   `site_enc` (l'enseigne du produit) : **13.2%**
    *   `cat_enc` (la catégorie de meuble) : **12.2%**
    *   `remise_pct` (taux de réduction) : **7.2%**
*   Les résultats de la modélisation et l'évaluation sont stockés dans [ml_results.json](file:///C:/Users/admin/Downloads/price_intelligence_FINAL/data_analy/outputs/ml_results.json).

### 3. Vélocité des Prix & Alertes Intelligentes
*   **Vélocité :** Analyse de la tendance des prix sur 30 jours (pente de la droite de régression temporelle).
*   **Anomalies :** Identification des fluctuations extrêmes de prix (> 20% en 1 jour).
*   **Génération d'Alertes :** Journalisation de 100 alertes automatiques (baisses $\le -2\%$ et hausses $\ge +2\%$) stockées dans [alertes.json](file:///C:/Users/admin/Downloads/price_intelligence_FINAL/data_analy/outputs/alertes.json).

### 4. Automatisation des Rapports
*   **Générateur PDF :** Le script [generer_rapport.py](file:///C:/Users/admin/Downloads/price_intelligence_FINAL/data_analy/generer_rapport.py) compile automatiquement les résultats calculés dans [analyse_results.json](file:///C:/Users/admin/Downloads/price_intelligence_FINAL/data_analy/outputs/analyse_results.json) pour générer un rapport PDF professionnel de 7 pages.

---

## 📊 fullstack development

### 1. API Rest (FastAPI)
L'API dans [main.py](file:///C:/Users/admin/Downloads/price_intelligence_FINAL/data_analy/api/main.py) fournit 21 endpoints structurés pour exposer :
*   Les statistiques descriptives (globales, par site, par catégorie).
*   Les résultats des tests d'hypothèses statistiques (Shapiro-Wilk, Kruskal-Wallis, Mann-Whitney).
*   L'analyse de régression et de vélocité des prix.
*   Les alertes intelligentes (hausses/baisses anormales) et les graphiques Plotly sérialisés en JSON.

### 2. Dashboard Streamlit (Analyse Avancée)
Le dashboard dans [app.py](file:///C:/Users/admin/Downloads/price_intelligence_FINAL/data_analy/dashboard/app.py) offre 6 onglets interactifs :
*   **Vue Générale :** Boxplot, prix moyens, KDE des distributions.
*   **Évolution des Prix :** Graphiques temporels sur 30 jours, tendance linéaire.
*   **Tests Statistiques :** Puissance des tests (Power Analysis), régressions OLS, intervalles de confiance à 95%.
*   **Segmentation & Alertes :** Répartition par gamme de prix et journal des alertes de prix.
*   **Explorateur de Données :** Recherche et filtrage avec export CSV.

### 3. Portail Angular de Production
L'application frontend utilise une architecture moderne Angular :
*   **Signals API :** Gestion réactive de l'état sans surcharge mémoire.
*   **Composants Standalone :** Structure légère et modulaire.
*   **Plotly.js :** Rendu fluide et interactif des graphiques scientifiques servis par le backend.
*   **Routage & Authentification :** Passerelle d'accès sécurisée vers le tableau de bord d'analyse.

---

## 🚀 Démarrage Rapide

### 1. Démarrer l'Infrastructure Docker
```bash
docker-compose up -d
```

### 2. Démarrer le Backend (API & Dashboard)
```bash
cd data_analy
pip install -r requirements.txt

# Lancer l'API (Port 8000)
python api/main.py

# Lancer Streamlit (Port 8501)
streamlit run dashboard/app.py
```

### 3. Démarrer le Frontend Angular
```bash
cd frontend
npm install
npm start
# Accéder à http://localhost:4200
```
