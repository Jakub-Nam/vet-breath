import { DatePipe } from '@angular/common';
import { HttpClient, httpResource } from '@angular/common/http';
import { Component, computed, inject, signal } from '@angular/core';
import { FormField, FormRoot, email, form, required, submit } from '@angular/forms/signals';
import { firstValueFrom } from 'rxjs';
import { Auth } from '../core/auth';
import { errorDetail } from '../core/http';
import { environment } from '../../environments/environment';

interface OwnerOnPanel {
  id: number;
  email: string;
  full_name: string | null;
  status: string;
}

interface DogOnPanel {
  id: number;
  name: string;
  breed: string;
  age: number;
  owner_name: string | null;
  owner_email: string;
  latest_bpm: number | null;
  latest_recommendation: string | null;
  latest_recorded_at: string | null;
  needs_attention: boolean;
}

interface NoteOnPanel {
  id: number;
  dog_id: number;
  vet_id: number;
  body: string;
  created_at: string;
}

interface PanelResponse {
  clients: OwnerOnPanel[];
  dogs: DogOnPanel[];
}

@Component({
  selector: 'app-vet-panel',
  imports: [FormRoot, FormField, DatePipe],
  templateUrl: './panel.html',
  styleUrl: './panel.scss',
})
export class VetPanel {
  private readonly http = inject(HttpClient);
  protected readonly auth = inject(Auth);

  protected readonly panelResource = httpResource<PanelResponse>(
    () => `${environment.apiUrl}/vets/panel`,
    { defaultValue: { clients: [], dogs: [] } },
  );

  protected readonly notesDogId = signal<number | null>(null);

  /** Refetches on its own whenever `notesDogId` changes; no request while closed. */
  protected readonly notesResource = httpResource<NoteOnPanel[]>(
    () => {
      const dogId = this.notesDogId();
      return dogId === null ? undefined : `${environment.apiUrl}/vets/notes/${dogId}`;
    },
    { defaultValue: [] },
  );

  protected readonly attentionDogs = computed(() =>
    this.panelResource.value().dogs.filter((dog) => dog.needs_attention),
  );

  protected readonly inviteModel = signal({ email: '', name: '', password: '', confirmPassword: '' });
  protected readonly inviteForm = form(this.inviteModel, (path) => {
    required(path.email);
    email(path.email);
    required(path.password);
    required(path.confirmPassword);
  });

  protected readonly noteModel = signal({ body: '' });
  protected readonly noteForm = form(this.noteModel, (path) => {
    required(path.body);
  });

  protected readonly inviteError = signal('');
  protected readonly inviteSuccess = signal('');
  protected readonly showInvite = signal(false);
  protected readonly deleteError = signal('');

  protected async onDeleteAccount(): Promise<void> {
    const confirmed = window.confirm(
      'Delete your account? This permanently removes your account and every client, dog, ' +
        'reading, and note under it. This cannot be undone.',
    );
    if (!confirmed) return;
    this.deleteError.set('');
    try {
      await firstValueFrom(this.auth.deleteAccount());
      this.auth.logout();
    } catch (err) {
      this.deleteError.set(errorDetail(err, 'Failed to delete account'));
    }
  }

  protected async onCreateClient(event: Event): Promise<void> {
    event.preventDefault();
    this.inviteError.set('');
    this.inviteSuccess.set('');
    await submit(this.inviteForm, {
      action: async () => {
        const { email: address, name, password, confirmPassword } = this.inviteModel();
        if (password !== confirmPassword) {
          this.inviteError.set('Passwords do not match');
          return;
        }
        try {
          await firstValueFrom(
            this.http.post<OwnerOnPanel>(`${environment.apiUrl}/vets/clients`, {
              email: address,
              full_name: name || null,
              password,
            }),
          );
          this.inviteSuccess.set(`Client account created for ${address}`);
          this.inviteModel.set({ email: '', name: '', password: '', confirmPassword: '' });
          this.panelResource.reload();
        } catch (err) {
          this.inviteError.set(errorDetail(err, 'Failed to create client'));
        }
      },
    });
  }

  protected toggleNotes(dogId: number): void {
    this.noteModel.set({ body: '' });
    this.notesDogId.set(this.notesDogId() === dogId ? null : dogId);
  }

  protected async onAddNote(event: Event): Promise<void> {
    event.preventDefault();
    const dogId = this.notesDogId();
    if (dogId === null) return;
    await submit(this.noteForm, {
      action: async () => {
        const body = this.noteModel().body.trim();
        if (!body) return;
        await firstValueFrom(
          this.http.post<NoteOnPanel>(`${environment.apiUrl}/vets/notes`, {
            dog_id: dogId,
            body,
          }),
        );
        this.noteModel.set({ body: '' });
        this.notesResource.reload();
      },
    });
  }

  protected recommendationLabel(recommendation: string | null): string {
    switch (recommendation) {
      case 'recount':
        return 'Recount';
      case 'check_membranes_hr':
        return 'Check membranes & HR';
      case 'go_to_vet':
        return 'Go to vet';
      default:
        return 'No readings';
    }
  }

  protected recommendationClass(recommendation: string | null): string {
    switch (recommendation) {
      case 'recount':
        return 'rec-ok';
      case 'check_membranes_hr':
        return 'rec-warn';
      case 'go_to_vet':
        return 'rec-urgent';
      default:
        return '';
    }
  }
}
