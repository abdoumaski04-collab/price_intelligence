import { Component, inject, signal, computed } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { ApiService, Product } from '../api.service';

interface Category {
  name: string;
  image: string;
}

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [FormsModule, CommonModule],
  templateUrl: './home.html',
  styleUrl: './home.css'
})
export class HomeComponent {
  private api = inject(ApiService);
  private router = inject(Router);

  categories: Category[] = [
    { name: 'Salon',      image: 'salon.png' },
    { name: 'Chambre',    image: 'chambre.png' },
    { name: 'Bureau',     image: 'bureau.png' },
    { name: 'Cuisine',    image: 'cuisine.png' },
    { name: 'Rangement',  image: 'rangement.png' }
  ];

  sources = ['Jumia', 'IKEA', 'Kitea'];

  searchQuery      = signal('');
  selectedCategory = signal('');
  selectedSource   = signal('');
  sortDir          = signal<'asc' | 'desc'>('asc');
  products         = signal<Product[]>([]);
  isLoading        = signal(false);
  hasSearched      = signal(false);
  totalResults     = signal(0);

  priceFilterEnabled = signal(false);
  minPriceFilter     = signal<number | null>(null);
  maxPriceFilter     = signal<number | null>(null);

  currentPage      = signal(1);
  pageSize         = signal(24);
  totalPages       = computed(() => Math.ceil(this.totalResults() / this.pageSize()));
  visiblePages     = computed(() => {
    const current = this.currentPage();
    const total = this.totalPages();
    const maxVisible = 5;

    if (total <= maxVisible) {
      return Array.from({ length: total }, (_, i) => i + 1);
    }

    let start = Math.max(1, current - 2);
    let end = Math.min(total, current + 2);

    if (current - 1 <= 2) {
      end = maxVisible;
    } else if (total - current <= 2) {
      start = total - maxVisible + 1;
    }

    const pages: (number | string)[] = [];

    if (start > 1) {
      pages.push(1);
      if (start > 2) pages.push('...');
    }

    for (let i = start; i <= end; i++) pages.push(i);

    if (end < total) {
      if (end < total - 1) pages.push('...');
      pages.push(total);
    }

    return pages;
  });

  bestDealUrl = computed(() =>
    this.sortDir() === 'asc' && this.products().length > 0
      ? this.products()[0].url
      : null
  );

  onCategoryClick(catName: string) {
    this.selectedCategory.set(this.selectedCategory() === catName ? '' : catName);
    this.searchQuery.set('');
    this.currentPage.set(1);
    this.executeSearch();
  }

  onSourceClick(src: string) {
    this.selectedSource.set(this.selectedSource() === src ? '' : src);
    this.currentPage.set(1);
    if (this.hasSearched()) this.executeSearch();
  }

  toggleSort() {
    this.sortDir.set(this.sortDir() === 'asc' ? 'desc' : 'asc');
    this.currentPage.set(1);
    if (this.hasSearched()) this.executeSearch();
  }

  onSearch() {
    this.selectedCategory.set('');
    this.currentPage.set(1);
    this.executeSearch();
  }

  onPriceFilterToggle() {
    this.priceFilterEnabled.set(!this.priceFilterEnabled());
    this.currentPage.set(1);
    if (this.hasSearched()) this.executeSearch();
  }

  onPriceBoundsChange() {
    this.currentPage.set(1);
    if (this.hasSearched() && this.priceFilterEnabled()) {
      this.executeSearch();
    }
  }

  goToPage(page: number | string) {
    if (typeof page === 'number' && page >= 1 && page <= this.totalPages()) {
      this.currentPage.set(page);
      this.executeSearch();
    }
  }

  nextPage()  { this.goToPage(this.currentPage() + 1); }
  prevPage()  { this.goToPage(this.currentPage() - 1); }

  executeSearch() {
    const query    = this.searchQuery().trim();
    const category = this.selectedCategory();
    const source   = this.selectedSource();

    if (!query && !category) {
      this.products.set([]);
      this.hasSearched.set(false);
      this.totalResults.set(0);
      return;
    }

    this.isLoading.set(true);
    this.hasSearched.set(true);

    const minP = this.priceFilterEnabled() ? this.minPriceFilter() : null;
    const maxP = this.priceFilterEnabled() ? this.maxPriceFilter() : null;

    this.api.searchProducts(
      query, category, source,
      this.sortDir(), this.currentPage(), this.pageSize(),
      minP, maxP
    ).subscribe({
      next: (res) => {
        this.products.set(res.results);
        this.totalResults.set(res.total);
        this.isLoading.set(false);
      },
      error: () => { this.isLoading.set(false); }
    });
  }

  getSiteColor(url: string): string {
    if (url?.includes('jumia'))  return '#c49a45';
    if (url?.includes('ikea'))   return '#0058a3';
    if (url?.includes('kitea'))  return '#5c7a65';
    return '#7a736a';
  }

  getSiteName(url: string): string {
    if (url?.includes('jumia'))  return 'Jumia';
    if (url?.includes('ikea'))   return 'IKEA';
    if (url?.includes('kitea'))  return 'Kitea';
    return 'Autre';
  }

  isBestDeal(product: Product): boolean {
    return this.sortDir() === 'asc' &&
           this.products().length > 0 &&
           this.products()[0].url === product.url;
  }

  goToAnalytics() {
    this.router.navigate(['/analytics-access']);
  }
}
