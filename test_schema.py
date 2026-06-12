import os
from google.cloud import bigquery

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"C:\Users\AYOUB\Desktop\price-intelligence-platform\dataengineer\diesel-patrol-491520-j8-16dd83a23f21.json"

client = bigquery.Client(project="diesel-patrol-491520-j8")
table = client.get_table("diesel-patrol-491520-j8.jumia_price_intelligence.produits")
print([field.name for field in table.schema])
