import scrapy
import re
import json
from datetime import datetime
from kafka import KafkaProducer


class KiteaSpider(scrapy.Spider):
    name = "kitea"
    allowed_domains = ["kitea.com", "www.kitea.com"]

    start_urls = [
        "https://www.kitea.com/par-espaces/salon-et-sejour.html",
        "https://www.kitea.com/mobilier-pro.html",
        "https://www.kitea.com/par-espaces/salle-a-manger.html",
        "https://www.kitea.com/par-espaces/chambre-adulte.html",
        "https://www.kitea.com/par-espaces/rangement.html",

    ]

    custom_settings = {
        "ROBOTSTXT_OBEY": True,
        "DOWNLOAD_DELAY": 2,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 1,
        "DEFAULT_REQUEST_HEADERS": {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "fr,en;q=0.5",
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
        },
        "LOG_LEVEL": "INFO",
    }

    def __init__(self):
        self.producer = KafkaProducer(
            bootstrap_servers='kafka:29092',
            value_serializer=lambda x: json.dumps(x, ensure_ascii=False).encode('utf-8')
        )
        self.produits_vus = set()   # URLs produits déjà scrapés
        self.total_scrapes = 0      # Compteur global

    def nettoyer_prix(self, prix_str):
        if not prix_str:
            return None
        try:
            propre = re.sub(r"[^\d,\.]", "", str(prix_str).strip())
            propre = propre.replace(",", ".")
            parties = propre.split(".")
            if len(parties) > 2:
                propre = "".join(parties[:-1]) + "." + parties[-1]
            return float(propre) if propre else None
        except (ValueError, AttributeError):
            return None

    def parse(self, response):
        self.logger.info(f"=== Page : {response.url} | Status : {response.status} ===")

        produits = response.css("li.item.product.product-item")
        self.logger.info(f"  → {len(produits)} produits trouvés sur cette page")

        # Compter combien de produits sont NOUVEAUX sur cette page
        nouveaux = 0

        for produit in produits:
            nom = produit.css("h2.product-item-titre::text").get("").strip()
            url_produit = produit.css("a.product-item-link::attr(href)").get("")

            # ── STOP si ce produit a déjà été vu → page dupliquée ────────
            if url_produit in self.produits_vus:
                continue

            self.produits_vus.add(url_produit)
            nouveaux += 1

            prix_data = produit.css(
                "span[data-price-type='finalPrice']::attr(data-price-amount)"
            ).get()
            ancien_prix_data = produit.css(
                "span[data-price-type='oldPrice']::attr(data-price-amount)"
            ).get()

            if not prix_data:
                prix_data = produit.css("span.price::text").get("")

            prix_actuel = self.nettoyer_prix(prix_data)
            ancien_prix = self.nettoyer_prix(ancien_prix_data)

            remise = None
            if prix_actuel and ancien_prix and ancien_prix > 0:
                remise = round((1 - prix_actuel / ancien_prix) * 100, 1)

            badge = produit.css(
                "span.label-percent::text, span.sale-label::text"
            ).get("").strip()

            image_url = (
                produit.css("img.product-image-photo::attr(src)").get()
                or produit.css("img.product-image-photo::attr(data-src)").get("")
            )

            categorie = (
                response.url.split("/")[-1]
                .split("?")[0]
                .replace(".html", "")
                .replace("-", " ")
                .title()
            )

            if prix_actuel is None:
                self.logger.warning(f"  ⚠ Prix non trouvé pour [{nom}]")

            item = {
                "nom":           nom,
                "url":           url_produit,
                "categorie":     categorie,
                "prix":   prix_actuel,
                "ancien_prix":   ancien_prix,
                "remise":    remise,
                "image_url":     image_url,
                "source":        "kitea.com",
                "date_scraping": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }

            self.producer.send('prix-kitea', value=item)
            self.logger.info(
                f"  ✓ {nom[:45]:<45} | {prix_actuel} Dhs | Remise: {remise}%"
            )
            self.total_scrapes += 1
            yield item

        # ── Pagination : s'arrêter si aucun nouveau produit ──────────────
        if nouveaux == 0:
            self.logger.info(
                f"  → STOP : 0 nouveaux produits sur cette page "
                f"(total : {self.total_scrapes} produits scrapés)"
            )
            return

        # Continuer vers la page suivante
        url_base = response.url.split("?")[0]
        page_actuelle = int(response.meta.get("page", 1))
        prochaine_page = page_actuelle + 1
        prochaine_url = f"{url_base}?p={prochaine_page}"

        self.logger.info(
            f"  → Page suivante : {prochaine_url} "
            f"({nouveaux} nouveaux produits sur cette page)"
        )
        yield scrapy.Request(
            url=prochaine_url,
            callback=self.parse,
            meta={"page": prochaine_page},
        )

    def closed(self, reason):
        self.producer.flush()
        self.producer.close()
        self.logger.info(
            f"Spider fermé ({reason}) — Total scrapé : {self.total_scrapes} produits"
        )