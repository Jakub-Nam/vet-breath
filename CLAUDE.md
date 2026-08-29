# VetBreath — reguły projektu

Kanoniczne reguły i onboarding są w @AGENTS.md (per-pakiet: `backend/CLAUDE.md`, `frontend/AGENTS.md`).

Poniższy blok to auto-zarządzana dokumentacja toolkitu 10x — nie są to reguły projektu.

<!-- BEGIN @przeprogramowani/10x-cli -->

## 10xDevs AI Toolkit — Moduł 1, Lekcja 5

Wybierz platformę wdrożeniową i wdróż do produkcji za pomocą **łańcucha infrastruktury**:

```
(/10x-init  →  /10x-shape  →  /10x-prd  →  /10x-tech-stack-selector  →  /10x-bootstrapper  →  /10x-agents-md  →  /10x-rule-review  →  /10x-lesson)  →  /10x-infra-research  →  Plan Mode deploy
```

Pełny łańcuch Modułu 1 obejmuje Lekcje 1–4 (ponownie włączone, aby można było naprawić wcześniejsze kontrakty w trakcie lotu). `/10x-infra-research` to główny temat lekcji; sam krok wdrożenia wykorzystuje wbudowany w hosta **Plan Mode**, a nie dedykowaną umiejętność — artefakt (`context/deployment/deploy-plan.md`) jest tym, co jest przekazywane dalej.

### Router zadań — Od czego zacząć

| Umiejętność | Kiedy jej używać |
| --- | --- |
| **Infrastruktura (główny temat lekcji)** | |
| `/10x-infra-research [path-to-tech-stack-or-prd]` | Masz `context/foundation/tech-stack.md` (i idealnie `prd.md`) i musisz wybrać platformę wdrożeniową MVP. Umiejętność ładuje stos jako twarde ograniczenie, przeprowadza 5-pytaniowy wywiad z deweloperem (trwałe połączenia, wrażliwość na koszty, istniejąca znajomość, globalny zasięg, preferencje kolokacji), uruchamia równoległe badania subagentów na sześciu platformach kandydujących, ocenia je Pass/Partial/Fail według pięciu kryteriów przyjaznych agentom z `references/agent-friendly-criteria.md`, tworzy krótką listę trzech najlepszych i przeprowadza trójwymiarową kontrolę anty-uprzedzeniową lidera (adwokat diabła, pre-mortem, nieznane niewiadome) przed zapisaniem `context/foundation/infrastructure.md`. Użyj PO `/10x-tech-stack-selector`, PRZED `/10x-implement`. |
| **Wdrożenie (wbudowane w hosta, nie umiejętność)** | |
| Plan Mode deploy | Masz `infrastructure.md` + `tech-stack.md` i chcesz, aby plan tylko do odczytu został przejrzany przed wprowadzeniem jakichkolwiek zmian na platformie. Aktywuj tryb planowania hosta (Claude Code: `Shift+Tab` przełącza domyślny → auto-akceptacja → plan; IDE: dedykowany przycisk) z komunikatem "Wykonajmy pierwsze wdrożenie w oparciu o `@infrastructure.md`, zgodnie ze stackiem z `@tech-stack.md`". Przeczytaj plan, zażądaj poprawek, zatwierdź, a następnie pozwól agentowi wykonać. Zatwierdzony plan pozostaje w `context/deployment/deploy-plan.md`, dzięki czemu planowanie kamieni milowych w następnej lekcji może odwoływać się do tego, co zostało już wdrożone i jakie sekrety są już podłączone. |
| **Ponowne uruchomienie upstream w razie potrzeby** | |
| `/10x-init` / `/10x-shape` / `/10x-prd` / `/10x-tech-stack-selector` / `/10x-bootstrapper` / `/10x-agents-md` / `/10x-rule-review` / `/10x-lesson` / `/10x-stack-assess` / `/10x-health-check` | Zestawione, aby można było załatać wcześniejsze kontrakty w trakcie lotu. Jeśli kontrola anty-uprzedzeniowa wymusi zmianę platformy, która wpływa na decyzję dotyczącą stosu (np. "ta baza danych nie pasuje do żadnej platformy, którą byśmy zaakceptowali"), uruchom ponownie `/10x-tech-stack-selector`, aby utrzymać zgodność `tech-stack.md` i `infrastructure.md`. |

### Jak łańcuch przekazuje dane

- `/10x-infra-research` odczytuje `context/foundation/tech-stack.md` (język, framework, środowisko uruchomieniowe, baza danych) jako **twarde ograniczenia** — platformy, które nie mogą uruchomić stosu, są odrzucane przed oceną. Odczytuje również `context/foundation/prd.md` (skala, opóźnienia, oczekiwania dotyczące czasu pracy) jako **miękkie wagi** podczas oceny. Oba wejścia są opcjonalne, ale zdecydowanie zalecane; bez nich umiejętność działa, ale ostrzega.
- Umiejętność zapisuje `context/foundation/infrastructure.md` jako trzeci kontrakt podstawowy: frontmatter (`project`, `researched_at`, `recommended_platform`, `runner_up`, `context_type`, `tech_stack`) plus treść obejmującą rekomendację, pełne porównanie platform z macierzą punktacji, wyniki anty-uprzedzeniowe, historię operacyjną (podgląd / sekrety / wycofywanie / zatwierdzanie / logi) oraz rejestr ryzyka, wiążący każdy wpis z soczewką, która go ujawniła. W przypadku kolizji umiejętność pyta: nadpisać, zapisać jako `infrastructure-v2.md` lub przerwać.
- Plan Mode odczytuje `infrastructure.md` i `tech-stack.md` razem. Agent emituje plan krok po kroku, obejmujący zautomatyzowane kroki, które wykonuje, ręczne bramki konfiguracji (tworzenie konta, konfiguracja sekretów), dokładne polecenia wdrożenia (polecenia Pages vs Workers NIE są zamienne na Cloudflare — plan musi to określać) oraz kroki weryfikacji. Plan jest odrzucany/edytowany, dopóki nie będzie poprawny; dopiero wtedy Plan Mode kończy działanie i rozpoczyna się wykonanie. Zatwierdzony plan trafia do `context/deployment/deploy-plan.md` i jest wykorzystywany przez umiejętności planowania kamieni milowych jako źródło prawdy o tym, "co zostało już wdrożone".

### Co umiejętności lekcji obejmują (a czego NIE)

- **`/10x-infra-research` obejmuje**: krótką listę platform ocenionych według pięciu kryteriów przyjaznych agentom (jakość CLI, stopień zarządzania/serverless, dokumentacja czytelna dla agenta, stabilne/skryptowalne API wdrożeniowe, MCP lub integracja agenta pierwszej klasy), trzy wyniki anty-uprzedzeniowe dotyczące lidera (numerowane słabości, 150–200-słowowa narracja o awarii, 3–5 nieznanych niewiadomych), historię operacyjną z jedną konkretną odpowiedzią na każdą oś (nie kategorie) oraz rejestr ryzyka, w którym każdy wiersz nazywa swoją soczewkę źródłową (`Devil's advocate` / `Pre-mortem` / `Unknown unknowns` / `Research finding`). Status każdej funkcji niebędącej w GA jest rejestrowany w tekście (`beta` / `preview` / `region-limited` / `deprecated`) z datą sprawdzenia statusu.
- **`/10x-infra-research` NIE** tworzy obrazów Docker ani nie pisze Dockerfile'ów, nie konfiguruje potoków CI/CD ani nie planuje poza zakresem MVP (HA w wielu regionach jest wyraźnie poza zakresem). NIE decyduje za Ciebie — użytkownik akceptuje, zamienia na drugiego w kolejności lub przerywa po kontroli krzyżowej, a ta decyzja jest rejestrowana w wynikach.
- **Plan Mode** obejmuje: wyraźną ludzką bramkę między "agent ma plan" a "agent zmienia produkcję". Artefakt (`deploy-plan.md`) jest ścieżką audytu dla "co miało się wydarzyć", gdy uruchomienie na żywo pójdzie nie tak. Plan Mode NIE zastępuje `/10x-infra-research` (decyzja o platformie musi być już podjęta — Plan Mode planuje wdrożenie, nie wybiera miejsca wdrożenia).

### Pięć kryteriów przyjaznych agentom (i dlaczego są one kluczowe)

Kryteria, które tworzą macierz punktacji `/10x-infra-research`, nie są ogólnymi osiami "dobrej platformy" — są to specyficzne cechy, które określają, czy agent może obsługiwać tę platformę z sesji bez Twojej pomocy:

1. **CLI-first** — każda rutynowa operacja ma udokumentowane polecenie; agent nie musi klikać w panelu.
2. **Managed / serverless** — mniej ruchomych części oznacza mniej sposobów, w jakie agent (lub Ty) może coś zepsuć, co platforma miała obsłużyć.
3. **Agent-readable docs** — dokumentacja w formacie markdown / `llms.txt` / hostowana na GitHubie, którą agent może pobrać i przeanalizować, a nie strony marketingowe renderowane w JS.
4. **Stable, scriptable deploy API** — przewidywalne kody wyjścia, ustrukturyzowane dane wyjściowe, brak interaktywnych monitów w trakcie wdrożenia.
5. **MCP server or first-class agent integration** — bonus, nie wymagane. Samo CLI wystarczy dla MVP; MCP sprawdza się, gdy agent wykonuje dziesiątki ustrukturyzowanych zapytań do stanu na żywo.

Twarde filtry stosuje się przed punktacją (wymóg trwałego połączenia odrzuca Netlify/Vercel tylko serverless; niezgodność środowiska uruchomieniowego stosu technologicznego całkowicie odrzuca platformę). Odpowiedzi na wywiad ponownie ważą kryteria później — wrażliwość na koszty karze drogie podstawowe poziomy, znajomość rozstrzyga remisy, preferencja globalnego zasięgu faworyzuje platformy edge-native, preferencja kolokacji faworyzuje zintegrowane bazy danych.

### Anty-uprzedzenia jako dyscyplina decyzyjna (nie teatr)

Każda rozmowa badawcza z LLM ma wbudowane skłonności do tego, co użytkownik już zasygnalizował. `/10x-infra-research` uruchamia trzy ustrukturyzowane soczewki przeciwko liderowi ZANIM plik zostanie zapisany, a nie po:

- **Devil's advocate** — *znajdź słabości, ukryte koszty i tryby awarii specyficzne dla wdrożenia `<tego stosu>` na `<tej platformie>`*. Wynikiem jest numerowana lista 3–5 konkretów, a nie kategorii.
- **Pre-mortem** — *sześć miesięcy później ta decyzja okazała się kompletną katastrofą; przeanalizuj założenia i niedoszacowane ryzyka, które do tego doprowadziły*. Wynikiem jest narracja o długości 150–200 słów; narracje ujawniają konkretne kształty awarii, które abstrakcyjne listy ryzyka ukrywają.
- **Unknown unknowns** — *co jest prawdą o tej kombinacji, czego strona marketingowa i dokumentacja nie ujawniają w oczywisty sposób?* Wynikiem jest 3–5 nieoczywistych ryzyk.

Po kontroli krzyżowej użytkownik ma trzy realne opcje: **kontynuować z liderem i włączyć ryzyka do rejestru**, **zamienić na drugiego w kolejności** (i ponownie uruchomić kontrolę krzyżową na nowym liderze) lub **zamienić na trzecie miejsce**. Trzecia opcja jest rzadka; jeśli nigdy nie występuje w wielu uruchomieniach, kontrola krzyżowa zdegradowała się do rytuału i powinna zostać przepisana.

Dwie dodatkowe techniki (nie wymagające umiejętności, surowe podpowiedzi) należą do tego samego zestawu narzędzi: zmuszanie modelu do porównania trzech alternatyw w tabeli markdown (struktura jest lepsza niż "ta sama odpowiedź innymi słowami) oraz rotacja ról (ta sama decyzja oczami programisty frontendowego, osoby odpowiedzialnej za bezpieczeństwo i właściciela kosztów — ujawnienie kosztów, które ponosi każda rola, i zaproponowanie alternatyw, jeśli którakolwiek z nich się wzdrygnie).

### CLI vs MCP dla operacyjności infrastruktury na żywo

Po wdrożeniu agent potrzebuje sposobu na komunikację z działającą platformą. Dwie ścieżki, uzupełniające się, a nie konkurujące:

- **CLI** (`wrangler`, `flyctl`, `vercel`, `gh`) — jawne i audytowalne, dane wyjściowe pozostają w terminalu, bezpieczniejsze domyślne ustawienia dla nieodwracalnych działań (np. `netlify deploy` jest domyślnie szkicem; należy przekazać `--prod`). Najlepsze dla MVP: minimalna konfiguracja, niski koszt kontekstu (brak wstępnie załadowanych schematów narzędzi), a agent musi znać polecenie (w czym pomaga umiejętność dla każdego narzędzia).
- **MCP** — dedykowany serwer udostępniający ustrukturyzowane narzędzia ze schematami (`pages_deployments_list` itp.). Każdy podłączony serwer MCP dodaje definicje narzędzi do okna kontekstu, więc koszt rośnie wraz z liczbą serwerów. Sprawdza się, gdy agent wykonuje wiele zapytań typu discovery do stanu na żywo (logi, różnice w wdrożeniach), a ustrukturyzowany JSON jest lepszy niż parsowanie danych wyjściowych CLI.

Rozsądne domyślne ustawienie: zacznij od CLI, dodaj MCP, gdy zauważysz powtarzający się wzorzec przechodzenia przez `--help`, który agent musi wykonać, aby odpowiedzieć na klasę pytań. Własne ramy Anthropic [building-agents-that-reach-production](https://claude.com/blog/building-agents-that-reach-production-systems-with-mcp) mówią, że "API, CLI i MCP to trzy uzupełniające się ścieżki" — wybieraj według zadania, a nie według szumu.

### Granica dostępu produkcyjnego (minimalne uprawnienia, człowiek przy nieodwracalnych operacjach)

Zarówno CLI, jak i MCP mogą zapewnić agentowi bezpośredni dostęp do produkcji. Lekcja ustala domyślną postawę:

- **Tokeny są ograniczone, a nie klucze główne.** Na Cloudflare: token API ograniczony do Pages lub Workers dla jednego projektu, bez DNS, bez Workers Secrets dla niepowiązanych projektów, bez rozliczeń. Odpowiednik AWS / GCP: ograniczona rola IAM z `console-only-user` lub tylko do odczytu na produkcji, pełny dostęp na środowisku staging.
- **Tokeny znajdują się w zmiennych środowiskowych, a nie w `.mcp.json` zatwierdzonym w repozytorium.** Agent pobiera je za pośrednictwem serwera MCP lub wykrywania środowiska CLI, a nie w postaci jawnego tekstu w rozmowie.
- **Destrukcyjne działania są tylko dla ludzi.** Usunięcie bazy danych, rotacja głównego sekretu, usunięcie projektu — to operacje wykonywane ręcznie w panelu, nawet jeśli agent je sugeruje. Ręczne kliknięcie kosztuje 30 sekund; sprzątanie po zautomatyzowanym błędzie kosztuje godziny.

To jest postawa MVP. W miarę dojrzewania projektu naturalną ewolucją jest pełny dostęp agenta do środowiska staging, a produkcja staje się tylko do odczytu — omówione w późniejszych modułach.

### Ścieżki podstawowe używane w tej lekcji

- `context/foundation/tech-stack.md` — wejście (przekazanie z Lekcji 2, twarde ograniczenia)
- `context/foundation/prd.md` — wejście (przekazanie z Lekcji 1, miękkie wagi)
- `context/foundation/infrastructure.md` — wyjście (trzeci kontrakt podstawowy)
- `context/deployment/deploy-plan.md` — wyjście z Plan Mode deploy (ścieżka audytu "co miało się wydarzyć")
- `context/foundation/lessons.md` — powtarzające się zasady i pułapki (użyj `/10x-lesson` z Lekcji 4, jeśli zauważysz klasę błędów agenta podczas badań lub wdrożenia)
- `docs/reference/contract-surfaces.md` — rejestr kluczowych nazw

### Uniwersalny język

Dostarczona umiejętność nie zawiera odniesień do 10xDevs / kohorty / certyfikacji. Lista platform kandydujących (Cloudflare, Vercel, Netlify, Fly.io, Railway, Render) jest początkową soczewką badawczą, a nie zestawem rekomendacji — kluczowe są potok punktacji + wywiad + kontrola krzyżowa, a platformę nieobecną na domyślnej liście można dodać, rozszerzając krok badawczy. Pięć kryteriów przyjaznych agentom to prawdziwy rdzeń artefaktu; `/10x-infra-research` ponownie odczytuje je z `references/agent-friendly-criteria.md`, aby ewoluowały wraz z platformami.

Umiejętności nie mogą zapisywać do `context/archive/`. Zarchiwizowane zmiany są niezmienne; jeśli rozwiązana ścieżka docelowa zaczyna się od `context/archive/`, przerwij z komunikatem: "This change is archived. Open a new change with `/10x-new` instead."

<!-- END @przeprogramowani/10x-cli -->
