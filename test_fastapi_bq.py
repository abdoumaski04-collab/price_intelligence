import os
from google.cloud import bigquery

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"C:\Users\AYOUB\Desktop\price-intelligence-platform\dataengineer\diesel-patrol-491520-j8-16dd83a23f21.json"

try:
    client = bigquery.Client(project="diesel-patrol-491520-j8")
    
    query = "samsung"
    limit = 50
    
    sql = """
        SELECT nom, marque, prix, ancien_prix, remise, rating, url, CAST(date_scraping AS STRING) as date_scraping
        FROM `diesel-patrol-491520-j8.jumia_price_intelligence.produits`
        WHERE LOWER(nom) LIKE @search_term OR LOWER(marque) LIKE @search_term
        ORDER BY prix ASC
        LIMIT @limit
    """
    
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("search_term", "STRING", f"%{query}%"),
            bigquery.ScalarQueryParameter("limit", "INT64", limit),
        ]
    )
    
    query_job = client.query(sql, job_config=job_config)
    results = [dict(row) for row in query_job]
    print(f"Success! Found {len(results)} rows.")
except Exception as e:
    import traceback
    traceback.print_exc()
