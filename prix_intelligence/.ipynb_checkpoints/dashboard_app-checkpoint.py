"""
╔══════════════════════════════════════════════════════════════╗
║     DASHBOARD PRIX INTELLIGENCE — Streamlit v2.0            ║
║     Kitea · Jumia · Ikea — Meubles & Maison Maroc           ║
║     Data Analyst | Prof. Elaachak 2025-2026                 ║
╚══════════════════════════════════════════════════════════════╝
"""

import streamlit as st
import pandas as pd
import numpy as np
import json
import os
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy.stats import gaussian_kde
import warnings
warnings.filterwarnings('ignore')

# ══════════════════════════════════════════════════════════════
# CONFIGURATION STREAMLIT
# ══════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="Prix Intelligence — Kitea · Jumia · Ikea",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── THÈME COULEURS ────────────────────────────────────────────
COLORS = {
    'kitea' : '#E74C3C',
    'jumia' : '#F39C12',
    'ikea'  : '#0058A3',
}
COLORS_LIGHT = {
    'kitea' : '#FADBD8',
    'jumia' : '#FDEBD0',
    'ikea'  : '#D6EAF8',
}
SITES = ['ikea', 'jumia', 'kitea']

# ── CSS PERSONNALISÉ ──────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500;600&display=swap');

  /* Global */
  html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

  /* Header principal */
  .main-header {
    background: linear-gradient(135deg, #1A1A2E 0%, #16213E 50%, #0F3460 100%);
    padding: 2rem 2.5rem;
    border-radius: 16px;
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
  }
  .main-header::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -10%;
    width: 400px;
    height: 400px;
    background: radial-gradient(circle, rgba(231,76,60,0.15) 0%, transparent 70%);
    border-radius: 50%;
  }
  .main-header::after {
    content: '';
    position: absolute;
    bottom: -30%;
    left: 20%;
    width: 300px;
    height: 300px;
    background: radial-gradient(circle, rgba(0,88,163,0.2) 0%, transparent 70%);
    border-radius: 50%;
  }
  .header-title {
    font-family: 'Space Mono', monospace;
    font-size: 1.9rem;
    font-weight: 700;
    color: white;
    margin: 0;
    letter-spacing: -0.5px;
  }
  .header-sub {
    color: rgba(255,255,255,0.65);
    font-size: 0.95rem;
    margin-top: 0.3rem;
    font-weight: 300;
  }
  .site-badge {
    display: inline-block;
    padding: 4px 14px;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 600;
    margin-right: 8px;
    margin-top: 10px;
    letter-spacing: 0.5px;
  }
  .badge-kitea { background: #E74C3C; color: white; }
  .badge-jumia { background: #F39C12; color: white; }
  .badge-ikea  { background: #0058A3; color: white; }

  /* Metric cards */
  .metric-card {
    background: white;
    border: 1px solid #E8ECF0;
    border-radius: 14px;
    padding: 1.2rem 1.4rem;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    transition: transform 0.2s, box-shadow 0.2s;
    position: relative;
    overflow: hidden;
  }
  .metric-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(0,0,0,0.1);
  }
  .metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 4px;
    height: 100%;
    border-radius: 14px 0 0 14px;
  }
  .metric-card-red::before   { background: #E74C3C; }
  .metric-card-amber::before { background: #F39C12; }
  .metric-card-blue::before  { background: #0058A3; }
  .metric-card-green::before { background: #27AE60; }
  .metric-value {
    font-family: 'Space Mono', monospace;
    font-size: 2rem;
    font-weight: 700;
    color: #1A1A2E;
    line-height: 1;
    margin-bottom: 0.3rem;
  }
  .metric-label {
    font-size: 0.8rem;
    color: #7F8C8D;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }
  .metric-delta {
    font-size: 0.85rem;
    font-weight: 500;
    margin-top: 0.3rem;
  }
  .delta-up   { color: #27AE60; }
  .delta-down { color: #E74C3C; }

  /* Section titles */
  .section-title {
    font-family: 'Space Mono', monospace;
    font-size: 1.1rem;
    font-weight: 700;
    color: #1A1A2E;
    margin: 1.5rem 0 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid #E74C3C;
    display: inline-block;
  }

  /* Insight cards */
  .insight-card {
    background: linear-gradient(135deg, #EAF3DE, #F0FFF4);
    border: 1px solid #C3E6CB;
    border-left: 4px solid #27AE60;
    border-radius: 10px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.8rem;
  }
  .insight-title {
    font-weight: 600;
    color: #155724;
    font-size: 0.9rem;
    margin-bottom: 0.3rem;
  }
  .insight-text {
    color: #1E5631;
    font-size: 0.85rem;
    line-height: 1.5;
  }

  /* Alert cards */
  .alert-haute {
    background: #FDEDEC;
    border-left: 4px solid #E74C3C;
    border-radius: 8px;
    padding: 0.7rem 1rem;
    margin-bottom: 0.5rem;
    font-size: 0.85rem;
  }
  .alert-moyenne {
    background: #FEF9E7;
    border-left: 4px solid #F39C12;
    border-radius: 8px;
    padding: 0.7rem 1rem;
    margin-bottom: 0.5rem;
    font-size: 0.85rem;
  }

  /* Stat table */
  .stat-table {
    background: white;
    border-radius: 12px;
    border: 1px solid #E8ECF0;
    overflow: hidden;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  }

  /* Sidebar */
  .sidebar-section {
    background: #F8F9FA;
    border-radius: 10px;
    padding: 1rem;
    margin-bottom: 1rem;
  }
  .sidebar-title {
    font-family: 'Space Mono', monospace;
    font-size: 0.75rem;
    font-weight: 700;
    color: #7F8C8D;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    margin-bottom: 0.7rem;
  }

  /* Hide streamlit default */
  #MainMenu {visibility: hidden;}
  footer {visibility: hidden;}
  .stDeployButton {display:none;}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# CHARGEMENT DES DONNÉES
# ══════════════════════════════════════════════════════════════

@st.cache_data
def load_data():
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    df = pd.read_csv(os.path.join(base, 'data', 'clean', 'clean_prices.csv'))
    df_h = pd.read_csv(os.path.join(base, 'data', 'raw', 'historique_prices.csv'),
        parse_dates=['date_scraping'])
    with open(os.path.join(base, 'outputs', 'analyse_results.json'), encoding='utf-8') as f:
        results = json.load(f)

    # Alertes si disponibles
    alertes_path = os.path.join(base, 'outputs', 'alertes.json')
    alertes = []
    if os.path.exists(alertes_path):
        with open(alertes_path, encoding='utf-8') as f:
            alertes = json.load(f)

    for col in ['prix', 'ancien_prix', 'remise_pct']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df['en_promotion'] = df['en_promotion'].fillna(False).astype(bool)
    return df, df_h, results, alertes


df_all, df_hist, results, alertes = load_data()


# ══════════════════════════════════════════════════════════════
# SIDEBAR — FILTRES
# ══════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:1rem 0 0.5rem">
      <span style="font-family:'Space Mono',monospace;font-size:1.1rem;font-weight:700;color:#1A1A2E">
        📊 Prix Intelligence
      </span><br>
      <span style="font-size:0.75rem;color:#7F8C8D">Dashboard v2.0</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    st.markdown('<div class="sidebar-title">🏪 Sites</div>', unsafe_allow_html=True)
    sites_sel = []
    cols_s = st.columns(3)
    site_defaults = {'ikea': True, 'jumia': True, 'kitea': True}
    for i, site in enumerate(SITES):
        with cols_s[i]:
            checked = st.checkbox(site.capitalize(), value=True, key=f'site_{site}')
            if checked:
                sites_sel.append(site)
    if not sites_sel:
        sites_sel = SITES.copy()

    st.markdown("---")

    st.markdown('<div class="sidebar-title">🗂️ Catégories</div>', unsafe_allow_html=True)
    cats_all = sorted(df_all['categorie'].unique())
    cats_sel = st.multiselect("", cats_all, default=cats_all, label_visibility='collapsed')
    if not cats_sel:
        cats_sel = cats_all

    st.markdown("---")

    st.markdown('<div class="sidebar-title">💰 Gamme de prix (MAD)</div>', unsafe_allow_html=True)
    prix_min = int(df_all['prix'].min())
    prix_max = int(df_all['prix'].max())
    prix_range = st.slider("", prix_min, prix_max, (prix_min, prix_max),
        label_visibility='collapsed', step=100)

    st.markdown("---")

    st.markdown('<div class="sidebar-title">⚙️ Options</div>', unsafe_allow_html=True)
    show_promos_only = st.toggle("En promotion uniquement", False)
    show_anomalies   = st.toggle("Afficher anomalies", True)

    st.markdown("---")
    st.markdown(f"""
    <div style="font-size:0.75rem;color:#B0B8C1;text-align:center">
      Données : {results['meta']['date_analyse']}<br>
      Source : Google Cloud Bigtable<br>
      <span style="color:#27AE60">● Production ready</span>
    </div>
    """, unsafe_allow_html=True)

# ── FILTRE LES DONNÉES ────────────────────────────────────────
df = df_all[
    df_all['site'].isin(sites_sel) &
    df_all['categorie'].isin(cats_sel) &
    (df_all['prix'] >= prix_range[0]) &
    (df_all['prix'] <= prix_range[1])
].copy()
if show_promos_only:
    df = df[df['en_promotion'] == True]

df_h_fil = df_hist[df_hist['site'].isin(sites_sel)]


# ══════════════════════════════════════════════════════════════
# HEADER PRINCIPAL
# ══════════════════════════════════════════════════════════════

st.markdown("""
<div class="main-header">
  <p class="header-title">📊 Prix Intelligence Dashboard</p>
  <p class="header-sub">Analyse des prix Meubles & Maison — Maroc · Real-Time E-commerce Platform</p>
  <div>
    <span class="site-badge badge-kitea">🔴 KITEA</span>
    <span class="site-badge badge-jumia">🟡 JUMIA</span>
    <span class="site-badge badge-ikea">🔵 IKEA</span>
  </div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# KPIs PRINCIPAUX
# ══════════════════════════════════════════════════════════════

k1, k2, k3, k4, k5 = st.columns(5)

with k1:
    st.markdown(f"""
    <div class="metric-card metric-card-blue">
      <div class="metric-value">{len(df):,}</div>
      <div class="metric-label">Produits analysés</div>
      <div class="metric-delta delta-up">↑ {len(sites_sel)} sites actifs</div>
    </div>
    """, unsafe_allow_html=True)

with k2:
    prix_moy = df['prix'].mean()
    st.markdown(f"""
    <div class="metric-card metric-card-red">
      <div class="metric-value">{prix_moy:,.0f}</div>
      <div class="metric-label">Prix moyen (MAD)</div>
      <div class="metric-delta">Médiane : {df['prix'].median():,.0f} MAD</div>
    </div>
    """, unsafe_allow_html=True)

with k3:
    pct_promo = df['en_promotion'].mean() * 100
    nb_promo  = df['en_promotion'].sum()
    st.markdown(f"""
    <div class="metric-card metric-card-amber">
      <div class="metric-value">{pct_promo:.1f}%</div>
      <div class="metric-label">En promotion</div>
      <div class="metric-delta delta-up">↑ {nb_promo:,} produits soldés</div>
    </div>
    """, unsafe_allow_html=True)

with k4:
    remise_moy = df[df['remise_pct'] > 0]['remise_pct'].mean()
    st.markdown(f"""
    <div class="metric-card metric-card-green">
      <div class="metric-value">{remise_moy:.1f}%</div>
      <div class="metric-label">Remise moyenne</div>
      <div class="metric-delta">Sur produits en promo</div>
    </div>
    """, unsafe_allow_html=True)

with k5:
    nb_cats = len(cats_sel)
    st.markdown(f"""
    <div class="metric-card metric-card-blue">
      <div class="metric-value">{nb_cats}</div>
      <div class="metric-label">Catégories</div>
      <div class="metric-delta">{len(sites_sel)} sites comparés</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# ONGLETS PRINCIPAUX
# ══════════════════════════════════════════════════════════════

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Vue Générale",
    "📈 Évolution des Prix",
    "🔬 Tests Statistiques",
    "🎯 Segmentation",
    "🚨 Alertes",
    "🔍 Explorer les Données",
])


# ══════════════════════════════════════════════════════════════
# ONGLET 1 — VUE GÉNÉRALE
# ══════════════════════════════════════════════════════════════

with tab1:
    col_l, col_r = st.columns([3, 2])

    with col_l:
        st.markdown('<div class="section-title">Distribution des Prix</div>', unsafe_allow_html=True)

        # Boxplot interactif
        fig_box = px.box(
            df, x='categorie', y='prix', color='site',
            color_discrete_map=COLORS,
            labels={'prix': 'Prix (MAD)', 'categorie': 'Catégorie', 'site': 'Site'},
            template='plotly_white',
            hover_data=['nom'] if 'nom' in df.columns else None,
        )
        fig_box.update_layout(
            height=380, margin=dict(l=10,r=10,t=10,b=10),
            legend=dict(orientation='h', yanchor='bottom', y=1.02),
            font=dict(family='DM Sans'),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
        )
        fig_box.update_xaxes(showgrid=False)
        fig_box.update_yaxes(gridcolor='#F0F0F0')
        st.plotly_chart(fig_box, use_container_width=True)

        # Bar chart prix moyen
        st.markdown('<div class="section-title">Prix Moyen par Catégorie</div>', unsafe_allow_html=True)
        prix_moy_cat = df.groupby(['categorie','site'])['prix'].mean().round(0).reset_index()
        fig_bar = px.bar(
            prix_moy_cat, x='categorie', y='prix', color='site',
            barmode='group', color_discrete_map=COLORS,
            labels={'prix':'Prix Moyen (MAD)', 'categorie':'Catégorie'},
            template='plotly_white', text='prix',
        )
        fig_bar.update_traces(texttemplate='%{text:.0f}', textposition='outside',
            textfont=dict(size=9))
        fig_bar.update_layout(
            height=370, margin=dict(l=10,r=10,t=20,b=10),
            legend=dict(orientation='h', yanchor='bottom', y=1.02),
            font=dict(family='DM Sans'),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
        )
        fig_bar.update_xaxes(showgrid=False)
        fig_bar.update_yaxes(gridcolor='#F0F0F0')
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_r:
        st.markdown('<div class="section-title">Stats par Site</div>', unsafe_allow_html=True)

        # Stats cards par site
        for site in sites_sel:
            d = df[df['site'] == site]['prix']
            if len(d) == 0:
                continue
            col = COLORS[site]
            col_light = COLORS_LIGHT[site]
            promo_site = df[df['site']==site]['en_promotion'].mean()*100
            st.markdown(f"""
            <div style="background:linear-gradient(135deg,{col_light},{col_light}88);
              border:1px solid {col}44;border-left:4px solid {col};
              border-radius:12px;padding:1rem 1.2rem;margin-bottom:0.8rem">
              <div style="display:flex;justify-content:space-between;align-items:center">
                <span style="font-weight:700;color:{col};font-size:1rem">
                  {'🔴' if site=='kitea' else '🟡' if site=='jumia' else '🔵'} {site.upper()}
                </span>
                <span style="font-size:0.75rem;background:{col};color:white;
                  padding:2px 8px;border-radius:10px">{len(d):,} produits</span>
              </div>
              <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:0.8rem">
                <div>
                  <div style="font-size:1.3rem;font-weight:700;color:#1A1A2E">{d.mean():,.0f} MAD</div>
                  <div style="font-size:0.7rem;color:#7F8C8D;text-transform:uppercase">Moyenne</div>
                </div>
                <div>
                  <div style="font-size:1.3rem;font-weight:700;color:#1A1A2E">{d.median():,.0f} MAD</div>
                  <div style="font-size:0.7rem;color:#7F8C8D;text-transform:uppercase">Médiane</div>
                </div>
                <div>
                  <div style="font-size:1rem;font-weight:600;color:#1A1A2E">{d.min():,.0f} — {d.max():,.0f}</div>
                  <div style="font-size:0.7rem;color:#7F8C8D;text-transform:uppercase">Min — Max</div>
                </div>
                <div>
                  <div style="font-size:1rem;font-weight:600;color:#27AE60">{promo_site:.1f}%</div>
                  <div style="font-size:0.7rem;color:#7F8C8D;text-transform:uppercase">En promo</div>
                </div>
              </div>
            </div>
            """, unsafe_allow_html=True)

        # Distribution KDE
        st.markdown('<div class="section-title">Distribution (KDE)</div>', unsafe_allow_html=True)
        fig_kde = go.Figure()
        for site in sites_sel:
            data = df[df['site']==site]['prix'].dropna()
            if len(data) < 5:
                continue
            kde = gaussian_kde(data)
            x_r = np.linspace(data.min(), min(data.max(), 12000), 300)
            fig_kde.add_trace(go.Scatter(
                x=x_r, y=kde(x_r), mode='lines', name=site.capitalize(),
                line=dict(color=COLORS[site], width=2.5),
                fill='tozeroy', fillcolor=COLORS[site].replace(')', ',0.08)').replace('rgb','rgba')
                    if 'rgb' in COLORS[site] else COLORS[site] + '14',
            ))
        fig_kde.update_layout(
            height=240, margin=dict(l=10,r=10,t=10,b=10),
            xaxis_title='Prix (MAD)', yaxis_title='Densité',
            legend=dict(orientation='h', yanchor='bottom', y=1.02),
            template='plotly_white', font=dict(family='DM Sans'),
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        )
        st.plotly_chart(fig_kde, use_container_width=True)

    # Promotions (bas de page)
    st.markdown('<div class="section-title">Analyse des Promotions</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)

    with c1:
        promo_data = df.groupby('site').agg(
            nb=('prix','count'), promos=('en_promotion','sum'),
            remise=('remise_pct','mean')).reset_index()
        promo_data['taux'] = promo_data['promos'] / promo_data['nb'] * 100

        fig_promo = px.bar(promo_data[promo_data['site'].isin(sites_sel)],
            x='site', y='taux', color='site',
            color_discrete_map=COLORS, text='taux',
            labels={'taux':'Taux promo (%)','site':'Site'},
            template='plotly_white')
        fig_promo.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        fig_promo.update_layout(height=300, showlegend=False,
            margin=dict(l=10,r=10,t=20,b=10), font=dict(family='DM Sans'),
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_promo, use_container_width=True)

    with c2:
        df_sc = df[df['ancien_prix'].notna() & (df['remise_pct']>0)].copy()
        if len(df_sc) > 0:
            fig_sc = px.scatter(
                df_sc.sample(min(500, len(df_sc))),
                x='ancien_prix', y='prix', color='site',
                size='remise_pct', color_discrete_map=COLORS,
                hover_data=['nom','categorie','remise_pct'] if 'nom' in df_sc.columns else None,
                labels={'ancien_prix':'Ancien Prix (MAD)','prix':'Prix Actuel (MAD)'},
                opacity=0.7, template='plotly_white',
            )
            max_p = df_sc['ancien_prix'].max()
            fig_sc.add_trace(go.Scatter(x=[0,max_p], y=[0,max_p], mode='lines',
                name='Pas de remise', line=dict(dash='dash', color='gray', width=1)))
            fig_sc.update_layout(height=300, margin=dict(l=10,r=10,t=20,b=10),
                font=dict(family='DM Sans'),
                plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_sc, use_container_width=True)
        else:
            st.info("Pas assez de données avec remise pour ce filtre.")


# ══════════════════════════════════════════════════════════════
# ONGLET 2 — ÉVOLUTION DES PRIX
# ══════════════════════════════════════════════════════════════

with tab2:
    st.markdown('<div class="section-title">Évolution du Prix Moyen — 30 Jours</div>',
        unsafe_allow_html=True)

    # Ligne temporelle principale
    evol = df_h_fil.groupby(['site','date_scraping'])['prix'].mean().round(2).reset_index()

    fig_evol = px.line(evol, x='date_scraping', y='prix', color='site',
        color_discrete_map=COLORS,
        labels={'prix':'Prix Moyen (MAD)','date_scraping':'Date'},
        template='plotly_white', markers=True,
    )
    fig_evol.update_traces(line=dict(width=2.5), marker=dict(size=4))
    fig_evol.update_layout(
        height=400, margin=dict(l=10,r=10,t=10,b=10),
        legend=dict(orientation='h', yanchor='bottom', y=1.02),
        font=dict(family='DM Sans'),
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=False), yaxis=dict(gridcolor='#F0F0F0'),
    )
    st.plotly_chart(fig_evol, use_container_width=True)

    # Métriques évolution
    col1, col2, col3 = st.columns(3)
    vel = results.get('velocity', {})
    for i, (col, site) in enumerate(zip([col1, col2, col3], SITES)):
        if site not in sites_sel or site not in vel:
            continue
        d = vel[site]
        with col:
            tendance_icon = '↗️' if 'HAUSSE' in d['tendance'] else '↘️' if 'BAISSE' in d['tendance'] else '→'
            color = '#27AE60' if 'BAISSE' in d['tendance'] else '#E74C3C' if 'HAUSSE' in d['tendance'] else '#7F8C8D'
            st.markdown(f"""
            <div class="metric-card" style="border-left:4px solid {COLORS[site]}">
              <div style="font-weight:700;color:{COLORS[site]};margin-bottom:0.5rem">
                {site.upper()} {tendance_icon}
              </div>
              <div style="font-size:1.2rem;font-weight:700;color:{color}">
                {d['variation_pct']:+.1f}% en 30j
              </div>
              <div style="font-size:0.8rem;color:#7F8C8D;margin-top:0.2rem">
                Pente : {d['pente_jour']:+.2f} MAD/jour
              </div>
              <div style="font-size:0.8rem;color:#7F8C8D">
                R² = {d['r_carre']:.3f}
              </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Évolution par catégorie (sélectionnable)
    st.markdown('<div class="section-title">Évolution par Catégorie</div>', unsafe_allow_html=True)
    cat_sel_evol = st.selectbox("Choisir une catégorie", cats_sel, key='cat_evol')

    df_h_cat = df_hist[
        df_hist['site'].isin(sites_sel) &
        (df_hist['categorie'] == cat_sel_evol)
    ].groupby(['site','date_scraping'])['prix'].mean().round(2).reset_index()

    if len(df_h_cat) > 0:
        fig_cat = px.line(df_h_cat, x='date_scraping', y='prix', color='site',
            color_discrete_map=COLORS,
            title=f'Évolution des prix — {cat_sel_evol}',
            labels={'prix':'Prix Moyen (MAD)','date_scraping':'Date'},
            template='plotly_white', markers=True,
        )
        fig_cat.update_layout(height=350, font=dict(family='DM Sans'),
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_cat, use_container_width=True)


# ══════════════════════════════════════════════════════════════
# ONGLET 3 — TESTS STATISTIQUES
# ══════════════════════════════════════════════════════════════

with tab3:
    c_left, c_right = st.columns(2)

    with c_left:
        # Intervalles de confiance
        st.markdown('<div class="section-title">Intervalles de Confiance 95%</div>',
            unsafe_allow_html=True)
        ic = results.get('intervalles_confiance', {})
        if ic:
            ic_data = []
            for site in sites_sel:
                if site in ic:
                    d = ic[site]
                    ic_data.append({
                        'Site': site.capitalize(),
                        'Moyenne': f"{d['moyenne']:,.0f} MAD",
                        'IC Inf.': f"{d['ic_low']:,.0f} MAD",
                        'IC Sup.': f"{d['ic_high']:,.0f} MAD",
                        'Marge ±': f"{d['marge']:,.0f} MAD",
                        'CV': f"{d['cv_pct']:.1f}%",
                    })
            if ic_data:
                st.dataframe(pd.DataFrame(ic_data), hide_index=True, use_container_width=True)

                # Graphique IC
                sites_ic  = [d['Site'] for d in ic_data]
                moys_ic   = [ic[s.lower()]['moyenne']  for s in sites_ic if s.lower() in ic]
                errs_ic   = [ic[s.lower()]['marge']    for s in sites_ic if s.lower() in ic]
                cols_ic   = [COLORS[s.lower()]         for s in sites_ic if s.lower() in ic]

                fig_ic = go.Figure(go.Bar(
                    x=sites_ic, y=moys_ic,
                    error_y=dict(type='data', array=errs_ic, visible=True, color='#555'),
                    marker_color=cols_ic, text=[f'{m:,.0f}' for m in moys_ic],
                    textposition='outside',
                ))
                fig_ic.update_layout(height=300, showlegend=False,
                    template='plotly_white', font=dict(family='DM Sans'),
                    plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                    yaxis_title='Prix (MAD)', margin=dict(l=10,r=10,t=20,b=10))
                st.plotly_chart(fig_ic, use_container_width=True)

        # Shapiro-Wilk
        st.markdown('<div class="section-title">Test Shapiro-Wilk (Normalité)</div>',
            unsafe_allow_html=True)
        shapiro = results.get('shapiro', {})
        for site in sites_sel:
            if site not in shapiro:
                continue
            d = shapiro[site]
            icon = '✅' if d['normal'] else '❌'
            msg = 'Distribution normale' if d['normal'] else 'Non normale → tests non-param.'
            st.markdown(f"""
            <div style="display:flex;justify-content:space-between;align-items:center;
              padding:0.5rem 0.8rem;margin-bottom:0.4rem;border-radius:8px;
              background:{'#EAF3DE' if d['normal'] else '#FDEDEC'}">
              <span style="font-weight:600;color:{COLORS[site]}">{site.capitalize()}</span>
              <span style="font-size:0.85rem">W = {d['stat']:.4f} | p = {d['p_value']:.6f}</span>
              <span>{icon} {msg}</span>
            </div>
            """, unsafe_allow_html=True)

    with c_right:
        # Kruskal-Wallis
        st.markdown('<div class="section-title">Tests de Kruskal-Wallis</div>',
            unsafe_allow_html=True)
        kw_cat  = results.get('kruskal_categories', {})
        kw_site = results.get('kruskal_sites', {})
        for label, kw in [('Entre Catégories', kw_cat), ('Entre Sites', kw_site)]:
            if not kw:
                continue
            sig = kw['p_value'] < 0.05
            st.markdown(f"""
            <div style="padding:0.8rem 1rem;margin-bottom:0.6rem;border-radius:10px;
              background:{'#EAF3DE' if sig else '#FDEDEC'};
              border-left:4px solid {'#27AE60' if sig else '#E74C3C'}">
              <div style="font-weight:600;margin-bottom:0.3rem">{label}</div>
              <div style="font-size:0.85rem">
                H = {kw['stat']:.4f} | p = {kw['p_value']:.2e}
              </div>
              <div style="font-size:0.85rem;margin-top:0.2rem">
                {'✅ Différences significatives (p<0.05)' if sig else '❌ Pas de différence significative'}
              </div>
            </div>
            """, unsafe_allow_html=True)

        # Power Analysis
        st.markdown('<div class="section-title">Power Analysis (Cohen\'s d)</div>',
            unsafe_allow_html=True)
        power = results.get('power_analysis', {})
        if power:
            for key, d in power.items():
                pair = key.replace('_vs_', ' vs ').upper()
                puissance = d['puissance'] * 100
                ok = puissance >= 80
                color_bar = '#27AE60' if ok else '#E74C3C'
                st.markdown(f"""
                <div style="padding:0.7rem 1rem;margin-bottom:0.5rem;
                  border-radius:10px;background:#F8F9FA;border:1px solid #E8ECF0">
                  <div style="display:flex;justify-content:space-between;align-items:center">
                    <span style="font-weight:600;font-size:0.85rem">{pair}</span>
                    <span style="font-size:0.8rem;background:{color_bar};color:white;
                      padding:2px 8px;border-radius:10px">
                      {'✅' if ok else '⚠️'} {puissance:.1f}%
                    </span>
                  </div>
                  <div style="margin-top:0.4rem">
                    <div style="height:6px;background:#E8ECF0;border-radius:3px">
                      <div style="height:6px;width:{min(puissance,100):.1f}%;
                        background:{color_bar};border-radius:3px"></div>
                    </div>
                  </div>
                  <div style="font-size:0.75rem;color:#7F8C8D;margin-top:0.3rem">
                    Cohen's d = {d['cohens_d']:.4f} ({d['taille_effet']}) |
                    n = {d['n_actuel']:,}
                  </div>
                </div>
                """, unsafe_allow_html=True)

        # Régression
        st.markdown('<div class="section-title">Régression Linéaire (OLS)</div>',
            unsafe_allow_html=True)
        reg = results.get('regression', {})
        if reg:
            st.markdown(f"""
            <div style="background:linear-gradient(135deg,#EFF6FF,#DBEAFE);
              border:1px solid #93C5FD;border-radius:12px;padding:1rem 1.2rem">
              <div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem">
                <div>
                  <div style="font-size:1.5rem;font-weight:700;color:#1D4ED8">
                    {reg['r2_adj']:.4f}
                  </div>
                  <div style="font-size:0.75rem;color:#3B82F6;text-transform:uppercase">
                    R² Ajusté
                  </div>
                </div>
                <div>
                  <div style="font-size:1.5rem;font-weight:700;color:#1D4ED8">
                    {reg['r2_adj']*100:.1f}%
                  </div>
                  <div style="font-size:0.75rem;color:#3B82F6;text-transform:uppercase">
                    Variance expliquée
                  </div>
                </div>
              </div>
              <div style="margin-top:0.8rem;font-size:0.85rem;color:#1E40AF">
                F = {reg['f_stat']:.2f} | p = {reg['p_global']:.6f}
              </div>
              <div style="margin-top:0.3rem;font-size:0.8rem;color:#3B82F6">
                Modèle : prix ~ site + catégorie + promotion
              </div>
            </div>
            """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# ONGLET 4 — SEGMENTATION
# ══════════════════════════════════════════════════════════════

with tab4:
    st.markdown('<div class="section-title">Segmentation par Gamme de Prix</div>',
        unsafe_allow_html=True)

    gammes = ['Entrée (<500)', 'Économique (500-1500)',
              'Milieu (1500-4000)', 'Premium (4000-10k)', 'Luxe (>10k)']

    gamme_data = []
    for g in gammes:
        for site in sites_sel:
            n = len(df[(df['gamme_prix']==g) & (df['site']==site)])
            gamme_data.append({'Gamme':g, 'Site':site.capitalize(), 'Count':n})
    df_gamme = pd.DataFrame(gamme_data)

    fig_seg = px.bar(df_gamme, x='Gamme', y='Count', color='Site',
        barmode='group', color_discrete_map={s.capitalize():COLORS[s] for s in SITES},
        text='Count', template='plotly_white',
        labels={'Count':'Nb produits','Gamme':'Gamme de prix'})
    fig_seg.update_traces(textposition='outside')
    fig_seg.update_layout(height=380, font=dict(family='DM Sans'),
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        legend=dict(orientation='h', yanchor='bottom', y=1.02),
        margin=dict(l=10,r=10,t=20,b=10))
    st.plotly_chart(fig_seg, use_container_width=True)

    # Tableau croisé
    st.markdown('<div class="section-title">Tableau croisé Gamme × Site</div>',
        unsafe_allow_html=True)
    pivot = df.groupby(['gamme_prix','site'])['prix'].agg(
        count='count', moy='mean', med='median').round(0)
    pivot.columns = ['N produits', 'Prix moyen', 'Prix médian']
    st.dataframe(pivot, use_container_width=True)

    # Matrice corrélation
    st.markdown('<div class="section-title">Matrice de Corrélation Spearman</div>',
        unsafe_allow_html=True)
    df_c = df[['prix','ancien_prix','remise_pct']].copy()
    df_c['en_promo'] = df['en_promotion'].astype(int)
    df_c = df_c.dropna()
    if len(df_c) > 5:
        df_c.columns = ['Prix','Ancien Prix','Remise %','En Promo']
        corr = df_c.corr(method='spearman')
        fig_corr = px.imshow(corr, text_auto='.2f',
            color_continuous_scale='RdBu_r', zmin=-1, zmax=1,
            template='plotly_white', aspect='auto')
        fig_corr.update_layout(height=350, font=dict(family='DM Sans'),
            margin=dict(l=10,r=10,t=10,b=10))
        st.plotly_chart(fig_corr, use_container_width=True)


# ══════════════════════════════════════════════════════════════
# ONGLET 5 — ALERTES
# ══════════════════════════════════════════════════════════════

with tab5:
    st.markdown('<div class="section-title">🚨 Système d\'Alertes Intelligentes</div>',
        unsafe_allow_html=True)

    alertes_fil = [a for a in alertes if a.get('site','') in sites_sel]

    if alertes_fil:
        # Résumé
        nb_haute  = sum(1 for a in alertes_fil if a.get('priorite')=='HAUTE')
        nb_moy    = sum(1 for a in alertes_fil if a.get('priorite')=='MOYENNE')
        nb_baisse = sum(1 for a in alertes_fil if a.get('type_alerte')=='BAISSE_FORTE')
        nb_hausse = sum(1 for a in alertes_fil if a.get('type_alerte')=='HAUSSE_FORTE')

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("🔴 Priorité HAUTE", nb_haute)
        with col2:
            st.metric("🟡 Priorité MOYENNE", nb_moy)
        with col3:
            st.metric("📉 Baisses fortes", nb_baisse)
        with col4:
            st.metric("📈 Hausses fortes", nb_hausse)

        st.markdown("<br>", unsafe_allow_html=True)

        # Filtres alertes
        type_filtre = st.selectbox("Filtrer par type",
            ['TOUS','BAISSE_FORTE','HAUSSE_FORTE','ANOMALIE_STAT'])
        prio_filtre = st.selectbox("Filtrer par priorité", ['TOUS','HAUTE','MOYENNE'])

        alertes_show = alertes_fil
        if type_filtre != 'TOUS':
            alertes_show = [a for a in alertes_show if a.get('type_alerte')==type_filtre]
        if prio_filtre != 'TOUS':
            alertes_show = [a for a in alertes_show if a.get('priorite')==prio_filtre]

        st.markdown(f"**{len(alertes_show)} alertes affichées**")

        for a in alertes_show[:20]:
            prio = a.get('priorite','')
            typ  = a.get('type_alerte','')
            var  = a.get('variation_pct', 0)
            site = a.get('site','')
            color_class = 'alert-haute' if prio=='HAUTE' else 'alert-moyenne'
            icon = '📉' if 'BAISSE' in typ else '📈' if 'HAUSSE' in typ else '⚠️'
            st.markdown(f"""
            <div class="{color_class}">
              <div style="display:flex;justify-content:space-between;align-items:center">
                <span><b>{icon} {a.get('nom','')[:40]}</b></span>
                <span style="font-size:0.8rem;color:{COLORS.get(site,'#999')};font-weight:600">
                  {site.upper()}
                </span>
              </div>
              <div style="font-size:0.8rem;color:#555;margin-top:0.2rem">
                {a.get('categorie','')} · {typ} · Variation : <b>{var:+.1f}%</b> ·
                {a.get('message','')}
              </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Aucune alerte pour les filtres sélectionnés. "
            "Lancez d'abord le notebook pour générer les alertes.")


# ══════════════════════════════════════════════════════════════
# ONGLET 6 — EXPLORER LES DONNÉES
# ══════════════════════════════════════════════════════════════

with tab6:
    st.markdown('<div class="section-title">🔍 Explorateur de Données</div>',
        unsafe_allow_html=True)

    col_s, col_c, col_p = st.columns(3)
    with col_s:
        site_ex = st.selectbox("Site", ['TOUS'] + [s.capitalize() for s in sites_sel])
    with col_c:
        cat_ex = st.selectbox("Catégorie", ['TOUTES'] + cats_sel)
    with col_p:
        promo_ex = st.selectbox("Promotion", ['TOUS', 'En promo', 'Hors promo'])

    df_ex = df.copy()
    if site_ex != 'TOUS':
        df_ex = df_ex[df_ex['site'] == site_ex.lower()]
    if cat_ex != 'TOUTES':
        df_ex = df_ex[df_ex['categorie'] == cat_ex]
    if promo_ex == 'En promo':
        df_ex = df_ex[df_ex['en_promotion']==True]
    elif promo_ex == 'Hors promo':
        df_ex = df_ex[df_ex['en_promotion']==False]

    col_search = st.text_input("🔎 Recherche par nom de produit", placeholder="Ex: canapé, lit, table...")
    if col_search:
        df_ex = df_ex[df_ex['nom'].str.lower().str.contains(col_search.lower(), na=False)]

    st.markdown(f"**{len(df_ex):,} produits trouvés**")

    # Tableau
    cols_show = ['nom','site','categorie','prix','ancien_prix','remise_pct','en_promotion']
    cols_show = [c for c in cols_show if c in df_ex.columns]
    df_display = df_ex[cols_show].copy()
    df_display.columns = [c.replace('_',' ').capitalize() for c in cols_show]

    st.dataframe(
        df_display.head(100),
        hide_index=True,
        use_container_width=True,
        height=400,
    )

    # Download
    csv = df_ex.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="⬇️ Télécharger les données filtrées (CSV)",
        data=csv,
        file_name=f"prix_intelligence_export_{datetime.now().strftime('%Y%m%d')}.csv",
        mime='text/csv',
    )

