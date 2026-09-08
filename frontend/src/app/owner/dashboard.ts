import { DatePipe } from '@angular/common';
import { HttpClient, httpResource } from '@angular/common/http';
import { Component, inject, linkedSignal, signal } from '@angular/core';
import { FormField, FormRoot, form, max, min, required, submit } from '@angular/forms/signals';
import { firstValueFrom } from 'rxjs';
import { Auth } from '../core/auth';
import { errorDetail } from '../core/http';
import { environment } from '../../environments/environment';

interface Dog {
  id: number;
  name: string;
  breed: string;
  age: number;
}

interface Reading {
  id: number;
  dog_id: number;
  bpm: number;
  recommendation: string;
  recorded_at: string;
}

interface Note {
  id: number;
  dog_id: number;
  vet_id: number;
  body: string;
  created_at: string;
}

@Component({
  selector: 'app-owner-dashboard',
  imports: [FormRoot, FormField, DatePipe],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.scss',
})
export class OwnerDashboard {
  private readonly http = inject(HttpClient);
  protected readonly auth = inject(Auth);

  protected readonly dogsResource = httpResource<Dog[]>(() => `${environment.apiUrl}/dogs`, {
    defaultValue: [],
  });

  /** Keeps the current pick across reloads, falling back to the first dog. */
  protected readonly selectedDog = linkedSignal<Dog[], Dog | null>({
    source: () => this.dogsResource.value(),
    computation: (dogs, previous) =>
      dogs.find((dog) => dog.id === previous?.value?.id) ?? dogs[0] ?? null,
  });

  protected readonly readingsResource = httpResource<Reading[]>(
    () => {
      const dog = this.selectedDog();
      return dog ? `${environment.apiUrl}/readings?dog_id=${dog.id}` : undefined;
    },
    { defaultValue: [] },
  );

  protected readonly notesResource = httpResource<Note[]>(
    () => {
      const dog = this.selectedDog();
      return dog ? `${environment.apiUrl}/dogs/${dog.id}/notes` : undefined;
    },
    { defaultValue: [] },
  );

  protected readonly addDogModel = signal<{ name: string; breed: string; age: number | null }>({
    name: '',
    breed: '',
    age: null,
  });

  protected readonly addDogForm = form(this.addDogModel, (path) => {
    required(path.name);
    required(path.breed);
    required(path.age);
    min(path.age, 0);
  });

  protected readonly readingModel = signal<{ bpm: number | null }>({ bpm: null });

  protected readonly readingForm = form(this.readingModel, (path) => {
    required(path.bpm);
    min(path.bpm, 1);
    max(path.bpm, 200);
  });

  protected readonly noteModel = signal({ body: '' });
  protected readonly noteForm = form(this.noteModel, (path) => {
    required(path.body);
  });

  protected readonly lastRecommendation = signal<string | null>(null);
  protected readonly showAddDog = signal(false);
  protected readonly error = signal('');
  protected readonly noteSuccess = signal('');

  protected selectDog(dog: Dog): void {
    this.selectedDog.set(dog);
    this.lastRecommendation.set(null);
  }

  protected async onDeleteAccount(): Promise<void> {
    const confirmed = window.confirm(
      'Delete your account? This permanently removes your account and all your dogs and ' +
        'readings. This cannot be undone.',
    );
    if (!confirmed) return;
    this.error.set('');
    try {
      await firstValueFrom(this.auth.deleteAccount());
      this.auth.logout();
    } catch (err) {
      this.error.set(errorDetail(err, 'Failed to delete account'));
    }
  }

  protected async onAddDog(event: Event): Promise<void> {
    event.preventDefault();
    this.error.set('');
    await submit(this.addDogForm, {
      action: async () => {
        try {
          const dog = await firstValueFrom(
            this.http.post<Dog>(`${environment.apiUrl}/dogs`, this.addDogModel()),
          );
          this.dogsResource.update((dogs) => [...dogs, dog]);
          this.selectDog(dog);
          this.showAddDog.set(false);
          this.addDogModel.set({ name: '', breed: '', age: null });
        } catch (err) {
          this.error.set(errorDetail(err, 'Failed to add dog'));
        }
      },
    });
  }

  protected async onSubmitReading(event: Event): Promise<void> {
    event.preventDefault();
    const dog = this.selectedDog();
    if (!dog) return;
    this.error.set('');
    await submit(this.readingForm, {
      action: async () => {
        try {
          const reading = await firstValueFrom(
            this.http.post<Reading>(`${environment.apiUrl}/readings`, {
              dog_id: dog.id,
              bpm: this.readingModel().bpm,
            }),
          );
          this.lastRecommendation.set(reading.recommendation);
          this.readingsResource.update((readings) => [reading, ...readings]);
          this.readingModel.set({ bpm: null });
        } catch (err) {
          this.error.set(errorDetail(err, 'Failed to submit reading'));
        }
      },
    });
  }

  protected async onAddNote(event: Event): Promise<void> {
    event.preventDefault();
    const dog = this.selectedDog();
    if (!dog) return;
    this.noteSuccess.set('');
    this.error.set('');
    await submit(this.noteForm, {
      action: async () => {
        try {
          await firstValueFrom(
            this.http.post<Note>(`${environment.apiUrl}/dogs/${dog.id}/notes`, {
              body: this.noteModel().body,
            }),
          );
          this.noteSuccess.set('Note sent to your vet.');
          this.noteModel.set({ body: '' });
          this.notesResource.reload();
        } catch (err) {
          this.error.set(errorDetail(err, 'Failed to send note'));
        }
      },
    });
  }

  protected recommendationLabel(recommendation: string): string {
    switch (recommendation) {
      case 'recount':
        return 'Recount';
      case 'check_membranes_hr':
        return 'Check mucous membranes & heart rate';
      case 'go_to_vet':
        return 'Go to vet';
      default:
        return recommendation;
    }
  }

  protected recommendationClass(recommendation: string): string {
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
