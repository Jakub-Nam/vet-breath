import { HttpClient } from '@angular/common/http';
import { Injectable, signal, computed, inject } from '@angular/core';
import { Router } from '@angular/router';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

interface TokenPayload {
  sub: string;
  role: 'vet' | 'owner';
  exp: number;
}

interface TokenResponse {
  access_token: string;
  token_type: string;
}

/** Mirrors `VetRead` in `backend/app/schemas/vet.py`. */
export interface VetRead {
  id: number;
  email: string;
  full_name: string | null;
  created_at: string;
}

@Injectable({ providedIn: 'root' })
export class Auth {
  private readonly http = inject(HttpClient);
  private readonly router = inject(Router);

  private readonly token = signal<string | null>(localStorage.getItem('token'));
  private readonly payload = computed<TokenPayload | null>(() => {
    const t = this.token();
    if (!t) return null;
    try {
      return JSON.parse(atob(t.split('.')[1]));
    } catch {
      return null;
    }
  });

  public readonly isLoggedIn = computed(() => {
    const payload = this.payload();
    return !!payload && payload.exp * 1000 > Date.now();
  });

  public readonly role = computed(() => this.payload()?.role ?? null);
  public readonly userId = computed(() => this.payload()?.sub ?? null);

  public register(email: string, password: string, fullName: string): Observable<VetRead> {
    return this.http.post<VetRead>(`${environment.apiUrl}/auth/register`, {
      email,
      password,
      full_name: fullName,
    });
  }

  public login(email: string, password: string): Observable<TokenResponse> {
    return this.http.post<TokenResponse>(`${environment.apiUrl}/auth/login`, {
      email,
      password,
    });
  }

  public deleteAccount(): Observable<void> {
    return this.http.delete<void>(`${environment.apiUrl}/auth/me`);
  }

  public setToken(token: string): void {
    localStorage.setItem('token', token);
    this.token.set(token);
  }

  public logout(): void {
    localStorage.removeItem('token');
    this.token.set(null);
    this.router.navigate(['/login']);
  }

  public getToken(): string | null {
    return this.token();
  }
}
