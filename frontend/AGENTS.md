# Frontend — Angular 22 SPA

Angular 22 standalone SPA under `src/app/` (no NgModules). See `@AGENTS.md` at the repo root for repo-wide rules and dev commands.

## Zoneless — read this first

This app runs **zoneless**: no `zone.js` dependency, no `polyfills` entry in `@./angular.json`. Nothing outside a signal triggers change detection, so assigning to a plain field inside a `subscribe`, `setTimeout`, or event callback updates the object but never repaints. Every value a template reads must be a `signal()`, `computed()`, `linkedSignal()`, or a resource. When a change "doesn't show up in the UI", this is why.

## Angular 22 APIs — use these, not the older equivalents

These landed in v21/22 and are newer than most training data. Prefer them over the pattern you would reach for by default.

- **Reads over HTTP → `httpResource()`** (`@angular/common/http`), not `HttpClient.get()` + `.subscribe()`. It takes a reactive request function and exposes `value()`, `isLoading()`, `error()`, `status()`, `reload()` as signals, re-fetching whenever a signal it reads changes. Use `rxResource()` (`@angular/core/rxjs-interop`) only when the source genuinely is an Observable, `resource()` for a bare promise. `HttpClient` stays for writes (POST/PUT/DELETE). Return `undefined` from the request function to skip the call until its inputs are ready — `notesResource` in `@./src/app/vet/panel.ts` does this while the notes panel is closed. `value` is writable, so a POST that returns the created entity can push into it (`@./src/app/owner/dashboard.ts`) instead of forcing a refetch; use `.reload()` when the server is the source of truth.
- **Forms → signal forms** (`@angular/forms/signals`), not `FormsModule` / `ReactiveFormsModule`. The model is a `signal()`, `form(model, schema)` returns a `FieldTree`, and the component imports the `FormRoot` + `FormField` directives. Copy the shape from `@./src/app/login/login.ts` (single form) or `@./src/app/password-reset/password-reset.ts` (two forms in one component).

  Three things that bite:
  - `formRoot` is a **required** input — `<form [formRoot]="loginForm">`, never a bare `formRoot` attribute.
  - `FormRoot` declares no outputs, so there is no `ngSubmit` without `FormsModule`. Use the native `(submit)` and call `event.preventDefault()` yourself.
  - Submit through `submit(this.loginForm, { action })` — it awaits validation, and `loginForm().submitting()` drives the button. Never hand-roll a `valid`/`loading` flag pair.

  Field state for error display: `loginForm.email().touched()`, `.invalid()`, `.errors()`.

- **Derived state → `computed()`; derived-but-writable → `linkedSignal()`** (a selection that resets when its source list reloads). Never use `effect()` to copy one signal into another — `effect()` is only for leaving Angular (localStorage, `document`, a third-party lib).
- **DI → `inject()`** as a `private readonly` field initializer, never constructor parameters — see `@./src/app/core/auth.ts`. Enforced by `@angular-eslint/prefer-inject`.
- **Component I/O → `input()` / `output()` / `model()`**, never `@Input()` / `@Output()`. Element queries → `viewChild()` / `contentChild()`.
- **Leave `changeDetection` out of `@Component`.** In v22 `OnPush` is the default — writing `ChangeDetectionStrategy.Default` (or `.Eager`) opts out of it and is a lint error.

## TypeScript style

- **No single-letter identifiers — ever.** Every binding gets a full word, including lambda parameters and short-lived locals: `loginForm` not `f`, `path` not `p`, `dog` not `d`, `reading` not `r`. This holds even where the scope is two lines long; brevity is never the reason. Applies to variables, parameters, fields, and destructured names.
- **Explicit access modifier on every class member** — `private`, `protected`, or `public`, never bare. Template-facing members are `protected readonly`; the rest is `private readonly` unless it belongs to a service's public surface.
- **Explicit return type on every method and exported function**, including `void` and `Promise<void>`.
- **No `any`.** Declare the response interface instead, mirroring the backend Pydantic schema — `VetRead` in `@./src/app/core/auth.ts` mirrors `backend/app/schemas/vet.py`.

The last three are ESLint errors, not suggestions; the naming rule is on you, since no rule can check it. A `PostToolUse` hook (`@../.claude/hooks/eslint-fix.sh`) runs `eslint --fix` on every `.ts`/`.html` touched under `frontend/` and reports back whatever it could not fix. `npm run lint` is the full-repo check — run it before declaring frontend work done.

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
