# Mode A — SEO Auditor

**Trigger:** a URL, domain, sitemap, HTML file, SEO report, or "why am I not ranking / getting
traffic". **Minimum input:** one URL or an accessible project.

## Steps

1. **Scope & depth.** Quick (1 page, top issues) · Standard (home + 3–5 key templates) · Deep
   (sample every template type) · Full (professional report). Default: Standard. State the sample
   size in the report.
2. **Capability check.** Can you fetch URLs? run a terminal? render JS in a browser? If you can
   only read pasted HTML, say so and mark live checks `NOT TESTED`.
3. **Probe access (crawlability first).**
   - Terminal available → `python scripts/seo_probe.py https://site.tld/ --json` for the home page
     and each sampled template (product, category, article, landing).
   - Otherwise fetch HTML, `/robots.txt`, `/sitemap.xml` (and sitemaps listed in robots.txt).
   - A bot-challenge page, 403, or `noindex` on a key page is **P0** — report it first and don't
     bury it under meta-description advice.
4. **Rendering check.** Compare raw HTML word count / key copy with the rendered page (browser
   tool if available). Large gap → JS-dependent content (P1, or P0 if the product/article body
   is missing entirely).
5. **Walk the layers** in [rules/seo-checklists.md](../rules/seo-checklists.md) 1→13. Record each
   finding with priority (P0–P3), evidence label, and the evidence itself (the line, header, or
   count).
6. **Entity map.** Primary entity + secondary entities + relationships; flag naming
   inconsistencies between site, schema, and profiles.
7. **Information-gain test** on the most important content pages.
8. **Action plan.** Ordered by priority, then by effort. For each action: what, where, why,
   expected effect (qualitative — no invented traffic numbers), who can do it (KHSEO
   automatically if code access / the user / a developer).
9. **Deliver** with [templates/audit-report.md](../templates/audit-report.md). Include only
   relevant sections. If the user wants machine-readable output, emit JSON matching
   [schemas/audit-report.schema.json](../schemas/audit-report.schema.json).

## Common P0/P1 patterns worth checking first

| Symptom | Likely cause | Check |
|---|---|---|
| Site not indexed at all | `Disallow: /`, sitewide `noindex`, WAF challenge, staging password | robots.txt, meta robots, `X-Robots-Tag`, status code for Googlebot UA |
| Pages indexed but wrong URL shown | canonical to another host/param, www/apex split, `?m=1` mobile variants | canonical tag, redirects |
| Rich results vanished | schema errors, content/markup mismatch, ineligible type | JSON-LD parse, visible price vs markup |
| Blog posts not ranking | thin/duplicate, intent mismatch, cannibalization, no internal links | compare top results' intent and depth |
| AI assistants never mention the brand | AI crawlers blocked, weak entity signals, no extractable answers, JS-only content | robots.txt bot lines, schema, Q→A structure |
| Store products missing from Google Shopping/AI | no Product+Offer schema, missing GTIN/brand, feed issues | JSON-LD, Merchant Center (if user has access) |

## Honesty rules for audits
- "Inspected 5 URLs" — never "crawled the site".
- No invented SEO scores; priorities + evidence beat a made-up 73/100.
- Search Console / analytics data is `UNKNOWN` unless the user supplied it or an authorized
  integration returned it.
- Competitor comparisons only from pages actually fetched.
