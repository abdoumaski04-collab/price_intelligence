import os, sys, json, hashlib
from datetime import datetime
from google.cloud import bigtable
from google.oauth2 import service_account

credentials = service_account.Credentials.from_service_account_file(
    '/opt/nifi/scripts/gcp-key.json'
)
client = bigtable.Client(project='diesel-patrol-491520-j8', admin=True, credentials=credentials)
table  = client.instance('price-intelligence').table('produits')
data = json.loads(sys.stdin.read())
url    = data.get('url', '')
source = data.get('source', '')
if 'ikea' in source.lower():
    source = 'ikea'
elif 'kitea' in source.lower():
    source = 'kitea'
elif 'jumia' in source.lower():
    source = 'jumia'
data['source'] = source
row_key = source + '#' + hashlib.md5(url.encode()).hexdigest()[:8] + '#' + datetime.now().strftime('%Y%m%d%H%M%S')
row = table.direct_row(row_key)
for col in ['nom','prix','ancien_prix','remise','url','image_url','source','categorie','date_scraping']:
    val = str(data.get(col, ''))
    if val and val != 'None':
        row.set_cell('price_cf', col, val.encode('utf-8'))
row.commit()
print('OK')
