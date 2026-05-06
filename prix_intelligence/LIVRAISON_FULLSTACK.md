# 📦 Data Analyst → Fullstack Handoff
**Projet : Price Intelligence — Kitea · Jumia · Ikea**
**Date : 2026-04-25**
**Version : 2.0**

## 🔗 API Endpoints disponibles

Base URL : `http://<IP_DATA_ANALYST>:8000`

| Endpoint | Méthode | Description | Exemple réponse |
|----------|---------|-------------|-----------------|
| `/` | GET | Liste tous les endpoints | `{"api": "Prix Intelligence..."}` |
| `/stats` | GET | Stats globales par site | moyenne, médiane, min, max |
| `/stats/categories` | GET | Stats par catégorie | par Salon, Chambre, etc. |
| `/stats/sites` | GET | Stats site × catégorie | croisement complet |
| `/tests` | GET | Résultats tests statistiques | Shapiro, Kruskal, Mann-Whitney |
| `/regression` | GET | Régression linéaire | R², coefficients |
| `/promotions` | GET | Analyse des promotions | taux, remise moyenne |
| `/evolution` | GET | Évolution prix 30 jours | série temporelle par site |
| `/anomalies` | GET | Anomalies de prix détectées | variations > 20% |
| `/figure/boxplot` | GET | Graphique Plotly JSON | prêt à afficher |
| `/figure/barchart` | GET | Graphique Plotly JSON | prêt à afficher |
| `/figure/evolution` | GET | Graphique Plotly JSON | prêt à afficher |
| `/figure/scatter` | GET | Graphique Plotly JSON | prêt à afficher |

## 📊 Données disponibles

- **2 647 produits** nettoyés et analysés
- **3 sites** : Ikea, Jumia, Kitea
- **5 catégories** : Salon, Chambre, Salle à Manger, Rangement, Mobilier Pro
- **30 jours** d'historique de prix

## 🖥️ Comment afficher un graphique Plotly

```javascript
// Installer : npm install plotly.js
import Plotly from 'plotly.js'

fetch('http://<IP>:8000/figure/boxplot')
  .then(r => r.json())
  .then(fig => Plotly.newPlot('mon-div', fig.data, fig.layout))
```

## ⚙️ Format des données

### /stats
```json
{
  "stats_par_site": {
    "moyenne": {"ikea": 4230, "jumia": 1306, "kitea": 3190},
    "mediane": {"ikea": 2697, "jumia": 850,  "kitea": 2295}
  }
}
```

### /evolution
```json
[
  {"site": "ikea",  "date_scraping": "2026-03-25", "prix": 4180.5},
  {"site": "jumia", "date_scraping": "2026-03-25", "prix": 1290.3}
]
```

### /anomalies
```json
[
  {"nom": "Canapé Donna", "site": "kitea", 
   "categorie": "Salon Et Sejour", "variation_max_pct": 25.3}
]
```

## 🐳 Lancer via Docker

```bash
docker pull prix-intelligence:2.0
docker run -d -p 8000:8000 --name prix-api prix-intelligence:2.0
```

## 📞 Contact Data Analyst

En cas de problème avec l'API, contacter le Data Analyst.
