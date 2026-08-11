# Frontend — Angular 22 SPA

Angular 22 standalone SPA under `src/app/` (no NgModules). See `@AGENTS.md` at the repo root for repo-wide rules and dev commands.

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
