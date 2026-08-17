import { Component, signal, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { Auth } from '../core/auth';

@Component({
  selector: 'app-register',
  imports: [FormsModule, RouterLink],
  templateUrl: './register.html',
  styleUrl: './register.scss',
})
export class Register {
  private readonly auth = inject(Auth);
  private readonly router = inject(Router);

  protected readonly email = signal('');
  protected readonly password = signal('');
  protected readonly fullName = signal('');
  protected readonly error = signal('');
  protected readonly loading = signal(false);

  protected submit(): void {
    this.loading.set(true);
    this.error.set('');
    this.auth.register(this.email(), this.password(), this.fullName()).subscribe({
      next: () => {
        this.auth.login(this.email(), this.password()).subscribe({
          next: (res) => {
            this.auth.setToken(res.access_token);
            this.router.navigate(['/vet/panel']);
          },
        });
      },
      error: (err) => {
        this.error.set(err.error?.detail ?? 'Registration failed');
        this.loading.set(false);
      },
    });
  }
}
