"""
Script de test API — Prix Intelligence
Data Analyst → validation avant livraison au Fullstack
"""
import requests
import json
import sys

BASE_URL = "http://localhost:8000"

def test_endpoint(nom, url, cle_attendue=None):
    """Teste un endpoint et affiche le résultat"""
    try:
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            data = r.json()
            if cle_attendue and cle_attendue not in str(data):
                print(f"  ⚠️  {nom} → OK mais clé '{cle_attendue}' manquante")
            else:
                print(f"  ✅ {nom} → {r.status_code} OK")
            return True
        else:
            print(f"  ❌ {nom} → {r.status_code} ERREUR")
            return False
    except requests.exceptions.ConnectionError:
        print(f"  ❌ {nom} → API non accessible (Docker pas lancé ?)")
        return False
    except Exception as e:
        print(f"  ❌ {nom} → Erreur: {e}")
        return False

def main():
    print("=" * 50)
    print("🧪 TEST API — Prix Intelligence")
    print("=" * 50)
    print(f"URL testée : {BASE_URL}")
    print()

    tests = [
        ("Accueil /",            f"{BASE_URL}/",                "Prix Intelligence"),
        ("Stats sites",          f"{BASE_URL}/stats",           "moyenne"),
        ("Stats catégories",     f"{BASE_URL}/stats/categories","moyenne"),
        ("Tests statistiques",   f"{BASE_URL}/tests",           "shapiro"),
        ("Régression",           f"{BASE_URL}/regression",      "r2"),
        ("Promotions",           f"{BASE_URL}/promotions",      "nb_promos"),
        ("Évolution 30j",        f"{BASE_URL}/evolution",       "prix"),
        ("Anomalies",            f"{BASE_URL}/anomalies",       None),
        ("Figure boxplot",       f"{BASE_URL}/figure/boxplot",  "data"),
        ("Figure barchart",      f"{BASE_URL}/figure/barchart", "data"),
        ("Figure évolution",     f"{BASE_URL}/figure/evolution","data"),
        ("Figure scatter",       f"{BASE_URL}/figure/scatter",  "data"),
    ]

    resultats = []
    for nom, url, cle in tests:
        ok = test_endpoint(nom, url, cle)
        resultats.append(ok)

    print()
    total = len(resultats)
    succes = sum(resultats)
    print("=" * 50)
    print(f"RÉSULTAT : {succes}/{total} endpoints OK")

    if succes == total:
        print("✅ API prête — livraison au Fullstack possible !")
    elif succes > total // 2:
        print("⚠️  API partiellement prête — vérifier les erreurs")
    else:
        print("❌ API non prête — vérifier Docker")
    print("=" * 50)

if __name__ == "__main__":
    main()
