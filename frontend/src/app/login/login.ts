import { Component, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { Auth } from '../core/auth';

@Component({
  selector: 'app-login',
  imports: [FormsModule, RouterLink],
  templateUrl: './login.html',
  styleUrl: './login.scss',
})
export class Login {
  protected readonly email = signal('');
  protected readonly password = signal('');
  protected readonly error = signal('');
  protected readonly loading = signal(false);

  constructor(
    private auth: Auth,
    private router: Router,
  ) {}

  submit() {
    this.loading.set(true);
    this.error.set('');
    this.auth.login(this.email(), this.password()).subscribe({
      next: (res) => {
        this.auth.setToken(res.access_token);
        const role = this.auth.role();
        this.router.navigate([role === 'vet' ? '/vet/panel' : '/owner']);
      },
      error: () => {
        this.error.set('Invalid email or password');
        this.loading.set(false);
      },
    });
  }
}
