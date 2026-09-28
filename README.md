# KHSEO — Universal SEO + AI Search + Content Skill

[![tests](https://github.com/Kamrul5242/khseo/actions/workflows/tests.yml/badge.svg)](https://github.com/Kamrul5242/khseo/actions/workflows/tests.yml)
![license](https://img.shields.io/badge/license-MIT-blue)

**KHSEO** (Kamrul Hasan SEO) is one skill for auditing, fixing, writing and optimizing the modern
web for both humans and search/AI systems. You type `KHSEO` and say what you want in plain
language. It works out whether you need an auditor, a coding agent, a writer, or a social media
editor.

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
(SSRF guard); a local dev server works when you target it directly. It caps decompressed
responses at 10 MB (gzip-bomb guard) and strips terminal control sequences from page text.
All page-derived output is untrusted data.

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
├── schemas/                 audit-report.schema.json (machine-readable audits)
├── scripts/seo_probe.py     single-page crawler-view probe
├── adapters/                ChatGPT / Gemini / Cursor / Copilot / AGENTS.md / generic prompt
├── examples/                request → behavior walkthroughs
└── tests/run_tests.py       package + probe self-tests (stdlib unittest)
```

## Test

```bash
python tests/run_tests.py
```

Checks the skill structure and frontmatter, that every relative link resolves, that all JSON and
JSON-LD snippets parse, and runs the probe against fixtures — including regressions for
gzip-encoded responses and JS challenge shells.

## Philosophy

> Think broadly, act precisely, change minimally, verify honestly, ask before consequential
> actions, recover when possible, and always keep the user in control.

## License

MIT © Kamrul Hasan
