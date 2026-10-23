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

    def test_every_mapped_route_generates_index(self):
        for route in build.LANDING | build.DOCS | build.LEGAL:
            output = build._output_path(route)
            self.assertTrue(output.is_file(), route)

    def test_public_routes_are_exactly_in_crawler_files(self):
        expected = {f"{build.SITE_BASE}{route}" for route, _, _ in build.PUBLIC_ROUTES}

        sitemap = ElementTree.parse(self.output / "sitemap.xml")
        namespace = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        sitemap_urls = [
            element.text
            for element in sitemap.findall("s:url/s:loc", namespace)
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
            r'^/(?:teams-waitlist|auth|decision-trees|billing|api|\.well-known)(?:/|$)'
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


if __name__ == "__main__":
    unittest.main()
