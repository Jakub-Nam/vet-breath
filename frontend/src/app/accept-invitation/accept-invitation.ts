import { Component, OnInit, signal } from '@angular/core';
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
  protected readonly password = signal('');
  protected readonly error = signal('');
  protected readonly loading = signal(false);
  private token = '';

  constructor(
    private auth: Auth,
    private router: Router,
    private route: ActivatedRoute,
  ) {}

  ngOnInit() {
    this.token = this.route.snapshot.queryParamMap.get('token') ?? '';
    if (!this.token) {
      this.error.set('Missing invitation token');
    }
  }

  submit() {
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
