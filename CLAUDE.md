# p2cx-website — Projektkontext

Öffentliche Website **p2cx.de** — statische HTML-Seiten, mehrsprachig (DE/EN/DK).
Repo: `p2cx/p2cx-website` (früher `p2cx-landing` — alter Name leitet per GitHub-Redirect weiter).

## Deployment (WICHTIG)
- **Dev zuerst:** Push auf `dev` mit Änderungen unter `p2cx/**` → Workflow „Deploy to Dev"
  (`.github/workflows/deploy-dev.yml`) rsync't (**mit** `--delete`) auf den Dev-Server
  `root@85.215.254.100:/var/www/p2cx-website-dev/p2cx/` → **https://dev.p2cx.de**
  (nginx-Vhost `p2cx-website-dev`, `X-Robots-Tag: noindex`). Prod-Weg: PR/Merge `dev` → `main`.
- **Auto-Deploy via GitHub Actions:** Push auf `main` mit Änderungen unter `p2cx/**` → Workflow
  „Deploy to IONOS" (`.github/workflows/deploy.yml`) rsync't `p2cx/` auf den IONOS-Server.
- Ziel: `root@87.106.190.113:/var/www/p2cx-landing/p2cx/` — **Server-Pfad heißt weiterhin
  `p2cx-landing`** (bewusst nicht umbenannt, sonst müsste die nginx-Config angefasst werden).
- rsync läuft **ohne `--delete`** (nicht-destruktiv: Server-Dateien, die nicht im Repo liegen,
  z. B. separat hochgeladene Seiten, bleiben erhalten).
- Secret: `IONOS_SSH_KEY` (im Repo hinterlegt). Manueller Fallback: `./deploy.sh <datei>` (scp).
- **Deploy-Check-Falle:** Nach `git push` NICHT sofort `gh run list` (der neue Run ist evtl. noch
  nicht registriert → man erwischt den vorherigen und denkt „fertig"). Per Commit-SHA matchen:
  `RUN=$(gh run list -R p2cx/p2cx-website --workflow="Deploy to IONOS" --limit 5 --json databaseId,headSha -q ".[] | select(.headSha|startswith(\"$SHA\")) | .databaseId")`
- Live prüfen: `curl -s -o /dev/null -w '%{http_code}' https://p2cx.de/...` (Cache-Buster `?nc=$(date +%s)`)
- Details zu Hosting/nginx/SSH: siehe `HOSTING-NOTES.md`.

## Struktur
- `p2cx/de|en|dk/` — Sprachversionen (index, plattform, impressum, datenschutz, agb/, avv/)
- `p2cx/de/products/` — **Produktkatalog**: Übersicht + Detailseite je Produkt; in en/dk gespiegelt
- `p2cx/css/p2cx.css`, `p2cx/logo/` — Design-System (Bootstrap 5.3.3 + p2cx.css, Akzent Gold `#c9a44c`)
- nginx mappt `p2cx.de/` → `/var/www/p2cx-landing/p2cx/` → absolute Pfade (`/css`, `/logo`, `/de/...`) funktionieren

## Konventionen
- **Deutsche Texte: immer korrekte Umlaute & ß** (kein ae/oe/ue/ss).
- **Produktkatalog `/products`:** deep-link only (NICHT in der Hauptnav), nur dezenter Footer-Link auf
  den Startseiten. Karten **ganz klickbar** (Bootstrap `stretched-link` + `position:relative`),
  klickbare zeigen goldenes „Details →" (CSS `:has()`). Ehrliche Status-Badges:
  Live / MVP / Konzept / intern·auf Anfrage.
- **Sprachumschalter (Flaggen):** springt immer zur GLEICHEN Seite in der anderen Sprache,
  nie zur index. `aria-current` auf der aktiven Sprache.
- **Tonalität:** Leitmotiv „gehärteter Kern + Individualisierung" — siehe `../kernbotschaften.md`
  und die globale Corporate Language (`~/.claude/CLAUDE.md`).

## Recht
- **AGB** (`p2cx/de/agb/`): produkt-unabhängig — §2.2 verweist nur auf den Katalog (keine Produktliste),
  §2.3 erlaubt formloses Hinzubuchen weiterer Produkte ohne neuen Vertragsschluss.
- **AVV** (`p2cx/de/avv/`): Subprozessoren inkl. **Mammouth** mit Hinweis „wird durch Langdock ersetzt".
  Mammouth bleibt drin, bis Dealflow / EU-Radar / Steuerportal auf Langdock migriert sind
  (Issue `p2cx/myp2cx#81`). Erst danach Mammouth streichen.
- **Anwalts-Briefing:** `LEGAL-REVIEW.md` (offene Prüfung → Issue `p2cx/p2cx-website#2`).
