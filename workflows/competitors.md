# Competitors: find them, reverse-engineer their strategy, beat it

**Trigger:** `KHSEO competitors <keyword|url>`, "who ranks above me", "copy what they do".

> **Adopt strategies, never content.** KHSEO studies *why* competitors rank (intent fit, depth,
> structure, entities, schema, links, speed, trust) and builds something **better and
> original**. It never copies, spins or lightly rewrites their text, images or data. That is
> plagiarism and copyright infringement, and duplicate content doesn't outrank the original anyway.

## 1. Find the real search competitors
- For each target keyword: the top 10 organic results for the user's market (Tier 1 SERP data
  tool, else live SERP via web search/browser, labelled with location and date).
- Separate **business competitors** (sell the same thing) from **SERP competitors** (whoever
  ranks: marketplaces, publishers, forums, Reddit, YouTube). You compete with the second group
  for clicks.
- Note SERP features: shopping/product grids, PAA, featured snippet, video, local pack, AI
  Overview, and who owns them.

## 2. Analyze each top result (only what you actually fetched)
| Dimension | What to record |
|---|---|
| Page type & intent | product / category / guide / listicle / tool / video, and whether it matches the query intent |
| Title & meta | pattern, primary keyword placement, hooks (price, year, number) |
| Content | depth (sections, words), unique elements (tables, calculators, photos, data), freshness |
| Structure | H2/H3 outline as *question coverage* (not text to copy) |
| Entities & topics | concepts, attributes and related entities covered that we don't |
| Structured data | types present (Product, Review, FAQ, HowTo, Article…) |
| E-E-A-T | author, first-hand evidence, reviews, brand signals |
| Technical | indexable, fast, mobile, rendered vs raw content (`seo_probe.py`) |
| Off-page (Tier 1 only) | referring domains, notable links, brand mentions |

## 3. Gap analysis
- **Content gap**: questions, subtopics, entities and formats they cover and we don't.
- **Keyword gap** (Tier 1): terms they rank for that we don't.
- **Link gap** (Tier 1): domains linking to several competitors but not to us.
- **Experience gap**: what we can offer that they can't (own photos, real specs, local knowledge,
  customer data). This is the information-gain lever.

## 4. Strategy to outrank (the "10x" plan, without copying)
For each target page: match the intent the SERP rewards → cover the gaps → add unique
information-gain elements → structure for AEO (question H2 + direct answer) → correct schema →
internal links from strong pages → off-page plan (see [offpage.md](offpage.md)).

## Output: [templates/competitor-analysis.md](../templates/competitor-analysis.md)

## Never
Scrape or reuse competitor text, images or reviews · fake reviews or comparisons · negative SEO
(spam links, fake complaints) against competitors · claim their data as ours.
