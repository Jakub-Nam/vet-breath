import { Component, signal, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { Auth } from '../core/auth';
import { environment } from '../../environments/environment';

@Component({
  selector: 'app-password-reset',
  imports: [FormsModule, RouterLink],
  templateUrl: './password-reset.html',
  styleUrl: './password-reset.scss',
})
export class PasswordReset {
  private readonly http = inject(HttpClient);
  private readonly auth = inject(Auth);
  private readonly router = inject(Router);

  protected readonly email = signal('');
  protected readonly newPassword = signal('');
  protected readonly error = signal('');
  protected readonly success = signal('');
  protected readonly loading = signal(false);

  protected readonly hasToken: boolean;
  private readonly token: string;

  public constructor() {
    const route = inject(ActivatedRoute);

    this.token = route.snapshot.queryParamMap.get('token') ?? '';
    this.hasToken = !!this.token;
  }

  protected requestReset(): void {
    this.loading.set(true);
    this.error.set('');
    this.http
      .post(`${environment.apiUrl}/auth/password-reset-request`, { email: this.email() })
      .subscribe({
        next: () => {
          this.success.set('If the email exists, a reset link has been sent.');
          this.loading.set(false);
        },
        error: () => {
          this.error.set('Something went wrong. Try again.');
          this.loading.set(false);
        },
      });
  }

  protected resetPassword(): void {
    this.loading.set(true);
    this.error.set('');
    this.http
      .post<{ access_token: string }>(`${environment.apiUrl}/auth/password-reset`, {
        token: this.token,
        new_password: this.newPassword(),
      })
      .subscribe({
        next: (res) => {
          this.auth.setToken(res.access_token);
          const role = this.auth.role();
          this.router.navigate([role === 'vet' ? '/vet/panel' : '/owner']);
        },
        error: (err) => {
          this.error.set(err.error?.detail ?? 'Invalid or expired reset link');
          this.loading.set(false);
        },
      });
  }
}
