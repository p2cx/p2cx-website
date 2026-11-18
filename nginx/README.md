# nginx-Vorschlag: Security-Header für p2cx.de und www.p2cx.de

Board #1817 · Befund B-5 aus `compliance/isms/pruefprotokolle/netzwerk-2026-11.md` (ISO 27001 A.8.21)

**Stand 18.11.2026 nur Vorschlag.** Die nginx-Config liegt auf Prod (`/etc/nginx/sites-enabled/p2cx*`)
und nicht in diesem Repo. Einbauen nur mit Haukes OK (Prod-Schutz), nie die Site überschreiben
(certbot-Blöcke), nur die Zeilen unten ergänzen.

## Gemessen vorher

`curl -sI https://p2cx.de/` und `https://www.p2cx.de/` (301 auf p2cx.de): kein HSTS, keine CSP,
kein X-Frame-Options, kein X-Content-Type-Options, keine Referrer-Policy.

## Was die Seite braucht (aus dem Repo gelesen)

| Bereich | Fremdquellen | Folge für die CSP |
|---|---|---|
| `p2cx/` (Website) | keine; Bootstrap und Fonts lokal, Formulare an `/api/kontakt` | `'self'` reicht, aber 14 Inline-`<script>` und `onsubmit=` → `'unsafe-inline'` |
| `sl/` (Social-Listening-Landingpages) | Power-BI-Iframes `app.powerbi.com`, Icons von `api.iconify.design` | eigene CSP im `location /sl/` |
| `p2cxApps/`, `media/` | keine | Standard-CSP |

## Einbau

1. `security-headers.conf` aus diesem Ordner nach `/etc/nginx/snippets/p2cx-security-headers.conf`.
2. Im HTTPS-`server`-Block von **p2cx.de**:

   ```nginx
   include snippets/p2cx-security-headers.conf;
   add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self' data:; connect-src 'self'; frame-ancestors 'self'; object-src 'none'; base-uri 'self'; form-action 'self'" always;
   ```

3. Im `location /sl/` (eigene CSP, deshalb das Snippet dort noch einmal):

   ```nginx
   include snippets/p2cx-security-headers.conf;
   add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https://api.iconify.design; font-src 'self' data:; connect-src 'self'; frame-src https://app.powerbi.com; frame-ancestors 'self'; object-src 'none'; base-uri 'self'; form-action 'self'" always;
   ```

4. Jeder weitere `location`-Block mit eigenem `add_header` (etwa Cache-Header, `/api/kontakt`)
   bekommt `include snippets/p2cx-security-headers.conf;` und die Standard-CSP aus Schritt 2.
   Sonst fallen dort alle Header weg (nginx vererbt `add_header` dann nicht).
5. Im HTTPS-`server`-Block von **www.p2cx.de** (nur Redirect): `include snippets/p2cx-security-headers.conf;`
6. `nginx -t && systemctl reload nginx`

## Prüfen

```bash
for u in https://p2cx.de/ https://www.p2cx.de/ https://p2cx.de/de/ https://p2cx.de/sl/; do
  echo "== $u"; curl -sI "$u" | grep -iE "strict-transport|content-security|x-frame|x-content-type|referrer|permissions"
done
```

Danach eine Seite mit Kontaktformular und eine `/sl/`-Seite im Browser öffnen: Formular absenden,
Power-BI-Bericht lädt, keine CSP-Fehler in der Konsole.

## Bewusst nicht

- `includeSubDomains` steht im HSTS, wie im Playbook. Alle `*.p2cx.de`, die aufgerufen werden,
  laufen über HTTPS; eine Subdomain nur mit HTTP wäre danach ein Jahr lang nicht erreichbar.
- Kein `preload`, das ist ein eigener, schwer rückholbarer Schritt.
