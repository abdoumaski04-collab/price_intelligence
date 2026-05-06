# ÉTAPE 15 — MACHINE LEARNING PRÉDICTION DES PRIX
# À ajouter au notebook analyse_prix_intelligence.ipynb après l'export JSON

print("""
╔══════════════════════════════════════════════════════════════╗
║      ÉTAPE 15 — MACHINE LEARNING PRÉDICTION DES PRIX       ║
║      Random Forest + Linear Regression                       ║
╚══════════════════════════════════════════════════════════════╝
""")

# Imports ML
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# ════════════════════════════════════════════════════════════════
# PRÉPARATION DES FEATURES
# ════════════════════════════════════════════════════════════════

print("Préparation des features pour ML...")

df_ml = df_clean.copy()
df_ml['remise_pct'] = df_ml['remise_pct'].fillna(0)
df_ml['ancien_prix'] = df_ml['ancien_prix'].fillna(df_ml['prix'].mean())

# Encoder catégories
le_site = LabelEncoder()
le_cat = LabelEncoder()
df_ml['site_enc'] = le_site.fit_transform(df_ml['site'])
df_ml['cat_enc'] = le_cat.fit_transform(df_ml['categorie'])

# Jour de la semaine (depuis historique si possible)
if len(df_hist) > 0:
    df_hist_moy = df_hist.groupby('product_id')['date_scraping'].first().reset_index()
    df_ml = df_ml.merge(df_hist_moy, on='product_id', how='left', suffixes=('', '_hist'))
    df_ml['date_scraping'] = pd.to_datetime(df_ml['date_scraping'], errors='coerce')
    df_ml['jour_semaine'] = df_ml['date_scraping'].dt.dayofweek + 1
    df_ml['jour_semaine'] = df_ml['jour_semaine'].fillna(3)
else:
    df_ml['jour_semaine'] = 3

# Features log (aide la régression)
df_ml['prix_log'] = np.log1p(df_ml['prix'])
df_ml['ancien_prix_log'] = np.log1p(df_ml['ancien_prix'])
df_ml['ratio_prix'] = df_ml['prix'] / (df_ml['ancien_prix'] + 1)

# Features finales
feature_cols = [
    'site_enc', 'cat_enc', 'remise_pct',
    'ancien_prix', 'jour_semaine',
    'prix_log', 'ancien_prix_log', 'ratio_prix'
]

X = df_ml[feature_cols].copy()
y = df_ml['prix'].copy()

# Nettoyer NaN
mask = ~(X.isna().any(axis=1) | y.isna())
X = X[mask]
y = y[mask]

print(f"✅ {len(X):,} observations valides pour l'entraînement")
print(f"   Features : {', '.join(feature_cols)}")

# ════════════════════════════════════════════════════════════════
# SPLIT DONNÉES
# ════════════════════════════════════════════════════════════════

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

print(f"\nSplit données :")
print(f"  Entraînement : {len(X_train):,}")
print(f"  Test         : {len(X_test):,}")

# ════════════════════════════════════════════════════════════════
# RANDOM FOREST
# ════════════════════════════════════════════════════════════════

print("\n🌳 Entraînement Random Forest (100 arbres)...")

rf_model = RandomForestRegressor(
    n_estimators=100,
    max_depth=20,
    min_samples_split=5,
    min_samples_leaf=2,
    random_state=42,
    n_jobs=-1
)
rf_model.fit(X_train, y_train)

y_pred_rf = rf_model.predict(X_test)
mae_rf = mean_absolute_error(y_test, y_pred_rf)
rmse_rf = np.sqrt(mean_squared_error(y_test, y_pred_rf))
r2_rf = r2_score(y_test, y_pred_rf)

print(f"  MAE  : ± {mae_rf:.2f} MAD")
print(f"  RMSE : ± {rmse_rf:.2f} MAD")
print(f"  R²   : {r2_rf:.4f}")

# Feature importance
feature_imp = pd.DataFrame({
    'feature': feature_cols,
    'importance': rf_model.feature_importances_
}).sort_values('importance', ascending=False)

print("\n  Top 5 features :")
for idx, row in feature_imp.head(5).iterrows():
    print(f"    {row['feature']:20} : {row['importance']:.3f}")

# ════════════════════════════════════════════════════════════════
# LINEAR REGRESSION (BASELINE)
# ════════════════════════════════════════════════════════════════

print("\n📊 Entraînement Linear Regression (baseline)...")

lr_model = LinearRegression()
lr_model.fit(X_train, y_train)

y_pred_lr = lr_model.predict(X_test)
mae_lr = mean_absolute_error(y_test, y_pred_lr)
rmse_lr = np.sqrt(mean_squared_error(y_test, y_pred_lr))
r2_lr = r2_score(y_test, y_pred_lr)

print(f"  MAE  : ± {mae_lr:.2f} MAD")
print(f"  RMSE : ± {rmse_lr:.2f} MAD")
print(f"  R²   : {r2_lr:.4f}")

# Meilleur modèle
best_model = 'random_forest' if r2_rf > r2_lr else 'linear_regression'
best_mae = mae_rf if r2_rf > r2_lr else mae_lr
best_r2 = r2_rf if r2_rf > r2_lr else r2_lr

print(f"\n✅ Meilleur modèle : {best_model.upper()}")
print(f"   R² = {best_r2:.4f} (explique {best_r2*100:.1f}% de la variance)")

# ════════════════════════════════════════════════════════════════
# FONCTION DE PRÉDICTION
# ════════════════════════════════════════════════════════════════

def predict_price(site, categorie, remise_pct=0, ancien_prix=None):
    """Prédit le prix demain"""
    
    if ancien_prix is None:
        ancien_prix = y_train.mean()
    
    # Features
    site_e = le_site.transform([site])[0]
    cat_e = le_cat.transform([categorie])[0]
    jour = 3  # Mercredi par défaut
    p_log = np.log1p(ancien_prix * (1 - remise_pct/100) if remise_pct > 0 else ancien_prix)
    ap_log = np.log1p(ancien_prix)
    ratio = (ancien_prix * (1 - remise_pct/100)) / (ancien_prix + 1) if ancien_prix > 0 else 1
    
    X_new = np.array([[site_e, cat_e, remise_pct, ancien_prix, jour, p_log, ap_log, ratio]])
    
    if best_model == 'random_forest':
        pred = rf_model.predict(X_new)[0]
    else:
        pred = lr_model.predict(X_new)[0]
    
    pred = max(pred, 100)  # Minimum 100 MAD
    
    return {
        'prix_predit': round(pred, 0),
        'marge_erreur': round(best_mae, 0),
        'intervalle': [round(pred - best_mae, 0), round(pred + best_mae, 0)],
        'r2': round(best_r2, 4),
    }

# ════════════════════════════════════════════════════════════════
# EXEMPLES DE PRÉDICTIONS
# ════════════════════════════════════════════════════════════════

print("\n" + "="*60)
print("EXEMPLES DE PRÉDICTIONS")
print("="*60)

examples = [
    {'site': 'kitea', 'categorie': 'Salon Et Sejour', 'remise_pct': 15},
    {'site': 'jumia', 'categorie': 'Chambre Adulte', 'remise_pct': 25},
    {'site': 'ikea', 'categorie': 'Rangement', 'remise_pct': 0},
]

predictions = []
for ex in examples:
    pred = predict_price(**ex)
    predictions.append(pred)
    
    print(f"\n{ex['site'].upper()} - {ex['categorie']}")
    print(f"  Remise      : {ex['remise_pct']}%")
    print(f"  Prédiction  : {pred['prix_predit']:,} MAD")
    print(f"  Intervalle  : [{pred['intervalle'][0]:,}, {pred['intervalle'][1]:,}] MAD")
    print(f"  Confiance   : {'HAUTE' if pred['marge_erreur'] < 200 else 'MOYEN'}")

# ════════════════════════════════════════════════════════════════
# EXPORT RÉSULTATS ML
# ════════════════════════════════════════════════════════════════

ml_results = {
    'modeles': {
        'random_forest': {
            'mae': float(mae_rf),
            'rmse': float(rmse_rf),
            'r2': float(r2_rf),
            'n_estimators': 100,
            'features': feature_cols,
        },
        'linear_regression': {
            'mae': float(mae_lr),
            'rmse': float(rmse_lr),
            'r2': float(r2_lr),
        },
    },
    'meilleur_modele': best_model,
    'feature_importance': feature_imp.set_index('feature')['importance'].round(4).to_dict(),
    'exemples_predictions': predictions,
}

with open(os.path.join(OUTPUTS_DIR, 'ml_results.json'), 'w', encoding='utf-8') as f:
    json.dump(ml_results, f, ensure_ascii=False, indent=2, default=str)

print(f"\n✅ ml_results.json sauvegardé")

# ════════════════════════════════════════════════════════════════
# AJOUT À ANALYSE_RESULTS.json
# ════════════════════════════════════════════════════════════════

# Charger le JSON existant
with open(os.path.join(OUTPUTS_DIR, 'analyse_results.json'), 'r', encoding='utf-8') as f:
    analysis = json.load(f)

# Ajouter ML
analysis['machine_learning'] = ml_results

# Sauvegarder
with open(os.path.join(OUTPUTS_DIR, 'analyse_results.json'), 'w', encoding='utf-8') as f:
    json.dump(analysis, f, ensure_ascii=False, indent=2, default=str)

print(f"✅ analyse_results.json mis à jour avec ML")

# Afficher résumé
print("\n" + "="*60)
print("✅ ÉTAPE 15 COMPLÉTÉE")
print("="*60)
print(f"""
Machine Learning Prédiction des Prix

Données d'entraînement : {len(X_train):,}
Données de test       : {len(X_test):,}

Meilleur modèle       : {best_model.upper()}
MAE (erreur moyenne)  : ± {best_mae:.0f} MAD
R² (variance expliqu.) : {best_r2:.4f}

Prêt pour l'API :
  GET /ml/predict?site=kitea&categorie=Salon&remise=15
  
Intégration Dashboard :
  Tab "Prédictions" affichera les estimations 30 jours
""")
