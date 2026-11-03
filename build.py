"""Build the hosted SMEme public site as plain static files."""

from __future__ import annotations

import json
import re
import shutil
from pathlib import Path
from types import SimpleNamespace

from jinja2 import Environment, FileSystemLoader, select_autoescape

ROOT = Path(__file__).parent
SOURCE = ROOT / "src"
TEMPLATES = SOURCE / "templates"
OUTPUT = ROOT / "public"

SITE_BASE = "https://smeme.ai"
APP_BASE = "https://app.smeme.ai"
MCP_ENDPOINT = f"{APP_BASE}/api/v1/mcp"
OAUTH_CLIENT_ID = "NRdsdBvrio0DW9yo"

PUBLIC_ROUTES = [
    ("/", "SMEme — Rational AI for the decisions that run your business", "Your name is on the conclusion. SMEme checks each matter against the procedure you authorized, so you can approve the decision knowing exactly why it holds. Approve your procedure once as a decision tree, and SMEme shows what it requires, which facts decided it, and what is still open, inside Claude, ChatGPT, and agent workflows."),
    ("/pricing", "Pricing", "SMEme hosted Free and Pro plans. Limits for decision trees and MCP tool calls."),
    ("/faq", "FAQ", "Answers about SMEme: what a decision tree is, what you approve, where your data stays, and what the free tier includes."),
    ("/mcp", "MCP", "Copy prompts to connect your chatbot to SMEme, then browse the public tool wire reference. Creator connector steps live in the MCP setup guide."),
    ("/marketplace/business", "Business tier", "SMEme Business (Coming Soon) will let experts share deployed decision trees with clients and colleagues. Join the waitlist — grantees get conclusions and reasoning chains; your decision logic stays on SMEme."),
    ("/docs", "Docs", "SMEme documentation: copy-paste quick start, then building decision trees, Deploy and Listed, MCP setup, and reports from evidence."),
    ("/docs/quick-start", "Quick start", "Connect SMEme to the chatbot you already use, choose and build a decision tree with copyable prompts, then Deploy, List, and try it."),
    ("/docs/run-a-tree", "Run a tree", "Run a deployed SMEme decision tree in a new chat. Your agent answers one question at a time from your files and apps, and SMEme returns a report with the outcome, the path, and the evidence."),
    ("/docs/ask-more", "Ask more", "After a SMEme run, ask which answers decided the outcome, what would change it, and what it would take to reach a different outcome. Every answer comes from the rules of the tree."),
    ("/docs/mcp", "Connect your agent (MCP)", "Add SMEme to your AI app over MCP: the endpoint URL, the OAuth Client ID, step-by-step setup for Claude and ChatGPT, and what to check after you sign in. For the public tool wire reference, see /mcp."),
    ("/docs/introduction", "Building decision trees", "Learn how to create and edit SMEme decision trees: question and conclusion nodes, edges, validation, and review before Deploy."),
    ("/docs/download-workflow", "Download your decision tree", "Export a SMEme decision tree as JSON from the dashboard or editor. A version 2 file can be imported as a new copy on your account."),
    ("/docs/import", "Upload decision tree", "Upload a .smeme.json file you downloaded, or one someone shared with you, by clicking Import copy on the dashboard."),
    ("/docs/plans", "Plans & usage", "SMEme Free and Pro plan limits for decision trees and MCP tool calls, plus how caps reset and what happens when you hit them."),
    ("/docs/creator-dashboard", "Deploy, list, & delete", "How to Deploy and Redeploy a SMEme decision tree, fix readiness checks, choose Listed or Hidden, read Live vs Stale, and delete a tree from the dashboard."),
    ("/docs/changelog", "Docs changelog", "Changelog for SMEme in-app documentation: public creator docs, metadata and discovery improvements, and release notes by docs version."),
    ("/legal", "Legal", "Legal and policy index."),
    ("/legal/principles", "Guiding principles", "How SMEme handles expertise and data."),
    ("/legal/security", "Security", "Security and data handling."),
    ("/legal/privacy", "Privacy policy", "How data is collected and retained."),
    ("/legal/terms", "Terms of service", "Terms governing SMEme."),
    ("/legal/subprocessors", "Subprocessors", "Third-party processors."),
]

DOCS = {
    "/docs": "index.html",
    "/docs/quick-start": "quick_start.html",
    "/docs/run-a-tree": "run_a_tree.html",
    "/docs/ask-more": "ask_more.html",
    "/docs/introduction": "introduction.html",
    "/docs/download-workflow": "download_workflow.html",
    "/docs/import": "import.html",
    "/docs/plans": "plans.html",
    "/docs/creator-dashboard": "creator_dashboard.html",
    "/docs/changelog": "changelog.html",
    "/docs/mcp": "mcp.html",
}

LANDING = {
    "/": "preview.html",
    "/pricing": "pricing.html",
    "/faq": "faq.html",
    "/mcp": "mcp.html",
    "/marketplace/business": "business.html",
}

LEGAL = {
    "/legal": "index.html",
    "/legal/principles": "principles.html",
    "/legal/security": "security.html",
    "/legal/privacy": "privacy.html",
    "/legal/terms": "terms.html",
    "/legal/subprocessors": "subprocessors.html",
}


def _output_path(route: str) -> Path:
    if route == "/":
        return OUTPUT / "index.html"
    return OUTPUT / route.strip("/") / "index.html"


def _context(route: str) -> dict[str, object]:
    request = SimpleNamespace(state=SimpleNamespace(csrf_token=""))
    return {
        "request": request,
        "user": None,
        "brand": {"dark_logo_src": "/static/smeme_logo_v15_dark.svg"},
        "site_base": SITE_BASE,
        "canonical_path": route,
        "active_page": "docs" if route.startswith("/docs") else route.strip("/"),
        "docs_section": route.removeprefix("/docs/") or "index",
        "docs_version": "static",
        "show_nav": True,
        "show_footer": True,
        "theme_pin_light": True,
        "mcp_enabled": True,
        "mcp_endpoint_url": MCP_ENDPOINT,
        "mcp_connector_url": MCP_ENDPOINT,
        "mcp_connector_url_differs": False,
        "mcp_oauth_client_id": OAUTH_CLIENT_ID,
        "creator_ui": {"ai_generation_enabled": False},
        "acme_example_disclaimer": "",
        "page_title": next((label for path, label, _ in PUBLIC_ROUTES if path == route), "SMEme"),
    }


def _rewrite_host_links(html: str) -> str:
    replacements = {
        'href="/auth/login"': f'href="{APP_BASE}/auth/login"',
        'href="/auth/register"': f'href="{APP_BASE}/auth/register"',
        'href="/auth/profile/dashboard"': f'href="{APP_BASE}/auth/profile/dashboard"',
        'href="/decision-trees/dashboard"': f'href="{APP_BASE}/decision-trees/dashboard"',
        'href="/docs/delete-account"': f'href="{APP_BASE}/docs/delete-account"',
        'action="/teams-waitlist"': f'action="{APP_BASE}/teams-waitlist"',
        'hx-post="/teams-waitlist"': f'action="{APP_BASE}/teams-waitlist" method="post"',
        'hx-target="#waitlist-form-panel"': "",
        'hx-swap="innerHTML"': "",
    }
    for old, new in replacements.items():
        html = html.replace(old, new)
    html = re.sub(
        r'(href|action)="(/(?:auth|decision-trees|billing|api|\.well-known)/[^"]*)"',
        lambda match: f'{match.group(1)}="{APP_BASE}{match.group(2)}"',
        html,
    )
    return html.replace("https://smeme.ai/api/v1/mcp", MCP_ENDPOINT)


def main() -> None:
    if OUTPUT.exists():
        shutil.rmtree(OUTPUT)
    OUTPUT.mkdir(parents=True)

    env = Environment(
        loader=FileSystemLoader(TEMPLATES),
        autoescape=select_autoescape(["html", "xml"]),
    )
    env.globals["url_for"] = lambda endpoint, **kwargs: "#"
    env.globals["brand"] = {"dark_logo_src": "/static/smeme_logo_v15_dark.svg"}

    for route, template_name in {**LANDING, **DOCS, **LEGAL}.items():
        template = env.get_template(
            f"landing/{template_name}"
            if route in LANDING
            else f"docs/{template_name}"
            if route in DOCS
            else f"legal/{template_name}"
        )
        rendered = _rewrite_host_links(template.render(**_context(route)))
        destination = _output_path(route)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(rendered, encoding="utf-8")

    static_destination = OUTPUT / "static"
    shutil.copytree(SOURCE / "static", static_destination)
    dataset = ROOT / "src" / "downloads" / "smeme-acme-dataset-distributed.zip"
    if dataset.exists():
        destination = OUTPUT / "downloads" / dataset.name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(dataset, destination)
    media = ROOT / "src" / "media"
    if media.is_dir():
        for asset in media.iterdir():
            if asset.suffix.lower() not in {".mp4", ".jpg", ".png", ".webp"}:
                continue
            destination = OUTPUT / "media" / asset.name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(asset, destination)

    routes = "\n".join(
        f"- [{label}]({SITE_BASE}{path}): {description}"
        for path, label, description in PUBLIC_ROUTES
    )
    (OUTPUT / "robots.txt").write_text(
        "User-agent: *\nAllow: /\n"
        "Disallow: /auth/\nDisallow: /decision-trees/\nDisallow: /billing\n"
        "Disallow: /api/\nDisallow: /.well-known/\n"
        f"Sitemap: {SITE_BASE}/sitemap.xml\n",
        encoding="utf-8",
    )
    sitemap = "".join(f"  <url><loc>{SITE_BASE}{path}</loc></url>\n" for path, _, _ in PUBLIC_ROUTES)
    (OUTPUT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{sitemap}</urlset>\n",
        encoding="utf-8",
    )
    intro = (
        "# SMEme\n\n"
        "> SMEme is the formal reasoning layer for AI — a symbolic solver that evaluates "
        "expert-authored decision trees over MCP and returns traceable conclusions.\n\n"
    )
    (OUTPUT / "llms.txt").write_text(f"{intro}## Pages\n\n{routes}\n", encoding="utf-8")
    (OUTPUT / "llms-full.txt").write_text(
        f"{intro}## Canonical public pages\n\n{routes}\n", encoding="utf-8"
    )
    (OUTPUT / "build-manifest.json").write_text(
        json.dumps({"site_base": SITE_BASE, "app_base": APP_BASE, "mcp_endpoint": MCP_ENDPOINT}, indent=2) + "\n",
        encoding="utf-8",
    )
    # Retired URLs. Kept out of PUBLIC_ROUTES so they are not in the sitemap or crawler files.
    for retired_path in ("/builders", "/docs/langgraph"):
        retired = OUTPUT / retired_path.strip("/") / "index.html"
        retired.parent.mkdir(parents=True, exist_ok=True)
        retired.write_text(
            "<!DOCTYPE html>\n"
            '<html lang="en">\n'
            "<head>\n"
            '<meta charset="utf-8">\n'
            f'<link rel="canonical" href="{SITE_BASE}/docs">\n'
            '<meta http-equiv="refresh" content="0; url=/docs">\n'
            "<title>Docs — SMEme</title>\n"
            "</head>\n"
            "<body>\n"
            '<p><a href="/docs">Docs</a></p>\n'
            "</body>\n"
            "</html>\n",
            encoding="utf-8",
        )


if __name__ == "__main__":
    main()
