import scrapy
from bs4 import BeautifulSoup
import json
from datetime import datetime
from kafka import KafkaProducer


class JumiaSpider(scrapy.Spider):
    name = "jumia"
    allowed_domains = ["jumia.ma"]

    start_urls = [
    "https://www.jumia.ma/salle-a-manger/",
    "https://www.jumia.ma/meubles-meubles-chambre-coucher/",
    "https://www.jumia.ma/meubles-mobilier-bureau-domicile/",
    "https://www.jumia.ma/fauteuils/",
    "https://www.jumia.ma/canape/",
    "https://www.jumia.ma/meubles-tables/",
]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        bootstrap = kwargs.get('kafka_bootstrap', 'kafka:29092')
        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap,
            value_serializer=lambda x: json.dumps(x, ensure_ascii=False).encode('utf-8')
        )

    def nettoyer_prix(self, prix_str):
        if not prix_str:
            return None
        try:
            return float(prix_str.replace(" Dhs", "").replace(",", "").split(" - ")[0])
        except Exception:
            return None

    def nettoyer_remise(self, remise_str):
        if not remise_str:
            return None
        try:
            return float(remise_str.replace("%", ""))
        except Exception:
            return None

    def parse(self, response):
        soup = BeautifulSoup(response.text, "lxml")
        script = soup.find("script", string=lambda t: t and "window.__STORE__" in t)

        if not script:
            return

        data = json.loads(script.text.split("window.__STORE__=")[1].rstrip(";"))
        produits = data.get("products", [])

        articles = soup.select("article.prd")

        for produit, article in zip(produits, articles):
            img_tag = article.select_one("div.img-c img")
            image_url = img_tag.get("data-src") or img_tag.get("src") if img_tag else ""

            item = {
                "nom":          produit.get("displayName", ""),
                "url":          "https://www.jumia.ma" + produit.get("url", ""),
                "categorie":    response.url.split("jumia.ma/")[1].split("/")[0],
                "prix":         self.nettoyer_prix(produit["prices"].get("price", "")),
                "ancien_prix":  self.nettoyer_prix(produit["prices"].get("oldPrice", "")),
                "remise":       self.nettoyer_remise(produit["prices"].get("discount", "")),
                "image_url":    image_url,
                "source":       "jumia",
                "date_scraping": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }

            self.producer.send('prix-jumia', value=item)
            print(f"[Jumia] Kafka ← {item['nom']} - {item['prix']}")

            yield item

        # Pagination
        page_actuelle = response.meta.get("page", 1)
        prochaine_page = page_actuelle + 1
        prochaine_url = f"{response.url.split('?')[0]}?page={prochaine_page}"

        if produits:
            yield scrapy.Request(
                url=prochaine_url,
                callback=self.parse,
                meta={"page": prochaine_page}
            )

    def closed(self, reason):
        self.producer.flush()
        self.producer.close()