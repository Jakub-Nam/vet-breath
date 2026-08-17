import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { Auth } from './auth';

export const authGuard: CanActivateFn = () => {
  const auth = inject(Auth);
  const router = inject(Router);
  if (auth.isLoggedIn()) return true;
  router.navigate(['/login']);
  return false;
};

export const vetGuard: CanActivateFn = () => {
  const auth = inject(Auth);
  const router = inject(Router);
  if (auth.isLoggedIn() && auth.role() === 'vet') return true;
  router.navigate(['/login']);
  return false;
};

export const ownerGuard: CanActivateFn = () => {
  const auth = inject(Auth);
  const router = inject(Router);
  if (auth.isLoggedIn() && auth.role() === 'owner') return true;
  router.navigate(['/login']);
  return false;
};
