# Changelog

Newest first. Format and version rules: [RELEASING.md](RELEASING.md).

## 1.4.1 — 2026-10-07   (spec 1.4, schema 1.1)

### Fixed
- README no longer hard-codes a stale test count ("59").
- `examples/README.md`: added a Mode G (Freelancer gig) worked example.
- `tests/run_tests.py`: the `clean_text` fixture's invisible characters are written as `\u200b` /
  `\u00a0` escapes (same runtime strings), so watermark scanners stop flagging the source.

### Security
- Raw invisible, bidirectional-control and odd-space characters in `clean_text.py` (its detection
  regex) and `audit_report.py` (transliteration table) are now escape sequences, with identical
  compiled behavior. Raw bidi controls in source risk "Trojan Source" (CVE-2021-42574), and an editor
  or cleaner stripping them would have silently disabled zero-width detection. A new test rejects
  any such raw character in repo source.

## 1.4.0 — 2026-10-07   (spec 1.4, schema 1.1)

Freelancer Gig SEO, token efficiency, and a capability router. No change to existing SEO logic,
governance semantics or security behavior.

### Added
- **Freelancer Gig SEO (Mode G, `KHSEO gig`)** for Fiverr, Upwork, Freelancer.com and other
  marketplaces, in `workflows/gig.md`: gig/service title and description, tags/skills, category,
  packages, FAQ, profile and portfolio SEO, competitor-gig analysis, and platform character limits
  (last-known values; the live editor wins). Additive only, with existing modes and commands unchanged.

### Changed (token efficiency, no rule removed)
- `SKILL.md` (loaded on every call): ~3,830 → ~2,590 tokens (−33%). The command table became a
  grouped list (behavior stays in `commands.md`), tool docs moved to `scripts/README.md`, and a
  **Context budget** rule was added (accuracy-first priority order; load only the mode's files;
  never drop a rule, check or evidence to save tokens).
- `commands.md`: agents read only the command's own section (−67% when using a command).
- `rules/governance.md`: load scope §0–2 by default, §3+ only for R3/R4, approvals, rollback, DB or
  deploy (−36% on routine code fixes).
- `adapters/system-prompt.md`: now routes Mode F (and its workflows), which was missing, plus a
  load-only-what's-needed line.
- Tests: SKILL.md token budget (<3,000), load-scope notes, moved tool docs, adapter mode coverage.
- **Capability router**: SKILL.md §1 is now the single capability registry
  (`intent → capability → sub-capability → module + named rules → validate → output`), and
  adapters defer to it. A drift-guard test fails if a mode is added to SKILL.md but not the adapter.
- Context budget also covers sending external AI only what's needed and preferring structured data.

## 1.3.1 — 2026-09-28   (spec 1.3, schema 1.1)

Open-source hardening from an external review. No change to SEO logic or governance semantics.

### Security
- CI: all GitHub Actions pinned to full commit SHAs (resolved from the upstream tags), with a
  test that fails on any unpinned `uses:`. Dependabot keeps the pins current.
- CodeQL code scanning (`security-extended`, Python + GitHub Actions) on push, PR and weekly.
- Dependency review on pull requests; weekly OpenSSF Scorecard.
- `persist-credentials: false` on every checkout; least-privilege permissions per job.
- `SECURITY.md` with the reporting process and scope.
- **Fixed (found by the new CodeQL scan):** `capture_rendered.py` reflected the request's
  `Origin` header into `Access-Control-Allow-Origin` on every OPTIONS request, even without the
  token (response-splitting / permissive-CORS risk). It now always sends `*`, with a regression test.
- Private vulnerability reporting enabled on the repository.

### Added
- Canonical `VERSION` file and `scripts/khseo_version.py` (KHSEO, spec, schema versions); every
  schema carries `x-khseo-schema-version`. Probe output, audit JSON (`versions`), PDF reports
  and `KHSEO status` show them. Consistency tests tie VERSION, CHANGELOG, report engine and
  schemas together.
- `RELEASING.md`: semantic versioning that treats loosened governance as a breaking change.
- `tests/behavior/README.md`: offline contract tests vs live agent-behavior tests.

### Changed
- Probe component 1.2.1 (adds the `VERSIONS` line). CI job renamed "offline contract tests".

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
