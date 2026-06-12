"""
Fixtures partagées pour tous les tests pytest
"""
import pytest
import pandas as pd
import numpy as np
import json
import os
import sys

# Ajouter le chemin du projet
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.join(BASE_DIR, 'api'))

CSV_CLEAN   = os.path.join(BASE_DIR, 'data', 'clean', 'clean_prices.csv')
CSV_RAW     = os.path.join(BASE_DIR, 'data', 'raw', 'raw_prices.csv')
CSV_HIST    = os.path.join(BASE_DIR, 'data', 'raw', 'historique_prices.csv')
JSON_RESULT = os.path.join(BASE_DIR, 'outputs', 'analyse_results.json')

# ─────────────────────────────────────────────────────────────────────────────
# DATA_MODE : csv (défaut) | bigquery | json
#
# En mode bigquery/json, le notebook lit depuis GCP et regénère le JSON avec
# des volumes différents (ex: 177 655 produits BigQuery vs 2 839 CSV local).
# Les tests qui comparent nb_produits JSON ↔ nb_lignes CSV échoueraient car
# ils comparent deux sources différentes.
#
# Solution : en mode bigquery/json, la fixture df_clean lit nb_produits
# directement depuis le JSON (source de vérité = ce que le notebook a produit).
# ─────────────────────────────────────────────────────────────────────────────
DATA_MODE = os.environ.get('DATA_MODE', 'csv').lower()


@pytest.fixture(scope='session')
def data_mode():
    """Retourne le mode actif : 'csv', 'bigquery' ou 'json'"""
    return DATA_MODE


@pytest.fixture(scope='session')
def df_clean():
    """
    DataFrame des données nettoyées.

    - Mode csv     → lit data/clean/clean_prices.csv  (comportement historique)
    - Mode bigquery/json → lit quand même le CSV local pour les tests de qualité
      (structure, colonnes, types), mais la fixture nb_produits_attendu
      sera tirée du JSON pour le test de cohérence.
    """
    df = pd.read_csv(CSV_CLEAN)
    for col in ['prix', 'ancien_prix', 'remise_pct']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df['en_promotion'] = df['en_promotion'].fillna(False).astype(bool)
    return df


@pytest.fixture(scope='session')
def df_hist():
    """DataFrame de l'historique 30 jours"""
    return pd.read_csv(CSV_HIST, parse_dates=['date_scraping'])


@pytest.fixture(scope='session')
def results_json():
    """Résultats JSON de l'analyse — source de vérité produite par le notebook"""
    with open(JSON_RESULT, encoding='utf-8') as f:
        return json.load(f)


@pytest.fixture(scope='session')
def nb_produits_attendu(results_json, df_clean):
    """
    Nombre de produits de référence selon le mode actif.

    - Mode csv     → len(df_clean) depuis le CSV local
    - Mode bigquery/json → results_json['meta']['nb_produits']
      (le notebook a analysé des données venant de BigQuery/JSON,
       pas du CSV local — comparer les deux n'aurait aucun sens)
    """
    if DATA_MODE in ('bigquery', 'json'):
        # Source de vérité = ce que le notebook a réellement analysé
        return results_json.get('meta', {}).get('nb_produits', len(df_clean))
    else:
        # Mode CSV : les deux doivent être synchronisés
        return len(df_clean)


@pytest.fixture(scope='session')
def sites():
    return ['ikea', 'jumia', 'kitea']


@pytest.fixture(scope='session')
def categories():
    return [
        'Salon Et Sejour', 'Chambre Adulte',
        'Salle A Manger', 'Mobilier Pro', 'Rangement'
    ]
