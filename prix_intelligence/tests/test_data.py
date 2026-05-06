"""
╔══════════════════════════════════════════════════════════╗
║   TEST DATA QUALITY — Prix Intelligence Platform         ║
║   Valide la qualité et l'intégrité des données           ║
╚══════════════════════════════════════════════════════════╝
"""
import pytest
import pandas as pd
import numpy as np
import os
import json

BASE_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_CLEAN   = os.path.join(BASE_DIR, 'data', 'clean', 'clean_prices.csv')
CSV_RAW     = os.path.join(BASE_DIR, 'data', 'raw', 'raw_prices.csv')
CSV_HIST    = os.path.join(BASE_DIR, 'data', 'raw', 'historique_prices.csv')
JSON_RESULT = os.path.join(BASE_DIR, 'outputs', 'analyse_results.json')


# ═══════════════════════════════════════════════════════════
# TEST 1 — FICHIERS EXISTENT
# ═══════════════════════════════════════════════════════════

class TestFichiersExistent:
    """Vérifie que tous les fichiers requis existent"""

    def test_csv_clean_existe(self):
        assert os.path.exists(CSV_CLEAN), f"Fichier manquant : {CSV_CLEAN}"

    def test_csv_raw_existe(self):
        assert os.path.exists(CSV_RAW), f"Fichier manquant : {CSV_RAW}"

    def test_historique_existe(self):
        assert os.path.exists(CSV_HIST), f"Fichier manquant : {CSV_HIST}"

    def test_json_resultats_existe(self):
        assert os.path.exists(JSON_RESULT), f"Fichier manquant : {JSON_RESULT}"

    def test_outputs_dir_existe(self):
        outputs_dir = os.path.join(BASE_DIR, 'outputs')
        assert os.path.isdir(outputs_dir), f"Dossier manquant : {outputs_dir}"


# ═══════════════════════════════════════════════════════════
# TEST 2 — TAILLE DES DONNÉES
# ═══════════════════════════════════════════════════════════

class TestTailleDonnees:
    """Vérifie la taille minimale des datasets"""

    def test_clean_nb_lignes_minimum(self, df_clean):
        assert len(df_clean) >= 1000, (
            f"Trop peu de produits : {len(df_clean)} (min 1000)"
        )

    def test_clean_nb_lignes_exact(self, df_clean):
        """On a exactement 2647 produits nettoyés"""
        assert len(df_clean) >= 2000, (
            f"Dataset trop petit : {len(df_clean)}"
        )

    def test_hist_nb_lignes_minimum(self, df_hist):
        assert len(df_hist) >= 10000, (
            f"Historique trop petit : {len(df_hist)} (min 10000)"
        )

    def test_hist_30_jours(self, df_hist):
        """Historique couvre 30 jours"""
        n_jours = df_hist['date_scraping'].dt.date.nunique()
        assert n_jours >= 25, (
            f"Historique couvre seulement {n_jours} jours (min 25)"
        )

    def test_nb_sites(self, df_clean, sites):
        sites_presents = df_clean['site'].unique().tolist()
        for site in sites:
            assert site in sites_presents, (
                f"Site manquant dans les données : {site}"
            )

    def test_nb_categories(self, df_clean):
        assert df_clean['categorie'].nunique() >= 4, (
            f"Trop peu de catégories : {df_clean['categorie'].nunique()}"
        )


# ═══════════════════════════════════════════════════════════
# TEST 3 — COLONNES REQUISES
# ═══════════════════════════════════════════════════════════

class TestColonnesRequises:
    """Vérifie que toutes les colonnes nécessaires sont présentes"""

    COLONNES_REQUISES = [
        'product_id', 'nom', 'site', 'categorie',
        'prix', 'ancien_prix', 'remise_pct',
        'en_promotion', 'gamme_prix'
    ]

    def test_colonnes_clean(self, df_clean):
        cols_manquantes = [
            c for c in self.COLONNES_REQUISES
            if c not in df_clean.columns
        ]
        assert len(cols_manquantes) == 0, (
            f"Colonnes manquantes : {cols_manquantes}"
        )

    def test_colonnes_historique(self, df_hist):
        cols_requises = ['product_id', 'site', 'prix', 'date_scraping']
        cols_manquantes = [c for c in cols_requises if c not in df_hist.columns]
        assert len(cols_manquantes) == 0, (
            f"Colonnes historique manquantes : {cols_manquantes}"
        )


# ═══════════════════════════════════════════════════════════
# TEST 4 — QUALITÉ DES PRIX
# ═══════════════════════════════════════════════════════════

class TestQualitePrix:
    """Vérifie l'intégrité des valeurs de prix"""

    def test_aucun_prix_nul(self, df_clean):
        nb_nuls = df_clean['prix'].isna().sum()
        assert nb_nuls == 0, (
            f"{nb_nuls} valeurs nulles dans la colonne prix"
        )

    def test_aucun_prix_negatif(self, df_clean):
        nb_negatifs = (df_clean['prix'] <= 0).sum()
        assert nb_negatifs == 0, (
            f"{nb_negatifs} prix négatifs ou nuls"
        )

    def test_prix_minimum_raisonnable(self, df_clean):
        prix_min = df_clean['prix'].min()
        assert prix_min >= 10, (
            f"Prix minimum trop bas : {prix_min} MAD"
        )

    def test_prix_maximum_raisonnable(self, df_clean):
        prix_max = df_clean['prix'].max()
        assert prix_max <= 500000, (
            f"Prix maximum suspect : {prix_max} MAD"
        )

    def test_remise_entre_0_et_100(self, df_clean):
        df_r = df_clean[df_clean['remise_pct'].notna()]
        hors_bornes = ((df_r['remise_pct'] < 0) | (df_r['remise_pct'] > 100)).sum()
        assert hors_bornes == 0, (
            f"{hors_bornes} remises hors bornes [0, 100]"
        )

    def test_ancien_prix_superieur_ou_egal_prix(self, df_clean):
        """Ancien prix doit être >= prix actuel (logique promotion)"""
        df_promo = df_clean[
            df_clean['en_promotion'] &
            df_clean['ancien_prix'].notna()
        ]
        incoherents = (df_promo['ancien_prix'] < df_promo['prix']).sum()
        pct = incoherents / len(df_promo) * 100 if len(df_promo) > 0 else 0
        assert pct < 10, (
            f"Trop d'incohérences prix/ancien_prix : {pct:.1f}% (max 10%)"
        )

    def test_prix_historique_positifs(self, df_hist):
        nb_neg = (df_hist['prix'] <= 0).sum()
        assert nb_neg == 0, (
            f"{nb_neg} prix négatifs dans l'historique"
        )


# ═══════════════════════════════════════════════════════════
# TEST 5 — DOUBLONS
# ═══════════════════════════════════════════════════════════

class TestDoublons:
    """Vérifie l'absence de doublons"""

    def test_pas_de_doublons_produit_site(self, df_clean):
        dups = df_clean.duplicated(subset=['nom', 'site']).sum()
        assert dups == 0, (
            f"{dups} doublons (nom, site) détectés"
        )

    def test_product_id_unique(self, df_clean):
        dups = df_clean['product_id'].duplicated().sum()
        assert dups == 0, (
            f"{dups} product_id dupliqués"
        )


# ═══════════════════════════════════════════════════════════
# TEST 6 — DISTRIBUTIONS STATISTIQUES
# ═══════════════════════════════════════════════════════════

class TestDistributions:
    """Vérifie les distributions attendues"""

    def test_taux_promotion_raisonnable(self, df_clean):
        taux = df_clean['en_promotion'].mean() * 100
        assert 10 <= taux <= 90, (
            f"Taux promotion suspect : {taux:.1f}% (attendu entre 10% et 90%)"
        )

    def test_chaque_site_represente(self, df_clean, sites):
        for site in sites:
            n = len(df_clean[df_clean['site'] == site])
            assert n >= 100, (
                f"Site {site} sous-représenté : {n} produits (min 100)"
            )

    def test_prix_moyen_par_site_coherent(self, df_clean):
        stats = df_clean.groupby('site')['prix'].mean()
        # Ikea doit être plus cher que Jumia en général
        if 'ikea' in stats and 'jumia' in stats:
            assert stats['ikea'] > stats['jumia'], (
                f"Ikea ({stats['ikea']:.0f}) devrait être plus cher que Jumia ({stats['jumia']:.0f})"
            )

    def test_gamme_prix_valeurs_valides(self, df_clean):
        gammes_valides = {
            'Entrée (<500)', 'Économique (500-1500)',
            'Milieu (1500-4000)', 'Premium (4000-10k)', 'Luxe (>10k)'
        }
        gammes_presentes = set(df_clean['gamme_prix'].dropna().unique())
        inconnues = gammes_presentes - gammes_valides
        assert len(inconnues) == 0, (
            f"Gammes de prix inconnues : {inconnues}"
        )


# ═══════════════════════════════════════════════════════════
# TEST 7 — JSON RÉSULTATS
# ═══════════════════════════════════════════════════════════

class TestJsonResultats:
    """Vérifie la structure du fichier de résultats"""

    CLES_REQUISES = [
        'meta', 'stats_par_site', 'stats_par_categorie',
        'promotions', 'shapiro', 'kruskal_categories',
        'kruskal_sites', 'regression', 'evolution_prix',
    ]

    def test_json_lisible(self, results_json):
        assert isinstance(results_json, dict), "Le JSON doit être un dictionnaire"

    def test_cles_requises_presentes(self, results_json):
        for cle in self.CLES_REQUISES:
            assert cle in results_json, (
                f"Clé manquante dans analyse_results.json : '{cle}'"
            )

    def test_meta_contient_sites(self, results_json):
        sites = results_json.get('meta', {}).get('sites', [])
        assert len(sites) == 3, (
            f"3 sites attendus dans meta, trouvé : {sites}"
        )

    def test_meta_nb_produits_coherent(self, results_json, df_clean):
        nb_json = results_json.get('meta', {}).get('nb_produits', 0)
        nb_csv  = len(df_clean)
        assert abs(nb_json - nb_csv) <= 10, (
            f"Incohérence nb_produits : JSON={nb_json} / CSV={nb_csv}"
        )

    def test_regression_r2_present(self, results_json):
        reg = results_json.get('regression', {})
        assert 'r2_adj' in reg, "r2_adj manquant dans regression"
        r2 = reg['r2_adj']
        assert 0 <= r2 <= 1, f"R² invalide : {r2}"

    def test_shapiro_trois_sites(self, results_json):
        shapiro = results_json.get('shapiro', {})
        assert len(shapiro) >= 3, (
            f"Shapiro : 3 sites attendus, trouvé {len(shapiro)}"
        )

    def test_evolution_prix_non_vide(self, results_json):
        evol = results_json.get('evolution_prix', [])
        assert len(evol) > 0, "evolution_prix vide dans JSON"

    def test_kruskal_p_value_valide(self, results_json):
        kw = results_json.get('kruskal_sites', {})
        p = kw.get('p_value', None)
        assert p is not None, "p_value manquante dans kruskal_sites"
        assert 0 <= p <= 1, f"p_value invalide : {p}"
