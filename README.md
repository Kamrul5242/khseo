# KHSEO — Universal SEO + AI Search + Content Skill

[![tests](https://github.com/Kamrul5242/khseo/actions/workflows/tests.yml/badge.svg)](https://github.com/Kamrul5242/khseo/actions/workflows/tests.yml)
[![codeql](https://github.com/Kamrul5242/khseo/actions/workflows/codeql.yml/badge.svg)](https://github.com/Kamrul5242/khseo/actions/workflows/codeql.yml)
![license](https://img.shields.io/badge/license-MIT-blue)

**KHSEO** (Kamrul Hasan SEO) is one skill for auditing, fixing, writing and optimizing the modern
web for both humans and search/AI systems. You type `KHSEO` and say what you want in plain
language. It works out whether you need an auditor, a coding agent, a writer, or a social media
editor.

**What it is:** a model-agnostic, host-adaptable AI skill (rules, workflows, output contracts,
governance) plus a security-conscious single-page crawler-view probe and a PDF audit reporter.
**What it isn't:** a full-site crawler, rank tracker or backlink tool. It doesn't replace
Screaming Frog, Ahrefs or Search Console, and it says so in every report.

```text
KHSEO audit my website https://example.com
KHSEO fix the SEO problems in this Next.js project
KHSEO write a 2000-word blog about electric cars for first-time buyers in the UK
KHSEO humanize this article and improve its SEO
KHSEO turn this blog into Facebook, LinkedIn and Instagram posts
KHSEO check whether my site is ready for AI search
KHSEO make my website better for Google and AI        ← no SEO knowledge needed
```

## Commands

`KHSEO` + plain language is all you need. Advanced users can use optional control commands.
Full behavior is in [commands.md](commands.md).

| Command | Purpose | Changes files? |
|---|---|---|
| `KHSEO` | universal: detects what you want | depends |
| `KHSEO audit` | audit/analyze | no |
| `KHSEO fix` | find and apply fixes (risky ones ask first) | yes |
| `KHSEO write` | create SEO / website / social content | drafts |
| `KHSEO optimize` | improve existing content, page, site, or code | yes |
| `KHSEO build` | build SEO features into a project | yes |
| `KHSEO verify` | validate what's actually implemented | no |
| `KHSEO research` | sourced research | no |
| `KHSEO plan` | implementation plan | no |
| `KHSEO dry-run` | show exact proposed changes | no |
| `KHSEO status` | task, tools, risk, approval, progress | no |
| `KHSEO approve` / `reject` | decide on a pending risky action | — |
| `KHSEO rollback` | undo KHSEO's own recent changes | reverts |
| `KHSEO stop` | emergency stop | stops |
| `KHSEO help` | compact command card | no |
| `KHSEO keywords` | short-tail, mid-tail, long-tail keywords, intent, clusters | no |
| `KHSEO competitors` | who ranks, why, and how to outrank them with original work | no |
| `KHSEO rank` | ranking result + plan to reach page 1 / top 3 (a target, never a promise) | no |
| `KHSEO offpage` | backlinks, digital PR, citations, reviews (outreach as drafts) | no |
| `KHSEO meta` | write + grade title, description, canonical, OG and Twitter tags | drafts |
| `KHSEO schema` | truthful JSON-LD structured data | drafts |
| `KHSEO aeo` / `KHSEO trust` | AEO/GEO/LLM readiness / E-E-A-T and trust | no |
| `KHSEO social` | platform-native posts | drafts |
| `KHSEO clean` | remove hidden AI artifacts from your own text | returns text |
| `KHSEO report` | PDF report, optionally white-label or with your agency brand | creates files |
| `KHSEO gig` | Fiverr / Upwork / Freelancer.com gig and profile SEO | drafts |

## What it covers

| Area | Includes |
|---|---|
| **Technical SEO** | crawlability, indexability, robots.txt, sitemaps, canonicals, redirects, status codes, JS rendering, bot/WAF challenges, mobile, Core Web Vitals, hreflang |
| **On-page & semantic** | titles, descriptions, headings, intent matching, topic maps, entities, internal links, thin/duplicate content |
| **AEO / GEO / LLM** | question → direct-answer structure, extractable passages, entity clarity, attributable facts, AI-crawler access (GPTBot, ClaudeBot, PerplexityBot, Google-Extended…) |
| **Trust** | E-E-A-T signals, Information Gain test, reputation, genuine reviews only |
| **Structured data** | Organization, WebSite, Product/Offer, BreadcrumbList, Article, LocalBusiness, FAQPage — only when true and visible |
| **Content** | blogs, guides, product & category copy, landing/service/about pages, rewrites, humanizing, FAQs, newsletters |
| **Social** | platform-native posts for Facebook, Instagram, LinkedIn, X, Threads, TikTok, YouTube, Pinterest |
| **Freelancer Gig SEO** | Fiverr, Upwork, Freelancer.com and other marketplaces: gig/service titles and descriptions, tags/skills, category, packages, FAQ, profile and portfolio SEO, competitor gigs, platform character limits |
| **Vibe coding** | detects Next.js, Nuxt, Astro, SvelteKit, React/Vue SPAs, Laravel, Django, WordPress, Shopify, Blogger, static HTML — then plans, implements, and validates the smallest safe fix |

## How it behaves

- **Crawlability first** — a blocked or JS-only page outranks every copywriting tip.
- **Evidence labels** — every finding is `VERIFIED`, `OBSERVED`, `INFERRED`, `RECOMMENDED`,
  `ASSUMED`, `UNKNOWN` or `NOT TESTED`. It never claims a crawl, build or deploy it didn't do.
- **Priority × Risk** — P0–P3 says how urgent, R0–R4 says how careful. Priority is never
  permission: risky fixes (robots, mass redirects, URL changes, deploys, deletes) need your
  approval, with backup and rollback planned first.
- **No fabrication** — no invented stats, sources, reviews, credentials, prices or product
  details. Missing facts become `[ADD: …]` placeholders.
- **No manipulation** — no keyword stuffing, hidden text, fake schema, copied competitors, or
  ranking/AI-citation guarantees.
- **Proportional** — a quick question gets a quick answer; a full audit gets a full report.

## Core vs host

```text
KHSEO CORE  = intelligence: rules, workflows, risk + approval model, output contracts, schemas
HOST        = the AI + its tools: model, filesystem, terminal, browser, git, search, deploy
ADAPTER     = how a given host loads the core (adapters/)
```

The core behaves the same everywhere. What it can *do* depends on the host. KHSEO starts every
tool-dependent task with a **capability handshake** and reports anything it can't do as
`NOT TESTED`. Rollback, backups and change journals are **protocols**: in Claude Code with git they
are real, while in a chat-only host KHSEO can only give you the change and say it can't roll back.
It's model-agnostic, not "identical on every AI".

## Install

**Claude Code**
```bash
git clone https://github.com/Kamrul5242/khseo.git ~/.claude/skills/khseo
```
(or into `.claude/skills/khseo` inside a project). Then just type `KHSEO …`.

**Claude.ai / Claude Desktop** — download the repo as ZIP → Settings → Capabilities → Skills → upload.

**ChatGPT, Gemini, Cursor, Copilot, Codex, DeepSeek, local LLMs** — see
[adapters/README.md](adapters/README.md). The core is provider-neutral; the adapters just
explain how to load it.

## The probe tool

A stdlib-only Python script (no installs) that checks one page the way a crawler sees it:

```bash
python scripts/seo_probe.py https://example.com/            # readable report
python scripts/seo_probe.py https://example.com/ --json     # machine-readable
python scripts/seo_probe.py dist/index.html --base https://example.com/   # built file
```

It reports status and redirects, `X-Robots-Tag`, bot-challenge pages (Cloudflare, Reblaze,
Incapsula, DataDome…), robots.txt rules for search and AI crawlers, sitemap reachability,
title/description/canonical/robots meta, H1–H3, image alt coverage, links, JSON-LD validity and
types, Open Graph, and raw-HTML word count. It's honest about limits: it lists what it did
**not** test (JS rendering, Core Web Vitals, index coverage, other pages).

robots.txt is evaluated with Google's rules (RFC 9309): exact user-agent tokens, longest match
wins, `Allow` wins ties, `*` and `$` wildcards. Python's built-in `robotparser` uses first-match,
which can report a false "blocked".

**Safe by default.** It only fetches `http(s)`. It refuses redirects and robots.txt `Sitemap:`
lines that point into private or internal networks, such as cloud metadata at `169.254.169.254`
(SSRF guard). The IP it validates is the IP it connects to (DNS-pinned, so DNS rebinding can't swap addresses between check and connect), and proxy env vars are ignored for the same reason. A local dev server works when you target it directly. It caps decompressed
responses at 10 MB (gzip-bomb guard) and strips terminal control sequences from page text.
All page-derived output is untrusted data.

## PDF audit reports

```bash
python scripts/seo_probe.py https://example.com/ --audit-json > audit.json   # or write a full audit JSON
python scripts/validate_json.py audit-report audit.json                     # schema + honesty lint
python scripts/audit_report.py audit.json -o example-seo-audit.pdf          # PDF + HTML
```

The report includes a cover with status, the executive summary, priority counts, findings (each
with priority, evidence label, layer, evidence, fix, fix risk and owner), the action plan,
AI-search readiness, what KHSEO can do next, uncertainties, scope and host capabilities, what
was **not tested**, and a no-guarantees disclaimer. It uses a local Chrome/Edge/Chromium when
available and a built-in stdlib PDF writer otherwise (`--engine builtin`). Dishonest input is
refused: a `VERIFIED` claim about something listed as not tested, or `PASSED` without evidence.
A sample report comes from [examples/json/sample-audit.json](examples/json/sample-audit.json).

White-label: `--white-label` removes KHSEO branding and `--brand "Your Agency"` puts your name
on it. The disclaimer and "Not tested" list always stay. Reports can include a **Ranking results**
table (`rankings[]`: keyword, position or "not in top N", source, location, device, date).

## Growth tools

```bash
python scripts/meta_tags.py --title "..." --description "..." --url https://site/p --image https://site/i.jpg
python scripts/meta_tags.py --check page.html        # grade existing tags (SERP pixel widths, canonical, noindex)
python scripts/clean_text.py draft.md -o clean.md --strip-boilerplate   # your own text only
```

Keyword, competitor, ranking and off-page work follows
[workflows/keywords.md](workflows/keywords.md), [competitors.md](workflows/competitors.md),
[ranking.md](workflows/ranking.md) and [offpage.md](workflows/offpage.md). KHSEO copies
strategies but never content, treats top 3 as a target rather than a promise, and shows metrics
only when they come from a real data source.

## Governance as data

[schemas/](schemas/) holds machine-readable contracts for `audit-report`, `approval`,
`change-set`, `validation` and `capabilities`, with examples in [examples/json/](examples/json/).
`scripts/validate_json.py` checks them with no dependencies.

## Repository layout

```text
khseo/
├── SKILL.md                 entry point: mode detection, execution loop, risk matrix
├── commands.md              optional control commands + help card
├── rules/
│   ├── core-rules.md        universal rules, evidence labels, writing & source rules, privacy
│   ├── governance.md        approvals, conflicts, backups, rollback, deploy & DB gates
│   └── seo-checklists.md    13-layer checklists (crawlability → AI-search readiness)
├── workflows/               audit · code · content · social · general-user
├── templates/               audit report, writing package, rewrite, social, code report,
│                            approval/assumption formats, JSON-LD snippets
├── schemas/                 audit-report, approval, change-set, validation, capabilities
├── scripts/
│   ├── seo_probe.py         single-page crawler-view probe (raw vs rendered, --audit-json)
│   ├── capture_rendered.py  one-shot receiver for a rendered DOM from a real browser
│   ├── audit_report.py      audit JSON -> HTML + PDF report
│   ├── validate_json.py     schema validator + honesty lint
│   ├── meta_tags.py         build + grade meta tags
│   └── clean_text.py        strip hidden AI artifacts from your own text
├── config/ai-crawlers.json  crawler registry (update without code changes)
├── adapters/                ChatGPT / Gemini / Cursor / Copilot / AGENTS.md / generic prompt
├── examples/                request → behavior walkthroughs
├── tests/run_tests.py       offline test suite (stdlib unittest)
├── tests/behavior/          agent-behavior scenarios + live runner
└── CHANGELOG.md
```

## Test

```bash
python tests/run_tests.py
```

The offline suite covers the skill structure and links, every JSON contract and the honesty
lint, the probe (including RFC 9309 robots, SSRF/DNS-pinning, gzip-bomb, challenge pages and
raw-vs-rendered), both PDF engines, HTML escaping, and the agent-behavior scenarios' spec anchors.

**Offline contract tests ≠ live agent tests.** CI runs only the offline suite: it proves every
behavior scenario is governed by real spec text, but it doesn't call an LLM, so a green badge
means the contract is intact, not that a model obeyed it. See
[tests/behavior/README.md](tests/behavior/README.md).

Live agent-behavior check (manual; costs model calls; needs a host with KHSEO installed):

```bash
python tests/behavior/run_live.py --cmd "claude -p"
```

## Philosophy

> Think broadly, act precisely, change minimally, verify honestly, ask before consequential
> actions, recover when possible, and always keep the user in control.

## Versions, releases & security

- Versions: [VERSION](VERSION) (package), plus spec, schema and probe versions shown in every
  probe output and report. Policy: [RELEASING.md](RELEASING.md). History: [CHANGELOG.md](CHANGELOG.md).
- Security: [SECURITY.md](SECURITY.md). CI runs the offline tests, CodeQL, dependency review
  and OpenSSF Scorecard, with every action pinned to a commit SHA.

## Related projects

- **[KHSEO WordPress](https://github.com/Kamrul5242/khseo-wordpress)**: a WordPress plugin that
  implements this specification natively, and works without an AI API. It is a separate repository;
  this repo stays the model-neutral specification and contains no WordPress code.

## License

MIT © Kamrul Hasan
