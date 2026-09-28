# KHSEO Checklists (per layer)

Work top-down. A failure in an earlier layer usually outranks everything below it.

## 1. Crawlability (P0 territory)
- [ ] URL returns 200 (not 403/429/5xx) for a normal crawler UA; note redirect chain length (≤1 hop ideal)
- [ ] robots.txt reachable, not blocking the page, CSS/JS, or important sections; no `Disallow: /` left from staging
- [ ] No WAF/CAPTCHA/bot-challenge page served to crawlers (Cloudflare "Just a moment", Akamai, DataDome, hCaptcha)
- [ ] Main content present in raw HTML **or** reliably server-rendered; JS-only content flagged
- [ ] Internal links are real `<a href>` (not `onclick` / JS routing only)
- [ ] AI crawlers: decide deliberately on GPTBot, OAI-SearchBot, ChatGPT-User, ClaudeBot, Claude-SearchBot, PerplexityBot, Google-Extended, Applebot-Extended, CCBot — blocking some search/answer bots removes the site from those answers

## 2. Indexability
- [ ] No unintended `noindex` (meta robots or `X-Robots-Tag` header)
- [ ] Canonical present, absolute, self-referencing on the canonical version, not pointing to a redirect/404/noindexed URL
- [ ] One host + protocol (https, www vs apex consistent); HTTP → HTTPS 301
- [ ] XML sitemap exists, referenced in robots.txt, lists only 200 + indexable + canonical URLs, `lastmod` truthful
- [ ] Duplicate URL variants controlled (trailing slash, params, case, `?m=1`, session ids)
- [ ] Pagination crawlable with real links; faceted navigation not creating infinite URL space
- [ ] Soft 404s / thin placeholder pages identified

## 3. Technical
- [ ] Mobile viewport meta; responsive; no horizontal scroll; tap targets
- [ ] Core Web Vitals (LCP ≤ 2.5s, INP ≤ 200ms, CLS ≤ 0.1) — field data if available, else lab, label which
- [ ] Images: modern formats, width/height set, lazy-load below the fold only, LCP image not lazy
- [ ] `lang` attribute; hreflang pairs reciprocal with x-default when multi-language
- [ ] HTTPS, no mixed content; sensible security headers (don't weaken them for SEO)
- [ ] 404 page returns real 404 status; no orphan pages among important URLs

## 4. On-page
- [ ] Title: unique, intent-matching, primary topic early, ~50–60 chars (pixel-truncation, not a rule)
- [ ] Meta description: unique, benefit + specifics, ~140–160 chars (may be rewritten by engines)
- [ ] Exactly one clear H1; H2/H3 outline that mirrors the reader's questions
- [ ] Descriptive, short, lowercase, hyphenated slug; stable
- [ ] Alt text describes image meaning (decorative → empty alt)
- [ ] Descriptive anchor text; no "click here" for important links
- [ ] Freshness shown where it matters (updated date with real changes)
- [ ] Thin / duplicate / cannibalizing pages flagged

## 5. Entity & semantic
- [ ] Primary entity named explicitly and consistently (brand, product, person, org, place)
- [ ] Organization / Person / Product schema with `sameAs` to real profiles
- [ ] About, contact, policies pages reachable and consistent (NAP identical everywhere for local)
- [ ] Topic map: subtopics, related entities, questions, comparisons, use cases, attributes covered
- [ ] Consistent terminology — the same thing isn't called three names

## 6. AEO (answer engines)
- [ ] Each key question has a heading phrased as the question + a 40–60 word direct answer right below
- [ ] Definitions ("X is …") stated plainly in the first sentence
- [ ] Steps as ordered lists; comparisons as tables; specs as definition lists/tables
- [ ] FAQ block only with real questions users ask; FAQPage schema only where eligible (Google shows FAQ rich results for a narrow set of sites — markup still helps parsers)

## 7. GEO / LLM readability
- [ ] Self-contained passages: each section makes sense if extracted alone
- [ ] Concrete facts with units, dates, sources; first-party data called out as such
- [ ] Claims attributable (author, date, organization visible)
- [ ] No contradictions between pages, schema and profiles
- [ ] Optional `llms.txt` / Markdown mirror for docs-heavy sites — treat as a low-cost experiment, not a ranking factor

## 8. E-E-A-T & trust
- [ ] Real author bylines with bios and relevant experience; reviewer for YMYL topics
- [ ] Business identity: legal name, address, contact, policies (returns, shipping, privacy, terms)
- [ ] Sources cited for non-obvious claims; original photos where experience is claimed
- [ ] Genuine reviews only; no incentivized/fabricated testimonials

## 9. Information gain
- [ ] Something here that the top results don't have (data, test, case, template, local detail, expert quote, better diagram)
- [ ] If not — list specific, feasible additions the user can actually produce

## 10. Structured data
- [ ] Valid JSON-LD (parses), correct `@type`, required properties present
- [ ] Matches visible content exactly (price, availability, rating, author, dates)
- [ ] No duplicate conflicting blocks from theme + plugin
- [ ] Types used appropriately: Organization, WebSite, WebPage, BreadcrumbList, Product+Offer, Review/AggregateRating (genuine only), Article/BlogPosting, Person, LocalBusiness, FAQPage (eligible only), HowTo (no rich result, still descriptive), VideoObject

## 11. Internal linking
- [ ] Important pages ≤ 3 clicks from home
- [ ] Hub/cluster structure: pillar ↔ supporting articles linked both ways
- [ ] Contextual links in body copy, not only nav/footer
- [ ] No broken internal links; no links to redirected URLs

## 12. Reputation & zero-click
- [ ] Brand SERP: knowledge panel signals, consistent profiles, reviews on third-party platforms
- [ ] Google Business Profile for local businesses (categories, hours, photos, Q&A)
- [ ] Mentions/citations on relevant, reputable sites (earned, not bought)
- [ ] Zero-click value: answers, tables, and brand name visible in the snippet itself

## 13. AI-search readiness summary
Score as a short table, not a fake number:

| Area | Status | Evidence |
|---|---|---|
| AI crawlers allowed | Yes / Partial / No | robots.txt lines |
| Content in raw HTML | Yes / Partial / No | probe word count vs rendered |
| Extractable answers | Strong / Weak | # of Q→A sections |
| Entity clarity | Strong / Weak | schema + about page |
| Attributable facts | Strong / Weak | bylines, dates, sources |
