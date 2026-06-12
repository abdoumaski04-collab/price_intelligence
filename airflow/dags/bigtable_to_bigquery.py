import os
import logging
from datetime import datetime
from google.oauth2 import service_account
from google.cloud import bigtable, bigquery

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PROJECT_ID = "diesel-patrol-491520-j8"
BQ_TABLE   = f"{PROJECT_ID}.jumia_price_intelligence.produits"
BATCH_SIZE = 500

def parse_date(val):
    if not val or val == 'None':
        return None
    try:
        return datetime.strptime(val, '%Y-%m-%d %H:%M:%S').isoformat()
    except:
        try:
            return datetime.strptime(val, '%Y-%m-%d').isoformat()
        except:
            return None

def read_from_bigtable():
    credentials = service_account.Credentials.from_service_account_file('/opt/airflow/gcp-key.json')
    client = bigtable.Client(project=PROJECT_ID, admin=True, credentials=credentials)
    table  = client.instance('price-intelligence').table('produits')
    rows   = table.read_rows()
    rows.consume_all()
    produits = []
    for row_key, row in rows.rows.items():
        cf = row.cells.get('price_cf', row.cells.get(b'price_cf', {}))
        def get(col):
            cells = cf.get(col.encode(), [])
            return cells[0].value.decode('utf-8') if cells else None
        prix = get('prix')
        nom  = get('nom')
        if not prix or not nom:
            continue
        try:
            prix_float = float(prix)
        except:
            continue
        produits.append({
            'url':           get('url'),
            'prix':          prix_float,
            'date_scraping': parse_date(get('date_scraping')),
            'nom':           nom,
            'ancien_prix':   float(get('ancien_prix')) if get('ancien_prix') and get('ancien_prix') != 'None' else None,
            'remise':        float(get('remise')) if get('remise') and get('remise') != 'None' else None,
            'source':        get('source'),
            'categorie':     get('categorie'),
            'image_url':     get('image_url'),
        })
    logger.info(f'OK {len(produits)} produits lus depuis GCP Bigtable')
    return produits

def write_to_bigquery(produits):
    if not produits:
        logger.warning('Aucun produit a ecrire')
        return
    credentials = service_account.Credentials.from_service_account_file('/opt/airflow/gcp-key.json')
    client = bigquery.Client(project=PROJECT_ID, credentials=credentials)
    total  = 0
    for i in range(0, len(produits), BATCH_SIZE):
        batch  = produits[i:i + BATCH_SIZE]
        errors = client.insert_rows_json(BQ_TABLE, batch)
        if errors:
            logger.error(f'Erreurs : {errors[:3]}')
        else:
            total += len(batch)
            logger.info(f'OK {total} lignes inserees dans BigQuery')

def main():
    produits = read_from_bigtable()
    write_to_bigquery(produits)
    logger.info('OK Transfert GCP Bigtable vers BigQuery termine')

if __name__ == '__main__':
    main()
