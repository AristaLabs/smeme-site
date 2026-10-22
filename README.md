# SMEme public site

Static marketing site and public documentation for `smeme.ai`.

The hosted application lives at `app.smeme.ai`. This repository has no
database, authentication runtime, or Core image dependency. Render builds the
Jinja templates in `src/templates/` into `public/`.

## Local build

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python build.py
python -m http.server 8000 --directory public
```

The build uses production URLs intentionally:

- Site: `https://smeme.ai`
- App: `https://app.smeme.ai`
- MCP: `https://app.smeme.ai/api/v1/mcp`

The waitlist is a normal form post to the app. Account, dashboard, API, and
MCP links leave the static site for `app.smeme.ai`.

For the procedure for changing public copy, routes, generated crawler files,
and publishing, see [docs/website-copy.md](docs/website-copy.md).
