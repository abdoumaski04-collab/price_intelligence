import { Routes } from '@angular/router';
import { HomeComponent } from './home/home';
import { AnalyticsLoginComponent } from './analytics-login/analytics-login';
import { DashboardComponent } from './dashboard/dashboard';

export const routes: Routes = [
  { path: '', component: HomeComponent },
  { path: 'analytics-access', component: AnalyticsLoginComponent },
  { path: 'dashboard', component: DashboardComponent },
  { path: '**', redirectTo: '' }
];
