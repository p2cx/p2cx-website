# Hosting & Deployment — p2cx.de Website

## Wichtig: Die Domain p2cx.de liegt auf dem IONOS-Server, NICHT auf Strato!

### IONOS Server (87.106.190.113)
- nginx Web-Root: `/var/www/p2cx-landing/p2cx/`
- URL-Mapping: `p2cx.de/de/...` → `/var/www/p2cx-landing/p2cx/de/...`
- SSH-Zugang: `root@87.106.190.113` mit Key aus `C:\Users\Hauke Loyos\Documents\.ssh\id_ed25519`
- SSL: Let's Encrypt (managed by Certbot)
- nginx-Config: `/etc/nginx/sites-enabled/p2cx*`

### nginx Location-Blöcke
- `/` → `/var/www/p2cx-landing/p2cx/` (statische HTML-Dateien)
- `/media/` → `/var/www/p2cx-landing/media/`
- `/sl/` → `/var/www/p2cx-landing/sl/` (Social Listening Landingpages)
- `/apps/` → `/var/www/p2cx-landing/p2cxApps/`
- Security-Header: Vorschlag in `nginx/` (Board #1817), Stand 18.11.2026 noch nicht auf Prod

### Deployment
- **Primär: GitHub Actions** — Push auf `main` (Änderungen unter `p2cx/**`) → Workflow „Deploy to IONOS"
  rsync't automatisch nach `/var/www/p2cx-landing/p2cx/` (ohne `--delete`, nicht-destruktiv).
  Secret: `IONOS_SSH_KEY`. Details + Deploy-Check-Falle siehe `CLAUDE.md`.
- **Manueller Fallback (SCP):**
```bash
scp -i "C:/Users/Hauke Loyos/Documents/.ssh/id_ed25519" DATEI root@87.106.190.113:/var/www/p2cx-landing/p2cx/de/DATEI
```

### Strato SFTP (ssh.strato.de)
- User: `ftp_admin@loyos.de` / Passwort in `.env.local`
- Enthält eine Kopie der Website-Dateien, wird aber NICHT von der Domain genutzt
- Vermutlich altes Hosting / Backup — nicht für Live-Deployment verwenden!

### Vorhandene Seiten unter /de/
- index.html, impressum.html, datenschutz.html
- plattform.html, onepager.html
- 01-zielbild.html, 02-argumentation.html, 03-architektur.html, 04-enablement.html
- technische-anforderungen-vm.html (hochgeladen 2026-05-04)
