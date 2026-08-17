# Frontend — Angular 22 SPA

Angular 22 standalone SPA under `src/app/` (no NgModules). See `@AGENTS.md` at the repo root for repo-wide rules and dev commands.

## Zoneless — read this first

This app runs **zoneless**: no `zone.js` dependency, no `polyfills` entry in `@./angular.json`. Nothing outside a signal triggers change detection, so assigning to a plain field inside a `subscribe`, `setTimeout`, or event callback updates the object but never repaints. Every value a template reads must be a `signal()`, `computed()`, `linkedSignal()`, or a resource. When a change "doesn't show up in the UI", this is why.

## Angular 22 APIs — use these, not the older equivalents

These landed in v21/22 and are newer than most training data. Prefer them over the pattern you would reach for by default.

- **Reads over HTTP → `httpResource()`** (`@angular/common/http`), not `HttpClient.get()` + `.subscribe()`. It takes a reactive request function and exposes `value()`, `isLoading()`, `error()`, `status()`, `reload()` as signals, re-fetching whenever a signal it reads changes. Use `rxResource()` (`@angular/core/rxjs-interop`) only when the source genuinely is an Observable, `resource()` for a bare promise. `HttpClient` stays for writes (POST/PUT/DELETE).
- **Forms → signal forms** (`@angular/forms/signals`), not `FormsModule` / `ReactiveFormsModule`. The model is a `signal()`, `form(model, schema)` returns a `FieldTree`, the `<form>` element carries `formRoot`, and each control binds via `[formField]`:

  ```ts
  import { form, required, email, minLength, submit } from '@angular/forms/signals';

  protected readonly model = signal({ email: '', password: '' });
  protected readonly f = form(this.model, (p) => {
    required(p.email);
    email(p.email);
    minLength(p.password, 8);
  });
  ```

  ```html
  <form formRoot><input type="email" [formField]="f.email" /></form>
  ```

  Submit through `submit(this.f, { action })` — it awaits validation and returns `Promise<boolean>`; don't hand-roll a `valid`/`loading` flag pair.

- **Derived state → `computed()`; derived-but-writable → `linkedSignal()`** (a selection that resets when its source list reloads). Never use `effect()` to copy one signal into another — `effect()` is only for leaving Angular (localStorage, `document`, a third-party lib).
- **DI → `inject()`** as a `private readonly` field initializer, never constructor parameters — see `@./src/app/core/auth.ts`. Enforced by `@angular-eslint/prefer-inject`.
- **Component I/O → `input()` / `output()` / `model()`**, never `@Input()` / `@Output()`. Element queries → `viewChild()` / `contentChild()`.
- **Leave `changeDetection` out of `@Component`.** In v22 `OnPush` is the default — writing `ChangeDetectionStrategy.Default` (or `.Eager`) opts out of it and is a lint error.

## TypeScript style

- **Explicit access modifier on every class member** — `private`, `protected`, or `public`, never bare. Template-facing members are `protected readonly`; the rest is `private readonly` unless it belongs to a service's public surface.
- **Explicit return type on every method and exported function**, including `void` and `Promise<void>`.
- **No `any`.** Declare the response interface instead, mirroring the backend Pydantic schema — `VetRead` in `@./src/app/core/auth.ts` mirrors `backend/app/schemas/vet.py`.

All three are ESLint errors, not suggestions: run `npm run lint` (and `npm run lint -- --fix` for what is auto-fixable) before declaring frontend work done.

## Local rules

- **Standalone components only.** No NgModules anywhere. A component declares its own dependencies inline in `@Component({ imports: [...] })` — see `@./src/app/app.ts`. Register global providers in `@./src/app/app.config.ts` and routes in `@./src/app/app.routes.ts`.
- **No type suffix in names.** Drop the legacy Angular suffix: a dashboard is `dashboard.ts` with class `Dashboard`, not `dashboard.component.ts` / `DashboardComponent`. Files are kebab-case; the class is PascalCase of the same base.
- **Co-locate the triad.** Each component is `<name>.ts` + `<name>.html` + `<name>.scss` sharing one base name, wired via singular `templateUrl` / `styleUrl` (never the plural `styleUrls`).
- **View state via `signal()`.** Hold component state in `signal()` fields declared `protected readonly` — see `title` in `@./src/app/app.ts`.
- **Selectors are `app-`-prefixed** (e.g. `app-root`).

## Adding a component

Create `src/app/<feature>/<feature>.ts` (+ `.html`, `.scss`) shaped like `@./src/app/app.ts`, then register its path in `@./src/app/app.routes.ts`. The single bootstrap lives in `@./src/main.ts` — don't add a second.

## Tooling

Prettier (`@./.prettierrc`) and `@./.editorconfig` enforce formatting. Scaffolded with `--skip-tests`: no `.spec.ts` files exist and `npm test` has no specs — add a spec and confirm the runner before writing tests.
