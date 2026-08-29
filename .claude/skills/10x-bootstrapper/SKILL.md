---
name: 10x-bootstrapper
description: >
  Scaffold a project into the current working directory after the tech stack
  is picked. Reads context/foundation/tech-stack.md, runs the chosen starter's
  CLI with a strict conflict policy that always preserves context/, and writes
  a verification log. Use when the user says "bootstrap the project",
  "scaffold the app", "set up the codebase", "let's start the project".
  Use AFTER /10x-tech-stack-selector.
argument-hint: "[path-to-tech-stack]"
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - AskUserQuestion
  - TaskCreate
  - TaskUpdate
---

# Bootstrapper: Od stosu technologicznego do projektu z szablonu

Ta umiejętność jest końcowym ogniwem sekwencji uruchamiania (`/10x-shape → /10x-prd → /10x-tech-stack-selector → 10x-bootstrapper`). Jej jedyne zadanie: przekształcić pisemne przekazanie stosu technologicznego w projekt z szablonu w bieżącym katalogu roboczym, z wynikami weryfikacji zapisanymi w dzienniku do wglądu użytkownika.

Umiejętność ta jest **konsumentem rejestru**, a nie jego właścicielem. Rejestr starterów znajduje się w `/10x-tech-stack-selector` (`/skills/10x-tech-stack-selector/references/starter-registry.yaml`); bootstrapper wyszukuje wybraną kartę po `starter_id`, podstawia jej `cmd_template` i przekazuje do odpowiedniej strategii cwd. Walidator CI (`scripts/validate-starter-registry-sync.mjs`) zapobiega odwoływaniu się bootstrapper'a do `starter_id` nieobecnego w tym rejestrze.

v1 działa **tylko w trybie łańcuchowym**. Bez `context/foundation/tech-stack.md` umiejętność odmawia i przekierowuje do `/10x-tech-stack-selector`. Nie ma wbudowanego mini-przekazania, trybu samodzielnego, ani awaryjnego rozwiązania AI-as-bridge dla nieznanych stosów. v1 również **nie** generuje `AGENTS.md` / `CLAUDE.md` — ta odpowiedzialność należy do przyszłej umiejętności M1L4.

## Kiedy uruchomić

Użyj, gdy `context/foundation/tech-stack.md` istnieje, a użytkownik jest gotowy do utworzenia szablonu. Frazy wyzwalające: "bootstrap the project", "scaffold the app", "set up the codebase", "let's start the project", "spin up the repo" lub dowolne naturalne następstwo uruchomienia `/10x-tech-stack-selector`, które właśnie zapisało przekazanie.

Warunkiem wstępnym jest pojedynczy plik na dysku: `context/foundation/tech-stack.md`. Umiejętność nigdy nie wraca do historii rozmów, nigdy nie uruchamia ponownie wywiadu dotyczącego stosu technologicznego, nigdy nie akceptuje stosu nazwanego w tekście.

## Kiedy pominąć

Pomiń, gdy:

- Użytkownik jest w trakcie implementacji istniejącej bazy kodu i prosi o dodanie pojedynczej biblioteki lub zastąpienie pojedynczej zależności — to jest obszar `/10x-frame`, a nie bootstrap.
- Użytkownik podaje stos spoza rejestru tech-stack-selector — przekieruj do `/10x-tech-stack-selector` (jest on właścicielem rejestru; jeśli brakuje startera, tam się on znajduje).
- `context/foundation/tech-stack.md` jest nieobecny — sprawdzenie warunku wstępnego w Kroku 0 obsługuje to z wyraźnym przekierowaniem.

## Wymagane dane wejściowe

1. `context/foundation/tech-stack.md` — przekazanie zapisane przez `/10x-tech-stack-selector`. Umowa: patrz `references/handoff-consumer.md` (który odwołuje się do `/10x-tech-stack-selector/references/handoff-schema.md` jako autorytatywnego schematu).
2. Wybrana karta z `/skills/10x-tech-stack-selector/references/starter-registry.yaml`. Rozwiązana przez wyszukiwanie `starter_id`. Zawiera `cmd_template`, `language_family`, `bootstrapper_confidence`, `toolchain.package_manager`, `deployment_defaults`.
3. `references/bootstrapper-config.yaml` — nadpisania `cwd_strategy` dla każdego startera po stronie bootstrapper'a + wyszukiwanie `language_family → audit_command`. Dołączone do umiejętności.
4. `references/handoff-consumer.md` — dołączone. Ładowane w Kroku 0.
5. `references/refusal-protocol.md` — dołączone. Ładowane, gdy wystąpi jakikolwiek warunek odmowy.
6. `references/pre-scaffold-verification.md` — dołączone. Ładowane w Kroku 1.
7. `references/scaffold-merge.md` — dołączone. Ładowane w Kroku 2.
8. `references/post-scaffold-verification.md` — dołączone. Ładowane w Kroku 3.
9. `references/verification-log-schema.md` — dołączone. Ładowane w Kroku 4.

## Początkowa odpowiedź

Gdy ta umiejętność zostanie wywołana:

1. **Jeśli podano argument ścieżki** (np. `/10x-bootstrapper @context/foundation/tech-stack-v2.md` lub `/10x-bootstrapper path/to/tech-stack.md`), usuń początkowy `@`, jeśli jest obecny, i użyj ścieżki dosłownie jako lokalizacji przekazania dla tego uruchomienia.
2. **Jeśli nie podano argumentu**, domyślnie ustaw ścieżkę przekazania na `context/foundation/tech-stack.md`.

Przenieś rozwiązaną ścieżkę przez Krok 0; reszta przepływu pracy działa na niej jako `<handoff-path>`.

## Przepływ pracy

### Krok 0 — Warunek wstępny przekazania

Sprawdź warunek wstępny przekazania względem rozwiązanej ścieżki:

```bash
test -f "<handoff-path>"
```

**Jeśli brak**, wykonaj dokładnie to i ZATRZYMAJ — bez awaryjnego wywiadu, bez wbudowanego mini-przekazania, bez czytania rozmowy w poszukiwaniu zastępczego wyboru stosu:

```bash
echo -n "/10x-tech-stack-selector" | pbcopy 2>/dev/null || echo -n "/10x-tech-stack-selector" | clip.exe 2>/dev/null || echo -n "/10x-tech-stack-selector" | xclip -selection clipboard 2>/dev/null || true
```

```powershell
# PowerShell (Windows)
Set-Clipboard "/10x-tech-stack-selector"
```

Wydrukuj dosłownie (podstaw rozwiązaną ścieżkę; jeśli domyślna, to `context/foundation/tech-stack.md`):

```
Bootstrapper wymaga przekazania stosu technologicznego pod adresem `<handoff-path>`. Najpierw uruchom `/10x-tech-stack-selector`, a następnie wywołaj ponownie.
```

Następnie ZATRZYMAJ. Kontekst rozmowy **nie** jest awaryjnym rozwiązaniem — nawet jeśli wybór stosu był wcześniej omawiany na czacie, umiejętność wymaga pliku na dysku. Zobacz `references/refusal-protocol.md` dla pełnego zestawu warunków odmowy i ciągów schowka.

**Jeśli obecny**, przeczytaj go W CAŁOŚCI (bez `limit`/`offset`) i kontynuuj. Przeanalizuj frontmatter zgodnie z `references/handoff-consumer.md` i rozwiąż wybraną kartę przez wyszukiwanie `starter_id` w `/skills/10x-tech-stack-selector/references/starter-registry.yaml`. Jeśli wyszukiwanie się nie powiedzie, uruchom odmowę dryfu rejestru z `references/refusal-protocol.md` i ZATRZYMAJ.

Wyświetl zużyte pola użytkownikowi jako podsumowanie do potwierdzenia lub poprawienia:

```
Otrzymano przekazanie:
  Starter:        <starter_id> — <name>
  Nazwa projektu:   <project_name>
  Menedżer pakietów:<package_manager | "(card default)" jeśli pominięto>
  Język:       <hints.language_family>
  Pewność:     <hints.bootstrapper_confidence>
  Wybrana ścieżka:     <hints.path_taken>
  Wdrożenie:     <hints.deployment_target>
  Flagi funkcji:  <lista oddzielona przecinkami has_* ustawionych na true, lub "none">
```

Zadaj jedno pytanie potwierdzające:

AskUserQuestion:
- question: "Kontynuować z tym przekazaniem, czy najpierw coś poprawić?"
  header: "Przekazanie"
  options:
  - label: "Kontynuuj (zalecane)"
    description: "Kontynuuj z przekazaniem w odczytanej formie."
  - label: "Popraw wartość"
    description: "Zapytam, które pole nadpisać dla tego uruchomienia; plik na dysku pozostanie niezmieniony."
  - label: "Zatrzymaj — najpierw popraw przekazanie"
    description: "Wyjdź. Uruchom ponownie /10x-tech-stack-selector, aby zaktualizować tech-stack.md, a następnie wywołaj ponownie."
  multiSelect: false

Jeśli "Popraw wartość": zapytaj, które pole, przechwyć nadpisanie, kontynuuj z nadpisaniem zastosowanym tylko dla tej sesji. Następnie uruchom strażnika zapełnionego cwd z `references/refusal-protocol.md` (ostrzeż i potwierdź, jeśli cwd już zawiera odcisk palca w kształcie szablonu, taki jak `package.json`, `Cargo.toml`, `Gemfile`, `pyproject.toml` itp.).

### Krok 1 — Weryfikacja przed utworzeniem szablonu

Przed uruchomieniem CLI startera, wykonaj lekkie sprawdzenie aktualności opisane w `references/pre-scaffold-verification.md`. Przeczytaj teraz to odniesienie. Slot jest tylko do odczytu — bez klonowania, bez instalacji, bez zmian w systemie plików — i ma charakter edukacyjny, a nie blokujący: każde znalezisko to OSTRZEŻENIE-I-KONTYNUUJ.

Sekwencja:

1. Z wybranej karty, wywnioskuj nazwę pakietu npm z `cmd_template`, jeśli `hints.language_family == js` i szablon wywołuje CLI `create-*` (np. `npm create next-app` → `create-next-app`, `npm create astro` → `create-astro`, `npm create vite` → `create-vite`). Jeśli szablon zaczyna się od `git clone`, pomiń krok npm.
2. Jeśli nazwa pakietu została wywnioskowana, uruchom `npm view <package> version` i `npm view <package> time.modified`.
3. Z wybranej karty, przeanalizuj `docs_url`. Jeśli wskazuje na `github.com/<owner>/<repo>`, uruchom `gh api repos/<owner>/<repo> --jq '.pushed_at'`.
4. Oblicz ważność zgodnie z progami w `pre-scaffold-verification.md` (świeży / stary / przestarzały).
5. Wydrukuj jedną linię podsumowania w rozmowie. Poprzedź jednowierszowym ostrzeżeniem "Heads-up", jeśli jakikolwiek sygnał jest przestarzały. Nigdy nie blokuj — przejdź do Kroku 2 niezależnie.
6. Przygotuj rozwiązaną nazwę pakietu (jeśli istnieje), adres URL repozytorium GitHub (jeśli istnieje), oba znaczniki czasu i obie ważności do rekordu weryfikacji w pamięci. Krok 4 zapisuje ten rekord na dysku.

Jeśli wywołanie sieciowe się nie powiedzie, zaloguj błąd i kontynuuj z częściowym rekordem — patrz "Failure mode" w odniesieniu.

Wyszukaj `cwd_strategy` dla wybranego `starter_id` z `references/bootstrapper-config.yaml` teraz (domyślnie `subdir-then-move`, jeśli id nie jest wymienione). Krok 2 tego potrzebuje. Wyszukaj `audit_commands[<hints.language_family>]` z tego samego pliku w tym samym czasie i przygotuj go do Kroku 3 (wartość `null` oznacza, że Krok 3 pominie audyt i zanotuje pominięcie w dzienniku).

### Krok 2 — Utwórz szablon i scal

Przeczytaj teraz `references/scaffold-merge.md`. Zawiera on pełną mechanikę dla trzech strategii cwd, macierz konfliktów, reguły podstawiania i ścieżkę TWARDEGO ZATRZYMANIA w przypadku awarii CLI.

Sekwencja:

1. Rozwiąż `cmd_template` z wybranej karty. Podstaw `{name}` i `{pm}` zgodnie z obowiązującą strategią (patrz `scaffold-merge.md` § Reguły podstawiania). Awaryjnym rozwiązaniem dla `{pm}` jest `toolchain.package_manager` karty, jeśli przekazanie pomija to pole.
2. Wyślij do `cwd_strategy` (rozwiązane w Kroku 1 z `bootstrapper-config.yaml`, domyślnie `subdir-then-move`):
   - **`subdir-then-move`** — uruchom rozwiązane polecenie z `{name}=.bootstrap-scaffold`. Po kodzie wyjścia 0, zastosuj macierz konfliktów przenosząc pliki do cwd, a następnie usuń `.bootstrap-scaffold/`.
   - **`native-cwd`** — uruchom rozwiązane polecenie z `{name}=.` bezpośrednio w cwd. Brak kroku scalania. Przed lotem: wyświetl pliki, które CLI ma zamiar dotknąć, wyświetl je w rozmowie przed wykonaniem.
   - **`git-clone`** — uruchom rozwiązane polecenie z `{name}=.bootstrap-scaffold`. Po kodzie wyjścia 0, usuń `.bootstrap-scaffold/.git/` przed zastosowaniem macierzy konfliktów i przeniesieniem plików. Następnie usuń `.bootstrap-scaffold/`.
3. Przechwyć stdout, stderr i kod wyjścia do rekordu weryfikacji w pamięci, niezależnie od wyniku.
4. **Awaria CLI to TWARDE ZATRZYMANIE.** Jeśli kod wyjścia jest różny od zera, uruchom ścieżkę obsługi awarii CLI w `scaffold-merge.md` § Obsługa awarii CLI: pozostaw `.bootstrap-scaffold/` na miejscu, nie stosuj macierzy konfliktów, zapisz częściowy `verification.md` z `phase_3_status: failed`, ustaw schowek na `/10x-bootstrapper`, wydrukuj podsumowanie awarii i ZATRZYMAJ. Nie przechodź do Kroku 3.
5. Po kodzie wyjścia 0, wydrukuj jedną linię podsumowania zgodnie z formatem w `scaffold-merge.md` § Wyświetlanie wyniku. Przygotuj dziennik przenoszenia plików do rekordu weryfikacji w pamięci. Przejdź do Kroku 3.

Strażnik zapełnionego cwd z Kroku 0 (`refusal-protocol.md` § (d)) został już uruchomiony przed tym krokiem. Macierz konfliktów jest siatką bezpieczeństwa: istniejące pliki stają się rodzeństwem `.scaffold`, `context/` jest zawsze zachowywany, `.gitignore` jest scalany przez dołączanie.

Mówiąc do użytkownika, przetłumacz nazwy strategii na język naturalny ("utwórz szablon w katalogu tymczasowym, a następnie przenieś pliki", "utwórz szablon bezpośrednio w bieżącym katalogu", "sklonuj repozytorium startera bez zachowywania jego historii git") zamiast dosłownie powtarzać wewnętrzne etykiety.

### Krok 3 — Weryfikacja po utworzeniu szablonu

Przeczytaj teraz `references/post-scaffold-verification.md`. Slot wysyła do polecenia audytu rozwiązanego w Kroku 1 (`audit_commands[<hints.language_family>]` z `bootstrapper-config.yaml`) i klasyfikuje wyniki według ważności.

Sekwencja:

1. Jeśli rozwiązane polecenie audytu to `null`, pomiń audyt i przygotuj ustrukturyzowaną notatkę "brak wbudowanego narzędzia audytu dla <language_family>" w rekordzie weryfikacji. Wydrukuj linię pominięcia zgodnie z formatem wyjściowym odniesienia. Przejdź do Kroku 4.
2. W przeciwnym razie, uruchom rozwiązane polecenie z cwd (lub odpowiedniego katalogu instalacji zależności, jeśli szablon tak ustrukturyzował projekt). Przechwyć stdout, stderr i kod wyjścia. Kod wyjścia narzędzia audytu ma charakter wyłącznie informacyjny — bootstrapper NIE zatrzymuje się w przypadku niezerowego wyjścia audytu.
3. Przeanalizuj dane wyjściowe zgodnie z blokiem wywołania dla każdego ekosystemu w odniesieniu. Podziel wyniki na KRYTYCZNE / WYSOKIE / UMIARKOWANE / NISKIE.
4. Jeśli narzędzie obsługuje rozróżnienie bezpośrednie vs. przechodnie, oblicz ten podział.
5. Wydrukuj jedną linię podsumowania w rozmowie zgodnie z formatem wyjściowym odniesienia. Liczby KRYTYCZNYCH i WYSOKICH są wyświetlane w tekście; UMIARKOWANE i NISKIE są tylko w dzienniku.
6. Przygotuj pełny podział (surowe dane wyjściowe, przeanalizowane liczby, szczegóły dla każdego znaleziska, podział bezpośredni/przechodni) do rekordu weryfikacji w pamięci.

Narzędzie niedostępne, awaria sieci lub błąd parsowania: OSTRZEŻ-I-KONTYNUUJ zgodnie z blokiem Failure mode w odniesieniu. Obecne znaleziska KRYTYCZNE: OSTRZEŻ-I-KONTYNUUJ — bootstrapper informuje, użytkownik decyduje.

### Krok 4 — Zapisz verification.md i zakończ

Przeczytaj teraz `references/verification-log-schema.md`. Ten krok zapisuje ścieżkę audytu uruchomienia na dysku i drukuje podsumowanie końcowe.

Sekwencja:

1. Upewnij się, że `context/changes/bootstrap-verification/` istnieje. Utwórz katalog, jeśli go brakuje (bez `change.md` — folder hostuje tylko dziennik).
2. Jeśli `context/changes/bootstrap-verification/verification.md` już istnieje, uruchom strażnika OSTRZEŻ-I-POTWIERDŹ z `references/refusal-protocol.md` § (e). W przypadku "Nadpisz", kontynuuj. W przypadku "Zapisz jako verification-v2.md", zwiększ do następnego dostępnego slotu `verification-vN.md`. W przypadku "Przerwij", zatrzymaj bez zapisywania.
3. Skomponuj treść pliku zgodnie z `references/verification-log-schema.md`: frontmatter (z `phase_3_status: ok` dla normalnych uruchomień, `failed` dla przypadku częściowego dziennika TWARDEGO ZATRZYMANIA), a następnie `## Hand-off`, `## Pre-scaffold verification`, `## Scaffold log`, `## Post-scaffold audit`, `## Hints recorded but not acted on`, `## Next steps`. Sekcja `Hints recorded but not acted on` pobiera wszystkie wskazówki z flag `handoff-consumer.md` przekazania jako "wyświetla, ale nie działa w v1".
4. Zapisz plik. Jeśli zapis się nie powiedzie (błąd systemu plików, brak uprawnień), wróć do drukowania całej treści na czacie zgodnie z blokiem failure-mode schematu.
5. Wydrukuj podsumowanie końcowe w rozmowie:

   ```
   Utworzono szablon <starter_id> w bieżącym katalogu. Dziennik weryfikacji: context/changes/bootstrap-verification/verification.md.

   Przed utworzeniem szablonu: <jednowierszowe podsumowanie aktualności>.
   Szablon:    <jednowierszowe podsumowanie szablonu>.
   Audyt:       <jednowierszowe podsumowanie audytu>.

   Następnie: przyszła umiejętność skonfiguruje kontekst agenta (CLAUDE.md, AGENTS.md). Na razie Twój projekt jest utworzony i zweryfikowany — miłego kodowania.
   ```

6. Zatrzymaj. Nie ustawiaj schowka do ponownej próby w przypadku udanego uruchomienia; łańcuch jest kompletny dla v1.

W przypadku częściowego dziennika TWARDEGO ZATRZYMANIA (awaria CLI w Kroku 2), Krok 4 nadal działa, ale ze skróconą formą treści w schemacie (sekcja `Audit not run`, `phase_3_status: failed`). Schowek jest ustawiony na `/10x-bootstrapper` do ponownej próby przez ścieżkę awarii Kroku 2, a nie przez ten krok.

## Wynik

Co umiejętność produkuje zewnętrznie:

- **Pliki projektu z szablonu w cwd** — zapisane przez CLI startera, z rodzeństwem `.scaffold` tam, gdzie polityka konfliktów wykryła kolizję. `context/` w cwd jest zachowywany dosłownie.
- **`context/changes/bootstrap-verification/verification.md`** — ścieżka audytu uruchomienia. Schemat w `references/verification-log-schema.md`. Jeden plik na uruchomienie; ponowne uruchomienia nadpisują (z strażnikiem OSTRZEŻ-I-POTWIERDŹ).
- **Podsumowania rozmów na każdym kroku** — Krok 0 echo potwierdzenia lub poprawienia, Krok 1 podsumowanie aktualności, Krok 2 podsumowanie szablonu (z notatkami o rodzeństwie `.scaffold` i obsłudze `.gitignore`), Krok 3 podsumowanie audytu, Krok 4 podsumowanie końcowe ze wskaźnikiem następnych kroków.
- **Wskaźnik schowka tylko w przypadku ścieżek awarii** — `/10x-tech-stack-selector` dla odmów braku przekazania i dryfu rejestru, `/10x-bootstrapper` dla ponownej próby TWARDEGO ZATRZYMANIA w przypadku awarii CLI w Kroku 2. Brak ustawienia schowka w przypadku udanego uruchomienia.

Czego umiejętność NIE produkuje w v1:

- **`AGENTS.md` / `CLAUDE.md`** — odłożone na przyszłą umiejętność M1L4 ("Architektura pamięci").
- **Pliki przepływu pracy CI** (`.github/workflows/ci.yml` itp.) — odłożone na tę samą przyszłą umiejętność.
- **`git init`** ani żadnej historii git — bootstrapper zakłada, że użytkownik zarządza własnym repozytorium. Strategia `git-clone` wyraźnie usuwa sklonowany `.git/` przed przeniesieniem, aby historia startera nadrzędnego nie wyciekła.
- **Automatyczne naprawianie / automatyczne łatanie wyników audytu** — bootstrapper informuje; użytkownik decyduje.

## Odniesienia

- `references/handoff-consumer.md` — które klucze frontmatter przekazania bootstrapper konsumuje, wyświetla lub ignoruje.
- `references/refusal-protocol.md` — warunki odmowy, kopia i ciągi schowka.
- `references/bootstrapper-config.yaml` — nadpisania `cwd_strategy` dla każdego startera + mapa `language_family → audit_command`.
- `references/pre-scaffold-verification.md` — lekkie sprawdzenie aktualności.
- `references/scaffold-merge.md` — mechanika `.bootstrap-scaffold/`, trzy strategie cwd, macierz konfliktów.
- `references/post-scaffold-verification.md` — wysyłanie audytu dla każdego języka + klasyfikacja ważności.
- `references/verification-log-schema.md` — kształt `context/changes/bootstrap-verification/verification.md`.

## Krytyczne zabezpieczenia

1. **Przekazanie jest warunkiem wstępnym, a nie awaryjnym rozwiązaniem.** Brak wbudowanego mini-przekazania, brak czytania historii rozmów w poszukiwaniu zastępczych pól. Plik na dysku jest umową.

2. **Bootstrapper konsumuje rejestr; nie jest jego właścicielem.** Kanoniczny rejestr starterów znajduje się w `/10x-tech-stack-selector`. Dryf między `starter_id` odwoływanymi przez bootstrapper a rejestrem jest awarią CI (`scripts/validate-starter-registry-sync.mjs`).

3. **`context/` jest zawsze zachowywany.** Polityka konfliktów jest ścisła: nic pod `context/` w cwd nigdy nie jest nadpisywane przez szablon. Zobacz `references/scaffold-merge.md` dla pełnej macierzy konfliktów (Faza 3).

4. **Awaria CLI to TWARDE ZATRZYMANIE.** Niezerowy kod wyjścia w Kroku 2 zatrzymuje umiejętność, pozostawia `.bootstrap-scaffold/` na miejscu do inspekcji i zapisuje częściowy dziennik weryfikacji. Wszystkie inne fazy używają OSTRZEŻ-I-KONTYNUUJ — wyniki weryfikacji mają charakter edukacyjny, a nie blokujący.

5. **v1 nie generuje `AGENTS.md` / `CLAUDE.md`.** Ta praca zostaje przeniesiona do przyszłej umiejętności M1L4 ("Architektura pamięci"). v1 wyświetla wartości wskazówek, takie jak `bootstrapper_confidence: best-effort` i `quality_override: true` w podsumowaniu rozmowy, ale nie podejmuje żadnych działań kompensacyjnych.

6. **Wewnętrzne etykiety umiejętności pozostają wewnętrzne.** Mówiąc do użytkownika, nigdy nie odwołuj się do numerów kroków (`Krok 0`, `Krok 2`), dosłownych nazw strategii (`subdir-then-move`, `native-cwd`, `git-clone`) bez kontekstu, ani wewnętrznych ścieżek pól (`hints.deployment_target`). Tłumacz na język naturalny: "krok tworzenia szablonu", "Twój cel wdrożenia", "jak CLI tworzy szablon w Twoim bieżącym katalogu", "przez klonowanie repozytorium startera".