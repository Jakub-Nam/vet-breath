import { HttpClient } from '@angular/common/http';
import { Injectable, signal, computed } from '@angular/core';
import { Router } from '@angular/router';
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

@Injectable({ providedIn: 'root' })
export class Auth {
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

  readonly isLoggedIn = computed(() => {
    const p = this.payload();
    return !!p && p.exp * 1000 > Date.now();
  });

  readonly role = computed(() => this.payload()?.role ?? null);
  readonly userId = computed(() => this.payload()?.sub ?? null);

  constructor(
    private http: HttpClient,
    private router: Router,
  ) {}

  register(email: string, password: string, fullName: string) {
    return this.http.post<any>(`${environment.apiUrl}/auth/register`, {
      email,
      password,
      full_name: fullName,
    });
  }

  login(email: string, password: string) {
    return this.http.post<TokenResponse>(`${environment.apiUrl}/auth/login`, {
      email,
      password,
    });
  }

  acceptInvitation(token: string, password: string) {
    return this.http.post<TokenResponse>(`${environment.apiUrl}/auth/accept-invitation`, {
      token,
      password,
    });
  }

  setToken(token: string) {
    localStorage.setItem('token', token);
    this.token.set(token);
  }

  logout() {
    localStorage.removeItem('token');
    this.token.set(null);
    this.router.navigate(['/login']);
  }

  getToken(): string | null {
    return this.token();
  }
}
