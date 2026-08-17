import { HttpClient } from '@angular/common/http';
import { Component, inject, signal } from '@angular/core';
import { FormField, FormRoot, email, form, required, submit } from '@angular/forms/signals';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { firstValueFrom } from 'rxjs';
import { Auth } from '../core/auth';
import { errorDetail } from '../core/http';
import { environment } from '../../environments/environment';

@Component({
  selector: 'app-password-reset',
  imports: [FormRoot, FormField, RouterLink],
  templateUrl: './password-reset.html',
  styleUrl: './password-reset.scss',
})
export class PasswordReset {
  private readonly http = inject(HttpClient);
  private readonly auth = inject(Auth);
  private readonly router = inject(Router);
  private readonly token = inject(ActivatedRoute).snapshot.queryParamMap.get('token') ?? '';

  /** Without a token the page asks for an email; with one it sets a new password. */
  protected readonly hasToken = !!this.token;

  protected readonly requestModel = signal({ email: '' });
  protected readonly requestForm = form(this.requestModel, (path) => {
    required(path.email);
    email(path.email);
  });

  protected readonly resetModel = signal({ newPassword: '' });
  protected readonly resetForm = form(this.resetModel, (path) => {
    required(path.newPassword);
  });

  protected readonly error = signal('');
  protected readonly success = signal('');

  protected async onRequestReset(event: Event): Promise<void> {
    event.preventDefault();
    this.error.set('');
    await submit(this.requestForm, {
      action: async () => {
        try {
          await firstValueFrom(
            this.http.post(`${environment.apiUrl}/auth/password-reset-request`, {
              email: this.requestModel().email,
            }),
          );
          this.success.set('If the email exists, a reset link has been sent.');
        } catch {
          this.error.set('Something went wrong. Try again.');
        }
      },
    });
  }

  protected async onResetPassword(event: Event): Promise<void> {
    event.preventDefault();
    this.error.set('');
    await submit(this.resetForm, {
      action: async () => {
        try {
          const res = await firstValueFrom(
            this.http.post<{ access_token: string }>(`${environment.apiUrl}/auth/password-reset`, {
              token: this.token,
              new_password: this.resetModel().newPassword,
            }),
          );
          this.auth.setToken(res.access_token);
          await this.router.navigate([this.auth.role() === 'vet' ? '/vet/panel' : '/owner']);
        } catch (err) {
          this.error.set(errorDetail(err, 'Invalid or expired reset link'));
        }
      },
    });
  }
}
