import scrapy
import re
import json
from datetime import datetime
from kafka import KafkaProducer

class IkeaSpider(scrapy.Spider):
    name = "ikea"
    allowed_domains = ["ikea.com", "www.ikea.com"]

    # Test avec une seule catégorie
    start_urls = [
        "https://www.ikea.com/ma/fr/cat/canapes-2-places-en-tissu-10668/",
        "https://www.ikea.com/ma/fr/cat/canapes-3-places-en-tissu-10670/",
        "https://www.ikea.com/ma/fr/cat/canapes-avec-meridienne-en-tissu-47388/",
        "https://www.ikea.com/ma/fr/cat/canapes-dangle-en-tissu-10671/",
        "https://www.ikea.com/ma/fr/cat/elements-modulables-canape-31786/",
        "https://www.ikea.com/ma/fr/cat/convertibles-10663/",
        "https://www.ikea.com/ma/fr/cat/fauteuils-et-meridiennes-fu006/",
        "https://www.ikea.com/ma/fr/cat/meridiennes-57527/",
        "https://www.ikea.com/ma/fr/cat/lits-simples-16285/",
        "https://www.ikea.com/ma/fr/cat/lits-doubles-16284/",
        "https://www.ikea.com/ma/fr/cat/lits-rembourres-49096/",
        "https://www.ikea.com/ma/fr/cat/cadres-de-lit-avec-rangement-25205/",
        "https://www.ikea.com/ma/fr/cat/lits-dappoint-et-banquettes-19037/",
        "https://www.ikea.com/ma/fr/cat/matelas-bm002/",
        "https://www.ikea.com/ma/fr/cat/tables-de-chevet-20656/",
        "https://www.ikea.com/ma/fr/cat/commodes-10451/",
        "https://www.ikea.com/ma/fr/cat/pax-armoires-avec-portes-24337/",
        "https://www.ikea.com/ma/fr/cat/pax-portes-coulissantes-19115/",
        "https://www.ikea.com/ma/fr/cat/pax-armoires-sans-porte-19110/",
        "https://www.ikea.com/ma/fr/cat/coiffeuses-20657/",
        "https://www.ikea.com/ma/fr/cat/armoires-integrees-43632/",
        "https://www.ikea.com/ma/fr/cat/armoires-a-portes-battantes-48005/",
        "https://www.ikea.com/ma/fr/cat/armoires-coulissantes-43635/",
        "https://www.ikea.com/ma/fr/cat/armoires-ouvertes-43634/",
        "https://www.ikea.com/ma/fr/cat/armoires-de-couloir-48007/",
        "https://www.ikea.com/ma/fr/cat/armoires-a-portes-miroir-48006/",
        "https://www.ikea.com/ma/fr/cat/armoires-independantes-43631/",
        "https://www.ikea.com/ma/fr/cat/meubles-de-rangement-salon-10409/",
        "https://www.ikea.com/ma/fr/cat/buffets-et-bahuts-10412/",
        "https://www.ikea.com/ma/fr/cat/meubles-tv-avec-rangements-14885/",
        "https://www.ikea.com/ma/fr/cat/banc-tv-10810/",
        "https://www.ikea.com/ma/fr/cat/combinaisons-bureaux-18623/",
        "https://www.ikea.com/ma/fr/cat/bureaux-pour-la-maison-20651/",
        "https://www.ikea.com/ma/fr/cat/bureaux-professionnels-47069/",
        "https://www.ikea.com/ma/fr/cat/chaises-de-bureau-20652/",
        "https://www.ikea.com/ma/fr/cat/chaises-de-salle-a-manger-25219/",
        "https://www.ikea.com/ma/fr/cat/ensembles-tables-et-chaises-19145/",
        "https://www.ikea.com/ma/fr/cat/ensemble-meuble-chambre-54992/",
        "https://www.ikea.com/ma/fr/cat/rangements-cubiques-55012/",
        "https://www.ikea.com/ma/fr/cat/meuble-etagere-11465/",
        "https://www.ikea.com/ma/fr/cat/bibliotheques-10382/",
        "https://www.ikea.com/ma/fr/cat/systemes-de-rangement-10397/",
        "https://www.ikea.com/ma/fr/cat/etageres-et-armoires-a-chaussures-10456/",
        "https://www.ikea.com/ma/fr/cat/repose-pieds-et-poufs-en-tissu-20927/",
        "https://www.ikea.com/ma/fr/cat/ensembles-tables-et-chaises-max-2-pers-36209/",
        "https://www.ikea.com/ma/fr/cat/ensembles-tables-et-chaises-max-4-pers-36212/",
        "https://www.ikea.com/ma/fr/cat/ensembles-tables-et-chaises-max-6-pers-36213/",

    ]

    custom_settings = {
        "ROBOTSTXT_OBEY": True,
        "DOWNLOAD_DELAY": 2,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 1,
        "DEFAULT_REQUEST_HEADERS": {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "fr-MA,fr;q=0.9,en;q=0.5",
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
        self.produits_vus = set()
        self.total_scrapes = 0

    def nettoyer_prix(self, prix_str):
        """Prix IKEA est en centimes entiers ex: '2999' → 2999.0 Dhs"""
        if not prix_str:
            return None
        try:
            propre = re.sub(r"[^\d]", "", str(prix_str).strip())
            return float(propre) if propre else None
        except (ValueError, AttributeError):
            return None

    def parse(self, response):
        self.logger.info(f"=== Page : {response.url} | Status : {response.status} ===")

        # ── Sélecteur principal : chaque carte produit ────────────────────
        # IKEA utilise data-ref-id sur chaque div produit
        produits = response.css("div[data-ref-id]")
        self.logger.info(f"  → {len(produits)} produits trouvés sur cette page")

        nouveaux = 0

        for produit in produits:
            # Données directement dans les attributs HTML ─────────────────
            ref_id       = produit.attrib.get("data-ref-id", "")
            product_num  = produit.attrib.get("data-product-number", "")
            nom          = produit.attrib.get("data-product-name", "").strip()
            prix_data    = produit.attrib.get("data-price", "")        # Prix actuel
            currency     = produit.attrib.get("data-currency", "MAD")

            # Déduplication par référence produit
            if ref_id in self.produits_vus:
                continue
            self.produits_vus.add(ref_id)
            nouveaux += 1

            # Prix ─────────────────────────────────────────────────────────
            prix_actuel = self.nettoyer_prix(prix_data)

            # Ancien prix (prix barré) — chercher dans secondary-current-price
            ancien_prix_str = produit.css(
                ".plp-price-module__secondary-current-price span[aria-hidden='true']::text,"
                ".plp-price-module__previous-price span[aria-hidden='true']::text"
            ).get()
            ancien_prix = self.nettoyer_prix(ancien_prix_str)

            # Remise
            remise = None
            if prix_actuel and ancien_prix and ancien_prix > 0:
                remise = round((1 - prix_actuel / ancien_prix) * 100, 1)

            # Badge remise
            badge = produit.css(
                ".plp-price-module__offer-badge::text,"
                "span[class*='offer']::text"
            ).get("").strip()

            # URL produit ──────────────────────────────────────────────────
            url_produit = produit.css("a.plp-mastercard__link::attr(href)").get("")
            if not url_produit:
                url_produit = produit.css("a[data-skapa]::attr(href)").get("")

            # Nom fallback depuis le HTML si attribut vide
            if not nom:
                nom = produit.css(
                    "h3 span.plp-price-module__name-decorator + span::text,"
                    ".plp-price-module__description span::text"
                ).getall()
                nom = " ".join(nom).strip()

            # Description (sous-titre produit)
            description = " ".join(
                produit.css(".plp-price-module__description span::text").getall()
            ).strip()

            # Image
            image_url = (
                produit.css("img[src*='ikea']::attr(src)").get()
                or produit.css("img::attr(src)").get("")
            )

            # Catégorie depuis l'URL
            categorie = response.url.split("/cat/")[-1].split("/")[0].rstrip("?")

            if prix_actuel is None:
                self.logger.warning(
                    f"  ⚠ Prix non trouvé pour [{nom}] | data-price={prix_data}"
                )

            item = {
                "nom":           nom,
                "url":           url_produit,
                "categorie":     categorie,
                "prix":   prix_actuel,
                "ancien_prix":   ancien_prix,
                "remise":    remise,
                "image_url":     image_url,
                "source":        "ikea.com",
                "date_scraping": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }

            self.producer.send('prix-ikea', value=item)
            self.logger.info(
                f"  ✓ {nom[:40]:<40} | {prix_actuel} Dhs | Remise: {remise}%"
            )
            self.total_scrapes += 1
            yield item

        # ── STOP si aucun nouveau produit (page dupliquée) ───────────────
        if nouveaux == 0:
            self.logger.info(
                f"  → STOP : 0 nouveaux produits "
                f"(total : {self.total_scrapes} produits)"
            )
            return

        # ── Pagination : ?page=2, ?page=3 ────────────────────────────────
        # Chercher le lien "Afficher plus" / page suivante
        next_page = response.css(
            "a[href*='?page=']::attr(href),"
            "a[href*='/page=']::attr(href)"
        ).get()

        if next_page:
            self.logger.info(f"  → Page suivante : {next_page}")
            yield scrapy.Request(
                url=next_page,
                callback=self.parse,
            )
        else:
            # Fallback : construire l'URL manuellement
            url_base = response.url.split("?")[0]
            page_actuelle = int(response.meta.get("page", 1))
            prochaine_page = page_actuelle + 1
            prochaine_url = f"{url_base}?page={prochaine_page}"

            # Vérifier via le tag <a id="products-page-N">
            has_next = response.css(f"a[id='products-page-{prochaine_page}']").get()
            if has_next or nouveaux > 0:
                self.logger.info(f"  → Page suivante (fallback) : {prochaine_url}")
                yield scrapy.Request(
                    url=prochaine_url,
                    callback=self.parse,
                    meta={"page": prochaine_page},
                )
            else:
                self.logger.info(f"  → Dernière page atteinte")

    def closed(self, reason):
        self.producer.flush()
        self.producer.close()
        self.logger.info(
            f"Spider fermé ({reason}) — Total : {self.total_scrapes} produits"
        )