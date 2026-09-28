# Changelog

## 1.3.0 — 2026-09-28

### Added
- **Growth commands**: `keywords` (short/mid/long-tail, intent, clusters), `competitors` (SERP
  competitors, strategy reverse-engineering, gap analysis), `rank` (ranking result + top-3
  plan across technical, content, meta, schema, AEO/GEO, trust, internal links, off-page and
  social), `offpage` (earned authority, outreach as drafts), `meta`, `schema`, `aeo`, `trust`,
  `social`, `clean`, `report`, all with workflows, templates and a grouped help card.
- `scripts/meta_tags.py`: builds escaped SEO/social tags and grades them (SERP pixel width,
  canonical, noindex, product price). `--check` grades an existing page.
- `scripts/clean_text.py`: removes invisible watermark/injection characters and chatbot
  boilerplate from the user's own text. Copyright notices are never touched.
- Reports: `rankings[]` (schema + PDF table), `--brand` and `--white-label`.
- 5 new behavior scenarios: no copying competitor content, no ranking guarantees, no removing
  third-party copyright, white-label allowed, no invented search volumes.

### Fixed (found while testing on real pages)
- `meta_tags --check` missed `og:price:amount` and reported the price as missing.
- `clean_text` flagged overlapping boilerplate twice and left trailing spaces.
- White-label reports still showed "owner: khseo"; ranking targets wrapped mid-word.
- The help card didn't list `help`. A scenario regex had `\b` stored as a backspace (it
  compiled but never matched), so a guard test now rejects control characters in patterns.

## 1.2.0 — 2026-09-28

Driven by a real audit (a store behind a Reblaze bot shield) and an external repository review.

### Fixed (found with real data)
- **Challenge pages were audited as if they were the site.** A 509-byte bot-challenge shell
  produced 10 false on-page findings (missing title, H1, viewport…). On-page SEO is now reported
  as `NOT TESTED` when the probe receives a challenge, and assessed from a rendered DOM instead.
- Challenged sitemaps are named as such ("bot-challenge page, not XML").
- `capture_rendered.py` rejected clients without draining the body, which aborted the connection on Windows.

### Added
- **PDF audit reports**: `scripts/audit_report.py` (audit JSON → HTML + PDF) using a local
  Chromium-family browser or a built-in stdlib PDF writer. Escapes all page-derived text, adds
  a CSP, and refuses invalid or dishonest input.
- `seo_probe.py --rendered FILE`: raw-vs-rendered comparison (JS-only titles, canonicals,
  schema, text). `--audit-json` feeds the PDF reporter.
- `scripts/capture_rendered.py`: one-shot, loopback-only, token-protected receiver for a
  rendered DOM from a real browser (bot shields often block headless browsers too).
- Governance schemas: `approval`, `change-set`, `validation`, `capabilities`, plus
  `scripts/validate_json.py` (stdlib validator) with an **honesty lint**: `PASSED` needs method
  + evidence, a check needing an unavailable capability must be `NOT_VERIFIED`, and `VERIFIED`
  claims about untested areas are rejected.
- `config/ai-crawlers.json` crawler registry (update tokens without code changes).
- Agent-behavior scenarios (`tests/behavior/`): 15 scenarios anchored to spec text (offline)
  plus `run_live.py` to test a real host + skill.

### Changed
- **One canonical risk rule** (`rules/governance.md §0`). R2 means *show and wait for
  authorization*; a generic "fix everything" authorizes R0–R1 only. All other files now defer to it.
- Mandatory **capability handshake** and explicit **core vs host** model: rollback, backups and
  deploy gates are protocols that depend on the host's tools.
- Probe hardening: **DNS-pinned connections** (the validated IP is the one connected to;
  defeats DNS rebinding), proxy env vars ignored, and a `SINGLE PAGE PROBE` scope banner in
  every report.
- Positioning: "model-agnostic, host-adaptable skill + single-page probe", not a full crawler.

## 1.1.0 — 2026-09-28
- Security: SSRF guards (http(s) only, no private-network pivots via redirects or robots
  `Sitemap:`), gzip-bomb cap, terminal-escape stripping, prompt-injection rules, least-privilege CI.
- Correctness: RFC 9309 robots.txt evaluation, `<svg><title>` miscount, reCAPTCHA false P0,
  bad-charset crash, missing-file traceback, uppercase scheme.
- Command system (`commands.md`).

## 1.0.0 — 2026-09-28
- Initial skill: mode detection, rules, workflows, templates, audit schema, adapters, probe, tests.
