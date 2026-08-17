import { Component, OnInit, signal, computed } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { FormsModule } from '@angular/forms';
import { DatePipe } from '@angular/common';
import { Auth } from '../core/auth';
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
  imports: [FormsModule, DatePipe],
  templateUrl: './panel.html',
  styleUrl: './panel.scss',
})
export class VetPanel implements OnInit {
  protected readonly panel = signal<PanelResponse | null>(null);
  protected readonly inviteEmail = signal('');
  protected readonly inviteName = signal('');
  protected readonly inviteError = signal('');
  protected readonly inviteSuccess = signal('');
  protected readonly showInvite = signal(false);
  protected readonly notesDogId = signal<number | null>(null);
  protected readonly notes = signal<NoteOnPanel[]>([]);
  protected readonly newNoteBody = signal('');

  protected readonly attentionDogs = computed(() =>
    (this.panel()?.dogs ?? []).filter((d) => d.needs_attention),
  );

  protected readonly normalDogs = computed(() =>
    (this.panel()?.dogs ?? []).filter((d) => !d.needs_attention),
  );

  constructor(
    private http: HttpClient,
    protected auth: Auth,
  ) {}

  ngOnInit() {
    this.loadPanel();
  }

  loadPanel() {
    this.http.get<PanelResponse>(`${environment.apiUrl}/vets/panel`).subscribe({
      next: (data) => this.panel.set(data),
    });
  }

  inviteClient() {
    if (!this.inviteEmail()) return;
    this.inviteError.set('');
    this.inviteSuccess.set('');
    this.http
      .post<OwnerOnPanel>(`${environment.apiUrl}/vets/clients`, {
        email: this.inviteEmail(),
        full_name: this.inviteName() || null,
      })
      .subscribe({
        next: () => {
          this.inviteSuccess.set(`Invitation sent to ${this.inviteEmail()}`);
          this.inviteEmail.set('');
          this.inviteName.set('');
          this.loadPanel();
        },
        error: (err) => {
          this.inviteError.set(err.error?.detail ?? 'Failed to invite');
        },
      });
  }

  recommendationLabel(rec: string | null): string {
    switch (rec) {
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

  recommendationClass(rec: string | null): string {
    switch (rec) {
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

  toggleNotes(dogId: number) {
    if (this.notesDogId() === dogId) {
      this.notesDogId.set(null);
      this.notes.set([]);
      this.newNoteBody.set('');
      return;
    }
    this.notesDogId.set(dogId);
    this.newNoteBody.set('');
    this.loadNotes(dogId);
  }

  loadNotes(dogId: number) {
    this.http.get<NoteOnPanel[]>(`${environment.apiUrl}/vets/notes/${dogId}`).subscribe({
      next: (data) => this.notes.set(data),
    });
  }

  addNote() {
    const dogId = this.notesDogId();
    const body = this.newNoteBody().trim();
    if (!dogId || !body) return;
    this.http
      .post<NoteOnPanel>(`${environment.apiUrl}/vets/notes`, { dog_id: dogId, body })
      .subscribe({
        next: () => {
          this.newNoteBody.set('');
          this.loadNotes(dogId);
        },
      });
  }
}
