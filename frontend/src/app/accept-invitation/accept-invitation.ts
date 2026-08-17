import { Component, OnInit, signal, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { Auth } from '../core/auth';

@Component({
  selector: 'app-accept-invitation',
  imports: [FormsModule],
  templateUrl: './accept-invitation.html',
  styleUrl: './accept-invitation.scss',
})
export class AcceptInvitation implements OnInit {
  private readonly auth = inject(Auth);
  private readonly router = inject(Router);
  private readonly route = inject(ActivatedRoute);

  protected readonly password = signal('');
  protected readonly error = signal('');
  protected readonly loading = signal(false);
  private token = '';

  public ngOnInit(): void {
    this.token = this.route.snapshot.queryParamMap.get('token') ?? '';
    if (!this.token) {
      this.error.set('Missing invitation token');
    }
  }

  protected submit(): void {
    this.loading.set(true);
    this.error.set('');
    this.auth.acceptInvitation(this.token, this.password()).subscribe({
      next: (res) => {
        this.auth.setToken(res.access_token);
        this.router.navigate(['/owner']);
      },
      error: (err) => {
        this.error.set(err.error?.detail ?? 'Invalid or expired invitation');
        this.loading.set(false);
      },
    });
  }
}
