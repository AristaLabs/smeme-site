import re
import tempfile
import unittest
from pathlib import Path
from xml.etree import ElementTree

import build


class StaticBuildTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.output = Path(tempfile.mkdtemp(prefix="smeme-site-build-"))
        cls.original_output = build.OUTPUT
        build.OUTPUT = cls.output
        build.main()

    @classmethod
    def tearDownClass(cls):
        build.OUTPUT = cls.original_output
        for path in cls.output.glob("**/*"):
            if path.is_file():
                path.unlink()
        for path in sorted(cls.output.glob("**/*"), reverse=True):
            if path.is_dir():
                path.rmdir()
        cls.output.rmdir()

    def test_route_maps_match_public_routes(self):
        mapped_routes = set(build.LANDING) | set(build.DOCS) | set(build.LEGAL)
        public_routes = {route for route, _, _ in build.PUBLIC_ROUTES}
        self.assertEqual(mapped_routes, public_routes)

    def test_docs_pages_are_pinned_light_without_theme_toggle(self):
        for route in build.DOCS:
            html = build._output_path(route).read_text(encoding="utf-8")
            self.assertIn('data-theme-pin="light"', html, route)
            self.assertNotIn('id="theme-toggle"', html, route)

    def test_docs_keep_the_marketing_header_and_sidebar(self):
        html = build._output_path("/docs").read_text(encoding="utf-8")
        self.assertIn('class="landing-header v4 v4-header', html)
        self.assertIn(">Pricing</a>", html)
        self.assertIn('aria-current="page">Docs</a>', html)
        self.assertIn("docs-public", html)
        self.assertNotIn('aria-label="Main navigation"', html)

    def test_docs_mark_the_current_page_and_hide_the_duplicate_nav(self):
        overview = build._output_path("/docs").read_text(encoding="utf-8")
        quick_start = build._output_path("/docs/quick-start").read_text(encoding="utf-8")
        self.assertIn('href="/docs" aria-current="page"', overview)
        self.assertNotIn('href="/docs/quick-start" aria-current="page"', overview)
        self.assertIn('href="/docs/quick-start" aria-current="page"', quick_start)
        self.assertIn(".docs-public .lg\\:hidden { display: none; }", quick_start)
        self.assertIn("docs-public v4", quick_start)

    def test_pricing_does_not_paint_a_blurred_glow(self):
        html = build._output_path("/pricing").read_text(encoding="utf-8")
        self.assertNotIn("filter: blur(30px)", html)
        self.assertIn("color-scheme: light", html)
        self.assertIn(".landing-page-shell { background: #F6F7FA; }", html)

    def test_homepage_shows_all_use_cases(self):
        html = build._output_path("/").read_text(encoding="utf-8")
        self.assertEqual(html.count('<article class="v4-case">'), 10)
        self.assertNotIn("v4-cases-more", html)

    def test_every_mapped_route_generates_index(self):
        for route in build.LANDING | build.DOCS | build.LEGAL:
            output = build._output_path(route)
            self.assertTrue(output.is_file(), route)

    def test_public_routes_are_exactly_in_crawler_files(self):
        expected = {f"{build.SITE_BASE}{route}" for route, _, _ in build.PUBLIC_ROUTES}

        sitemap = ElementTree.parse(self.output / "sitemap.xml")
        namespace = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        sitemap_urls = [
            element.text for element in sitemap.findall("s:url/s:loc", namespace)
        ]
        self.assertEqual(set(sitemap_urls), expected)
        self.assertEqual(len(sitemap_urls), len(expected))

        for filename in ("llms.txt", "llms-full.txt"):
            contents = (self.output / filename).read_text(encoding="utf-8")
            urls = re.findall(r"https://smeme\.ai(?:/[^\s)]*)?", contents)
            self.assertEqual(set(urls), expected, filename)
            self.assertEqual(len(urls), len(expected), filename)

    def test_every_public_page_has_one_site_canonical(self):
        for route in build.LANDING | build.DOCS | build.LEGAL:
            html = build._output_path(route).read_text(encoding="utf-8")
            canonical = re.findall(
                r'<link rel="canonical" href="([^"]+)"',
                html,
            )
            self.assertEqual(canonical, [f"{build.SITE_BASE}{route}"], route)

    def test_mcp_links_use_the_app_endpoint(self):
        mcp_urls = re.compile(r"https://[^\s\"'<>]*api/v1/mcp[^\s\"'<>]*")
        for path in self.output.glob("**/*.html"):
            html = path.read_text(encoding="utf-8")
            found = mcp_urls.findall(html)
            if "api/v1/mcp" in html:
                self.assertTrue(found, str(path))
            for url in found:
                self.assertEqual(url, build.MCP_ENDPOINT, str(path))

    def test_app_owned_attributes_are_absolute(self):
        app_attributes = re.compile(r'(?:href|action)="([^"]+)"')
        forbidden_relative = re.compile(
            r"^/(?:teams-waitlist|auth|decision-trees|billing|api|\.well-known)(?:/|$)"
        )
        app_prefixes = (
            "/teams-waitlist",
            "/auth",
            "/decision-trees",
            "/billing",
            "/api",
            "/.well-known",
            "/docs/delete-account",
        )

        for path in self.output.glob("**/*.html"):
            html = path.read_text(encoding="utf-8")
            for value in app_attributes.findall(html):
                if value.startswith(app_prefixes):
                    self.fail(f"relative app-owned attribute in {path}: {value}")
                if forbidden_relative.match(value):
                    self.fail(f"relative app-owned attribute in {path}: {value}")
            if "/docs/delete-account" in html:
                self.assertIn(
                    f"{build.APP_BASE}/docs/delete-account",
                    html,
                    str(path),
                )

    def test_docs_nav_has_one_tool_reference_link(self):
        for route in build.DOCS:
            html = build._output_path(route).read_text(encoding="utf-8")
            navs = re.findall(
                r'<nav aria-label="Docs sections"[^>]*>.*?</nav>',
                html,
                re.DOTALL,
            )
            self.assertEqual(len(navs), 2, route)
            for nav in navs:
                hrefs = re.findall(r'href="([^"]+)"', nav)
                self.assertEqual(hrefs.count("/mcp"), 1, route)
                self.assertIn("/docs/mcp", hrefs, route)
                self.assertIn("MCP tool reference", nav, route)
                self.assertIn("Connect your agent", nav, route)

    def test_homepage_does_not_link_the_arista_blog(self):
        html = build._output_path("/").read_text(encoding="utf-8")
        self.assertNotIn("aristalabs.ai/blog.html", html)
        self.assertNotIn("Arista Labs blog", html)

    def test_blog_route_is_unpublished(self):
        routes = {route for route, _, _ in build.PUBLIC_ROUTES}
        self.assertNotIn("/blog", routes)
        for filename in ("sitemap.xml", "llms.txt", "llms-full.txt"):
            contents = (self.output / filename).read_text(encoding="utf-8")
            self.assertNotIn("/blog", contents, filename)

    def test_delete_account_is_not_generated(self):
        self.assertFalse(
            (self.output / "docs" / "delete-account" / "index.html").exists()
        )

    def test_homepage_keeps_retained_elements(self):
        html = build._output_path("/").read_text(encoding="utf-8")
        self.assertTrue(
            "&#127482;&#127480;" in html or "\U0001f1fa\U0001f1f8" in html,
            "homepage footer flag",
        )
        self.assertIn("Veteran owned and operated", html)
        self.assertIn("lm-app-icon", html)
        self.assertIn("Decide the withholding", html)
        self.assertIn("Rational AI for the decisions that run your business", html)
        self.assertIn('href="/faq"', html)
        self.assertNotIn('id="faq"', html)

    def test_homepage_demos_section_follows_the_hero(self):
        html = build._output_path("/").read_text(encoding="utf-8")
        demos = html[html.index('id="demos"') : html.index('id="use-cases"')]
        self.assertIn("Build a decision tree", demos)
        self.assertIn("Run a decision tree", demos)
        self.assertIn(
            "Build a decision tree with the AI you already use, then run it on a real case.",
            demos,
        )
        self.assertNotIn("Two short demos.", demos)
        self.assertIn('href="/docs/quick-start"', demos)
        self.assertIn('href="/docs/mcp"', demos)
        self.assertIn("smeme_reasoning_evaluate", demos)
        self.assertNotIn("Why it matters", html)
        self.assertNotIn('id="why"', html)
        self.assertLess(html.index('id="use-cases"'), html.index('id="mission"'))
        self.assertNotIn('id="start"', html)
        for removed in ('id="how"', 'id="engine"', 'id="tech"', 'id="example"', "v4-close-steps", "v4-result"):
            self.assertNotIn(removed, html, removed)
        for removed in ("Natural language at the edges", "Does ACME withhold on the Party D royalty?"):
            self.assertNotIn(removed, html, removed)

    def test_homepage_leads_with_the_withholding_use_case(self):
        html = build._output_path("/").read_text(encoding="utf-8")
        self.assertIn(
            "so you can approve the decision knowing exactly why it holds.",
            html,
        )
        self.assertLess(
            html.index("Decide the withholding"), html.index("Accept a new client")
        )
        self.assertNotIn("download, share, and delete", html)

    def test_homepage_matches_gtm_entry_copy(self):
        html = build._output_path("/").read_text(encoding="utf-8")
        hero = html[html.index('id="top"') : html.index('id="demos"')]
        self.assertIn('class="v4-dict-word">ra&middot;tion&middot;al</dfn>', hero)
        self.assertNotIn('class="v4-kicker"', hero)
        self.assertIn('href="#demos" class="v4-btn v4-btn--primary">Get started</a>', hero)
        self.assertNotIn("/auth/register", hero)
        self.assertNotIn("Watch the demos", hero)
        self.assertNotIn("Build your first decision tree", hero)
        self.assertIn("A reasoned cause is how you keep agency.", html)
        self.assertIn("It is an act of autonomy", html)
        self.assertIn("The model proposes, you authorize, and the solver decides", html)
        security = html[html.index("Engineering") : html.index('id="mission"')]
        self.assertLess(
            security.index("Escalate the alert"), security.index("Ship the change")
        )
        self.assertIn("Splunk", security)
        self.assertNotIn("Triage the incident", html)
        self.assertIn(
            "Fictional examples. Incomplete procedures. Not professional advice.", html
        )
        for retired in (
            "Meets criteria",
            "Triage the issue",
            "SMEme is neurosymbolic",
            "Review the facts, not the reasoning",
            "DeveloperApplication",
            "Your AI understands the situation",
            "solver-backed",
            "Our mission is to make AI rational.",
            "Review admitted facts and unresolved cases",
        ):
            self.assertNotIn(retired, html, retired)
        self.assertIn('"applicationCategory": "BusinessApplication"', html)

    def test_supporting_pages_use_the_withholding_vignette(self):
        for route in ("/docs/quick-start", "/docs/run-a-tree"):
            html = build._output_path(route).read_text(encoding="utf-8")
            self.assertNotIn("deal qualification", html.lower(), route)
            self.assertIn("Cross-border withholding", html, route)

    def test_crawler_intro_uses_the_category_sentence(self):
        for filename in ("llms.txt", "llms-full.txt"):
            contents = (self.output / filename).read_text(encoding="utf-8")
            self.assertIn(
                "SMEme is the formal reasoning layer for AI", contents, filename
            )
            self.assertNotIn("deterministic", contents.lower(), filename)

    def test_v4_pages_have_no_design_tool_leftovers(self):
        for route in ("/",):
            html = build._output_path(route).read_text(encoding="utf-8")
            self.assertNotIn("{{", html, route)
            self.assertNotIn("Shot list", html, route)
            self.assertNotIn("Video placeholder", html, route)
            self.assertNotIn("poster frame", html, route)
            self.assertIn("IBM+Plex", html, route)

    def test_marketing_pages_do_not_offer_self_hosting(self):
        banned = (
            "self-host guide",
            "self-host-quickstart",
            "source available",
            "source-available",
            "sul 1.0",
            "fair-code",
            "fair code",
            "self hosting",
            "run it yourself",
            "run smeme core yourself",
            "smeme ai tree builds",
            "ai-assisted build credits",
            "ai-assisted wizard",
            "generation wizard",
            "build with the wizard",
        )
        for route in ("/", "/pricing", "/mcp", "/docs"):
            html = build._output_path(route).read_text(encoding="utf-8").lower()
            for phrase in banned:
                self.assertNotIn(phrase, html, f"{route} contains {phrase}")

    def test_faq_page_holds_the_homepage_questions(self):
        html = build._output_path("/faq").read_text(encoding="utf-8")
        self.assertIn('rel="canonical" href="https://smeme.ai/faq"', html)
        self.assertIn('aria-current="page">FAQ</a>', html)
        self.assertEqual(html.count("<summary>"), 12)
        self.assertIn("What is a decision tree?", html)
        self.assertIn("Hosted Free includes 3 decision trees and 150 MCP calls.", html)

    def test_how_it_works_is_unpublished(self):
        routes = {route for route, _, _ in build.PUBLIC_ROUTES}
        self.assertNotIn("/how-it-works", routes)
        self.assertNotIn("/how-it-works", build.LANDING)
        self.assertFalse((self.output / "how-it-works" / "index.html").exists())
        for filename in ("sitemap.xml", "llms.txt", "llms-full.txt"):
            contents = (self.output / filename).read_text(encoding="utf-8")
            self.assertNotIn("/how-it-works", contents, filename)

    def test_builders_page_is_unpublished(self):
        routes = {route for route, _, _ in build.PUBLIC_ROUTES}
        self.assertNotIn("/builders", routes)
        self.assertNotIn("/builders", build.LANDING)
        redirect = (self.output / "builders" / "index.html").read_text(encoding="utf-8")
        self.assertIn('rel="canonical" href="https://smeme.ai/docs/langgraph"', redirect)
        self.assertIn('url=/docs/langgraph', redirect)
        self.assertNotIn("For builders", redirect)
        for filename in ("sitemap.xml", "llms.txt", "llms-full.txt"):
            contents = (self.output / filename).read_text(encoding="utf-8")
            self.assertNotIn("/builders", contents, filename)
        for route in ("/", "/pricing", "/mcp", "/faq", "/docs"):
            html = build._output_path(route).read_text(encoding="utf-8")
            self.assertNotIn('href="/builders"', html, route)
            self.assertNotIn(">For builders<", html, route)
            self.assertIn('href="/faq"', html, route)
            self.assertNotIn('href="/how-it-works"', html, route)
            self.assertNotIn(">How it works<", html, route)
        faq = build._output_path("/faq").read_text(encoding="utf-8")
        self.assertIn('href="/docs/mcp"', faq)
        self.assertNotIn("builders page", faq)

    def test_public_pages_do_not_link_the_private_core_repo(self):
        private_repo = re.compile(r"github\.com/AristaLabs/smeme(?!-)", re.IGNORECASE)
        for path in self.output.rglob("*"):
            if path.suffix.lower() not in {".html", ".txt", ".xml", ".json"}:
                continue
            contents = path.read_text(encoding="utf-8")
            self.assertIsNone(private_repo.search(contents), path.relative_to(self.output))


if __name__ == "__main__":
    unittest.main()
