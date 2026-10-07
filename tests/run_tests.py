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
        "schemas/approval.schema.json", "schemas/change-set.schema.json", "schemas/validation.schema.json",
        "schemas/capabilities.schema.json", "scripts/validate_json.py", "scripts/capture_rendered.py",
        "config/ai-crawlers.json", "scripts/audit_report.py", "scripts/meta_tags.py", "scripts/clean_text.py", "VERSION", "scripts/khseo_version.py",
        "SECURITY.md", ".github/dependabot.yml",
        "workflows/keywords.md", "workflows/competitors.md", "workflows/ranking.md", "workflows/offpage.md",
        "workflows/gig.md",
        "templates/keyword-report.md", "templates/competitor-analysis.md", "templates/ranking-plan.md",
        "templates/offpage-plan.md",
    ]

    def test_required_files_exist(self):
        missing = [p for p in self.REQUIRED if not (ROOT / p).is_file()]
        self.assertEqual(missing, [], f"missing files: {missing}")

    def test_all_commands_documented(self):
        cmds = ["audit", "fix", "write", "optimize", "build", "verify", "research", "plan",
                "dry-run", "status", "approve", "reject", "rollback", "stop", "help",
                "meta", "keywords", "competitors", "rank", "offpage", "schema", "aeo", "trust",
                "social", "clean", "report"]
        ref = (ROOT / "commands.md").read_text(encoding="utf-8")
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        for c in cmds:
            self.assertIn(f"### `KHSEO {c}`", ref, f"commands.md missing section for {c}")
            self.assertIn(c, skill, f"SKILL.md missing {c}")
            self.assertIn(f"  {c} ", ref.split("KHSEO: just type", 1)[1].split("Examples", 1)[0] + " ",
                          f"help card missing {c}") if c not in ("approve", "reject") else None

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

    def test_versions_are_consistent(self):
        import khseo_version as kv
        ver = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
        self.assertRegex(ver, r"^\d+\.\d+\.\d+$", "VERSION must be semver")
        self.assertEqual(kv.KHSEO_VERSION, ver)
        top = re.search(r"(?m)^## (\d+\.\d+\.\d+)\b", (ROOT / "CHANGELOG.md").read_text(encoding="utf-8"))
        self.assertEqual(top.group(1), ver, "CHANGELOG's newest entry must match VERSION")
        self.assertRegex(kv.SPEC_VERSION, r"^\d+\.\d+$")
        self.assertRegex(kv.SCHEMA_VERSION, r"^\d+\.\d+$")
        for f in (ROOT / "schemas").glob("*.schema.json"):
            self.assertEqual(json.loads(f.read_text(encoding="utf-8")).get("x-khseo-schema-version"),
                             kv.SCHEMA_VERSION, f.name)
        self.assertEqual(audit_report.VERSION, ver)
        r = seo_probe.run(str(FIX / "good_page.html"), base="https://a.test/", network=False)
        self.assertEqual(r["versions"], kv.versions(seo_probe.VERSION))
        self.assertIn("VERSIONS: KHSEO " + ver, seo_probe.render_text(r))
        self.assertEqual(seo_probe.to_audit(r)["versions"]["khseo"], ver)

    def test_workflows_pin_actions_and_limit_permissions(self):
        """Supply-chain hardening: every action pinned to a 40-hex commit SHA (tags are mutable),
        and every workflow declares top-level permissions."""
        wf_dir = ROOT / ".github" / "workflows"
        files = sorted(wf_dir.glob("*.yml"))
        self.assertGreaterEqual(len(files), 4)
        unpinned = []
        for f in files:
            text = f.read_text(encoding="utf-8")
            self.assertRegex(text, r"(?m)^permissions:", f"{f.name} lacks top-level permissions")
            for m in re.finditer(r"(?m)^\s*-?\s*uses:\s*(\S+)", text):
                ref = m.group(1)
                if ref.startswith("./"):
                    continue
                if not re.fullmatch(r"[\w.-]+/[\w./-]+@[0-9a-f]{40}", ref):
                    unpinned.append(f"{f.name}: {ref}")
        self.assertEqual(unpinned, [], "actions must be pinned to full commit SHAs")

    def test_no_control_characters_in_repo_text(self):
        """Mangled escapes (\\b -> backspace) hit 3 files once; keep every text file clean."""
        bad = []
        for f in ROOT.rglob("*"):
            if ".git" in f.parts or f.suffix not in (".md", ".json", ".py", ".yml", ".html"):
                continue
            text = f.read_text(encoding="utf-8")
            if any(ord(c) < 32 and c not in "\n\r\t" for c in text):
                bad.append(str(f.relative_to(ROOT)))
        self.assertEqual(bad, [])

    def test_no_invisible_or_bidi_characters_in_source(self):
        """Invisible/bidi/odd-space characters must be written as escapes: raw ones can be silently
        stripped (breaking clean_text's regex) or hide code ('Trojan Source', CVE-2021-42574)."""
        import unicodedata
        bad = {}
        for f in ROOT.rglob("*"):
            if ".git" in f.parts or f.suffix not in (".md", ".json", ".py", ".yml", ".html"):
                continue
            hits = {f"U+{ord(c):04X}" for c in f.read_text(encoding="utf-8")
                    if ord(c) > 127 and unicodedata.category(c) in ("Cf", "Zs", "Zl", "Zp", "Cc")}
            if hits:
                bad[str(f.relative_to(ROOT))] = sorted(hits)
        self.assertEqual(bad, {})

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


import validate_json  # noqa: E402

EX = ROOT / "examples" / "json"


class GovernanceSchemas(unittest.TestCase):
    PAIRS = [("audit-report", "sample-audit"), ("capabilities", "capabilities"), ("approval", "approval"),
             ("change-set", "change-set"), ("validation", "validation")]

    def _load(self, name):
        return json.loads((EX / f"{name}.json").read_text(encoding="utf-8"))

    def test_examples_are_valid(self):
        for schema, ex in self.PAIRS:
            self.assertEqual(validate_json.check(schema, self._load(ex)), [], f"{ex} vs {schema}")

    def test_validator_catches_structural_errors(self):
        doc = self._load("approval")
        doc["risk"] = "R1"            # R0-R1 never need an approval object
        doc["status"] = "OK"          # not a state
        doc["surprise"] = 1           # additionalProperties false
        del doc["recovery"]
        errs = " | ".join(validate_json.check("approval", doc))
        for needle in ("$.risk", "$.status", "unexpected property 'surprise'", "missing required 'recovery'"):
            self.assertIn(needle, errs)

    # ---- NOT VERIFIED enforcement ("can't test -> never PASSED") ---------------------------
    def test_passed_without_evidence_is_rejected(self):
        doc = {"checks": [{"name": "Build", "status": "PASSED"}]}
        self.assertTrue(any("PASSED without method + evidence" in e for e in validate_json.check("validation", doc)))

    def test_pass_is_not_a_status(self):
        doc = {"checks": [{"name": "CWV", "status": "PASS", "method": "x", "evidence": "y"}]}
        self.assertTrue(validate_json.check("validation", doc))

    def test_unavailable_capability_forces_not_verified(self):
        caps = self._load("capabilities")
        caps["capabilities"]["browser_render"] = "UNAVAILABLE"
        doc = {"checks": [{"name": "Core Web Vitals", "status": "PASSED", "method": "guess",
                           "evidence": "looks fast", "requires": ["browser_render"]}]}
        errs = validate_json.check("validation", doc, caps)
        self.assertTrue(any("must be NOT_VERIFIED" in e for e in errs), errs)

    def test_verified_finding_about_untested_area_is_rejected(self):
        doc = self._load("sample-audit")
        doc["findings"].append({"id": "F9", "layer": "technical", "priority": "P2", "label": "VERIFIED",
                                "message": "Core Web Vitals are good", "evidence": "seems fine"})
        errs = validate_json.check("audit-report", doc)
        self.assertTrue(any("listed as not tested" in e for e in errs), errs)

    def test_change_set_cannot_claim_deployment(self):
        doc = self._load("change-set")
        doc["deployed"] = True
        self.assertTrue(validate_json.check("change-set", doc))

    def test_probe_output_never_passes_untested_areas(self):
        r = seo_probe.run(str(FIX / "good_page.html"), base="https://a.test/", network=False)
        for area in ("JavaScript rendering", "Core Web Vitals", "robots.txt"):
            self.assertIn(area, r["not_tested"])
        self.assertFalse(any(f["label"] == "VERIFIED" for f in r["findings"]),
                         "a single raw-HTML probe can observe, not verify")


import audit_report  # noqa: E402
import capture_rendered  # noqa: E402


class PdfReport(unittest.TestCase):
    def _audit(self):
        return json.loads((EX / "sample-audit.json").read_text(encoding="utf-8"))

    def test_builtin_pdf_is_well_formed(self):
        import tempfile, re as _re
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / "r.pdf"
            r = audit_report.render(self._audit(), out, engine="builtin")
            data = out.read_bytes()
            self.assertEqual(r["engine"], "builtin")
            self.assertTrue(data.startswith(b"%PDF-1.4"))
            self.assertTrue(data.rstrip().endswith(b"%%EOF"))
            pages = int(_re.search(rb"/Count (\d+)", data).group(1))
            self.assertGreaterEqual(pages, 1)
            self.assertEqual(len(_re.findall(rb"/Type /Page\b", data)), pages)
            xref = int(_re.search(rb"startxref\n(\d+)", data).group(1))
            self.assertEqual(data[xref:xref + 4], b"xref")
            self.assertTrue(Path(r["html"]).exists())

    def test_hostile_page_text_is_escaped(self):
        """Audit text often comes from untrusted pages: it must never become live HTML."""
        a = self._audit()
        a["findings"][0]["message"] = '<script>alert(1)</script><img src=x onerror=alert(2)>'
        a["site_name"] = '"><iframe src=//evil.example>'
        h = audit_report.build_html(a)
        self.assertNotIn("<script>alert", h)
        self.assertNotIn("<img src=x", h)
        self.assertNotIn("<iframe", h)
        self.assertIn("&lt;script&gt;", h)
        self.assertIn("default-src 'none'", h)

    def test_invalid_or_dishonest_audit_is_refused(self):
        import tempfile
        a = self._audit()
        a["findings"].append({"id": "X", "layer": "technical", "priority": "P1", "label": "VERIFIED",
                              "message": "Core Web Vitals pass"})
        with tempfile.TemporaryDirectory() as d, self.assertRaises(ValueError):
            audit_report.render(a, Path(d) / "r.pdf", engine="builtin")

    def test_non_latin_text_does_not_crash_builtin(self):
        import tempfile
        a = self._audit()
        a["summary"] = "বাংলা টেক্সট — “quotes” → arrows ✓ 日本語"
        with tempfile.TemporaryDirectory() as d:
            audit_report.render(a, Path(d) / "r.pdf", engine="builtin")

    def test_probe_audit_json_is_valid_input(self):
        r = seo_probe.run(str(FIX / "bad_page.html"), base="https://a.test/", network=False)
        doc = seo_probe.to_audit(r)
        self.assertEqual(validate_json.check("audit-report", doc), [])
        self.assertEqual(doc["overall_status"], "critical")  # noindex is P0


class RankingsAndWhiteLabel(unittest.TestCase):
    def _audit(self):
        return json.loads((EX / "sample-audit.json").read_text(encoding="utf-8"))

    def test_rankings_render_and_validate(self):
        a = self._audit()
        self.assertTrue(a["rankings"], "sample must carry ranking rows")
        self.assertEqual(validate_json.check("audit-report", a), [])
        h = audit_report.build_html(a)
        self.assertIn("Ranking results", h)
        self.assertIn("not in top 20", h)
        self.assertIn("not guarantees", h)

    def test_ranking_row_needs_source_and_date(self):
        a = self._audit()
        a["rankings"].append({"keyword": "x", "position": 1})
        errs = " | ".join(validate_json.check("audit-report", a))
        self.assertIn("missing required 'source'", errs)
        a["rankings"][-1].update(source="GSC", date="2026-09-28", position=0)
        self.assertTrue(validate_json.check("audit-report", a), "position 0 is impossible")

    def test_white_label_removes_all_khseo_branding(self):
        import tempfile, zlib, re as _re
        a = self._audit()
        for kwargs in ({"white_label": True}, {"brand": "Acme SEO"}):
            br = audit_report.labels(**kwargs)
            h = audit_report.build_html(a, br)
            self.assertNotRegex(h.lower(), "khseo", kwargs)
            self.assertIn("No ranking, traffic", h, "disclaimer must survive white-labelling")
            self.assertIn("Not tested", h)
            with tempfile.TemporaryDirectory() as d:
                out = Path(d) / "r.pdf"
                audit_report.render(a, out, engine="builtin", **kwargs)
                data = out.read_bytes()
                text = b"".join(zlib.decompress(m) for m in _re.findall(rb"stream\n(.*?)\nendstream", data, _re.S))
                self.assertNotRegex(text.lower(), rb"khseo", kwargs)
        self.assertIn("Acme SEO", audit_report.build_html(a, audit_report.labels(brand="Acme SEO")))


class CaptureRendered(unittest.TestCase):
    def test_origin_is_never_reflected(self):
        """Regression (CodeQL py/http-response-splitting): client headers must not be echoed."""
        import http.client
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            url, done, srv = capture_rendered.serve_once(str(Path(d) / "x.html"), timeout=5)
            try:
                conn = http.client.HTTPConnection("127.0.0.1", srv.server_address[1], timeout=5)
                conn.request("OPTIONS", "/anything", headers={"Origin": "https://evil.example"})
                r = conn.getresponse()
                r.read()
                self.assertEqual(r.getheader("Access-Control-Allow-Origin"), "*")
                conn.close()
            finally:
                srv.shutdown()
                srv.server_close()

    def test_one_shot_receiver_roundtrip_and_token(self):
        import tempfile, urllib.request, urllib.error
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / "dom.html"
            url, done, srv = capture_rendered.serve_once(str(out), timeout=10)
            try:
                bad = url.rsplit("/", 1)[0] + "/wrong-token"
                with self.assertRaises(urllib.error.HTTPError) as cm:
                    urllib.request.urlopen(urllib.request.Request(bad, data=b"<html>x</html>", method="POST"), timeout=5)
                cm.exception.close()
                urllib.request.urlopen(urllib.request.Request(url, data=b"<html><title>ok</title></html>",
                                                              method="POST"), timeout=5).read()
                self.assertTrue(done.wait(5))
                self.assertIn(b"<title>ok</title>", out.read_bytes())
                with self.assertRaises(urllib.error.HTTPError) as cm:  # one-shot: second POST refused
                    urllib.request.urlopen(urllib.request.Request(url, data=b"again", method="POST"), timeout=5)
                cm.exception.close()
            finally:
                srv.shutdown()
            srv.server_close()
            self.assertTrue(url.startswith("http://127.0.0.1:"))


import meta_tags  # noqa: E402
import clean_text  # noqa: E402


class MetaTags(unittest.TestCase):
    def test_build_escapes_and_includes_social(self):
        h = meta_tags.build({"title": 'Tee "Best" <b>', "description": "x" * 150,
                             "url": "https://a.test/p", "image": "https://a.test/i.jpg", "type": "product",
                             "price": "24.99"})
        self.assertIn("&quot;Best&quot; &lt;b&gt;", h)
        for needle in ('rel="canonical"', 'og:image', 'twitter:card" content="summary_large_image',
                       'product:price:amount'):
            self.assertIn(needle, h)

    def test_grade_catches_real_problems(self):
        g = meta_tags.grade({"title": "W" * 60, "description": "short", "url": "/relative",
                             "robots": "noindex", "keywords": "a,b"})
        self.assertTrue(any("truncated" in w for w in g["warnings"]))
        self.assertTrue(any("absolute" in e for e in g["errors"]))
        self.assertTrue(any("noindex" in w for w in g["warnings"]))
        self.assertTrue(any("ignored by Google" in w for w in g["warnings"]))

    def test_check_reads_price_from_existing_page(self):
        """Regression (real data): og:price:amount on the page was reported as missing."""
        page = ('<html><head><title>Wired for Christmas Electrician T-Shirt | Shop</title>'
                '<meta property="og:type" content="product"><meta property="og:price:amount" content="24.99">'
                '<link rel="canonical" href="https://a.test/p"></head></html>')
        g = meta_tags.grade(meta_tags.extract(page))
        self.assertFalse(any("price" in m for m in g["missing"]), g)


class CleanText(unittest.TestCase):
    RAW = ("Sure! Here's the rewritten intro:\nOur tee\u200b is soft\u00a0and warm.\U000e0041 I hope this helps!\n"
           "© 2026 Example Co. All rights reserved.\n")

    def test_removes_hidden_characters_keeps_copyright(self):
        out, rep = clean_text.clean(self.RAW)
        self.assertNotIn("\u200b", out)
        self.assertNotIn("\U000e0041", out)
        self.assertEqual(rep["invisible_removed"], 2)
        self.assertIn("© 2026 Example Co. All rights reserved.", out, "copyright notices are never touched")

    def test_flags_once_and_strips_on_request(self):
        out, rep = clean_text.clean(self.RAW)
        self.assertEqual(len(rep["boilerplate"]), 2, rep["boilerplate"])
        self.assertIn("I hope this helps", out, "flag-only by default")
        out2, rep2 = clean_text.clean(self.RAW, strip_boilerplate=True)
        self.assertNotIn("I hope this helps", out2)
        self.assertNotIn("Here's the rewritten", out2)
        self.assertFalse(any(line.endswith(" ") for line in out2.splitlines()))


class BehaviorScenarios(unittest.TestCase):
    """Offline half of the agent-behavior contract: every scenario must be governed by real
    spec text, so the skill can't silently drop a rule a scenario depends on."""
    DATA = json.loads((ROOT / "tests" / "behavior" / "scenarios.json").read_text(encoding="utf-8"))

    def test_scenarios_are_well_formed(self):
        ids = [s["id"] for s in self.DATA["scenarios"]]
        self.assertEqual(len(ids), len(set(ids)), "duplicate scenario id")
        self.assertGreaterEqual(len(ids), 12)
        for s in self.DATA["scenarios"]:
            self.assertTrue(s["expect"]["must"], s["id"])
            for pat in s["expect"]["must"] + s["expect"].get("must_not", []):
                re.compile(pat)
                # a mangled escape (e.g. \b stored as a backspace) compiles but never matches
                self.assertFalse(any(ord(c) < 32 for c in pat), f"{s['id']}: control char in /{pat!r}/")

    def test_every_scenario_is_anchored_in_the_spec(self):
        missing = []
        for s in self.DATA["scenarios"]:
            for rel, phrase in s["spec"]:
                text = (ROOT / rel).read_text(encoding="utf-8")
                if phrase not in text:
                    missing.append(f"{s['id']}: '{phrase}' not in {rel}")
        self.assertEqual(missing, [], "\n".join(missing))

    def test_live_runner_checker(self):
        sys.path.insert(0, str(ROOT / "tests" / "behavior"))
        import run_live
        exp = {"must": ["secret detected"], "must_not": ["sk_live_\\w+"]}
        self.assertEqual(run_live.check("SECRET DETECTED in .env.production (value not shown)", exp), [])
        self.assertEqual(len(run_live.check("found sk_live_abc123", exp)), 2)
        vol = next(s for s in self.DATA["scenarios"] if s["id"] == "invented_search_volume")["expect"]
        self.assertTrue(run_live.check("nurse christmas shirt: 12,100 monthly searches", vol),
                        "invented volumes must be caught")


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

    # ---- v1.2.0: real-data fixes from the clasicoz.shop audit + external review ---------------
    SHELL = ('<!DOCTYPE html><html><head><meta charset="utf-8"><script src="/x.lib.js"></script>'
             '<script>window.rbzns={"seed":"abc"};</script></head><body></body></html>')

    def _shell_fetch(self):
        return {"error": None, "status": 200, "redirects": [], "body": self.SHELL, "headers": {},
                "final_url": "https://shop.example/p"}

    def test_challenge_page_suppresses_onpage_findings(self):
        """Real data: a Reblaze shell produced 10 false on-page findings (missing title, H1...)."""
        page = seo_probe.analyze_html(self.SHELL, "https://shop.example/p")
        f = seo_probe.build_findings(self._shell_fetch(), page, None, None)
        msgs = [x["message"] for x in f]
        self.assertEqual(f[0]["priority"], "P0")
        self.assertFalse(any(m.startswith(("Missing <title>", "No <h1>", "No viewport", "Missing meta"))
                             for m in msgs), msgs)
        self.assertTrue(any(x["label"] == "NOT TESTED" and "On-page SEO" in x["message"] for x in f))

    def test_rendered_snapshot_assessed_when_raw_is_challenged(self):
        raw = seo_probe.analyze_html(self.SHELL, "https://shop.example/p")
        ren = seo_probe.analyze_html((FIX / "good_page.html").read_text(encoding="utf-8"), "https://shop.example/p")
        f = seo_probe.compare_rendered(raw, ren, raw_blocked=True)
        self.assertIn("only after the JS challenge", f[0]["message"])

    def test_raw_vs_rendered_detects_js_only_seo(self):
        raw = seo_probe.analyze_html("<html lang=en><head><title>Shop</title></head><body><h1>x</h1></body></html>",
                                     "https://a.test/")
        ren = seo_probe.analyze_html((FIX / "good_page.html").read_text(encoding="utf-8"), "https://a.test/")
        msgs = " | ".join(x["message"] for x in seo_probe.compare_rendered(raw, ren, raw_blocked=False))
        for needle in ("Meta description present only after JavaScript", "Canonical present only after",
                       "Structured data added only by JavaScript", "Most visible text is rendered by JavaScript"):
            self.assertIn(needle, msgs)

    def test_rendered_cli_end_to_end(self):
        r = seo_probe.run(str(FIX / "bad_page.html"), base="https://a.test/", network=False,
                          rendered=str(FIX / "good_page.html"))
        self.assertIsNotNone(r["rendered_page"])
        self.assertNotIn("JavaScript rendering", r["not_tested"])
        self.assertIn("single page", r["scope"])
        self.assertIn("SCOPE: SINGLE PAGE PROBE", seo_probe.render_text(r))

    def test_crawler_registry_loads_and_falls_back(self):
        import tempfile, os
        search, ai, ver = seo_probe.load_crawler_registry()
        self.assertIn("Googlebot", search)
        self.assertIn("OAI-SearchBot", ai)
        self.assertNotEqual(ver, "built-in", "config/ai-crawlers.json should be used")
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
            fh.write("{not json")
        try:
            s2, a2, v2 = seo_probe.load_crawler_registry(Path(fh.name))
        finally:
            os.unlink(fh.name)
        self.assertEqual(v2, "built-in")
        self.assertIn("GPTBot", a2)

    def test_connect_time_pinning_refuses_private_ip(self):
        """DNS-rebinding guard: the IP actually connected to is validated, not just a pre-check."""
        with self.assertRaises(seo_probe.UnsafeURL):
            seo_probe._guarded_create_connection(False, ("127.0.0.1", 9), timeout=2)

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
            srv.server_close()
        self.assertTrue(r["page"]["title"].startswith("Classic Cotton Tee"))
        self.assertEqual(r["page"]["h1_count"], 1)
        self.assertEqual(r["robots"]["status"], 200)

    def test_json_output_serializable(self):
        r, _ = self._findings("bad_page.html")
        json.dumps(r, default=list)


class FreelancerGigSEO(unittest.TestCase):
    """Additive Mode G: the module exists, is routed and discoverable, and keeps the honesty rules."""
    GIG = ROOT / "workflows" / "gig.md"

    def test_module_covers_required_assets(self):
        text = self.GIG.read_text(encoding="utf-8").lower()
        for need in ("fiverr", "upwork", "freelancer.com", "title", "description", "tags", "skills",
                     "category", "packages", "faq", "profile", "portfolio", "competitor", "limit",
                     "intent", "ctr", "conversion"):
            self.assertIn(need, text, f"gig.md missing '{need}'")

    def test_module_keeps_honesty_rules(self):
        text = self.GIG.read_text(encoding="utf-8")
        for rule in ("Fake reviews", "keyword stuffing", "off-platform", "UNKNOWN", "never guaranteed",
                     "the editor wins"):
            self.assertIn(rule, text)

    def test_registered_and_discoverable(self):
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("G · Freelancer gig SEO", skill)
        self.assertIn("workflows/gig.md", skill)
        self.assertRegex(skill.split("---", 2)[1], r"Fiverr")  # frontmatter description triggers the skill
        cmds = (ROOT / "commands.md").read_text(encoding="utf-8")
        self.assertIn("### `KHSEO gig`", cmds)
        self.assertIn("  gig ", cmds.split("KHSEO: just type", 1)[1].split("Examples", 1)[0])
        self.assertIn("G Freelancer gig SEO", (ROOT / "adapters" / "system-prompt.md").read_text(encoding="utf-8"))
        self.assertIn("Freelancer Gig SEO", (ROOT / "README.md").read_text(encoding="utf-8"))

    def test_existing_modes_still_present(self):
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        for mode in ("A · Auditor", "B · Vibe coder", "C · Writer", "D · Social", "E · General user",
                     "F · Growth strategist"):
            self.assertIn(mode, skill)


class TokenEfficiency(unittest.TestCase):
    """Always-loaded instructions stay lean; heavy files tell agents to load only what they need."""

    def test_skill_md_token_budget(self):
        chars = len((ROOT / "SKILL.md").read_text(encoding="utf-8"))
        self.assertLess(chars // 4, 3000, f"SKILL.md ~{chars // 4} tokens; it loads on every call")

    def test_context_budget_rule_and_load_scopes(self):
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("**Context budget.**", skill)
        self.assertIn("Never drop a required rule", skill)
        self.assertIn("read only the `### KHSEO <cmd>` section",
                      (ROOT / "commands.md").read_text(encoding="utf-8"))
        self.assertIn("**Load scope:**", (ROOT / "rules" / "governance.md").read_text(encoding="utf-8"))

    def test_moved_tool_docs_still_reachable(self):
        docs = (ROOT / "scripts" / "README.md").read_text(encoding="utf-8")
        for script in ("seo_probe.py", "capture_rendered.py", "audit_report.py", "validate_json.py",
                       "meta_tags.py", "clean_text.py", "SINGLE PAGE PROBE", "Open and check the PDF"):
            self.assertIn(script, docs)

    def test_adapter_modes_match_skill_registry(self):
        """Drift guard: the adapter fell behind SKILL.md once (mode F). Any mode added to the
        SKILL.md registry must appear in the adapter with the same letter and name."""
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        adapter = (ROOT / "adapters" / "system-prompt.md").read_text(encoding="utf-8").lower()
        modes = re.findall(r"\*\*([A-Z]) · ([^*]+)\*\*", skill)
        self.assertGreaterEqual(len(modes), 7)
        for letter, name in modes:
            self.assertIn(f"{letter.lower()} {name.strip().lower()}", adapter, f"adapter missing mode {letter}")

    def test_mode_ranges_match_registry(self):
        """Drift guard: any 'modes A–X' range in commands.md/adapters must end at the registry's last mode."""
        last = re.findall(r"\*\*([A-Z]) · ", (ROOT / "SKILL.md").read_text(encoding="utf-8"))[-1]
        for f in [ROOT / "commands.md", *(ROOT / "adapters").glob("*.md")]:
            for m in re.finditer(r"modes? A[–-]([A-Z])", f.read_text(encoding="utf-8")):
                self.assertEqual(m.group(1), last, f"{f.name} says modes A–{m.group(1)}, registry ends at {last}")

    def test_adapter_routes_every_mode(self):
        a = (ROOT / "adapters" / "system-prompt.md").read_text(encoding="utf-8")
        for m in ("A Auditor", "B Vibe coder", "C Writer", "D Social", "E General user",
                  "F Growth strategist", "G Freelancer gig SEO", "keywords.md", "gig.md"):
            self.assertIn(m, a)


if __name__ == "__main__":
    unittest.main(verbosity=2)
