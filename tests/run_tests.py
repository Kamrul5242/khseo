#!/usr/bin/env python3
"""KHSEO package self-test (stdlib only). Run from anywhere: python tests/run_tests.py"""
from __future__ import annotations

import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import seo_probe  # noqa: E402

FIX = ROOT / "tests" / "fixtures"


class PackageStructure(unittest.TestCase):
    REQUIRED = [
        "SKILL.md", "README.md", "LICENSE", "commands.md",
        "rules/core-rules.md", "rules/governance.md", "rules/seo-checklists.md",
        "workflows/audit.md", "workflows/code.md", "workflows/content.md",
        "workflows/social.md", "workflows/general-user.md",
        "templates/audit-report.md", "templates/writing-output.md", "templates/rewrite-output.md",
        "templates/social-output.md", "templates/code-change-report.md",
        "templates/approval-request.md", "templates/schema-snippets.md",
        "schemas/audit-report.schema.json", "scripts/seo_probe.py",
    ]

    def test_required_files_exist(self):
        missing = [p for p in self.REQUIRED if not (ROOT / p).is_file()]
        self.assertEqual(missing, [], f"missing files: {missing}")

    def test_all_commands_documented(self):
        cmds = ["audit", "fix", "write", "optimize", "build", "verify", "research", "plan",
                "dry-run", "status", "approve", "reject", "rollback", "stop", "help"]
        ref = (ROOT / "commands.md").read_text(encoding="utf-8")
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        for c in cmds:
            self.assertIn(f"### `KHSEO {c}`", ref, f"commands.md missing section for {c}")
            self.assertIn(f"`KHSEO {c}", skill, f"SKILL.md table missing {c}")

    def test_skill_frontmatter(self):
        text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
        self.assertIsNotNone(m, "SKILL.md must start with YAML frontmatter")
        fm = m.group(1)
        self.assertRegex(fm, r"(?m)^name:\s*khseo\s*$")
        self.assertRegex(fm, r"(?m)^description:")
        desc = fm.split("description:", 1)[1]
        self.assertIn("KHSEO", desc)
        self.assertLess(len(desc), 1024, "description should stay under 1024 chars")

    def test_skill_md_is_lean(self):
        lines = (ROOT / "SKILL.md").read_text(encoding="utf-8").count("\n")
        self.assertLess(lines, 500, "SKILL.md should stay under 500 lines (progressive disclosure)")

    def test_relative_markdown_links_resolve(self):
        broken = []
        for md in ROOT.rglob("*.md"):
            if ".git" in md.parts:
                continue
            for target in re.findall(r"\]\(([^)#\s]+)(?:#[^)]*)?\)", md.read_text(encoding="utf-8")):
                if target.startswith(("http://", "https://", "mailto:")):
                    continue
                if not (md.parent / target).resolve().exists():
                    broken.append(f"{md.relative_to(ROOT)} -> {target}")
        self.assertEqual(broken, [], "broken links:\n" + "\n".join(broken))

    def test_json_files_parse(self):
        for js in ROOT.rglob("*.json"):
            if ".git" in js.parts:
                continue
            json.loads(js.read_text(encoding="utf-8"))

    def test_schema_snippets_parse(self):
        text = (ROOT / "templates/schema-snippets.md").read_text(encoding="utf-8")
        blocks = re.findall(r"```json\n(.*?)```", text, re.S)
        self.assertGreaterEqual(len(blocks), 5)
        for b in blocks:
            data = json.loads(b)
            self.assertEqual(data.get("@context"), "https://schema.org")


class ProbeOnFixtures(unittest.TestCase):
    def _findings(self, name, base="https://example.com/products/classic-cotton-tee"):
        r = seo_probe.run(str(FIX / name), base=base, network=False)
        return r, {f["message"] for f in r["findings"]}

    def test_bad_page_flags_critical_issues(self):
        r, msgs = self._findings("bad_page.html", base="https://example.com/")
        self.assertTrue(any("noindex" in m for m in msgs))
        self.assertTrue(any("JSON-LD" in m and "parse" in m for m in msgs))
        self.assertTrue(any("conflicting canonicals" in m for m in msgs))
        self.assertTrue(any("<title> tags" in m for m in msgs))
        self.assertTrue(any("viewport" in m for m in msgs))
        self.assertEqual(r["findings"][0]["priority"], "P0", "P0 must sort first")
        self.assertEqual(r["page"]["h1_count"], 2)
        self.assertEqual(len(r["page"]["images_missing_alt"]), 1)

    def test_good_page_is_clean(self):
        r, msgs = self._findings("good_page.html")
        self.assertEqual([f for f in r["findings"] if f["priority"] in ("P0", "P1")], [], msgs)
        self.assertEqual(r["page"]["h1_count"], 1)
        types = [t for j in r["page"]["jsonld"] for t in j["types"]]
        self.assertIn("Product", types)
        self.assertIn("BreadcrumbList", types)
        self.assertTrue(all(j["valid"] for j in r["page"]["jsonld"]))

    def test_local_file_marks_network_checks_not_tested(self):
        r, _ = self._findings("good_page.html")
        self.assertIn("robots.txt", r["not_tested"])
        self.assertIsNone(r["fetch"])

    def test_js_challenge_shell_is_p0(self):
        """Regression: a Reblaze-style 200 response with only a script must be flagged P0."""
        shell = ('<!DOCTYPE html><html><head><meta charset="utf-8"><script src="/x.lib.js"></script>'
                 '<script>window.rbzns={"seed":"abc"};</script></head><body></body></html>')
        page = seo_probe.analyze_html(shell, "https://shop.example/")
        fr = {"error": None, "status": 200, "redirects": [], "body": shell, "headers": {},
              "final_url": "https://shop.example/"}
        f = seo_probe.build_findings(fr, page, None, None)
        self.assertEqual(f[0]["priority"], "P0")
        self.assertIn("Bot-challenge", f[0]["message"])

    # ---- regressions from the v1.1.0 security/bug audit -------------------------------------
    def test_svg_title_is_not_a_page_title(self):
        html = "<html><head><title>Real</title></head><body><svg><title>icon</title></svg></body></html>"
        p = seo_probe.analyze_html(html, "https://a.test/")
        self.assertEqual((p["title"], p["title_count"]), ("Real", 1))

    def test_robots_longest_match_allow_wins(self):
        g, _ = seo_probe.parse_robots("User-agent: *\nDisallow: /\nAllow: /public/\n")
        self.assertTrue(seo_probe.robots_allowed(g, "Googlebot", "https://a.test/public/x"))
        self.assertFalse(seo_probe.robots_allowed(g, "Googlebot", "https://a.test/private"))

    def test_robots_agent_token_is_exact(self):
        g, _ = seo_probe.parse_robots("User-agent: Google\nDisallow: /\n")
        self.assertTrue(seo_probe.robots_allowed(g, "Googlebot", "https://a.test/"))
        g, _ = seo_probe.parse_robots("User-agent: *\nAllow: /\n\nUser-agent: GPTBot\nDisallow: /\n")
        self.assertFalse(seo_probe.robots_allowed(g, "GPTBot", "https://a.test/"))
        self.assertTrue(seo_probe.robots_allowed(g, "ClaudeBot", "https://a.test/"))

    def test_robots_wildcards_and_empty_disallow(self):
        g, sm = seo_probe.parse_robots("User-agent: *\nDisallow: /*.pdf$\nDisallow:\nSitemap: https://a.test/s.xml\n")
        self.assertFalse(seo_probe.robots_allowed(g, "Googlebot", "https://a.test/doc.pdf"))
        self.assertTrue(seo_probe.robots_allowed(g, "Googlebot", "https://a.test/doc.pdf?x=1"))
        self.assertTrue(seo_probe.robots_allowed(g, "Googlebot", "https://a.test/page"))
        self.assertEqual(sm, ["https://a.test/s.xml"])

    def test_recaptcha_widget_is_not_p0(self):
        html = ('<html><head><title>Contact us</title><meta name="viewport" content="x"></head>'
                '<body><h1>Contact</h1><p>Send us a message.</p><div class="g-recaptcha"></div></body></html>')
        fr = {"error": None, "status": 200, "redirects": [], "body": html, "headers": {},
              "final_url": "https://a.test/contact"}
        f = seo_probe.build_findings(fr, seo_probe.analyze_html(html, fr["final_url"]), None, None)
        self.assertFalse([x for x in f if x["priority"] == "P0"])

    def test_ssrf_guards(self):
        for bad in ["http://169.254.169.254/latest/", "http://127.0.0.1/", "http://localhost/",
                    "http://[::1]/", "ftp://example.com/", "file:///etc/passwd"]:
            with self.assertRaises(seo_probe.UnsafeURL, msg=bad):
                seo_probe.check_url(bad, allow_private=False)
        seo_probe.check_url("http://127.0.0.1/", allow_private=True)  # explicit local target is fine
        with self.assertRaises(seo_probe.UnsafeURL):
            seo_probe.check_url("ftp://127.0.0.1/", allow_private=True)  # scheme never allowed

    def test_sitemap_on_foreign_host_not_fetched(self):
        r = seo_probe.check_sitemap("https://shop.example/", ["http://169.254.169.254/x", "https://cdn.other.example/s.xml"])
        self.assertTrue(all(c.get("skipped") for c in r["checked"]))
        self.assertTrue(seo_probe._same_site("https://blog.shop.example/s.xml", "https://www.shop.example/"))

    def test_control_chars_stripped(self):
        import tempfile, os
        with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as fh:
            fh.write("<title>A\x1b[2J\x9bB\x07</title>")
        try:
            title = seo_probe.run(fh.name, network=False)["page"]["title"]
        finally:
            os.unlink(fh.name)
        self.assertFalse(any(ord(c) < 32 or 127 <= ord(c) <= 159 for c in title), repr(title))

    def test_bad_charset_and_decompression_cap(self):
        import gzip
        self.assertEqual(seo_probe._charset("text/html; charset=utf8mb4-bogus"), "utf-8")
        self.assertEqual(seo_probe._charset('text/html; charset="ISO-8859-1"'), "iso8859-1")
        bomb = gzip.compress(b" " * (seo_probe.MAX_DECODED * 3))
        data, cut = seo_probe._decompress(bomb, "gzip")
        self.assertEqual((len(data), cut), (seo_probe.MAX_DECODED, True))

    def test_cli_missing_file_and_uppercase_scheme(self):
        import subprocess
        o = subprocess.run([sys.executable, str(ROOT / "scripts" / "seo_probe.py"), "no-such-file.html"],
                           capture_output=True, text=True)
        self.assertEqual(o.returncode, 2)
        self.assertNotIn("Traceback", o.stderr)
        self.assertTrue(seo_probe.urlparse("HTTPS://x.test/").scheme.lower() == "https")

    def test_challenged_sitemap_is_named(self):
        sm = {"checked": [{"url": "https://a.test/sitemap.xml", "status": 200, "is_xml": False,
                           "url_entries": 0, "is_index": False, "challenged": True}]}
        page = seo_probe.analyze_html("<title>x</title>", "https://a.test/")
        f = [x for x in seo_probe.build_findings(None, page, None, sm) if "sitemap" in x["message"]]
        self.assertIn("bot-challenge", f[0]["evidence"])

    def test_every_finding_has_label(self):
        r, _ = self._findings("bad_page.html")
        for f in r["findings"]:
            self.assertIn(f["priority"], {"P0", "P1", "P2", "P3"})
            self.assertIn(f["label"], {"VERIFIED", "OBSERVED", "INFERRED", "RECOMMENDED",
                                       "ASSUMED", "UNKNOWN", "NOT TESTED"})

    def test_gzip_response_is_decoded(self):
        """Regression: servers send gzip; parsing compressed bytes silently lost the <title>."""
        import gzip
        import http.server
        import threading

        html = (FIX / "good_page.html").read_bytes()

        class H(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                body = gzip.compress(html) if self.path == "/" else b"User-agent: *\nAllow: /\n"
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8" if self.path == "/" else "text/plain")
                if self.path == "/":
                    self.send_header("Content-Encoding", "gzip")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def log_message(self, *a):
                pass

        srv = http.server.HTTPServer(("127.0.0.1", 0), H)
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        try:
            r = seo_probe.run(f"http://127.0.0.1:{srv.server_port}/")
        finally:
            srv.shutdown()
        self.assertTrue(r["page"]["title"].startswith("Classic Cotton Tee"))
        self.assertEqual(r["page"]["h1_count"], 1)
        self.assertEqual(r["robots"]["status"], 200)

    def test_json_output_serializable(self):
        r, _ = self._findings("bad_page.html")
        json.dumps(r, default=list)


if __name__ == "__main__":
    unittest.main(verbosity=2)
