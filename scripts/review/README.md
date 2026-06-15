# Proofreading cockpit

Side-by-side review tool: the annual-report **PDF on the left**, the **extracted records
on the right**. Click a record's `📄 p.N` button to jump the PDF to that page, then mark
the record **✓ correct / ✗ false / ? unsure**, add a note, and optionally type a
**suggested correction** per field. Everything is saved automatically and tracked.

**Suggested corrections never touch the source.** Each field row has a "suggested
correction" input; what you type is stored only in `reviews/<stem>.json` (under the
record's `edits`), leaving the canonical `extracted/` JSON untouched. A `✎ N` badge on a
card shows how many fields have a proposed value. Applying these back to `extracted/` (if
ever wanted) is a deliberate, separate step — the cockpit only records the suggestion.

## Installation

Requires **Python 3.9+**. The only third-party dependency is Flask.

```bash
# from the repo root
python -m venv .venv
# Windows (PowerShell):
.venv\Scripts\Activate.ps1
# macOS/Linux:
# source .venv/bin/activate

pip install flask
```

The tool reads data straight from the repo, so make sure these exist locally:

- `extracted/<SYM>.SI_FY<YYYY>/` — the extractions to review
- `annual_reports/*.pdf` — the matching source PDFs

There is **no build step** — the app reads the JSON and PDFs at request time.

## Run

```bash
python scripts/review/app.py
```

Open **http://127.0.0.1:5057** in **Chrome or Edge** (the page-jump uses the native PDF
viewer's `#page=` parameter).

> The bundled server (`app.run`, host `127.0.0.1`) is for **local single-user** review.
> Sharing it with colleagues over a network/internet needs a production server, auth,
> HTTPS, and per-reviewer verdict storage — not yet wired up here.

## How it works

- Reads the canonical extractions from `extracted/<SYM>.SI_FY<YYYY>/` (all 8 files,
  flattened into one reviewable list per report) and the matching PDF from
  `annual_reports/`.
- Every record carries its `source_page` (the AR's printed page number). The page button
  navigates the PDF to `source_page + page_offset`.
- **Page offset**: printed page numbers usually differ from the physical PDF page (cover
  pages etc.). Click any page button once, see how far off it is, then set the **page
  offset** box (top bar) so jumps land exactly. The offset is saved per report.
- Verdicts and notes are written to `reviews/<SYM>.SI_FY<YYYY>.json` on every change —
  reload-safe, git-trackable. Re-running the server picks up where you left off.

## Reviews file format

```json
{
  "symbol": "C38U.SI", "financial_year": 2025, "page_offset": 2,
  "section_notes": {"properties": "valuations look one page off vs the audited statement"},
  "items": {
    "properties:3": {"verdict": "false", "note": "valuation should be 1,158.0m",
                     "edits": {"valuation": "1158.0", "valuation_currency": "SGD"},
                     "updated": "..."},
    "top_tenants:0": {"verdict": "correct", "updated": "..."}
  },
  "updated": "..."
}
```

Item id = `<section>:<index>` (e.g. `properties:3`, `profile:0`).

## UI notes

- **Section note** (under each section header): a free-text note that applies to the whole
  section (range of records), saved to `section_notes` in the review file — separate from
  per-item notes. Use it for "all valuations are one page off", etc.
- **Suggested correction** column (per field): type a value to record what it *should* be;
  the input turns amber and the card shows a `✎` count. Clear the input to drop the
  suggestion. The original extracted value beside it is read-only and never changes.
- **Filter** (top right): `all` / `unreviewed` / `false` / `unsure` — to sweep back through
  only the items you flagged.
- **Progress bar** + per-report `reviewed/total` in the dropdown update live.
- The `_notes.json` for each report (reconciliation, quirks, declared nulls) is shown
  collapsed at the top of the right panel for context.

## Deploy to a VPS

CI is wired up in `.github/workflows/deploy-review.yml`: on every push to `main` that
touches `scripts/review/**`, GitHub Actions SSHes into your VPS, pulls the code, and
restarts the service. **Only code is deployed** — the PDFs/extractions/reviews stay on the
VPS. Two one-time setup steps:

**1. On the VPS** — clone the repo, create the venv, and install a systemd service:

```bash
sudo mkdir -p /opt/s_reits && sudo chown $USER /opt/s_reits
git clone <your-repo-url> /opt/s_reits
cd /opt/s_reits
python3 -m venv .venv && .venv/bin/pip install flask waitress
# copy your data onto the box: annual_reports/, extracted/  (reviews/ is created on write)

sudo tee /etc/systemd/system/reit-review.service >/dev/null <<'EOF'
[Unit]
Description=REIT proofreading cockpit
After=network.target

[Service]
WorkingDirectory=/opt/s_reits
ExecStart=/opt/s_reits/.venv/bin/waitress-serve --host=127.0.0.1 --port=5057 scripts.review.app:app
Restart=always
User=YOUR_USER

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable --now reit-review
# allow the deploy user to restart it without a password prompt:
echo "YOUR_USER ALL=(root) NOPASSWD: /bin/systemctl restart reit-review, /bin/systemctl status reit-review" | sudo tee /etc/sudoers.d/reit-review
```

The app binds to `127.0.0.1` only — it is **not** reachable from the internet directly.
Caddy (below) terminates HTTPS + auth and proxies to it.

**3. HTTPS + auth via Caddy** (the app has no login of its own):

```bash
# DNS: add an A record for your subdomain -> the VPS IP, e.g.
#   review.yourdomain.com  A  43.157.212.145

# install Caddy (official apt repo)
sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https curl
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list
sudo apt update && sudo apt install -y caddy

# create a password hash for each reviewer
caddy hash-password --plaintext 'a-strong-password'

# edit scripts/review/deploy/Caddyfile (set your subdomain, email, paste the hash),
# then install it and reload
sudo cp scripts/review/deploy/Caddyfile /etc/caddy/Caddyfile
sudo systemctl reload caddy

# firewall: allow ssh + web
sudo ufw allow 22 && sudo ufw allow 80 && sudo ufw allow 443 && sudo ufw enable
```

Caddy auto-issues a Let's Encrypt cert for the subdomain on first request. Visit
`https://review.yourdomain.com` — you'll get a login prompt, then the cockpit.

### Managing who can log in

Logins are the lines in the Caddyfile's `basic_auth` block — one per person. Caddy is the
only gate; the app has no user list. All logged-in users share the same access (no roles),
and edits are **not** tagged by author (one shared review file).

```bash
# add / change a user: hash their password, then add or edit their line
caddy hash-password --plaintext 'their-password'      # -> $2a$14$...
sudo nano /etc/caddy/Caddyfile                         # add:  bob  $2a$14$...
sudo systemctl reload caddy                            # apply, no downtime

# remove a user: delete their line, then reload
sudo nano /etc/caddy/Caddyfile
sudo systemctl reload caddy
```

**2. SSH key for CI** (the VPS gives you a password, but CI must use a key). On your laptop:

```bash
ssh-keygen -t ed25519 -f deploy_key -N ''        # creates deploy_key (private) + deploy_key.pub
ssh-copy-id -i deploy_key.pub ubuntu@43.157.212.145   # or paste deploy_key.pub into ~/.ssh/authorized_keys
```

**3. In GitHub** (Settings → Secrets and variables → Actions) add the secrets the workflow
reads:
- `VPS_HOST` = `43.157.212.145`
- `VPS_USER` = `ubuntu`
- `VPS_SSH_KEY` = the **full contents of `deploy_key`** (the private key)
- `VPS_APP_DIR` = `/opt/s_reits`
- `VPS_PORT` = `22` (optional)

Then push to `main` (or run the workflow manually from the **Actions** tab) to deploy.
The deploy user also needs the passwordless `systemctl restart` sudoers line shown above.
