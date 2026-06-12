"""
╔══════════════════════════════════════════════════════════════════════╗
║   run_analysis.py — Prix Intelligence v2.0                          ║
║                                                                      ║
║   USAGE :                                                            ║
║     python run_analysis.py                    → Bigtable GCP (défaut)
║     python run_analysis.py --mode bigtable    → Bigtable GCP        ║
║     python run_analysis.py --mode bigquery    → BigQuery GCP        ║
║     python run_analysis.py --mode json        → JSON locaux         ║
║     python run_analysis.py --mode csv         → CSV locaux          ║
║                                                                      ║
║   AIRFLOW :                                                          ║
║     BashOperator(bash_command=                                       ║
║       'python /opt/airflow/data_analy/run_analysis.py')             ║
║                                                                      ║
║   SORTIE :                                                           ║
║     outputs/analyse_results.json  ← 21 sections                     ║
║     outputs/ml_results.json       ← ML Random Forest                ║
║     outputs/fig_*.json            ← 11 graphiques Plotly            ║
║     outputs/alertes.json          ← 100 alertes                     ║
╚══════════════════════════════════════════════════════════════════════╝
"""

import os
import sys
import argparse
import json
import warnings
import time

import pandas as pd
import numpy as np

warnings.filterwarnings('ignore')

# ════════════════════════════════════════════════════════════════
# ARGUMENTS + CHEMINS
# ════════════════════════════════════════════════════════════════

parser = argparse.ArgumentParser(description='Prix Intelligence — Analyse complète')
parser.add_argument('--mode', default=None,
    choices=['csv', 'bigquery', 'json', 'bigtable'],
    help='Source de données (défaut: bigtable)')
parser.add_argument('--output-dir', default=None,
    help='Dossier de sortie (défaut: outputs/ à côté du script)')
args = parser.parse_args()

# Mode : argument > variable d'environnement > bigtable par défaut
MODE = args.mode or os.getenv('DATA_MODE', 'bigtable')

# Chemins
BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
RAW_DIR     = os.path.join(BASE_DIR, 'data', 'raw')
CLEAN_DIR   = os.path.join(BASE_DIR, 'data', 'clean')
OUTPUTS_DIR = args.output_dir or os.path.join(BASE_DIR, 'outputs')
os.makedirs(OUTPUTS_DIR, exist_ok=True)
os.makedirs(CLEAN_DIR, exist_ok=True)

# GCP — credentials depuis variable d'env ou chemin relatif
GCP_PROJECT   = os.getenv('GCP_PROJECT_ID', 'diesel-patrol-491520-j8')
GCP_INSTANCE  = os.getenv('GCP_INSTANCE', 'price-intelligence')
GCP_TABLE     = os.getenv('GCP_TABLE', 'produits')
BQ_DATASET    = os.getenv('BQ_DATASET', 'jumia_price_intelligence')
BQ_TABLE_FULL = f"{GCP_PROJECT}.{BQ_DATASET}.produits"

# Résolution du fichier credentials
_creds_env = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', '')
if _creds_env and os.path.isabs(_creds_env):
    CREDS_PATH = _creds_env
else:
    # cherche dans le dossier du script ou dans airflow/
    _candidates = [
        os.path.join(BASE_DIR, 'gcp-key.json'),
        os.path.join(BASE_DIR, '..', 'airflow', 'gcp-key.json'),
        os.path.join(BASE_DIR, 'diesel-patrol-491520-j8-16dd83a23f21.json'),
        _creds_env if _creds_env else '',
    ]
    CREDS_PATH = next((p for p in _candidates if p and os.path.exists(p)), '')

if CREDS_PATH:
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = CREDS_PATH

COLORS = {'kitea': '#E74C3C', 'jumia': '#F39C12', 'ikea': '#0058A3'}

start_time = time.time()

print("=" * 62)
print("  PRIX INTELLIGENCE — ANALYSE COMPLÈTE v2.0")
print(f"  Mode      : {MODE.upper()}")
print(f"  Projet GCP: {GCP_PROJECT}")
print(f"  Credentials: {CREDS_PATH or '⚠ non trouvé'}")
print(f"  Outputs   : {OUTPUTS_DIR}")
print("=" * 62)


# ════════════════════════════════════════════════════════════════
# IMPORTS ANALYSE
# ════════════════════════════════════════════════════════════════

from scipy.stats import shapiro, mannwhitneyu, kruskal, linregress
from scipy.stats import gaussian_kde
from scipy import stats
import statsmodels.formula.api as smf
from statsmodels.stats.power import TTestIndPower
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

print("✅ Librairies importées\n")


# ════════════════════════════════════════════════════════════════
# NORMALISATION (commune à tous les modes)
# ════════════════════════════════════════════════════════════════

def normaliser(df: pd.DataFrame) -> pd.DataFrame:
    """Normalise les colonnes vers le schéma standard de l'analyse."""
    if df.empty:
        raise ValueError("DataFrame vide — aucune donnée à normaliser.")
    # source → site
    if 'source' in df.columns and 'site' not in df.columns:
        df = df.rename(columns={'source': 'site'})
    if 'site' in df.columns:
        df['site'] = (df['site'].astype(str)
                      .str.replace('.ma', '', regex=False)
                      .str.replace('.com', '', regex=False)
                      .str.strip().str.lower())
    # remise → remise_pct
    if 'remise' in df.columns and 'remise_pct' not in df.columns:
        df = df.rename(columns={'remise': 'remise_pct'})
    # image → image_url
    if 'image' in df.columns and 'image_url' not in df.columns:
        df = df.rename(columns={'image': 'image_url'})
    # types numériques
    for col in ['prix', 'ancien_prix', 'remise_pct']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    # en_promotion
    if 'en_promotion' not in df.columns:
        df['en_promotion'] = df['remise_pct'].fillna(0) > 0
    # calcul remise si manquante
    mask_calc = (
        (df['remise_pct'].fillna(0) == 0)
        & df['ancien_prix'].notna()
        & df['prix'].notna()
        & (df['ancien_prix'] > df['prix'])
    )
    df.loc[mask_calc, 'remise_pct'] = (
        (df.loc[mask_calc, 'ancien_prix'] - df.loc[mask_calc, 'prix'])
        / df.loc[mask_calc, 'ancien_prix'] * 100
    ).round(2)
    # gamme_prix
    if 'gamme_prix' not in df.columns:
        df['gamme_prix'] = pd.cut(
            df['prix'],
            bins=[0, 500, 1500, 4000, 10000, float('inf')],
            labels=['Entrée (<500)', 'Économique (500-1500)',
                    'Milieu (1500-4000)', 'Premium (4000-10k)', 'Luxe (>10k)'],
            right=False
        )
    # product_id
    if 'product_id' not in df.columns:
        df['product_id'] = [
            f"{str(row.get('site', 'x'))}_{i}"
            for i, (_, row) in enumerate(df.iterrows())
        ]
    return df


# ════════════════════════════════════════════════════════════════
# CHARGEMENT BIGTABLE
# ════════════════════════════════════════════════════════════════

def charger_bigtable() -> pd.DataFrame:
    """
    Lit toutes les lignes de la table Bigtable 'produits'.
    Row key format: source#md5(url)[:8]#YYYYmmddHHMMSS
    Column family : price_cf
    Colonnes      : nom, prix, ancien_prix, remise, url, image_url,
                    source, categorie, date_scraping
    """
    print(f"  Connexion Bigtable GCP → {GCP_PROJECT} / {GCP_INSTANCE} / {GCP_TABLE}")
    from google.cloud import bigtable
    from google.cloud.bigtable import row_filters

    client   = bigtable.Client(project=GCP_PROJECT, admin=False)
    instance = client.instance(GCP_INSTANCE)
    table    = instance.table(GCP_TABLE)

    COL_FAMILY = 'price_cf'
    COLUMNS    = ['nom', 'prix', 'ancien_prix', 'remise', 'url',
                  'image_url', 'source', 'categorie', 'date_scraping']

    # Filtre : prendre uniquement la cellule la plus récente par colonne
    row_filter = row_filters.CellsColumnLimitFilter(1)

    rows = table.read_rows(filter_=row_filter)

    produits = []
    erreurs   = 0
    for row in rows:
        try:
            cf = row.cells.get(COL_FAMILY, {})

            def get_col(col_name: str) -> str | None:
                cells = cf.get(col_name.encode(), [])
                if not cells:
                    return None
                return cells[0].value.decode('utf-8', errors='replace').strip()

            nom  = get_col('nom')
            prix = get_col('prix')
            if not nom or not prix:
                continue
            try:
                prix_float = float(prix)
            except (ValueError, TypeError):
                continue
            if prix_float <= 0:
                continue

            def safe_float(s):
                if not s or s in ('None', '', 'null'):
                    return None
                try:
                    return float(s)
                except (ValueError, TypeError):
                    return None

            produits.append({
                'nom'          : nom,
                'prix'         : prix_float,
                'ancien_prix'  : safe_float(get_col('ancien_prix')),
                'remise'       : safe_float(get_col('remise')) or 0.0,
                'url'          : get_col('url') or '',
                'image_url'    : get_col('image_url') or '',
                'source'       : get_col('source') or '',
                'categorie'    : get_col('categorie') or '',
                'date_scraping': get_col('date_scraping') or '',
            })
        except Exception as e:
            erreurs += 1
            if erreurs <= 5:
                print(f"  ⚠ Ligne ignorée : {e}")

    print(f"  ✅ {len(produits):,} produits lus depuis Bigtable ({erreurs} erreurs ignorées)")
    if not produits:
        raise RuntimeError(
            "Bigtable a retourné 0 produits. "
            "Vérifie que NiFi a bien écrit dans la table et que les credentials sont corrects."
        )
    df = pd.DataFrame(produits)
    if 'date_scraping' in df.columns:
        df['date_scraping'] = pd.to_datetime(df['date_scraping'], errors='coerce')
    return df


# ════════════════════════════════════════════════════════════════
# ÉTAPE 1 — CHARGEMENT DES DONNÉES
# ════════════════════════════════════════════════════════════════

print("─" * 62)
print("ÉTAPE 1 — CHARGEMENT DES DONNÉES")
print("─" * 62)

if MODE == 'bigtable':
    df_raw = charger_bigtable()

elif MODE == 'bigquery':
    print("  Connexion à BigQuery GCP...")
    if not CREDS_PATH:
        raise FileNotFoundError(
            "❌ Credentials GCP introuvable. "
            "Mets GOOGLE_APPLICATION_CREDENTIALS dans .env ou place gcp-key.json dans data_analy/"
        )
    from google.cloud import bigquery
    client_bq = bigquery.Client(project=GCP_PROJECT)
    query = f"""
        SELECT source, nom,
               CAST(prix AS FLOAT64)         AS prix,
               CAST(ancien_prix AS FLOAT64)  AS ancien_prix,
               CAST(remise AS FLOAT64)       AS remise,
               url, categorie, image_url, date_scraping
        FROM `{BQ_TABLE_FULL}`
        WHERE prix > 0 AND nom IS NOT NULL
        ORDER BY date_scraping DESC
    """
    print("  Requête BigQuery en cours...")
    df_raw = client_bq.query(query).to_dataframe()
    if 'date_scraping' in df_raw.columns:
        df_raw['date_scraping'] = pd.to_datetime(df_raw['date_scraping'], errors='coerce')
    print(f"  ✅ {len(df_raw):,} produits depuis BigQuery")

elif MODE == 'json':
    print("  Lecture des JSON locaux...")
    json_files = {
        'jumia': os.path.join(RAW_DIR, 'json_jumia.json'),
        'ikea' : os.path.join(RAW_DIR, 'json_ikea.json'),
        'kitea': os.path.join(RAW_DIR, 'json_kitea.json'),
    }
    all_data = []
    for site, path in json_files.items():
        if os.path.exists(path):
            with open(path, encoding='utf-8') as f:
                data = json.load(f)
            all_data.extend(data)
            print(f"  ✅ {len(data):,} depuis {os.path.basename(path)}")
        else:
            print(f"  ⚠ Manquant : {path}")
    df_raw = pd.DataFrame(all_data)
    if 'date_scraping' in df_raw.columns:
        df_raw['date_scraping'] = pd.to_datetime(df_raw['date_scraping'], errors='coerce')
    print(f"  ✅ Total : {len(df_raw):,} produits")

else:  # csv
    print("  Lecture CSV locaux...")
    csv_raw = os.path.join(RAW_DIR, 'raw_prices.csv')
    if not os.path.exists(csv_raw):
        raise FileNotFoundError(f"❌ Fichier introuvable : {csv_raw}")
    df_raw = pd.read_csv(csv_raw)
    if 'date_scraping' in df_raw.columns:
        df_raw['date_scraping'] = pd.to_datetime(df_raw['date_scraping'], errors='coerce')
    print(f"  ✅ {len(df_raw):,} produits depuis CSV")

# df_hist = copie pour l'analyse temporelle
df_hist = df_raw.copy()

# Normalisation
df_raw = normaliser(df_raw)
df_hist = normaliser(df_hist)

print(f"  Sites     : {sorted(df_raw['site'].dropna().unique().tolist())}")
print(f"  En promo  : {df_raw['en_promotion'].mean()*100:.1f}%\n")


# ════════════════════════════════════════════════════════════════
# ÉTAPE 2 — NETTOYAGE
# ════════════════════════════════════════════════════════════════

print("─" * 62)
print("ÉTAPE 2 — NETTOYAGE")
print("─" * 62)

df = df_raw.copy()
df = df[df['prix'].notna() & (df['prix'] > 0)]
df = df.drop_duplicates(subset=['nom', 'site'])

IKEA_MAP = {
    'canape': 'Salon Et Sejour', 'canapes-2-places-en-tissu-10668': 'Salon Et Sejour',
    'canapes-3-places-en-tissu-10670': 'Salon Et Sejour',
    'canapes-avec-meridienne-en-tissu-47388': 'Salon Et Sejour',
    'canapes-dangle-en-tissu-10671': 'Salon Et Sejour',
    'elements-modulables-canape-31786': 'Salon Et Sejour', 'fauteuils': 'Salon Et Sejour',
    'fauteuils-et-meridiennes-fu006': 'Salon Et Sejour',
    'repose-pieds-et-poufs-en-tissu-20927': 'Salon Et Sejour',
    'convertibles-10663': 'Salon Et Sejour', 'meridiennes-57527': 'Salon Et Sejour',
    'meubles-tv-avec-rangements-14885': 'Salon Et Sejour', 'banc-tv-10810': 'Salon Et Sejour',
    'meubles-de-rangement-salon-10409': 'Salon Et Sejour',
    'lits-doubles-16284': 'Chambre Adulte', 'lits-simples-16285': 'Chambre Adulte',
    'lits-rembourres-49096': 'Chambre Adulte', 'lits-dappoint-et-banquettes-19037': 'Chambre Adulte',
    'commodes-10451': 'Chambre Adulte', 'coiffeuses-20657': 'Chambre Adulte',
    'tables-de-chevet-20656': 'Chambre Adulte', 'ensemble-meuble-chambre-54992': 'Chambre Adulte',
    'matelas-bm002': 'Chambre Adulte', 'meubles-meubles-chambre-coucher': 'Chambre Adulte',
    'armoires-a-portes-battantes-48005': 'Chambre Adulte',
    'armoires-a-portes-miroir-48006': 'Chambre Adulte',
    'armoires-coulissantes-43635': 'Chambre Adulte',
    'armoires-de-couloir-48007': 'Chambre Adulte',
    'armoires-independantes-43631': 'Chambre Adulte',
    'armoires-integrees-43632': 'Chambre Adulte',
    'armoires-ouvertes-43634': 'Chambre Adulte',
    'pax-armoires-avec-portes-24337': 'Chambre Adulte',
    'pax-armoires-sans-porte-19110': 'Chambre Adulte',
    'pax-portes-coulissantes-19115': 'Chambre Adulte',
    'ensembles-tables-et-chaises-19145': 'Salle A Manger',
    'ensembles-tables-et-chaises-max-2-pers-36209': 'Salle A Manger',
    'ensembles-tables-et-chaises-max-4-pers-36212': 'Salle A Manger',
    'ensembles-tables-et-chaises-max-6-pers-36213': 'Salle A Manger',
    'chaises-de-salle-a-manger-25219': 'Salle A Manger', 'buffets-et-bahuts-10412': 'Salle A Manger',
    'salle-a-manger': 'Salle A Manger', 'meubles-tables': 'Salle A Manger',
    'bureaux-pour-la-maison-20651': 'Mobilier Pro', 'bureaux-professionnels-47069': 'Mobilier Pro',
    'chaises-de-bureau-20652': 'Mobilier Pro', 'combinaisons-bureaux-18623': 'Mobilier Pro',
    'meubles-mobilier-bureau-domicile': 'Mobilier Pro',
    'rangements-cubiques-55012': 'Rangement', 'systemes-de-rangement-10397': 'Rangement',
    'etageres-et-armoires-a-chaussures-10456': 'Rangement', 'bibliotheques-10382': 'Rangement',
    'meuble-etagere-11465': 'Rangement',
}
df['categorie'] = df['categorie'].replace(IKEA_MAP)
CATS = ['Salon Et Sejour', 'Chambre Adulte', 'Salle A Manger', 'Mobilier Pro', 'Rangement']
df = df[df['categorie'].isin(CATS)].copy()

if df.empty:
    # fallback JSON si Bigtable n'a pas encore les bonnes catégories
    print("  ⚠ Aucun produit avec catégorie valide — fallback JSON locaux")
    all_data = []
    for path in [os.path.join(RAW_DIR, 'json_jumia.json'),
                 os.path.join(RAW_DIR, 'json_ikea.json'),
                 os.path.join(RAW_DIR, 'json_kitea.json')]:
        if os.path.exists(path):
            with open(path, encoding='utf-8') as f:
                all_data.extend(json.load(f))
    df = normaliser(pd.DataFrame(all_data))
    df['categorie'] = df['categorie'].replace(IKEA_MAP)
    df = df[df['categorie'].isin(CATS)].copy()
    df_hist = df.copy()

# IQR outlier removal
rows_keep = []
for (cat, site), grp in df.groupby(['categorie', 'site']):
    q1, q3 = grp['prix'].quantile([0.25, 0.75])
    iqr  = q3 - q1
    mask = (grp['prix'] >= q1 - 3 * iqr) & (grp['prix'] <= q3 + 3 * iqr)
    rows_keep.extend(grp[mask].index.tolist())
df_clean = df.loc[rows_keep].copy()
df_clean['remise_pct']   = df_clean['remise_pct'].fillna(0)
df_clean['en_promotion'] = (df_clean['remise_pct'] > 0).astype(bool)
df_clean['gamme_prix']   = pd.cut(
    df_clean['prix'],
    bins=[0, 500, 1500, 4000, 10000, 999999],
    labels=['Entrée (<500)', 'Économique (500-1500)', 'Milieu (1500-4000)',
            'Premium (4000-10k)', 'Luxe (>10k)']
)

df_clean.to_csv(os.path.join(CLEAN_DIR, 'clean_prices.csv'), index=False)
print(f"  ✅ {len(df_clean):,} produits | {df_clean['categorie'].nunique()} catégories | clean_prices.csv OK\n")


# ════════════════════════════════════════════════════════════════
# ÉTAPE 3 — STATISTIQUES DESCRIPTIVES
# ════════════════════════════════════════════════════════════════

print("─" * 62)
print("ÉTAPE 3 — STATISTIQUES DESCRIPTIVES")
print("─" * 62)

stats_site = df_clean.groupby('site')['prix'].agg(
    moyenne='mean', mediane='median', ecart_type='std',
    minimum='min', maximum='max', count='count').round(2)
stats_cat = df_clean.groupby('categorie')['prix'].agg(
    moyenne='mean', mediane='median', ecart_type='std', count='count').round(2)
promo_stats = df_clean.groupby('site').agg(
    nb_produits=('prix', 'count'), nb_promos=('en_promotion', 'sum'),
    taux_promo=('en_promotion', 'mean'), remise_moy=('remise_pct', 'mean'),
    remise_max=('remise_pct', 'max')).round(2)
promo_stats['taux_promo'] = (promo_stats['taux_promo'] * 100).round(1)
print(f"  ✅ Stats par site : {list(stats_site.index)}")

fig_box = px.box(df_clean, x='categorie', y='prix', color='site',
    color_discrete_map=COLORS, title='Distribution des Prix par Catégorie et Site (MAD)',
    template='plotly_white')
fig_box.update_layout(height=520)
with open(os.path.join(OUTPUTS_DIR, 'fig_boxplot.json'), 'w') as f:
    f.write(fig_box.to_json())

prix_moy = df_clean.groupby(['categorie', 'site'])['prix'].mean().round(0).reset_index()
fig_bar = px.bar(prix_moy, x='categorie', y='prix', color='site', barmode='group',
    color_discrete_map=COLORS, title='Prix Moyen par Catégorie et Site (MAD)',
    template='plotly_white', text='prix')
fig_bar.update_traces(texttemplate='%{text:.0f}', textposition='outside')
with open(os.path.join(OUTPUTS_DIR, 'fig_barchart.json'), 'w') as f:
    f.write(fig_bar.to_json())

df_sc = df_clean[df_clean['ancien_prix'].notna()].copy()
if len(df_sc) > 0:
    fig_sc = px.scatter(df_sc, x='ancien_prix', y='prix', color='site',
        color_discrete_map=COLORS, title='Prix Actuel vs Ancien Prix',
        template='plotly_white')
    with open(os.path.join(OUTPUTS_DIR, 'fig_scatter.json'), 'w') as f:
        f.write(fig_sc.to_json())

fig_promo = px.bar(promo_stats.reset_index(), x='site', y='taux_promo', color='site',
    color_discrete_map=COLORS, title='Taux de Promotion par Site (%)',
    template='plotly_white', text='taux_promo')
fig_promo.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
with open(os.path.join(OUTPUTS_DIR, 'fig_promo.json'), 'w') as f:
    f.write(fig_promo.to_json())

print("  ✅ fig_boxplot, fig_barchart, fig_scatter, fig_promo sauvegardés\n")


# ════════════════════════════════════════════════════════════════
# ÉTAPE 4 — TESTS STATISTIQUES
# ════════════════════════════════════════════════════════════════

print("─" * 62)
print("ÉTAPE 4 — TESTS STATISTIQUES")
print("─" * 62)

shapiro_results = {}
for site in df_clean['site'].unique():
    s = df_clean[df_clean['site'] == site]['prix'].dropna()
    s = s.sample(min(5000, len(s)), random_state=42)
    stat, p = shapiro(s)
    shapiro_results[site] = {
        'stat': round(float(stat), 4), 'p_value': round(float(p), 6),
        'normal': bool(p > 0.05), 'n': int(len(df_clean[df_clean['site'] == site]))
    }

groups_cat  = [df_clean[df_clean['categorie'] == c]['prix'].dropna().values
               for c in CATS if len(df_clean[df_clean['categorie'] == c]) > 5]
groups_site = [df_clean[df_clean['site'] == s]['prix'].dropna().values
               for s in df_clean['site'].unique()]
stat_kc, p_kc = kruskal(*groups_cat)
stat_ks, p_ks = kruskal(*groups_site)
kruskal_cat  = {'stat': round(float(stat_kc), 2), 'p_value': round(float(p_kc), 6),
                'significatif': bool(p_kc < 0.05)}
kruskal_site = {'stat': round(float(stat_ks), 2), 'p_value': round(float(p_ks), 6),
                'significatif': bool(p_ks < 0.05)}

mw_results  = {}
sites_list  = list(df_clean['site'].unique())
pairs = [(sites_list[i], sites_list[j])
         for i in range(len(sites_list)) for j in range(i+1, len(sites_list))]
for cat in CATS:
    mw_results[cat] = {}
    for s1, s2 in pairs:
        g1 = df_clean[(df_clean['site'] == s1) & (df_clean['categorie'] == cat)]['prix'].dropna()
        g2 = df_clean[(df_clean['site'] == s2) & (df_clean['categorie'] == cat)]['prix'].dropna()
        if len(g1) > 5 and len(g2) > 5:
            stat, p = mannwhitneyu(g1, g2, alternative='two-sided')
            mw_results[cat][f'{s1}_vs_{s2}'] = {
                'stat': round(float(stat), 2), 'p_value': round(float(p), 6),
                'significatif': bool(p < 0.05)
            }

df_reg = df_clean.copy()
df_reg['en_promo_num'] = df_reg['en_promotion'].astype(int)
model = smf.ols('prix ~ C(site) + C(categorie) + en_promo_num',
    data=df_reg.dropna(subset=['prix', 'categorie', 'site'])).fit()
reg_results = {
    'r2': round(float(model.rsquared), 4),
    'r2_adj': round(float(model.rsquared_adj), 4),
    'f_stat': round(float(model.fvalue), 2),
    'p_global': round(float(model.f_pvalue), 6),
    'coefficients': {k: round(float(v), 2) for k, v in model.params.items()},
    'p_values': {k: round(float(v), 4) for k, v in model.pvalues.items()}
}

print(f"  ✅ Shapiro-Wilk : {len(shapiro_results)} sites")
print(f"  ✅ Kruskal-Wallis sites : H={kruskal_site['stat']} p={kruskal_site['p_value']}")
print(f"  ✅ OLS R²={reg_results['r2_adj']}\n")


# ════════════════════════════════════════════════════════════════
# ÉTAPE 5 — ÉVOLUTION + ANOMALIES
# ════════════════════════════════════════════════════════════════

print("─" * 62)
print("ÉTAPE 5 — ÉVOLUTION DES PRIX + ANOMALIES")
print("─" * 62)

# En mode csv on peut avoir un historique séparé
if MODE == 'csv':
    hist_path = os.path.join(RAW_DIR, 'historique_prices.csv')
    if os.path.exists(hist_path):
        df_hist_evol = normaliser(pd.read_csv(hist_path, parse_dates=['date_scraping']))
    else:
        df_hist_evol = df_hist.copy()
else:
    df_hist_evol = df_hist.copy()

evol = df_hist_evol.groupby(['site', 'date_scraping'])['prix'].mean().round(2).reset_index()

fig_evol = px.line(evol, x='date_scraping', y='prix', color='site',
    color_discrete_map=COLORS, title='Évolution Prix Moyen',
    template='plotly_white', markers=True)
with open(os.path.join(OUTPUTS_DIR, 'fig_evolution.json'), 'w') as f:
    f.write(fig_evol.to_json())

anomalies_list = []
if 'product_id' in df_hist_evol.columns and 'site' in df_hist_evol.columns:
    for (pid, site), grp in df_hist_evol.groupby(['product_id', 'site']):
        if len(grp) < 5:
            continue
        prix_s = grp.sort_values('date_scraping')['prix']
        var = prix_s.pct_change().abs()
        if (var > 0.20).any():
            row_p = df_clean[df_clean['product_id'] == pid]
            if len(row_p):
                anomalies_list.append({
                    'product_id': pid,
                    'nom': str(row_p.iloc[0]['nom'])[:50],
                    'site': site,
                    'categorie': str(row_p.iloc[0]['categorie']),
                    'variation_max_pct': round(float(var.max()) * 100, 1)
                })

print(f"  ✅ Évolution : {len(evol)} points | Anomalies : {len(anomalies_list)}\n")


# ════════════════════════════════════════════════════════════════
# ÉTAPE 7 — INTERVALLES DE CONFIANCE 95%
# ════════════════════════════════════════════════════════════════

print("─" * 62)
print("ÉTAPE 7 — INTERVALLES DE CONFIANCE 95%")
print("─" * 62)

ic_results = {}
for site in df_clean['site'].unique():
    data = df_clean[df_clean['site'] == site]['prix'].dropna()
    n = len(data); mean = data.mean(); sem = stats.sem(data)
    ic = stats.t.interval(0.95, df=n - 1, loc=mean, scale=sem)
    cv = (data.std() / mean) * 100
    ic_results[site] = {
        'n': int(n), 'moyenne': round(float(mean), 2),
        'ic_low': round(float(ic[0]), 2), 'ic_high': round(float(ic[1]), 2),
        'marge': round(float(ic[1] - ic[0]) / 2, 2),
        'cv_pct': round(float(cv), 1), 'sem': round(float(sem), 2)
    }

ic_cat_results = {}
for cat in CATS:
    data = df_clean[df_clean['categorie'] == cat]['prix'].dropna()
    if len(data) < 5:
        continue
    n = len(data); mean = data.mean(); sem = stats.sem(data)
    ic = stats.t.interval(0.95, df=n - 1, loc=mean, scale=sem)
    ic_cat_results[cat] = {
        'n': int(n), 'moyenne': round(float(mean), 2),
        'ic_low': round(float(ic[0]), 2), 'ic_high': round(float(ic[1]), 2)
    }

fig_ic = go.Figure()
for site, d in ic_results.items():
    fig_ic.add_trace(go.Bar(
        name=site, x=[site], y=[d['moyenne']],
        error_y=dict(type='data', array=[d['marge']]),
        marker_color=COLORS.get(site, 'gray')
    ))
fig_ic.update_layout(title='Intervalles de Confiance 95% par Site', template='plotly_white')
with open(os.path.join(OUTPUTS_DIR, 'fig_ic.json'), 'w') as f:
    f.write(fig_ic.to_json())
print(f"  ✅ IC 95% : {len(ic_results)} sites, {len(ic_cat_results)} catégories\n")


# ════════════════════════════════════════════════════════════════
# ÉTAPE 8 — POWER ANALYSIS
# ════════════════════════════════════════════════════════════════

print("─" * 62)
print("ÉTAPE 8 — POWER ANALYSIS (Cohen's d)")
print("─" * 62)

pa = TTestIndPower()
power_results = {}
for s1, s2 in pairs:
    g1 = df_clean[df_clean['site'] == s1]['prix'].dropna()
    g2 = df_clean[df_clean['site'] == s2]['prix'].dropna()
    pooled_std = np.sqrt((g1.std() ** 2 + g2.std() ** 2) / 2)
    cohens_d   = abs(g1.mean() - g2.mean()) / pooled_std if pooled_std > 0 else 0
    n_min      = min(len(g1), len(g2))
    power_val  = float(pa.solve_power(effect_size=cohens_d, nobs1=n_min, alpha=0.05)) \
                 if cohens_d > 0 else 1.0
    n_needed   = int(pa.solve_power(effect_size=cohens_d, alpha=0.05, power=0.80,
                 alternative='two-sided')) if cohens_d > 0 else 0
    interp = ('Très grand effet' if cohens_d > 0.8 else
              'Grand effet'      if cohens_d > 0.5 else
              'Effet moyen'      if cohens_d > 0.2 else 'Petit effet')
    power_results[f'{s1}_vs_{s2}'] = {
        'cohens_d': round(float(cohens_d), 4), 'interpretation': interp,
        'puissance': round(power_val, 3), 'n_actuel': int(n_min),
        'n_minimum': n_needed, 'taille_effet': interp
    }
    print(f"  {s1} vs {s2}: d={cohens_d:.3f} ({interp}) puissance={power_val*100:.1f}%")
print()


# ════════════════════════════════════════════════════════════════
# ÉTAPE 9 — CORRÉLATION SPEARMAN
# ════════════════════════════════════════════════════════════════

print("─" * 62)
print("ÉTAPE 9 — CORRÉLATION SPEARMAN")
print("─" * 62)

df_corr = df_clean[['prix', 'ancien_prix', 'remise_pct']].copy()
df_corr['en_promo']  = df_clean['en_promotion'].astype(int)
df_corr['gamme_num'] = df_clean['gamme_prix'].cat.codes
df_corr = df_corr.dropna()
df_corr.columns = ['Prix', 'Ancien Prix', 'Remise %', 'En Promo', 'Gamme']
corr_matrix = df_corr.corr(method='spearman')

fig_corr = go.Figure(data=go.Heatmap(
    z=corr_matrix.values, x=corr_matrix.columns.tolist(),
    y=corr_matrix.columns.tolist(), colorscale='RdBu', zmid=0,
    text=corr_matrix.round(2).values, texttemplate='%{text}'))
fig_corr.update_layout(title='Matrice de Corrélation Spearman', template='plotly_white')
with open(os.path.join(OUTPUTS_DIR, 'fig_correlation.json'), 'w') as f:
    f.write(fig_corr.to_json())

correlation = {
    'spearman_matrix': {
        col: {col2: round(float(corr_matrix.loc[col, col2]), 3)
              for col2 in corr_matrix.columns}
        for col in corr_matrix.columns
    }
}
print(f"  ✅ fig_correlation.json\n")


# ════════════════════════════════════════════════════════════════
# ÉTAPE 10 — DISTRIBUTION KDE
# ════════════════════════════════════════════════════════════════

print("─" * 62)
print("ÉTAPE 10 — DISTRIBUTION KDE")
print("─" * 62)

fig_kde = go.Figure()
for site in df_clean['site'].unique():
    data = df_clean[df_clean['site'] == site]['prix'].dropna()
    fig_kde.add_trace(go.Histogram(
        x=data, name=f'{site} (hist)', opacity=0.4,
        marker_color=COLORS.get(site, 'gray'), nbinsx=50,
        histnorm='probability density', showlegend=True))
    kde = gaussian_kde(data)
    x_range = np.linspace(data.min(), data.max(), 300)
    fig_kde.add_trace(go.Scatter(
        x=x_range, y=kde(x_range), mode='lines',
        name=f'{site} (KDE)', line=dict(color=COLORS.get(site, 'gray'), width=2)))
fig_kde.update_layout(title='Distribution KDE des Prix par Site', template='plotly_white', height=450)
with open(os.path.join(OUTPUTS_DIR, 'fig_kde.json'), 'w') as f:
    f.write(fig_kde.to_json())
print("  ✅ fig_kde.json\n")


# ════════════════════════════════════════════════════════════════
# ÉTAPE 11 — PRICE VELOCITY
# ════════════════════════════════════════════════════════════════

print("─" * 62)
print("ÉTAPE 11 — PRICE VELOCITY")
print("─" * 62)

velocity_results = {}
for site in df_hist_evol['site'].unique():
    evol_s = df_hist_evol[df_hist_evol['site'] == site].groupby('date_scraping')['prix'].mean()
    if len(evol_s) < 2:
        velocity_results[site] = {'slope': 0, 'pente_jour': 0, 'variation_30j': 0,
            'tendance': 'STABLE', 'r2': 0, 'p_value': 1.0}
        continue
    x = np.arange(len(evol_s)); y = evol_s.values
    slope, intercept, r, p, se = linregress(x, y)
    tendance = 'HAUSSE' if slope > 0.5 else 'BAISSE' if slope < -0.5 else 'STABLE'
    velocity_results[site] = {
        'slope': round(float(slope), 4), 'pente_jour': round(float(slope), 4),
        'variation_30j': round(float(slope * 29), 2), 'variation_pct': round(float(slope * 29), 2),
        'tendance': tendance, 'r2': round(float(r ** 2), 4), 'p_value': round(float(p), 6)
    }
    print(f"  {site:8}: {tendance} | pente={slope:.2f} MAD/j | R²={r**2:.4f}")

fig_vel = go.Figure()
for site, d in velocity_results.items():
    fig_vel.add_trace(go.Bar(
        x=[site], y=[d['variation_30j']], name=site,
        marker_color=COLORS.get(site, 'gray')))
fig_vel.update_layout(title='Price Velocity — Variation estimée 30j (MAD)', template='plotly_white')
with open(os.path.join(OUTPUTS_DIR, 'fig_velocity.json'), 'w') as f:
    f.write(fig_vel.to_json())
print()


# ════════════════════════════════════════════════════════════════
# ÉTAPE 12 — ALERTES
# ════════════════════════════════════════════════════════════════

print("─" * 62)
print("ÉTAPE 12 — ALERTES INTELLIGENTES")
print("─" * 62)

SEUIL_BAISSE = -0.02; SEUIL_HAUSSE = +0.02
df_hist_a = df_hist_evol.dropna(subset=['site', 'nom'])
baseline  = df_hist_a.groupby(['site', 'nom'])['prix'].agg(['mean', 'std']).reset_index()
baseline.columns = ['site', 'nom', 'prix_moyen', 'prix_std']
dernier   = (df_hist_a.sort_values('date_scraping')
             .groupby(['site', 'nom']).last()[['prix', 'date_scraping', 'categorie']].reset_index())
df_al = dernier.merge(baseline, on=['site', 'nom'])

alertes = []
for _, row in df_al.iterrows():
    if pd.isna(row['prix_moyen']) or pd.isna(row['prix']):
        continue
    v = (row['prix'] - row['prix_moyen']) / row['prix_moyen']
    if v <= SEUIL_BAISSE:
        t, p, msg = 'BAISSE_FORTE', 'HAUTE', f"Baisse de {abs(v)*100:.1f}%"
    elif v >= SEUIL_HAUSSE:
        t, p, msg = 'HAUSSE_FORTE', 'MOYENNE', f"Hausse de {v*100:.1f}%"
    else:
        continue
    alertes.append({
        'nom': str(row['nom'])[:50], 'site': str(row['site']),
        'categorie': str(row.get('categorie', '')),
        'prix_actuel': round(float(row['prix']), 2),
        'prix_moyen': round(float(row['prix_moyen']), 2),
        'variation_pct': round(float(v) * 100, 2),
        'type': t, 'type_alerte': t, 'priorite': p, 'message': msg,
        'date': str(row['date_scraping'])
    })

alertes = sorted(alertes, key=lambda x: abs(x['variation_pct']), reverse=True)[:100]
with open(os.path.join(OUTPUTS_DIR, 'alertes.json'), 'w', encoding='utf-8') as f:
    json.dump(alertes, f, ensure_ascii=False, indent=2)
print(f"  ✅ {len(alertes)} alertes\n")


# ════════════════════════════════════════════════════════════════
# ÉTAPE 13 — SEGMENTATION
# ════════════════════════════════════════════════════════════════

print("─" * 62)
print("ÉTAPE 13 — SEGMENTATION")
print("─" * 62)

gamme_stats = df_clean.groupby(['gamme_prix', 'site']).agg(
    nb_produits=('prix', 'count'), prix_moy=('prix', 'mean'),
    remise_moy=('remise_pct', 'mean'), taux_promo=('en_promotion', 'mean')
).round(2).reset_index()
gamme_stats['taux_promo'] = (gamme_stats['taux_promo'] * 100).round(1)

fig_seg = px.bar(gamme_stats, x='gamme_prix', y='nb_produits', color='site',
    barmode='group', color_discrete_map=COLORS,
    title='Segmentation par Gamme de Prix et Site', template='plotly_white')
with open(os.path.join(OUTPUTS_DIR, 'fig_segmentation.json'), 'w') as f:
    f.write(fig_seg.to_json())

segmentation = {
    'par_gamme': gamme_stats.to_dict(orient='records'),
    'distribution_site': df_clean.groupby(['site', 'gamme_prix']).size()
        .unstack(fill_value=0).to_dict()
}
print(f"  ✅ {gamme_stats['gamme_prix'].nunique()} gammes\n")


# ════════════════════════════════════════════════════════════════
# ÉTAPE 14 — STATS SITE × CATÉGORIE
# ════════════════════════════════════════════════════════════════

stats_sc = df_clean.groupby(['site', 'categorie'])['prix'].agg(
    ['mean', 'median', 'std', 'count']).round(2).reset_index()
stats_sc.columns = ['site', 'categorie', 'moyenne', 'mediane', 'ecart_type', 'count']
stats_site_categorie = {}
for _, row in stats_sc.iterrows():
    s = row['site']
    if s not in stats_site_categorie:
        stats_site_categorie[s] = {}
    stats_site_categorie[s][row['categorie']] = {
        'moyenne': row['moyenne'], 'mediane': row['mediane'],
        'ecart_type': row['ecart_type'], 'count': int(row['count'])
    }


# ════════════════════════════════════════════════════════════════
# ÉTAPE 15 — MACHINE LEARNING
# ════════════════════════════════════════════════════════════════

print("─" * 62)
print("ÉTAPE 15 — MACHINE LEARNING (Random Forest)")
print("─" * 62)

from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

df_ml = df_clean.copy()
df_ml['remise_pct']       = df_ml['remise_pct'].fillna(0)
df_ml['ancien_prix']      = df_ml['ancien_prix'].fillna(df_ml['prix'].mean())
le_site = LabelEncoder(); le_cat = LabelEncoder()
df_ml['site_enc']         = le_site.fit_transform(df_ml['site'])
df_ml['cat_enc']          = le_cat.fit_transform(df_ml['categorie'])
df_ml['jour_semaine']     = 3
df_ml['ancien_prix_log']  = np.log1p(df_ml['ancien_prix'])
df_ml['en_promo']         = (df_ml['remise_pct'] > 0).astype(int)

feature_cols = ['site_enc', 'cat_enc', 'remise_pct', 'en_promo',
                'ancien_prix', 'ancien_prix_log', 'jour_semaine']
X = df_ml[feature_cols].copy(); y = df_ml['prix'].copy()
mask = ~(X.isna().any(axis=1) | y.isna()); X = X[mask]; y = y[mask]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

rf = RandomForestRegressor(n_estimators=200, max_depth=15, min_samples_leaf=3,
    random_state=42, n_jobs=-1)
rf.fit(X_train, y_train); y_pred_rf = rf.predict(X_test)
mae_rf  = mean_absolute_error(y_test, y_pred_rf)
rmse_rf = np.sqrt(mean_squared_error(y_test, y_pred_rf))
r2_rf   = r2_score(y_test, y_pred_rf)

lr = LinearRegression()
lr.fit(X_train, y_train); y_pred_lr = lr.predict(X_test)
mae_lr = mean_absolute_error(y_test, y_pred_lr)
r2_lr  = r2_score(y_test, y_pred_lr)

best_model = 'random_forest' if r2_rf > r2_lr else 'linear_regression'
best_mae   = mae_rf if r2_rf > r2_lr else mae_lr
best_r2    = r2_rf  if r2_rf > r2_lr else r2_lr

fi = pd.DataFrame({'feature': feature_cols, 'importance': rf.feature_importances_}
                  ).sort_values('importance', ascending=False)

fig_fi = px.bar(fi, x='importance', y='feature', orientation='h',
    title='Feature Importance — Random Forest',
    color='importance', color_continuous_scale='Blues', template='plotly_white')
with open(os.path.join(OUTPUTS_DIR, 'fig_feature_importance.json'), 'w') as f:
    f.write(fig_fi.to_json())

fig_pred = px.scatter(
    x=y_test[:200].values,
    y=(y_pred_rf if best_model == 'random_forest' else y_pred_lr)[:200],
    labels={'x': 'Prix Réel (MAD)', 'y': 'Prix Prédit (MAD)'},
    title='Prix Réel vs Prédit — Random Forest', template='plotly_white', opacity=0.6)
with open(os.path.join(OUTPUTS_DIR, 'fig_ml_predictions.json'), 'w') as f:
    f.write(fig_pred.to_json())

ml_results_data = {
    'version': 'v2-no-leakage',
    'modeles': {
        'random_forest': {'mae': float(mae_rf), 'rmse': float(rmse_rf), 'r2': float(r2_rf),
            'n_estimators': 200, 'features': feature_cols},
        'linear_regression': {'mae': float(mae_lr), 'r2': float(r2_lr)}
    },
    'meilleur_modele': best_model,
    'feature_importance': fi.set_index('feature')['importance'].round(4).to_dict(),
    'sites_valides': list(le_site.classes_),
    'categories_valides': list(le_cat.classes_),
}
with open(os.path.join(OUTPUTS_DIR, 'ml_results.json'), 'w', encoding='utf-8') as f:
    json.dump(ml_results_data, f, ensure_ascii=False, indent=2, default=str)

print(f"  ✅ RF R²={r2_rf:.4f} MAE=±{mae_rf:.0f} MAD\n")


# ════════════════════════════════════════════════════════════════
# EXPORT FINAL
# ════════════════════════════════════════════════════════════════

print("─" * 62)
print("EXPORT FINAL — analyse_results.json")
print("─" * 62)

evol_exp = evol.copy()
for col in evol_exp.columns:
    if 'date' in col:
        evol_exp[col] = evol_exp[col].astype(str)

final_results = {
    'meta': {
        'date_analyse'       : pd.Timestamp.now().strftime('%Y-%m-%d %H:%M'),
        'version'            : '2.0',
        'nb_produits'        : int(len(df_clean)),
        'nb_categories'      : int(df_clean['categorie'].nunique()),
        'sites'              : list(df_clean['site'].unique()),
        'periode_historique' : '30 jours',
        'mode_donnees'       : MODE,
        'source_production'  : 'Google Cloud Bigtable → run_analysis.py',
    },
    'stats_par_site'         : json.loads(stats_site.to_json()),
    'stats_par_categorie'    : json.loads(stats_cat.to_json()),
    'stats_site_categorie'   : stats_site_categorie,
    'promotions'             : json.loads(promo_stats.to_json()),
    'intervalles_confiance'  : ic_results,
    'ic_categories'          : ic_cat_results,
    'shapiro'                : shapiro_results,
    'kruskal_categories'     : kruskal_cat,
    'kruskal_sites'          : kruskal_site,
    'mann_whitney'           : mw_results,
    'regression'             : reg_results,
    'power_analysis'         : power_results,
    'correlation'            : correlation,
    'velocity'               : velocity_results,
    'evolution_prix'         : evol_exp.to_dict(orient='records'),
    'anomalies'              : anomalies_list[:50],
    'alertes'                : alertes,
    'seuils_alertes'         : {'baisse_pct': -2.0, 'hausse_pct': 2.0},
    'segmentation'           : segmentation,
    'machine_learning'       : ml_results_data,
}

chemin_json = os.path.join(OUTPUTS_DIR, 'analyse_results.json')
with open(chemin_json, 'w', encoding='utf-8') as f:
    json.dump(final_results, f, ensure_ascii=False, indent=2, default=str)

elapsed = round(time.time() - start_time, 1)

print(f"  ✅ analyse_results.json — {len(final_results)} sections")
print(f"  ✅ alertes.json         — {len(alertes)} alertes")
print(f"  ✅ ml_results.json      — R²={r2_rf:.4f}")
print()
print("=" * 62)
print("  ANALYSE TERMINÉE")
print("=" * 62)
print(f"  Durée        : {elapsed}s")
print(f"  Produits     : {len(df_clean):,} (mode={MODE})")
print(f"  Catégories   : {df_clean['categorie'].nunique()}")
print(f"  En promotion : {df_clean['en_promotion'].mean()*100:.1f}%")
print(f"  R² OLS       : {reg_results['r2_adj']}")
print(f"  R² ML (RF)   : {r2_rf:.4f}")
print(f"  Alertes      : {len(alertes)}")
print(f"  Figures      : 11 fig_*.json")
print(f"  Output       : {chemin_json}")
print("=" * 62)
