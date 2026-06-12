from itemadapter import ItemAdapter
from kafka import KafkaProducer
import json
import logging

logger = logging.getLogger(__name__)


class ValidationPipeline:
    """
    Étape 1 — Valider et nettoyer chaque item avant envoi.
    Champs : nom, prix, date_scraping, ancien_prix, remise,
             url, categorie, image_url, source
    """

    CHAMPS_OBLIGATOIRES = ['nom', 'prix', 'date_scraping']

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        # ── Vérifier les champs obligatoires ──────────────────────────
        for champ in self.CHAMPS_OBLIGATOIRES:
            if not adapter.get(champ):
                raise Exception(f"❌ Champ manquant '{champ}' — item rejeté : {dict(item)}")

        # ── Nettoyer le prix ───────────────────────────────────────────
        try:
            prix_raw = str(adapter.get('prix', '')).replace('\xa0', '').replace(' ', '').replace(',', '.')
            adapter['prix'] = float(prix_raw)
        except (ValueError, TypeError):
            raise Exception(f"❌ Prix invalide : {adapter.get('prix')} — item rejeté")

        if adapter['prix'] <= 0:
            raise Exception(f"❌ Prix négatif ou nul : {adapter['prix']} — item rejeté")

        # ── Nettoyer l'ancien prix ─────────────────────────────────────
        ancien_prix = adapter.get('ancien_prix')
        if ancien_prix:
            try:
                ancien_prix_raw = str(ancien_prix).replace('\xa0', '').replace(' ', '').replace(',', '.')
                adapter['ancien_prix'] = float(ancien_prix_raw)
            except (ValueError, TypeError):
                adapter['ancien_prix'] = None
        else:
            adapter['ancien_prix'] = None

        # ── Nettoyer la remise ─────────────────────────────────────────
        remise = adapter.get('remise')
        if remise:
            try:
                adapter['remise'] = float(str(remise).replace('%', '').strip())
            except (ValueError, TypeError):
                adapter['remise'] = 0.0
        else:
            adapter['remise'] = 0.0

        
        # ── Gérer image vs image_url (Jumia) ──────────────────────────
        if not adapter.get('image_url') and adapter.get('image'):
            adapter['image_url'] = str(adapter.get('image')).strip()

        # ── Gérer remise_pct (IKEA et Kitea) ─────────────────────────
        if not adapter.get('remise') and adapter.get('remise_pct'):
            try:
                adapter['remise'] = float(str(adapter.get('remise_pct')).replace('%', '').strip())
            except (ValueError, TypeError):
                adapter['remise'] = 0.0

        # ── Nettoyer le nom ────────────────────────────────────────────
        adapter['nom'] = str(adapter.get('nom', '')).strip()[:500]

        # ── Nettoyer la catégorie ──────────────────────────────────────
        categorie = adapter.get('categorie')
        adapter['categorie'] = str(categorie).strip()[:200] if categorie else 'Non défini'

        # ── Nettoyer l'image_url ───────────────────────────────────────
        image_url = adapter.get('image_url')
        adapter['image_url'] = str(image_url).strip() if image_url else None




        # ── Nettoyer l'url ─────────────────────────────────────────────
        url = adapter.get('url')
        adapter['url'] = str(url).strip() if url else None

        # ── Ajouter la source (nom du spider) ─────────────────────────
        adapter['source'] = spider.name  # 'jumia', 'ikea', 'kitea'

        logger.debug(f"✅ Item validé : {adapter['nom']} — {adapter['prix']} MAD")
        return item


class KafkaPipeline:
    """
    Étape 2 — Envoyer chaque item validé dans le bon topic Kafka.
    Topic choisi selon le nom du spider : prix-jumia / prix-ikea / prix-kitea
    """

    TOPIC_MAP = {
        'jumia': 'prix-jumia',
        'ikea':  'prix-ikea',
        'kitea': 'prix-kitea',
    }

    def open_spider(self, spider):
        bootstrap = getattr(spider, 'kafka_bootstrap', 'kafka:29092')
        self.topic = self.TOPIC_MAP.get(spider.name, f'prix-{spider.name}')

        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap,
            value_serializer=lambda x: json.dumps(x, ensure_ascii=False).encode('utf-8'),
            retries=3,
            acks='all',
        )
        logger.info(f"🔗 Kafka connecté → topic : {self.topic}")

    def process_item(self, item, spider):
        try:
            self.producer.send(self.topic, value=dict(item))
            logger.debug(f"📤 Kafka ← {item.get('nom')} ({self.topic})")
        except Exception as e:
            logger.error(f"❌ Erreur envoi Kafka : {e}")
            raise
        return item

    def close_spider(self, spider):
        self.producer.flush()
        self.producer.close()
        logger.info(f"✅ Kafka fermé proprement — spider {spider.name} terminé")