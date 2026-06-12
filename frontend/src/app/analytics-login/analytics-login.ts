import { Component, signal, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';

@Component({
  selector: 'app-analytics-login',
  standalone: true,
  imports: [FormsModule, CommonModule],
  templateUrl: './analytics-login.html',
  styleUrl: './analytics-login.css'
})
export class AnalyticsLoginComponent {
  private router = inject(Router);

  email       = signal('');
  password    = signal('');
  confirmCode = signal('');
  purpose     = signal('');
  isSubmitting  = signal(false);
  errorMessage  = signal('');
  showPassword  = signal(false);

  togglePasswordVisibility() {
    this.showPassword.set(!this.showPassword());
  }

  onSubmit() {
    // Validate all fields
    if (!this.email() || !this.password() || !this.confirmCode() || !this.purpose()) {
      this.errorMessage.set('Veuillez remplir tous les champs obligatoires.');
      return;
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(this.email())) {
      this.errorMessage.set('Veuillez saisir une adresse email valide.');
      return;
    }

    if (this.password().length < 6) {
      this.errorMessage.set('Le mot de passe doit contenir au moins 6 caractères.');
      return;
    }

    if (this.confirmCode().length < 4) {
      this.errorMessage.set('Le code de confirmation doit contenir au moins 4 caractères.');
      return;
    }

    if (this.purpose().length < 20) {
      this.errorMessage.set('Veuillez détailler votre motif d\'accès (minimum 20 caractères).');
      return;
    }

    this.errorMessage.set('');
    this.isSubmitting.set(true);

    // Simulate authentication delay
    setTimeout(() => {
      sessionStorage.setItem('analytics_auth', 'true');
      sessionStorage.setItem('analytics_user', this.email());
      this.router.navigate(['/dashboard']);
    }, 1800);
  }

  goHome() {
    this.router.navigate(['/']);
  }
}
