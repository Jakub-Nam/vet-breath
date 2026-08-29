# Lessons Learned

> Append-only register of recurring rules and patterns. Re-read at start by /10x-frame, /10x-research, /10x-plan, /10x-plan-review, /10x-implement, /10x-impl-review.

## Never return ORM models across an endpoint — always go through app/schemas/

- **Context**: Backend (FastAPI). Każda operacja ścieżki w `app/api/*` zwracająca dane utrwalone; zawsze gdy obiekt ORM z `app/models/` mógłby zostać oddany bezpośrednio zamiast modelu Pydantic z `app/schemas/`.
- **Problem**: Zwrócenie obiektu ORM wprost wiąże publiczny kontrakt API ze schematem bazy, grozi wyciekiem wewnętrznych/wrażliwych kolumn i po cichu psuje kształt odpowiedzi, gdy warstwa persistence ewoluuje. Mylenie `models/` ze `schemas/`, bo „wyglądają identycznie", to powtarzalny trap FastAPI, który ten kod wprost odnotowuje (backend/AGENTS.md:62).
- **Rule**: Nigdy nie zwracaj modeli ORM z `app/models/` przez granicę endpointu. Każda odpowiedź przechodzi przez schema Pydantic z `app/schemas/` (modele odczytu budowane przez `from_attributes`). Trzymaj modele ORM i schematy API rozdzielone nawet gdy wyglądają identycznie.
- **Applies to**: plan, implement, impl-review

## Angular 22 — nie ustawiaj changeDetection; OnPush jest domyślny

- **Context**: Frontend (Angular 22, zoneless SPA). Każdy dekorator `@Component({...})`; zawsze gdy z przyzwyczajenia sięgasz po pole `changeDetection:`.
- **Problem**: Wiedza z ery starszego Angulara mówi „zawsze deklaruj `changeDetection: ChangeDetectionStrategy.OnPush`". W v22 OnPush jest już domyślny — więc wpisanie `ChangeDetectionStrategy.Default`/`.Eager` po cichu WYŁĄCZA OnPush, a nawet zbędne jawne ustawienie OnPush to błąd lintera. Konwencja, która kiedyś była best-practice, jest teraz defektem, który agent wprowadza odruchowo.
- **Rule**: Nigdy nie dodawaj pola `changeDetection` do `@Component` w tej aplikacji. Angular 22 domyślnie używa OnPush — pomiń je. Jeśli wydaje Ci się, że potrzebujesz `ChangeDetectionStrategy.Default`, poprawką jest `signal()`, a nie eager change detection.
- **Applies to**: implement, impl-review
