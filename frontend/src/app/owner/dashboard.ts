import { Component, OnInit, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { DatePipe } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Auth } from '../core/auth';
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

@Component({
  selector: 'app-owner-dashboard',
  imports: [FormsModule, DatePipe],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.scss',
})
export class OwnerDashboard implements OnInit {
  protected readonly dogs = signal<Dog[]>([]);
  protected readonly selectedDog = signal<Dog | null>(null);
  protected readonly readings = signal<Reading[]>([]);
  protected readonly lastRecommendation = signal<string | null>(null);

  protected readonly newDogName = signal('');
  protected readonly newDogBreed = signal('');
  protected readonly newDogAge = signal<number | null>(null);
  protected readonly bpm = signal<number | null>(null);

  protected readonly showAddDog = signal(false);
  protected readonly loading = signal(false);
  protected readonly error = signal('');

  constructor(
    private http: HttpClient,
    protected auth: Auth,
  ) {}

  ngOnInit() {
    this.loadDogs();
  }

  loadDogs() {
    this.http.get<Dog[]>(`${environment.apiUrl}/dogs`).subscribe({
      next: (dogs) => {
        this.dogs.set(dogs);
        if (dogs.length > 0 && !this.selectedDog()) {
          this.selectDog(dogs[0]);
        }
      },
    });
  }

  selectDog(dog: Dog) {
    this.selectedDog.set(dog);
    this.lastRecommendation.set(null);
    this.loadReadings(dog.id);
  }

  loadReadings(dogId: number) {
    this.http.get<Reading[]>(`${environment.apiUrl}/readings?dog_id=${dogId}`).subscribe({
      next: (readings) => this.readings.set(readings),
    });
  }

  addDog() {
    if (!this.newDogName() || !this.newDogBreed() || !this.newDogAge()) return;
    this.http
      .post<Dog>(`${environment.apiUrl}/dogs`, {
        name: this.newDogName(),
        breed: this.newDogBreed(),
        age: this.newDogAge(),
      })
      .subscribe({
        next: (dog) => {
          this.dogs.update((d) => [...d, dog]);
          this.selectDog(dog);
          this.showAddDog.set(false);
          this.newDogName.set('');
          this.newDogBreed.set('');
          this.newDogAge.set(null);
        },
        error: (err) => this.error.set(err.error?.detail ?? 'Failed to add dog'),
      });
  }

  submitReading() {
    const dog = this.selectedDog();
    const bpm = this.bpm();
    if (!dog || !bpm) return;

    this.loading.set(true);
    this.http
      .post<Reading>(`${environment.apiUrl}/readings`, {
        dog_id: dog.id,
        bpm,
      })
      .subscribe({
        next: (reading) => {
          this.lastRecommendation.set(reading.recommendation);
          this.readings.update((r) => [reading, ...r]);
          this.bpm.set(null);
          this.loading.set(false);
        },
        error: (err) => {
          this.error.set(err.error?.detail ?? 'Failed to submit reading');
          this.loading.set(false);
        },
      });
  }

  recommendationLabel(rec: string): string {
    switch (rec) {
      case 'recount':
        return 'Recount';
      case 'check_membranes_hr':
        return 'Check mucous membranes & heart rate';
      case 'go_to_vet':
        return 'Go to vet';
      default:
        return rec;
    }
  }

  recommendationClass(rec: string): string {
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
}
