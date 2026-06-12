import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface Product {
  nom: string;
  marque: string;
  prix: number | null;
  ancien_prix: number | null;
  remise: number | null;
  rating: number | null;
  url: string;
  date_scraping: string;
}

export interface SearchResponse {
  total: number;
  query: string;
  results: Product[];
}

@Injectable({ providedIn: 'root' })
export class ApiService {
  private http = inject(HttpClient);
  private apiUrl = 'http://localhost:8000';

  searchProducts(
    query: string,
    category: string = '',
    source: string = '',
    sortDir: string = 'asc',
    page: number = 1,
    limit: number = 50,
    minPrice: number | null = null,
    maxPrice: number | null = null
  ): Observable<SearchResponse> {
    const params: any = { limit: limit.toString(), sort_dir: sortDir, page: page.toString() };
    if (query) params['q'] = query;
    if (category) params['category'] = category;
    if (source) params['source'] = source;
    if (minPrice !== null && minPrice !== undefined) params['min_price'] = minPrice.toString();
    if (maxPrice !== null && maxPrice !== undefined) params['max_price'] = maxPrice.toString();
    return this.http.get<SearchResponse>(`${this.apiUrl}/search`, { params });
  }

  getStats(): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/stats`);
  }

  getPromotions(): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/promotions`);
  }

  getVelocity(): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/velocity`);
  }

  getFigure(chartId: string): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/figure/${chartId}`);
  }
}
