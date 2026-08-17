import { Routes } from '@angular/router';
import { vetGuard, ownerGuard } from './core/guards';

export const routes: Routes = [
  { path: '', redirectTo: 'login', pathMatch: 'full' },
  { path: 'login', loadComponent: () => import('./login/login').then((m) => m.Login) },
  { path: 'register', loadComponent: () => import('./register/register').then((m) => m.Register) },
  {
    path: 'accept-invitation',
    loadComponent: () =>
      import('./accept-invitation/accept-invitation').then((m) => m.AcceptInvitation),
  },
  {
    path: 'password-reset',
    loadComponent: () => import('./password-reset/password-reset').then((m) => m.PasswordReset),
  },
  {
    path: 'owner',
    canActivate: [ownerGuard],
    loadComponent: () => import('./owner/dashboard').then((m) => m.OwnerDashboard),
  },
  {
    path: 'vet/panel',
    canActivate: [vetGuard],
    loadComponent: () => import('./vet/panel').then((m) => m.VetPanel),
  },
];
