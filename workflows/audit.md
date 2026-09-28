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
4. **Rendering check (raw vs rendered).** Most AI crawlers and link-preview bots don't run
   JavaScript, so compare what the server sends with what a browser shows:
   - Browser tool available → open the page, then either run
     `scripts/capture_rendered.py dom.html` and execute the printed snippet in the tab, or, if the
     host browser blocks loopback requests, return a compacted `document.documentElement.outerHTML`
     (scripts except JSON-LD, styles and SVG removed) and save it. Then
     `seo_probe.py URL --rendered dom.html`.
   - If the probe got a **challenge page**, it reports on-page SEO as `NOT TESTED` rather than
     describing the shield. Assess on-page SEO from the rendered DOM and label it `[rendered]`.
   - Headless browsers are often challenged too. Don't treat a headless result as proof of what
     crawlers get.
   - No browser → JavaScript rendering is `NOT TESTED`. Say so.
   - Large gap (titles, canonicals, schema or body text only after JS) → P1, or P0 if the
     product/article body is missing entirely.
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
10. **PDF report** when the user asks for a PDF or a shareable report, or the depth is Full:
    - write the audit JSON (every finding with layer, priority, label, evidence; `not_tested`
      filled honestly). `seo_probe.py URL --audit-json` gives a single-page starting point to
      enrich;
    - `python scripts/validate_json.py audit-report audit.json` must print `VALID`;
    - `python scripts/audit_report.py audit.json -o <site>-seo-audit.pdf`;
    - **open the PDF and look at it** (layout, page breaks, nothing truncated) before handing it
      over, and tell the user which engine produced it (browser or built-in).
