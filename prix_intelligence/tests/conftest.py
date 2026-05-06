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

@pytest.fixture(scope='session')
def df_clean():
    """DataFrame des données nettoyées"""
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
    """Résultats JSON de l'analyse"""
    with open(JSON_RESULT, encoding='utf-8') as f:
        return json.load(f)

@pytest.fixture(scope='session')
def sites():
    return ['ikea', 'jumia', 'kitea']

@pytest.fixture(scope='session')
def categories():
    return [
        'Salon Et Sejour', 'Chambre Adulte',
        'Salle A Manger', 'Mobilier Pro', 'Rangement'
    ]
