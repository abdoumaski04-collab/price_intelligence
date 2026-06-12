"""
API FastAPI — Price Intelligence (Kitea + Jumia + Ikea)
Data Analyst : livraison des résultats au Fullstack
"""
import json
import os
import logging
from datetime import datetime
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# ==========================================
# 🔑 Chargement des variables d'environnement
# ==========================================
load_dotenv()

# ==========================================
# 📋 Audit Logging
# ==========================================
logging.basicConfig(
    filename="audit.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Prix Intelligence API",
    description="Analyse des prix Kitea, Jumia et Ikea — Maroc",
    version="2.0.0"
)

# ==========================================
# 🌐 CORS — restreint à Angular uniquement
# ==========================================
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:4200").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["GET"],
    allow_headers=["*"],
)

# ==========================================
# 📋 Middleware — Audit log chaque requête
# ==========================================
@app.middleware("http")
async def audit_middleware(request: Request, call_next):
    start = datetime.now()
    response = await call_next(request)
    duration = (datetime.now() - start).total_seconds()
    logger.info(
        f"IP={request.client.host} | "
        f"METHOD={request.method} | "
        f"URL={request.url.path} | "
        f"STATUS={response.status_code} | "
        f"DURATION={duration:.3f}s"
    )
    return response

OUTPUT_DIR   = os.path.join(os.path.dirname(__file__), '..', 'outputs')
RESULTS_PATH = os.path.join(OUTPUT_DIR, 'analyse_results.json')

def load_results() -> dict:
    """Lit analyse_results.json depuis le disque à chaque appel."""
    try:
        with open(RESULTS_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        raise HTTPException(
            status_code=503,
            detail=f"Fichier analyse_results.json introuvable dans {OUTPUT_DIR}. "
                   "Lance le notebook d'abord."
        )
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Erreur de parsing JSON : {e}")

try:
    _check = load_results()
    print(f"✅ analyse_results.json chargé — {len(_check)} sections")
    print(f"   Clés : {', '.join(_check.keys())}")
except Exception as e:
    print(f"⚠️  Avertissement au démarrage : {e}")

# ==========================================
# 🔑 Configuration GCP & Résolution Credentials
# ==========================================
DATA_MODE = os.getenv("DATA_MODE", "csv").lower()
PROJECT_ID = os.getenv("GCP_PROJECT_ID", "diesel-patrol-491520-j8")
TABLE_REF = f"{PROJECT_ID}.jumia_price_intelligence.produits"

# Résolution du fichier credentials
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
_creds_env = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")

if _creds_env and os.path.isabs(_creds_env) and os.path.exists(_creds_env):
    CREDS_PATH = _creds_env
else:
    _candidates = [
        os.path.join(BASE_DIR, '..', 'gcp-key.json'),
        os.path.join(BASE_DIR, '..', '..', 'airflow', 'gcp-key.json'),
        os.path.join(BASE_DIR, '..', 'diesel-patrol-491520-j8-16dd83a23f21.json'),
        _creds_env if _creds_env else '',
    ]
    if _creds_env and not os.path.isabs(_creds_env):
        _candidates.append(os.path.abspath(os.path.join(BASE_DIR, '..', '..', _creds_env)))
        _candidates.append(os.path.abspath(os.path.join(BASE_DIR, '..', _creds_env)))
    
    CREDS_PATH = next((p for p in _candidates if p and os.path.exists(p)), '')

if CREDS_PATH:
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = CREDS_PATH

BQ_CLIENT = None

def get_bq_client():
    from google.cloud import bigquery
    global BQ_CLIENT
    if BQ_CLIENT is None:
        BQ_CLIENT = bigquery.Client(project=PROJECT_ID)
    return BQ_CLIENT

BT_CLIENT = None
BT_TABLE = None

def get_bt_table():
    global BT_CLIENT, BT_TABLE
    if BT_TABLE is None:
        from google.cloud import bigtable
        if BT_CLIENT is None:
            BT_CLIENT = bigtable.Client(project=PROJECT_ID, admin=False)
        instance_id = os.getenv("GCP_INSTANCE", "price-intelligence")
        table_id = os.getenv("GCP_TABLE", "produits")
        BT_TABLE = BT_CLIENT.instance(instance_id).table(table_id)
    return BT_TABLE


# ─────────────────────────────────────────
# ENDPOINTS
# ─────────────────────────────────────────

@app.get("/")
def root():
    return {
        "api": "Prix Intelligence — Kitea + Jumia + Ikea",
        "version": "2.0.0",
        "endpoints": [
            "/stats", "/stats/categories", "/stats/sites",
            "/tests", "/regression", "/promotions",
            "/evolution", "/anomalies",
            "/intervalles-confiance", "/intervalles-confiance/categories",
            "/power-analysis", "/velocity",
            "/alertes", "/segmentation", "/correlation",
            "/figures", "/figure/{nom}",
        ]
    }

@app.get("/stats")
def get_stats():
    r = load_results()
    return {"meta": r.get("meta", {}), "stats_par_site": r.get("stats_par_site", {})}

@app.get("/stats/categories")
def get_stats_cat():
    return load_results().get("stats_par_categorie", {})

@app.get("/stats/sites")
def get_stats_sites():
    r = load_results()
    return r.get("stats_site_categorie", r.get("stats_par_site", {}))

@app.get("/tests")
def get_tests():
    r = load_results()
    return {
        "shapiro":            r.get("shapiro", {}),
        "kruskal_categories": r.get("kruskal_categories", {}),
        "kruskal_sites":      r.get("kruskal_sites", {}),
        "mann_whitney":       r.get("mann_whitney", {}),
    }

@app.get("/regression")
def get_regression():
    return load_results().get("regression", {})

@app.get("/promotions")
def get_promotions():
    return load_results().get("promotions", {})

@app.get("/evolution")
def get_evolution():
    return load_results().get("evolution_prix", [])

@app.get("/anomalies")
def get_anomalies():
    return load_results().get("anomalies", [])

@app.get("/intervalles-confiance")
def get_ic():
    r = load_results()
    return {
        "par_site":      r.get("intervalles_confiance", {}),
        "par_categorie": r.get("ic_categories", {}),
    }

@app.get("/intervalles-confiance/categories")
def get_ic_categories():
    return load_results().get("ic_categories", {})

@app.get("/power-analysis")
def get_power():
    return load_results().get("power_analysis", {})

@app.get("/velocity")
def get_velocity():
    return load_results().get("velocity", {})

@app.get("/alertes")
def get_alertes(priorite: str = None, site: str = None, type_alerte: str = None):
    r = load_results()
    alertes = r.get("alertes", [])
    seuils  = r.get("seuils_alertes", {})
    if priorite:
        alertes = [a for a in alertes if a.get("priorite", "").upper() == priorite.upper()]
    if site:
        alertes = [a for a in alertes if a.get("site", "").lower() == site.lower()]
    if type_alerte:
        alertes = [a for a in alertes if a.get("type", "").upper() == type_alerte.upper()]
    return {"total": len(alertes), "seuils": seuils, "alertes": alertes}

@app.get("/segmentation")
def get_segmentation():
    return load_results().get("segmentation", {})

@app.get("/correlation")
def get_correlation():
    return load_results().get("correlation", {})

VALID_FIGURES = [
    "boxplot", "barchart", "scatter", "promo",
    "evolution", "ic", "correlation", "kde",
    "velocity", "segmentation",
    "feature_importance", "ml_predictions",
]

@app.get("/figures")
def list_figures():
    return {"figures": [
        {"nom": nom, "url": f"/figure/{nom}",
         "disponible": os.path.exists(os.path.join(OUTPUT_DIR, f"fig_{nom}.json"))}
        for nom in VALID_FIGURES
    ]}

@app.get("/figure/{nom}")
def get_figure(nom: str):
    if nom not in VALID_FIGURES:
        raise HTTPException(
            status_code=404,
            detail=f"Figure '{nom}' invalide. Disponibles : {VALID_FIGURES}"
        )
    path = os.path.join(OUTPUT_DIR, f"fig_{nom}.json")
    if not os.path.exists(path):
        raise HTTPException(
            status_code=404,
            detail=f"fig_{nom}.json pas encore généré."
        )
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

# ==========================================
# 🔍 Recherche avec validation des inputs
# ==========================================
@app.get("/search")
def search_products(
    q: str = "",
    category: str = None,
    source: str = None,
    sort_dir: str = "asc",
    page: int = 1,
    limit: int = 50,
    min_price: float = None,
    max_price: float = None
):
    # ✅ Validation des inputs
    if len(q) > 100:
        raise HTTPException(status_code=400, detail="Paramètre q trop long (max 100 caractères)")
    if limit > 200 or limit < 1:
        raise HTTPException(status_code=400, detail="limit doit être entre 1 et 200")
    if page < 1:
        raise HTTPException(status_code=400, detail="page doit être >= 1")
    if sort_dir not in ["asc", "desc"]:
        raise HTTPException(status_code=400, detail="sort_dir doit être 'asc' ou 'desc'")
    if DATA_MODE not in ["csv", "bigquery", "bigtable"]:
        raise HTTPException(status_code=500, detail="DATA_MODE invalide")

    offset = (page - 1) * limit

    if DATA_MODE == "bigquery":
        try:
            client = get_bq_client()
            query = q.lower()
            where_clauses = ["(LOWER(nom) LIKE @search_term OR LOWER(source) LIKE @search_term)"]
            query_params = [
                __import__('google.cloud.bigquery', fromlist=['bigquery']).ScalarQueryParameter("search_term", "STRING", f"%{query}%"),
                __import__('google.cloud.bigquery', fromlist=['bigquery']).ScalarQueryParameter("limit", "INT64", limit),
                __import__('google.cloud.bigquery', fromlist=['bigquery']).ScalarQueryParameter("offset", "INT64", offset)
            ]
            if category:
                where_clauses.append("LOWER(categorie) LIKE @category_term")
                query_params.append(__import__('google.cloud.bigquery', fromlist=['bigquery']).ScalarQueryParameter("category_term", "STRING", f"%{category.lower()}%"))
            if source:
                where_clauses.append("LOWER(source) = @source_term")
                query_params.append(__import__('google.cloud.bigquery', fromlist=['bigquery']).ScalarQueryParameter("source_term", "STRING", source.lower()))
            if min_price is not None:
                where_clauses.append("prix >= @min_price")
                query_params.append(__import__('google.cloud.bigquery', fromlist=['bigquery']).ScalarQueryParameter("min_price", "FLOAT64", min_price))
            if max_price is not None:
                where_clauses.append("prix <= @max_price")
                query_params.append(__import__('google.cloud.bigquery', fromlist=['bigquery']).ScalarQueryParameter("max_price", "FLOAT64", max_price))
            
            where_sql = " AND ".join(where_clauses)
            order_dir = "ASC" if sort_dir.lower() != "desc" else "DESC"
            sql = f"""
                SELECT nom, source as marque, prix, ancien_prix, remise, NULL as rating, url, CAST(date_scraping AS STRING) as date_scraping, COUNT(*) OVER() as total_count
                FROM `{TABLE_REF}`
                WHERE {where_sql}
                ORDER BY prix {order_dir} NULLS LAST
                LIMIT @limit OFFSET @offset
            """
            from google.cloud import bigquery as bq
            job_config = bq.QueryJobConfig(query_parameters=query_params)
            query_job = client.query(sql, job_config=job_config)
            results = [dict(row) for row in query_job]
            total_count = results[0]["total_count"] if results else 0
            for r in results:
                r.pop("total_count", None)
            return {"total": total_count, "query": q, "results": results}
        except Exception as e:
            logger.error(f"Erreur BigQuery : {e}")
            raise HTTPException(status_code=500, detail=f"Erreur BigQuery : {e}")
    elif DATA_MODE == "bigtable":
        try:
            table = get_bt_table()
            from google.cloud.bigtable import row_filters
            row_filter = row_filters.CellsColumnLimitFilter(1)
            
            row_set = None
            if source:
                s_lower = source.lower()
                prefix = f"{s_lower}#"
                from google.cloud.bigtable.row_set import RowSet
                row_set = RowSet()
                row_set.add_row_range_from_keys(
                    start_key=prefix.encode('utf-8'),
                    end_key=(s_lower + chr(ord('#') + 1)).encode('utf-8')
                )
            
            rows = table.read_rows(row_set=row_set, filter_=row_filter)
            results = []
            query = q.lower()
            
            for row in rows:
                cf = row.cells.get('price_cf', {})
                
                def get_col(col_name: str) -> str:
                    cells = cf.get(col_name.encode(), [])
                    if not cells:
                        return ""
                    return cells[0].value.decode('utf-8', errors='replace').strip()
                
                nom = get_col('nom')
                if not nom:
                    continue
                
                nom_lower = nom.lower()
                site = get_col('source') or get_col('site')
                site_lower = site.lower() if site else ""
                
                if query and (query not in nom_lower and query not in site_lower):
                    continue
                
                cat = get_col('categorie')
                if category and (category.lower() not in cat.lower()):
                    continue
                
                if source and (source.lower() != site_lower):
                    continue
                
                try:
                    prix = float(get_col('prix')) if get_col('prix') else None
                except ValueError:
                    prix = None
                
                # Check price range
                if min_price is not None and (prix is None or prix < min_price):
                    continue
                if max_price is not None and (prix is None or prix > max_price):
                    continue
                    
                try:
                    ancien_prix = float(get_col('ancien_prix')) if get_col('ancien_prix') else None
                except ValueError:
                    ancien_prix = None
                    
                try:
                    remise = float(get_col('remise')) if get_col('remise') else None
                except ValueError:
                    remise = None
                
                results.append({
                    "nom": nom,
                    "marque": site,
                    "prix": prix,
                    "ancien_prix": ancien_prix,
                    "remise": remise,
                    "rating": None,
                    "url": get_col('url'),
                    "date_scraping": get_col('date_scraping')
                })
            
            valid_prices = [r for r in results if r['prix'] is not None]
            null_prices = [r for r in results if r['prix'] is None]
            reverse = (sort_dir.lower() == "desc")
            valid_prices.sort(key=lambda x: x['prix'], reverse=reverse)
            all_results = valid_prices + null_prices
            total_count = len(all_results)
            final_results = all_results[offset : offset + limit]
            return {"total": total_count, "query": q, "results": final_results}
        except Exception as e:
            logger.error(f"Erreur Bigtable : {e}")
            raise HTTPException(status_code=500, detail=f"Erreur Bigtable : {e}")
    else:
        import csv
        csv_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'clean', 'clean_prices.csv')
        if not os.path.exists(csv_path):
            raise HTTPException(status_code=404, detail=f"Fichier CSV introuvable : {csv_path}")
        results = []
        query = q.lower()
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    nom = row.get('nom', '').lower()
                    site = row.get('site', '').lower()
                    cat = row.get('categorie', '').lower()
                    if query and (query not in nom and query not in site):
                        continue
                    if category and (category.lower() not in cat):
                        continue
                    if source and (source.lower() != site):
                        continue
                    try:
                        prix = float(row.get('prix')) if row.get('prix') else None
                    except ValueError:
                        prix = None
                    
                    if min_price is not None and (prix is None or prix < min_price):
                        continue
                    if max_price is not None and (prix is None or prix > max_price):
                        continue

                    try:
                        ancien_prix = float(row.get('ancien_prix')) if row.get('ancien_prix') else None
                    except ValueError:
                        ancien_prix = None
                    try:
                        remise = float(row.get('remise_pct')) if row.get('remise_pct') else None
                    except ValueError:
                        remise = None
                    results.append({
                        "nom": row.get('nom'),
                        "marque": row.get('site'),
                        "prix": prix,
                        "ancien_prix": ancien_prix,
                        "remise": remise,
                        "rating": None,
                        "url": row.get('url'),
                        "date_scraping": row.get('date_scraping')
                    })
            valid_prices = [r for r in results if r['prix'] is not None]
            null_prices = [r for r in results if r['prix'] is None]
            reverse = (sort_dir.lower() == "desc")
            valid_prices.sort(key=lambda x: x['prix'], reverse=reverse)
            all_results = valid_prices + null_prices
            total_count = len(all_results)
            final_results = all_results[offset : offset + limit]
            return {"total": total_count, "query": q, "results": final_results}
        except Exception as e:
            logger.error(f"Erreur recherche locale : {e}")
            raise HTTPException(status_code=500, detail=f"Erreur recherche locale : {e}")


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)