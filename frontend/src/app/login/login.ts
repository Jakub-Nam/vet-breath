import { Component, inject, signal } from '@angular/core';
import { FormField, FormRoot, email, form, required, submit } from '@angular/forms/signals';
import { Router, RouterLink } from '@angular/router';
import { firstValueFrom } from 'rxjs';
import { Auth } from '../core/auth';

@Component({
  selector: 'app-login',
  imports: [FormRoot, FormField, RouterLink],
  templateUrl: './login.html',
  styleUrl: './login.scss',
})
export class Login {
  private readonly auth = inject(Auth);
  private readonly router = inject(Router);

  protected readonly model = signal({ email: '', password: '' });

  protected readonly loginForm = form(this.model, (path) => {
    required(path.email);
    email(path.email);
    required(path.password);
  });

  /** Server-side failures only; field-level problems live in the field tree. */
  protected readonly error = signal('');

  protected async onSubmit(event: Event): Promise<void> {
    event.preventDefault();
    this.error.set('');
    await submit(this.loginForm, {
      action: async () => {
        try {
          const response = await firstValueFrom(
            this.auth.login(this.model().email, this.model().password),
          );
          this.auth.setToken(response.access_token);
          await this.router.navigate([this.auth.role() === 'vet' ? '/vet/panel' : '/owner']);
        } catch {
          this.error.set('Invalid email or password');
        }
      },
    });
  }
}
