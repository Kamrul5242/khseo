# Keywords: short-tail, long-tail, intent, clusters

**Trigger:** `KHSEO keywords <topic|url|product>`, "find keywords", "what should I rank for".

## Data honesty (applies to keywords, competitors, ranking, off-page)

| Tier | Source | Label | Allowed numbers |
|---|---|---|---|
| 1 | Host SEO data tools: Search Console, GA4, Keyword Planner, DataForSEO/OpenSEO, Ahrefs, Semrush, Bing Webmaster (MCP/API) | `VERIFIED` (own-site data) / `OBSERVED` (third-party), with source + date + country/language | volume, difficulty, CPC, positions, clicks, as reported |
| 2 | Live SERP via the host's web search or browser | `OBSERVED` (location/personalization caveat) | positions seen, SERP features, competing URLs |
| 3 | Autocomplete, People Also Ask, related searches, forums, reviews, the user's own customer questions | `OBSERVED` | none (qualitative) |
| 4 | Model knowledge | `ESTIMATE` / `INFERRED` | **no numbers**: relative words only ("likely high competition") |

Never invent search volume, keyword difficulty, CPC, traffic, rankings or backlink counts. No
data tool → give the list with intent and priority, and mark metrics `UNKNOWN`.

## Steps
1. **Seed.** Take the topic from the user, their product/page, or the site's own categories. Ask
   market + language if they aren't obvious (label `ASSUMED` otherwise).
2. **Expand.**
   - **Short-tail (head)**: 1–2 words, broad, high competition (`christmas shirts`).
   - **Mid-tail**: 2–3 words, a clearer need (`funny christmas shirts`).
   - **Long-tail**: 4+ words or question form, specific, lower competition, higher conversion
     (`funny christmas shirt for electricians`, `what to gift an electrician for christmas`).
   - Sources: autocomplete, PAA, related searches, competitor titles/H2s (strategy only),
     product attributes (material, size, audience, occasion, profession), local modifiers,
     comparisons ("vs"), problem phrasing, and the user's customer questions.
3. **Classify intent**: informational · commercial investigation · transactional · navigational
   · local. The SERP decides intent: if the top 10 are product pages, a blog post won't rank.
4. **Score** each keyword on relevance to what the site actually sells/knows (1–3), business
   value (1–3), winnability (1–3: SERP dominated by giants vs. forums/small sites), plus volume
   and difficulty from a Tier 1 source when available.
5. **Cluster** by shared intent and SERP overlap (keywords whose top results share URLs belong
   on one page). One cluster = one page. Avoid cannibalization: never plan two pages for one cluster.
6. **Map** clusters to existing URLs or new pages; pick a primary keyword + secondaries for each.
7. **Prioritize quick wins**: long-tail + commercial intent + low competition + an existing
   page that can be improved. Head terms come later, through topical authority.

## Output: [templates/keyword-report.md](../templates/keyword-report.md)

## Rules
- Keyword density targets don't exist. Use the primary keyword in the title, H1, URL and first
  100 words, then cover the *topic* (entities, attributes, questions).
- Meta keywords are ignored by Google and Bing. Add them only if the user insists, and say so.
- No doorway pages (near-duplicate pages per city/keyword) and no keyword stuffing.
