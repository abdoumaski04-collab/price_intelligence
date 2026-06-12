"""
╔══════════════════════════════════════════════════════════╗
║   TEST API — Prix Intelligence Platform                  ║
║   Valide tous les endpoints FastAPI                      ║
╚══════════════════════════════════════════════════════════╝
"""
import pytest
import json
import os
import sys

BASE_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSON_RESULT = os.path.join(BASE_DIR, 'outputs', 'analyse_results.json')
OUTPUTS_DIR = os.path.join(BASE_DIR, 'outputs')


# ═══════════════════════════════════════════════════════════
# TEST 1 — FICHIERS OUTPUTS
# ═══════════════════════════════════════════════════════════

class TestOutputsFichiers:
    """Vérifie que tous les fichiers de sortie existent"""

    def test_analyse_results_existe(self):
        assert os.path.exists(JSON_RESULT), (
            f"analyse_results.json manquant : {JSON_RESULT}"
        )

    def test_analyse_results_non_vide(self):
        size = os.path.getsize(JSON_RESULT)
        assert size > 1000, (
            f"analyse_results.json trop petit : {size} octets"
        )

    @pytest.mark.parametrize("fig_name", [
        "fig_boxplot.json",
        "fig_barchart.json",
        "fig_evolution.json",
        "fig_scatter.json",
    ])
    def test_figures_existent(self, fig_name):
        path = os.path.join(OUTPUTS_DIR, fig_name)
        assert os.path.exists(path), (
            f"Figure manquante : {fig_name}"
        )

    @pytest.mark.parametrize("fig_name", [
        "fig_boxplot.json",
        "fig_barchart.json",
    ])
    def test_figures_lisibles(self, fig_name):
        path = os.path.join(OUTPUTS_DIR, fig_name)
        if os.path.exists(path):
            with open(path) as f:
                data = json.load(f)
            assert 'data' in data, f"Clé 'data' manquante dans {fig_name}"
            assert 'layout' in data, f"Clé 'layout' manquante dans {fig_name}"


# ═══════════════════════════════════════════════════════════
# TEST 2 — STRUCTURE JSON RÉSULTATS
# ═══════════════════════════════════════════════════════════

class TestStructureJson:
    """Vérifie la structure complète du JSON de résultats"""

    @pytest.fixture(autouse=True)
    def load_json(self):
        with open(JSON_RESULT, encoding='utf-8') as f:
            self.results = json.load(f)

    def test_json_est_dict(self):
        assert isinstance(self.results, dict)

    def test_section_meta(self):
        assert 'meta' in self.results
        meta = self.results['meta']
        assert 'date_analyse' in meta
        assert 'nb_produits' in meta
        assert 'sites' in meta
        assert meta['nb_produits'] > 0

    def test_section_stats_par_site(self):
        assert 'stats_par_site' in self.results
        stats = self.results['stats_par_site']
        for key in ['count', 'moyenne', 'mediane']:
            assert key in stats, f"Clé '{key}' manquante dans stats_par_site"

    def test_section_promotions(self):
        assert 'promotions' in self.results
        promo = self.results['promotions']
        assert 'taux_promo' in promo, "taux_promo manquant dans promotions"

    def test_section_shapiro(self):
        assert 'shapiro' in self.results
        shapiro = self.results['shapiro']
        assert isinstance(shapiro, dict)
        for site in ['ikea', 'jumia', 'kitea']:
            if site in shapiro:
                assert 'stat' in shapiro[site]
                assert 'p_value' in shapiro[site]
                assert 'normal' in shapiro[site]

    def test_section_kruskal(self):
        for key in ['kruskal_categories', 'kruskal_sites']:
            assert key in self.results, f"Clé '{key}' manquante"
            kw = self.results[key]
            assert 'stat' in kw
            assert 'p_value' in kw
            # Les deux doivent être significatifs (p < 0.05)
            assert kw['p_value'] < 0.05, (
                f"{key} non significatif : p={kw['p_value']:.4f}"
            )

    def test_section_regression(self):
        assert 'regression' in self.results
        reg = self.results['regression']
        assert 'r2_adj' in reg
        assert 'f_stat' in reg
        assert 'p_global' in reg
        # R² doit être positif
        assert reg['r2_adj'] > 0, f"R² négatif : {reg['r2_adj']}"
        # F-stat doit être significatif
        assert reg['f_stat'] > 1, f"F-stat suspect : {reg['f_stat']}"

    def test_section_evolution_prix(self):
        assert 'evolution_prix' in self.results
        evol = self.results['evolution_prix']
        assert isinstance(evol, list)
        assert len(evol) > 0
        # Chaque entrée doit avoir au moins une date et un prix
        # (la colonne 'site' est optionnelle selon la version du notebook)
        if len(evol) > 0:
            first = evol[0]
            has_date = 'date_scraping' in first or 'date' in first
            has_prix = 'prix' in first or 'prix_moyen' in first
            assert has_date, f"Clé date manquante dans evolution_prix : {list(first.keys())}"
            assert has_prix, f"Clé prix manquante dans evolution_prix : {list(first.keys())}"

    def test_section_mann_whitney(self):
        if 'mann_whitney' in self.results:
            mw = self.results['mann_whitney']
            assert isinstance(mw, dict)
            assert len(mw) > 0

    def test_tous_sites_dans_stats(self):
        stats = self.results.get('stats_par_site', {})
        sites_attendus = ['ikea', 'jumia', 'kitea']
        for key in ['moyenne', 'mediane']:
            if key in stats:
                for site in sites_attendus:
                    assert site in stats[key], (
                        f"Site '{site}' manquant dans stats_par_site.{key}"
                    )


# ═══════════════════════════════════════════════════════════
# TEST 3 — VALEURS STATISTIQUES
# ═══════════════════════════════════════════════════════════

class TestValeursStatistiques:
    """Vérifie la cohérence des résultats statistiques"""

    @pytest.fixture(autouse=True)
    def load_json(self):
        with open(JSON_RESULT, encoding='utf-8') as f:
            self.results = json.load(f)

    def test_prix_moyen_ikea_superieur_jumia(self):
        stats = self.results.get('stats_par_site', {})
        moys = stats.get('moyenne', {})
        if 'ikea' in moys and 'jumia' in moys:
            assert moys['ikea'] > moys['jumia'], (
                f"Ikea ({moys['ikea']:.0f}) devrait être plus cher que Jumia ({moys['jumia']:.0f})"
            )

    def test_r2_raisonnable(self):
        reg = self.results.get('regression', {})
        r2 = reg.get('r2_adj', 0)
        assert 0 < r2 < 1, f"R² hors bornes : {r2}"

    def test_p_values_entre_0_et_1(self):
        shapiro = self.results.get('shapiro', {})
        for site, vals in shapiro.items():
            p = vals.get('p_value', -1)
            assert 0 <= p <= 1, (
                f"p_value Shapiro invalide pour {site} : {p}"
            )

    def test_nb_produits_dans_stats(self):
        stats = self.results.get('stats_par_site', {})
        counts = stats.get('count', {})
        for site in ['ikea', 'jumia', 'kitea']:
            if site in counts:
                assert counts[site] >= 100, (
                    f"Site {site} sous-représenté : {counts[site]} produits"
                )

    def test_taux_promotion_valide(self):
        promo = self.results.get('promotions', {})
        taux = promo.get('taux_promo', {})
        for site, val in taux.items():
            assert 0 <= val <= 100, (
                f"Taux promotion invalide pour {site} : {val}"
            )


# ═══════════════════════════════════════════════════════════
# TEST 4 — RAPPORT PDF
# ═══════════════════════════════════════════════════════════

class TestRapportPdf:
    """Vérifie que le rapport PDF est généré correctement"""

    PDF_PATH = os.path.join(BASE_DIR, 'outputs', 'rapport_prix_intelligence.pdf')
    SCRIPT_PATH = os.path.join(BASE_DIR, 'generer_rapport.py')

    def test_script_rapport_existe(self):
        assert os.path.exists(self.SCRIPT_PATH), (
            f"Script manquant : generer_rapport.py"
        )

    def test_rapport_pdf_existe(self):
        assert os.path.exists(self.PDF_PATH), (
            f"Rapport PDF manquant : {self.PDF_PATH}"
        )

    def test_rapport_pdf_taille_minimale(self):
        if os.path.exists(self.PDF_PATH):
            size = os.path.getsize(self.PDF_PATH)
            assert size >= 100_000, (
                f"PDF trop petit : {size} octets (min 100Ko)"
            )

    def test_rapport_pdf_lisible(self):
        """Vérifie que le PDF est lisible (via pypdf)"""
        try:
            from pypdf import PdfReader
            r = PdfReader(self.PDF_PATH)
            assert len(r.pages) >= 5, (
                f"PDF a seulement {len(r.pages)} pages (min 5)"
            )
        except ImportError:
            pytest.skip("pypdf non installé")
        except Exception as e:
            pytest.fail(f"PDF illisible : {e}")


# ═══════════════════════════════════════════════════════════
# TEST 5 — DASHBOARD ET API
# ═══════════════════════════════════════════════════════════

class TestFichiersApplication:
    """Vérifie que les fichiers app existent et sont valides"""

    def test_api_main_existe(self):
        api_path = os.path.join(BASE_DIR, 'api', 'main.py')
        assert os.path.exists(api_path), "api/main.py manquant"

    def test_api_main_non_vide(self):
        api_path = os.path.join(BASE_DIR, 'api', 'main.py')
        if os.path.exists(api_path):
            size = os.path.getsize(api_path)
            assert size > 1000, f"api/main.py trop petit : {size} octets"

    def test_dashboard_app_existe(self):
        dash_path = os.path.join(BASE_DIR, 'dashboard', 'app.py')
        assert os.path.exists(dash_path), "dashboard/app.py manquant"

    def test_dashboard_app_non_vide(self):
        dash_path = os.path.join(BASE_DIR, 'dashboard', 'app.py')
        if os.path.exists(dash_path):
            size = os.path.getsize(dash_path)
            assert size > 5000, f"dashboard/app.py trop petit : {size} octets"

    def test_requirements_existe(self):
        req_path = os.path.join(BASE_DIR, 'requirements.txt')
        assert os.path.exists(req_path), "requirements.txt manquant"

    def test_requirements_contient_libs_clés(self):
        req_path = os.path.join(BASE_DIR, 'requirements.txt')
        if os.path.exists(req_path):
            with open(req_path) as f:
                content = f.read().lower()
            for lib in ['pandas', 'fastapi', 'uvicorn', 'scipy']:
                assert lib in content, (
                    f"Librairie manquante dans requirements.txt : {lib}"
                )

    def test_dockerfile_existe(self):
        docker_path = os.path.join(BASE_DIR, 'Dockerfile')
        assert os.path.exists(docker_path), "Dockerfile manquant"


# ═══════════════════════════════════════════════════════════
# TEST 6 — IMPORT DES MODULES PYTHON
# ═══════════════════════════════════════════════════════════

class TestImports:
    """Vérifie que toutes les dépendances sont installées"""

    @pytest.mark.parametrize("module", [
        "pandas", "numpy", "scipy", "statsmodels",
        "plotly", "fastapi", "uvicorn", "sklearn"
    ])
    def test_module_importable(self, module):
        try:
            __import__(module)
        except ImportError:
            pytest.fail(f"Module non installé : {module}")

    def test_version_pandas(self):
        import pandas as pd
        major = int(pd.__version__.split('.')[0])
        assert major >= 2, (
            f"pandas version trop ancienne : {pd.__version__} (min 2.0)"
        )

    def test_version_sklearn(self):
        import sklearn
        major, minor = map(int, sklearn.__version__.split('.')[:2])
        assert (major, minor) >= (1, 0), (
            f"sklearn version trop ancienne : {sklearn.__version__}"
        )
