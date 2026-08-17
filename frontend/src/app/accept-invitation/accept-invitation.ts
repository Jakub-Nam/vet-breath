import { Component, inject, signal } from '@angular/core';
import { FormField, FormRoot, form, required, submit } from '@angular/forms/signals';
import { ActivatedRoute, Router } from '@angular/router';
import { firstValueFrom } from 'rxjs';
import { Auth } from '../core/auth';
import { errorDetail } from '../core/http';

@Component({
  selector: 'app-accept-invitation',
  imports: [FormRoot, FormField],
  templateUrl: './accept-invitation.html',
  styleUrl: './accept-invitation.scss',
})
export class AcceptInvitation {
  private readonly auth = inject(Auth);
  private readonly router = inject(Router);
  private readonly token = inject(ActivatedRoute).snapshot.queryParamMap.get('token') ?? '';

  protected readonly model = signal({ password: '' });

  protected readonly invitationForm = form(this.model, (path) => {
    required(path.password);
  });

  protected readonly error = signal(this.token ? '' : 'Missing invitation token');

  protected async onSubmit(event: Event): Promise<void> {
    event.preventDefault();
    if (!this.token) return;
    this.error.set('');
    await submit(this.invitationForm, {
      action: async () => {
        try {
          const response = await firstValueFrom(
            this.auth.acceptInvitation(this.token, this.model().password),
          );
          this.auth.setToken(response.access_token);
          await this.router.navigate(['/owner']);
        } catch (err) {
          this.error.set(errorDetail(err, 'Invalid or expired invitation'));
        }
      },
    });
  }
}
