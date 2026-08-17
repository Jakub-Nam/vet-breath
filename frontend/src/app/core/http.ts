import { HttpErrorResponse, HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { Auth } from './auth';

/**
 * Pulls FastAPI's `{ "detail": "..." }` body out of a failed request.
 * `submit()` actions catch `unknown`, so the narrowing lives here once
 * instead of in every component.
 */
export function errorDetail(err: unknown, fallback: string): string {
  const detail = err instanceof HttpErrorResponse ? err.error?.detail : undefined;
  return typeof detail === 'string' ? detail : fallback;
}

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const auth = inject(Auth);
  const token = auth.getToken();
  if (token) {
    req = req.clone({ setHeaders: { Authorization: `Bearer ${token}` } });
  }
  return next(req);
};
