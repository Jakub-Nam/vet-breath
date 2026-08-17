import { Component, inject, signal } from '@angular/core';
import { FormField, FormRoot, email, form, required, submit } from '@angular/forms/signals';
import { Router, RouterLink } from '@angular/router';
import { firstValueFrom } from 'rxjs';
import { Auth } from '../core/auth';
import { errorDetail } from '../core/http';

@Component({
  selector: 'app-register',
  imports: [FormRoot, FormField, RouterLink],
  templateUrl: './register.html',
  styleUrl: './register.scss',
})
export class Register {
  private readonly auth = inject(Auth);
  private readonly router = inject(Router);

  protected readonly model = signal({ fullName: '', email: '', password: '' });

  protected readonly registerForm = form(this.model, (path) => {
    required(path.email);
    email(path.email);
    required(path.password);
  });

  protected readonly error = signal('');

  protected async onSubmit(event: Event): Promise<void> {
    event.preventDefault();
    this.error.set('');
    await submit(this.registerForm, {
      action: async () => {
        const { fullName, email: address, password } = this.model();
        try {
          await firstValueFrom(this.auth.register(address, password, fullName));
          const response = await firstValueFrom(this.auth.login(address, password));
          this.auth.setToken(response.access_token);
          await this.router.navigate(['/vet/panel']);
        } catch (err) {
          this.error.set(errorDetail(err, 'Registration failed'));
        }
      },
    });
  }
}
