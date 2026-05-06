"""
╔══════════════════════════════════════════════════════════╗
║   GÉNÉRATEUR DE RAPPORT PDF — Prix Intelligence v2.0    ║
║   Kitea · Jumia · Ikea — Maroc                          ║
║   Data Analyst | Prof. Elaachak 2025-2026               ║
╚══════════════════════════════════════════════════════════╝

Usage :
    python generer_rapport.py
    python generer_rapport.py --output mon_rapport.pdf

Le script :
  1. Lit les données depuis data/clean/clean_prices.csv
  2. Lit les résultats depuis outputs/analyse_results.json
  3. Génère tous les graphiques automatiquement
  4. Crée le PDF complet dans outputs/rapport_prix_intelligence.pdf
"""

import os, sys, json, argparse
import pandas as pd
import numpy as np
from datetime import datetime

# ── Matplotlib (graphiques) ──────────────────────────────────
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from scipy.stats import gaussian_kde

# ── ReportLab (PDF) ──────────────────────────────────────────
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
    TableStyle, Image, PageBreak, HRFlowable, KeepTogether)
from reportlab.lib.colors import HexColor, white, black

# ═══════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
CSV_PATH   = os.path.join(BASE_DIR, 'data', 'clean', 'clean_prices.csv')
HIST_PATH  = os.path.join(BASE_DIR, 'data', 'raw',   'historique_prices.csv')
JSON_PATH  = os.path.join(BASE_DIR, 'outputs', 'analyse_results.json')
OUT_DIR    = os.path.join(BASE_DIR, 'outputs')
PDF_PATH   = os.path.join(OUT_DIR, 'rapport_prix_intelligence.pdf')

COLORS = {'kitea': '#E74C3C', 'jumia': '#F39C12', 'ikea': '#0058A3'}
SITES  = ['ikea', 'jumia', 'kitea']

C_DARK   = HexColor('#1A1A2E')
C_KITEA  = HexColor('#E74C3C')
C_JUMIA  = HexColor('#F39C12')
C_IKEA   = HexColor('#0058A3')
C_LIGHT  = HexColor('#F8F9FA')
C_BORDER = HexColor('#DEE2E6')
C_ACCENT = HexColor('#2C3E50')

plt.rcParams.update({
    'font.family': 'DejaVu Sans', 'font.size': 10,
    'axes.spines.top': False, 'axes.spines.right': False,
    'figure.facecolor': 'white', 'axes.facecolor': 'white',
})


# ═══════════════════════════════════════════════════════════════
# ÉTAPE 1 — CHARGEMENT DES DONNÉES
# ═══════════════════════════════════════════════════════════════

def charger_donnees():
    print("  Chargement des données...")
    df = pd.read_csv(CSV_PATH)
    df_h = pd.read_csv(HIST_PATH, parse_dates=['date_scraping'])
    with open(JSON_PATH, encoding='utf-8') as f:
        results = json.load(f)
    print(f"  ✅ {len(df):,} produits | {len(df_h):,} lignes historique")
    return df, df_h, results


# ═══════════════════════════════════════════════════════════════
# ÉTAPE 2 — GÉNÉRATION DES GRAPHIQUES
# ═══════════════════════════════════════════════════════════════

def generer_graphiques(df, df_h):
    print("  Génération des graphiques...")
    os.makedirs(OUT_DIR, exist_ok=True)
    charts = {}

    # ── 1. Boxplot ────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(10, 5))
    cats = list(df['categorie'].unique())
    x_pos = np.arange(len(cats))
    w = 0.25
    for i, site in enumerate(SITES):
        data = [df[(df['categorie']==c) & (df['site']==site)]['prix'].dropna().values for c in cats]
        data = [d if len(d) > 0 else [0] for d in data]
        ax.boxplot(data, positions=x_pos + i*w - w, widths=w*0.85,
            patch_artist=True, showfliers=False,
            medianprops=dict(color='white', linewidth=2),
            boxprops=dict(facecolor=COLORS[site], alpha=0.85),
            whiskerprops=dict(color=COLORS[site]),
            capprops=dict(color=COLORS[site]))
    ax.set_xticks(x_pos)
    ax.set_xticklabels([c.replace(' ', '\n') for c in cats], fontsize=9)
    ax.set_ylabel('Prix (MAD)')
    ax.set_title('Distribution des Prix par Catégorie et Site', fontsize=13, fontweight='bold', pad=12)
    patches = [mpatches.Patch(color=COLORS[s], label=s.capitalize()) for s in SITES]
    ax.legend(handles=patches, loc='upper right')
    ax.yaxis.grid(True, alpha=0.3)
    plt.tight_layout()
    p = os.path.join(OUT_DIR, 'chart_boxplot.png')
    plt.savefig(p, dpi=150, bbox_inches='tight')
    plt.close()
    charts['boxplot'] = p
    print("    ✅ boxplot")

    # ── 2. Bar chart prix moyen ───────────────────────────────
    fig, ax = plt.subplots(figsize=(10, 5))
    x = np.arange(len(cats))
    for i, site in enumerate(SITES):
        means = [df[(df['categorie']==c) & (df['site']==site)]['prix'].mean() for c in cats]
        bars = ax.bar(x + i*w - w, means, w*0.9, label=site.capitalize(),
            color=COLORS[site], alpha=0.88)
        for bar, val in zip(bars, means):
            if val > 0:
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 50,
                    f'{val:.0f}', ha='center', va='bottom', fontsize=7.5, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels([c.replace(' ', '\n') for c in cats], fontsize=9)
    ax.set_ylabel('Prix Moyen (MAD)')
    ax.set_title('Prix Moyen par Catégorie et Site (MAD)', fontsize=13, fontweight='bold', pad=12)
    ax.legend()
    ax.yaxis.grid(True, alpha=0.3)
    plt.tight_layout()
    p = os.path.join(OUT_DIR, 'chart_barchart.png')
    plt.savefig(p, dpi=150, bbox_inches='tight')
    plt.close()
    charts['barchart'] = p
    print("    ✅ barchart")

    # ── 3. Promotions ─────────────────────────────────────────
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    promo = df.groupby('site').agg(nb=('prix','count'), promos=('en_promotion','sum')).reset_index()
    promo['taux'] = promo['promos'] / promo['nb'] * 100
    bars = axes[0].bar(promo['site'], promo['taux'],
        color=[COLORS[s] for s in promo['site']], alpha=0.88, width=0.5)
    for bar, val in zip(bars, promo['taux']):
        axes[0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
            f'{val:.1f}%', ha='center', va='bottom', fontweight='bold')
    axes[0].set_ylabel('Taux de promotion (%)')
    axes[0].set_title('Taux de Promotion par Site', fontweight='bold')
    axes[0].yaxis.grid(True, alpha=0.3)
    remise = df[df['remise_pct'] > 0].groupby('site')['remise_pct'].mean()
    if len(remise) > 0:
        bars2 = axes[1].bar(remise.index, remise.values,
            color=[COLORS.get(s, '#999') for s in remise.index], alpha=0.88, width=0.5)
        for bar, val in zip(bars2, remise.values):
            axes[1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.2,
                f'{val:.1f}%', ha='center', va='bottom', fontweight='bold')
    axes[1].set_ylabel('Remise moyenne (%)')
    axes[1].set_title('Remise Moyenne par Site', fontweight='bold')
    axes[1].yaxis.grid(True, alpha=0.3)
    plt.tight_layout()
    p = os.path.join(OUT_DIR, 'chart_promo.png')
    plt.savefig(p, dpi=150, bbox_inches='tight')
    plt.close()
    charts['promo'] = p
    print("    ✅ promotions")

    # ── 4. Distribution KDE ───────────────────────────────────
    fig, ax = plt.subplots(figsize=(10, 4))
    for site in SITES:
        data = df[df['site'] == site]['prix'].dropna()
        if len(data) < 5:
            continue
        ax.hist(data, bins=50, density=True, alpha=0.25, color=COLORS[site])
        kde = gaussian_kde(data)
        x_r = np.linspace(data.min(), min(data.max(), 15000), 300)
        ax.plot(x_r, kde(x_r), color=COLORS[site], linewidth=2.5, label=site.capitalize())
    ax.set_xlabel('Prix (MAD)')
    ax.set_ylabel('Densité')
    ax.set_title('Distribution des Prix — Histogramme + KDE par Site',
        fontsize=13, fontweight='bold', pad=12)
    ax.legend()
    ax.yaxis.grid(True, alpha=0.3)
    plt.tight_layout()
    p = os.path.join(OUT_DIR, 'chart_kde.png')
    plt.savefig(p, dpi=150, bbox_inches='tight')
    plt.close()
    charts['kde'] = p
    print("    ✅ KDE")

    # ── 5. Évolution 30 jours ─────────────────────────────────
    fig, ax = plt.subplots(figsize=(10, 4))
    for site in SITES:
        evol = df_h[df_h['site'] == site].groupby('date_scraping')['prix'].mean()
        if len(evol) > 0:
            ax.plot(evol.index, evol.values, color=COLORS[site],
                linewidth=2, label=site.capitalize(), marker='o', markersize=2)
    ax.set_xlabel('Date')
    ax.set_ylabel('Prix Moyen (MAD)')
    ax.set_title('Évolution du Prix Moyen sur 30 Jours',
        fontsize=13, fontweight='bold', pad=12)
    ax.legend()
    ax.yaxis.grid(True, alpha=0.3)
    plt.xticks(rotation=30, ha='right')
    plt.tight_layout()
    p = os.path.join(OUT_DIR, 'chart_evolution.png')
    plt.savefig(p, dpi=150, bbox_inches='tight')
    plt.close()
    charts['evolution'] = p
    print("    ✅ evolution")

    # ── 6. Corrélation heatmap ────────────────────────────────
    df_c = df[['prix', 'ancien_prix', 'remise_pct']].copy()
    df_c['en_promo'] = df['en_promotion'].astype(int)
    gamme_map = {'Entrée (<500)': 0, 'Économique (500-1500)': 1,
        'Milieu (1500-4000)': 2, 'Premium (4000-10k)': 3, 'Luxe (>10k)': 4}
    df_c['gamme'] = df['gamme_prix'].map(gamme_map).fillna(0)
    df_c.columns = ['Prix', 'AncienPrix', 'Remise', 'EnPromo', 'Gamme']
    corr = df_c.dropna().corr(method='spearman')
    fig, ax = plt.subplots(figsize=(6, 5))
    im = ax.imshow(corr, cmap='RdBu_r', vmin=-1, vmax=1)
    plt.colorbar(im, ax=ax, shrink=0.8)
    ax.set_xticks(range(len(corr.columns)))
    ax.set_yticks(range(len(corr.columns)))
    ax.set_xticklabels(corr.columns, fontsize=9)
    ax.set_yticklabels(corr.columns, fontsize=9)
    for i in range(len(corr)):
        for j in range(len(corr.columns)):
            v = corr.iloc[i, j]
            ax.text(j, i, f'{v:.2f}', ha='center', va='center', fontsize=9,
                color='white' if abs(v) > 0.5 else 'black')
    ax.set_title('Matrice de Corrélation Spearman', fontsize=12, fontweight='bold')
    plt.tight_layout()
    p = os.path.join(OUT_DIR, 'chart_correlation.png')
    plt.savefig(p, dpi=150, bbox_inches='tight')
    plt.close()
    charts['correlation'] = p
    print("    ✅ correlation")

    # ── 7. Segmentation ───────────────────────────────────────
    gammes = ['Entrée (<500)', 'Économique (500-1500)', 'Milieu (1500-4000)',
              'Premium (4000-10k)', 'Luxe (>10k)']
    short  = ['<500', '500-1500', '1500-4000', '4000-10k', '>10k']
    fig, ax = plt.subplots(figsize=(10, 4))
    x = np.arange(len(gammes))
    for i, site in enumerate(SITES):
        counts = [len(df[(df['gamme_prix'] == g) & (df['site'] == site)]) for g in gammes]
        bars = ax.bar(x + i*w - w, counts, w*0.9,
            label=site.capitalize(), color=COLORS[site], alpha=0.88)
        for bar, val in zip(bars, counts):
            if val > 0:
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                    str(val), ha='center', va='bottom', fontsize=8)
    ax.set_xticks(x)
    ax.set_xticklabels(short, fontsize=9)
    ax.set_xlabel('Gamme de prix (MAD)')
    ax.set_ylabel('Nombre de produits')
    ax.set_title('Segmentation par Gamme de Prix', fontsize=13, fontweight='bold')
    ax.legend()
    ax.yaxis.grid(True, alpha=0.3)
    plt.tight_layout()
    p = os.path.join(OUT_DIR, 'chart_segmentation.png')
    plt.savefig(p, dpi=150, bbox_inches='tight')
    plt.close()
    charts['segmentation'] = p
    print("    ✅ segmentation")

    print(f"  ✅ {len(charts)} graphiques générés")
    return charts


# ═══════════════════════════════════════════════════════════════
# ÉTAPE 3 — CONSTRUCTION DU PDF
# ═══════════════════════════════════════════════════════════════

def construire_pdf(df, df_h, results, charts, pdf_path):
    print("  Construction du PDF...")

    doc = SimpleDocTemplate(pdf_path, pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm,
        topMargin=2.5*cm, bottomMargin=2*cm,
        title='Rapport Prix Intelligence — Kitea · Jumia · Ikea',
        author='Data Analyst — Prix Intelligence',
        subject='Analyse statistique des prix e-commerce Maroc')

    styles = getSampleStyleSheet()
    S = {
        'h1': ParagraphStyle('h1', fontSize=18, fontName='Helvetica-Bold',
            textColor=C_DARK, spaceBefore=16, spaceAfter=8, leading=22),
        'h2': ParagraphStyle('h2', fontSize=13, fontName='Helvetica-Bold',
            textColor=C_ACCENT, spaceBefore=12, spaceAfter=6),
        'body': ParagraphStyle('body', fontSize=10, fontName='Helvetica',
            textColor=HexColor('#2C3E50'), leading=15, spaceAfter=6, alignment=TA_JUSTIFY),
        'caption': ParagraphStyle('cap', fontSize=8.5, fontName='Helvetica-Oblique',
            textColor=HexColor('#7F8C8D'), alignment=TA_CENTER, spaceAfter=6),
    }

    def tbl_style(header_color=C_ACCENT, row_colors=None):
        row_colors = row_colors or [C_LIGHT, white]
        return TableStyle([
            ('BACKGROUND', (0,0), (-1,0), header_color),
            ('TEXTCOLOR', (0,0), (-1,0), white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 9),
            ('ALIGN', (1,0), (-1,-1), 'CENTER'),
            ('GRID', (0,0), (-1,-1), 0.4, C_BORDER),
            ('ROWBACKGROUND', (0,1), (-1,-1), row_colors * 20),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('LEFTPADDING', (0,0), (-1,-1), 6),
        ])

    def hr(): return HRFlowable(width='100%', thickness=1.5, color=C_KITEA, spaceAfter=8)
    def img(key, w=17, h=8):
        if key in charts and os.path.exists(charts[key]):
            return Image(charts[key], width=w*cm, height=h*cm)
        return Spacer(1, 0.1*cm)

    story = []
    stats = results['stats_par_site']

    # ── PAGE DE COUVERTURE ────────────────────────────────────
    nb_prod   = results['meta']['nb_produits']
    nb_cat    = results['meta']['nb_categories']
    pct_promo = df['en_promotion'].mean() * 100
    date_str  = datetime.now().strftime('%d %B %Y')

    cover = [
        [Paragraph('<b>RAPPORT D\'ANALYSE</b>', ParagraphStyle('t',
            fontSize=30, fontName='Helvetica-Bold', textColor=white, alignment=TA_CENTER))],
        [Paragraph('<b>Prix Intelligence Platform</b>', ParagraphStyle('t2',
            fontSize=18, fontName='Helvetica', textColor=HexColor('#BDC3C7'), alignment=TA_CENTER))],
        [Paragraph('Kitea · Jumia · Ikea — Maroc', ParagraphStyle('t3',
            fontSize=13, fontName='Helvetica', textColor=HexColor('#95A5A6'), alignment=TA_CENTER))],
    ]
    cover_tbl = Table(cover, colWidths=[17*cm], rowHeights=[3*cm, 2*cm, 1.5*cm])
    cover_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), C_DARK),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 20),
        ('BOTTOMPADDING', (0,0), (-1,-1), 20),
    ]))
    story.append(cover_tbl)
    story.append(Spacer(1, 0.4*cm))

    # Métriques couverture
    m_data = [
        ['PRODUITS', 'CATÉGORIES', 'EN PROMOTION', 'PÉRIODE', 'SITES'],
        [f'{nb_prod:,}', str(nb_cat), f'{pct_promo:.1f}%', '30 jours', '3'],
    ]
    m_tbl = Table(m_data, colWidths=[3.4*cm]*5)
    m_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), HexColor('#2C3E50')),
        ('BACKGROUND', (0,1), (-1,1), HexColor('#ECF0F1')),
        ('TEXTCOLOR', (0,0), (-1,0), white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTNAME', (0,1), (-1,1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 8),
        ('FONTSIZE', (0,1), (-1,1), 18),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ROWHEIGHT', (0,0), (-1,-1), 1*cm),
        ('GRID', (0,0), (-1,-1), 0.5, C_BORDER),
    ]))
    story.append(m_tbl)
    story.append(Spacer(1, 0.4*cm))

    # Sites colorés
    s_data = [['KITEA', '·', 'JUMIA', '·', 'IKEA']]
    s_tbl = Table(s_data, colWidths=[3.5*cm, 1*cm, 3.5*cm, 1*cm, 3.5*cm])
    s_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,0), C_KITEA),
        ('BACKGROUND', (2,0), (2,0), C_JUMIA),
        ('BACKGROUND', (4,0), (4,0), C_IKEA),
        ('BACKGROUND', (1,0), (1,0), C_DARK),
        ('BACKGROUND', (3,0), (3,0), C_DARK),
        ('TEXTCOLOR', (0,0), (-1,-1), white),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 12),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ROWHEIGHT', (0,0), (-1,-1), 1.2*cm),
    ]))
    story.append(s_tbl)
    story.append(Spacer(1, 0.4*cm))

    info_data = [
        ['Projet :', 'Real-Time E-commerce Price Intelligence Platform'],
        ['Cours :', 'Data Engineering & Analytics — Prof. Elaachak'],
        ['Date :', date_str],
        ['Version :', '2.0 — Analyse complète niveau ingénieur'],
    ]
    i_tbl = Table(info_data, colWidths=[3.5*cm, 13.5*cm])
    i_tbl.setStyle(TableStyle([
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('FONTNAME', (1,0), (1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 9.5),
        ('TEXTCOLOR', (0,0), (0,-1), C_ACCENT),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(i_tbl)
    story.append(PageBreak())

    # ── SECTION 1 : STATS DESCRIPTIVES ───────────────────────
    story.append(Paragraph('1. Statistiques descriptives', S['h1']))
    story.append(hr())
    header = ['Site', 'N', 'Moyenne', 'Médiane', 'Min', 'Max', 'Écart-type']
    rows   = [header]
    for site in SITES:
        rows.append([
            site.capitalize(),
            f"{int(stats['count'][site]):,}",
            f"{stats['moyenne'][site]:,.0f} MAD",
            f"{stats['mediane'][site]:,.0f} MAD",
            f"{stats['minimum'][site]:,.0f} MAD",
            f"{stats['maximum'][site]:,.0f} MAD",
            f"{stats['ecart_type'][site]:,.0f} MAD",
        ])
    t = Table(rows, colWidths=[2.5*cm,1.8*cm,2.5*cm,2.5*cm,2*cm,2*cm,2.7*cm])
    t.setStyle(tbl_style(C_DARK,
        [HexColor('#EFF6FF'), HexColor('#FFFBF0'), HexColor('#FEF3F2')]))
    story.append(t)
    story.append(Spacer(1, 0.3*cm))
    story.append(img('boxplot', 17, 8.5))
    story.append(Paragraph('Figure 1 — Distribution des prix par catégorie et site.', S['caption']))
    story.append(img('barchart', 17, 8.5))
    story.append(Paragraph('Figure 2 — Prix moyen par catégorie et site (MAD).', S['caption']))
    story.append(PageBreak())

    # ── SECTION 2 : IC 95% ───────────────────────────────────
    story.append(Paragraph('2. Intervalles de confiance (IC 95%)', S['h1']))
    story.append(hr())
    story.append(Paragraph(
        "Un IC 95% signifie : nous sommes certains a 95% que le vrai prix moyen "
        "de la population est dans cet intervalle. Plus l'intervalle est etroit, "
        "plus notre estimation est precise.", S['body']))
    ic = results.get('intervalles_confiance', {})
    if ic:
        ic_rows = [['Site', 'N', 'Moyenne', 'IC 95% Inf.', 'IC 95% Sup.', 'Marge +/-', 'CV']]
        for site in SITES:
            if site in ic:
                d = ic[site]
                ic_rows.append([
                    site.capitalize(), f"{d['n']:,}",
                    f"{d['moyenne']:,.0f} MAD",
                    f"{d['ic_low']:,.0f} MAD",
                    f"{d['ic_high']:,.0f} MAD",
                    f"+/- {d['marge']:,.0f} MAD",
                    f"{d['cv_pct']:.1f}%",
                ])
        ic_t = Table(ic_rows, colWidths=[2.3*cm,1.5*cm,2.5*cm,2.5*cm,2.5*cm,2.7*cm,2.5*cm])
        ic_t.setStyle(tbl_style(C_ACCENT,
            [HexColor('#EFF6FF'), HexColor('#FFFBF0'), HexColor('#FEF3F2')]))
        story.append(ic_t)

    # ── SECTION 3 : TESTS STAT ───────────────────────────────
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph('3. Tests statistiques inferentiels', S['h1']))
    story.append(hr())
    story.append(Paragraph('3.1 Shapiro-Wilk (Normalite)', S['h2']))
    shapiro = results.get('shapiro', {})
    if shapiro:
        sh_rows = [['Site', 'Statistique W', 'p-value', 'Normale ?']]
        for site in SITES:
            if site in shapiro:
                d = shapiro[site]
                sh_rows.append([site.capitalize(), f"{d['stat']:.4f}",
                    f"{d['p_value']:.6f}", 'Oui' if d['normal'] else 'Non'])
        sh_t = Table(sh_rows, colWidths=[3.5*cm, 3.5*cm, 4*cm, 6*cm])
        sh_t.setStyle(tbl_style())
        story.append(sh_t)

    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph('3.2 Kruskal-Wallis', S['h2']))
    kw_cat  = results.get('kruskal_categories', {})
    kw_site = results.get('kruskal_sites', {})
    if kw_cat and kw_site:
        kw_rows = [
            ['Test', 'Groupes', 'Stat. H', 'p-value', 'Significatif'],
            ['Kruskal Categories', '5 categories',
                f"{kw_cat['stat']:.2f}", f"{kw_cat['p_value']:.2e}",
                'Oui' if kw_cat['p_value'] < 0.05 else 'Non'],
            ['Kruskal Sites', 'Ikea vs Jumia vs Kitea',
                f"{kw_site['stat']:.2f}", f"{kw_site['p_value']:.2e}",
                'Oui' if kw_site['p_value'] < 0.05 else 'Non'],
        ]
        kw_t = Table(kw_rows, colWidths=[4*cm, 4.5*cm, 2.5*cm, 2.5*cm, 3.5*cm])
        kw_t.setStyle(tbl_style())
        story.append(kw_t)
    story.append(PageBreak())

    # ── SECTION 4 : POWER + RÉGRESSION ───────────────────────
    story.append(Paragraph('4. Analyse de puissance (Power Analysis)', S['h1']))
    story.append(hr())
    story.append(Paragraph(
        "Cohen's d mesure la taille de l'effet : < 0.2 = negligeable, "
        "0.2-0.5 = petit, 0.5-0.8 = moyen, > 0.8 = grand. "
        "Puissance >= 80% = echantillon suffisant.", S['body']))
    power = results.get('power_analysis', {})
    if power:
        pw_rows = [["Comparaison", "Cohen's d", "Taille", "Puissance", "N actuel", "N requis", "OK?"]]
        for key, d in power.items():
            pw_rows.append([
                key.replace('_vs_', ' vs '),
                f"{d['cohens_d']:.4f}", d['taille_effet'],
                f"{d['puissance']*100:.1f}%",
                f"{d['n_actuel']:,}", str(d['n_necessaire']),
                d['conclusion'],
            ])
        pw_t = Table(pw_rows, colWidths=[3.5*cm,1.8*cm,1.8*cm,2*cm,2*cm,2*cm,4*cm])
        pw_t.setStyle(tbl_style())
        story.append(pw_t)

    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph('5. Regression lineaire', S['h1']))
    story.append(hr())
    reg = results.get('regression', {})
    if reg:
        story.append(Paragraph(
            f"Modele OLS : prix ~ site + categorie + promotion. "
            f"R ajuste = {reg['r2_adj']:.4f} ({reg['r2_adj']*100:.1f}% variance expliquee). "
            f"F = {reg['f_stat']:.2f}, p = {reg['p_global']:.6f}.", S['body']))
    story.append(PageBreak())

    # ── SECTION 5 : DISTRIBUTION + EVOLUTION ─────────────────
    story.append(Paragraph('6. Distribution des prix (KDE)', S['h1']))
    story.append(hr())
    story.append(img('kde', 17, 7))
    story.append(Paragraph('Figure 3 — Distribution KDE par site.', S['caption']))

    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph('7. Analyse des promotions', S['h1']))
    story.append(hr())
    story.append(img('promo', 17, 7))
    story.append(Paragraph('Figure 4 — Taux de promotion et remise moyenne par site.', S['caption']))
    story.append(PageBreak())

    # ── SECTION 6 : ÉVOLUTION + SEGMENTATION ─────────────────
    story.append(Paragraph('8. Evolution temporelle — 30 jours', S['h1']))
    story.append(hr())
    story.append(img('evolution', 17, 7))
    story.append(Paragraph('Figure 5 — Evolution du prix moyen sur 30 jours.', S['caption']))

    vel = results.get('velocity', {})
    if vel:
        story.append(Spacer(1, 0.2*cm))
        story.append(Paragraph('Price Velocity — Tendance des prix', S['h2']))
        v_rows = [['Site', 'Pente/jour', 'Variation 30j', 'Var. %', 'R2', 'Tendance']]
        for site in SITES:
            if site in vel:
                d = vel[site]
                v_rows.append([
                    site.capitalize(),
                    f"{d['pente_jour']:+.2f} MAD",
                    f"{d['variation_30j']:+.0f} MAD",
                    f"{d['variation_pct']:+.1f}%",
                    f"{d['r_carre']:.4f}",
                    d['tendance'],
                ])
        v_t = Table(v_rows, colWidths=[2.5*cm, 2.8*cm, 3*cm, 2.5*cm, 2.2*cm, 4*cm])
        v_t.setStyle(tbl_style(C_ACCENT,
            [HexColor('#EFF6FF'), HexColor('#FFFBF0'), HexColor('#FEF3F2')]))
        story.append(v_t)

    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph('9. Segmentation par gamme', S['h1']))
    story.append(hr())
    story.append(img('segmentation', 17, 7))
    story.append(Paragraph('Figure 6 — Repartition des produits par gamme de prix.', S['caption']))
    story.append(PageBreak())

    # ── SECTION 7 : CORRÉLATION + CONCLUSIONS ────────────────
    story.append(Paragraph('10. Matrice de correlation (Spearman)', S['h1']))
    story.append(hr())
    story.append(img('correlation', 10, 8))
    story.append(Paragraph('Figure 7 — Matrice de correlation Spearman.', S['caption']))

    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph('11. Conclusions et recommandations', S['h1']))
    story.append(hr())

    conclusions = [
        ('Positionnement', 'Ikea haut de gamme (moy. 4 230 MAD), Kitea milieu (3 190 MAD), '
            'Jumia entree de gamme (1 306 MAD). Differences significatives (Mann-Whitney p<0.05).'),
        ('Promotions', 'Jumia et Kitea : 55% de produits en promo. '
            'Ikea : 0% de promotions detectees. Remises moyennes 25-30% sur certaines categories.'),
        ('Volatilite', 'Ikea : CV > 100% (gamme tres large). '
            'Jumia : variation quotidienne la plus stable. Kitea : position intermediaire.'),
        ('Power Analysis', 'Echantillons suffisants (puissance > 80%) pour detecter '
            'les differences reelles entre tous les sites.'),
        ('Recommandation', 'Pour un consommateur : Jumia offre les meilleurs prix '
            'en entree et moyen de gamme. En production Bigtable : mise a jour quotidienne '
            'permettra de detecter les meilleures periodes d\'achat.'),
    ]

    for titre, texte in conclusions:
        c_data = [[titre, texte]]
        c_tbl = Table(c_data, colWidths=[3.5*cm, 13.5*cm])
        c_tbl.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (0,-1), HexColor('#2C3E50')),
            ('BACKGROUND', (1,0), (1,-1), HexColor('#F8F9FA')),
            ('TEXTCOLOR', (0,0), (0,-1), white),
            ('TEXTCOLOR', (1,0), (1,-1), HexColor('#2C3E50')),
            ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
            ('FONTNAME', (1,0), (1,-1), 'Helvetica'),
            ('FONTSIZE', (0,0), (-1,-1), 9),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('TOPPADDING', (0,0), (-1,-1), 8),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
            ('LINEBELOW', (0,0), (-1,-1), 0.5, C_BORDER),
        ]))
        story.append(c_tbl)
        story.append(Spacer(1, 0.1*cm))

    # Pied de page
    story.append(Spacer(1, 0.8*cm))
    story.append(HRFlowable(width='100%', thickness=1, color=C_KITEA))
    story.append(Spacer(1, 0.2*cm))
    footer = [[
        'Prix Intelligence Platform v2.0',
        f"Genere le {datetime.now().strftime('%d/%m/%Y a %H:%M')}",
        'Prof. Elaachak — Data Analytics'
    ]]
    f_tbl = Table(footer, colWidths=[6*cm, 5*cm, 6*cm])
    f_tbl.setStyle(TableStyle([
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('TEXTCOLOR', (0,0), (-1,-1), HexColor('#7F8C8D')),
        ('ALIGN', (1,0), (1,-1), 'CENTER'),
        ('ALIGN', (2,0), (2,-1), 'RIGHT'),
    ]))
    story.append(f_tbl)

    doc.build(story)
    size = os.path.getsize(pdf_path) / 1024
    print(f"  ✅ PDF genere : {pdf_path}")
    print(f"     Taille : {size:.0f} Ko")


# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description='Generer le rapport PDF Prix Intelligence')
    parser.add_argument('--output', default=PDF_PATH, help='Chemin du PDF de sortie')
    args = parser.parse_args()

    print("=" * 55)
    print("  GENERATEUR RAPPORT PDF — Prix Intelligence v2.0")
    print("=" * 55)
    print()

    print("ETAPE 1/3 — Chargement des donnees")
    df, df_h, results = charger_donnees()
    print()

    print("ETAPE 2/3 — Generation des graphiques")
    charts = generer_graphiques(df, df_h)
    print()

    print("ETAPE 3/3 — Construction du PDF")
    construire_pdf(df, df_h, results, charts, args.output)
    print()

    print("=" * 55)
    print("  RAPPORT GENERE AVEC SUCCES !")
    print(f"  Fichier : {args.output}")
    print("=" * 55)


if __name__ == "__main__":
    main()
