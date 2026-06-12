import { Component, inject, signal, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { ApiService } from '../api.service';

declare var Plotly: any;

interface ChartConfig {
  id: string;
  title: string;
  description: string;
  span?: 'wide';
}

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.css'
})
export class DashboardComponent implements OnInit {
  private api = inject(ApiService);
  private router = inject(Router);

  userName    = signal('');
  stats       = signal<any>(null);
  promotions  = signal<any>(null);
  velocity    = signal<any>(null);
  isLoading   = signal(true);
  chartsLoaded = signal<Set<string>>(new Set());

  charts: ChartConfig[] = [
    { id: 'boxplot',            title: 'Distribution des Prix',       description: 'Box plot — repartition des prix par site',        span: 'wide' },
    { id: 'barchart',           title: 'Prix Moyen par Categorie',    description: 'Comparaison des prix moyens par categorie' },
    { id: 'evolution',          title: 'Evolution des Prix',          description: 'Tendance temporelle des prix moyens',              span: 'wide' },
    { id: 'kde',                title: 'Densite des Prix (KDE)',      description: 'Distribution de densite par site',                 span: 'wide' },
    { id: 'scatter',            title: 'Nuage de Points',             description: 'Prix actuel vs ancien prix' },
    { id: 'promo',              title: 'Analyse des Promotions',      description: 'Taux et distribution des remises' },
    { id: 'ic',                 title: 'Intervalles de Confiance',    description: 'IC a 95 % par site' },
    { id: 'correlation',        title: 'Correlation Spearman',        description: 'Matrice de correlation entre variables' },
    { id: 'velocity',           title: 'Velocite des Prix',           description: 'Vitesse de changement des prix par site' },
    { id: 'segmentation',       title: 'Segmentation Produits',       description: 'Clustering des produits par gamme de prix' },
    { id: 'feature_importance', title: 'Importance des Variables',    description: 'Variables les plus influentes (ML)',               span: 'wide' },
    { id: 'ml_predictions',     title: 'Predictions ML',              description: 'Predictions du modele vs valeurs reelles',         span: 'wide' },
  ];

  ngOnInit() {
    if (!sessionStorage.getItem('analytics_auth')) {
      this.router.navigate(['/analytics-access']);
      return;
    }
    this.userName.set(sessionStorage.getItem('analytics_user') || 'Analyste');
    this.loadData();
  }

  loadData() {
    this.isLoading.set(true);

    // Fetch overview stats
    this.api.getStats().subscribe({
      next: (d: any) => this.stats.set(d),
      error: () => {}
    });

    this.api.getPromotions().subscribe({
      next: (d: any) => this.promotions.set(d),
      error: () => {}
    });

    this.api.getVelocity().subscribe({
      next: (d: any) => this.velocity.set(d),
      error: () => {}
    });

    // Fetch each Plotly figure
    let loaded = 0;
    const total = this.charts.length;

    for (const chart of this.charts) {
      this.api.getFigure(chart.id).subscribe({
        next: (data: any) => {
          loaded++;
          const set = new Set(this.chartsLoaded());
          set.add(chart.id);
          this.chartsLoaded.set(set);

          if (loaded >= 2) this.isLoading.set(false);

          setTimeout(() => this.renderChart(chart.id, data), 250);
        },
        error: () => {
          loaded++;
          if (loaded >= total) this.isLoading.set(false);
        }
      });
    }
  }

  renderChart(id: string, fig: any) {
    const el = document.getElementById(`chart-${id}`);
    if (!el || !fig) return;

    const baseLayout = fig.layout || {};

    const lightLayout: any = {
      ...baseLayout,
      paper_bgcolor: 'rgba(0,0,0,0)',
      plot_bgcolor:  'rgba(250,249,246,0.5)',
      font: { color: '#333333', family: 'Inter, sans-serif', size: 11 },
      autosize: true,
      margin: { t: 40, r: 25, b: 55, l: 60, pad: 4 },
      legend: {
        ...(baseLayout.legend || {}),
        font: { color: '#333333', size: 11 },
        bgcolor: 'rgba(0,0,0,0)',
      },
      colorway: ['#8B4513','#A0522D','#D2B48C','#CD853F','#F4A460','#DEB887','#D2C5B8','#000000'],
    };

    // Override each axis
    for (const ax of ['xaxis','yaxis','xaxis2','yaxis2','xaxis3','yaxis3']) {
      if (baseLayout[ax] || ax === 'xaxis' || ax === 'yaxis') {
        lightLayout[ax] = {
          ...(baseLayout[ax] || {}),
          gridcolor:     'rgba(210,197,184,0.45)',
          linecolor:     'rgba(210,197,184,0.45)',
          zerolinecolor: 'rgba(210,197,184,0.45)',
          tickfont:  { color: '#666666', size: 10 },
          titlefont: { color: '#000000', size: 12 },
        };
      }
    }

    try {
      Plotly.newPlot(el, fig.data, lightLayout, {
        responsive: true,
        displayModeBar: false,
      });
    } catch (e) {
      console.warn(`Chart ${id} render failed`, e);
    }
  }

  logout() {
    sessionStorage.removeItem('analytics_auth');
    sessionStorage.removeItem('analytics_user');
    this.router.navigate(['/']);
  }

  goHome() {
    this.router.navigate(['/']);
  }
}
