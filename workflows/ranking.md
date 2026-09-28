# Ranking: check positions and plan for Google page 1 (target: positions 1–3)

**Trigger:** `KHSEO rank <keyword(s)> [url]`, "rank me #1", "why am I on page 3", "ranking report".

> **Top-3 is a target, never a promise.** Rankings depend on Google, competitors and time.
> KHSEO builds the strongest honest plan and measures progress; it never guarantees positions,
> traffic or AI citations, and it never uses tactics that risk a penalty.

## 1. Check current rankings ("ranking result")
- **Tier 1** (preferred): Search Console (query, page, average position, clicks, impressions,
  CTR, date range) or a rank-tracking/SERP data tool, with country, language and device.
  → `VERIFIED` (own GSC data) / `OBSERVED` (third-party SERP data).
- **Tier 2**: live SERP via web search/browser for each keyword → position if found in the
  results actually loaded, `OBSERVED` with the date and a note that results vary by location,
  personalization and time.
- Not found in the results checked → "not in top N checked", never a guessed number.
- Record each row in the audit JSON `rankings[]` (keyword, position or null, url, engine,
  location, device, source, date), which appears as a table in the PDF report.

## 2. Diagnose the gap to top 3 (per keyword)
Work down this list; the first failing item is usually the real blocker:
1. **Access**: page crawlable, indexable, rendered content visible (`seo_probe.py` + rendered DOM).
2. **Intent match**: same page type/format as the current top 3?
3. **Relevance**: title/H1/first paragraph target the query; topic and entities fully covered.
4. **Quality & information gain**: something the top 3 lack (data, photos, tools, expertise).
5. **Page experience**: mobile, speed/Core Web Vitals (field data if available), no intrusive popups.
6. **Internal authority**: links from strong internal pages with descriptive anchors; within 3 clicks.
7. **External authority**: referring domains and brand mentions vs top 3 (Tier 1 data only).
8. **SERP features**: snippet/PAA/product-grid/video eligibility (schema, answer formatting).
9. **CTR**: title/description compelling vs neighbours (GSC CTR by position).

## 3. Top-3 plan: every pillar, with the owner
| Pillar | Actions | Mode / file |
|---|---|---|
| Technical & vibe coding | fix access, rendering, canonicals, speed, sitemap; ship code changes under the risk rules | [code.md](code.md) |
| Content | rewrite/expand to match intent, close gaps, add information gain | [content.md](content.md) |
| Meta & SERP CTR | new title/description (`scripts/meta_tags.py`), test via GSC CTR | `KHSEO meta` |
| Structured data | eligible, truthful schema for rich results | [schema-snippets](../templates/schema-snippets.md) |
| AEO / GEO / LLM | question headings + direct answers, entity clarity, citable facts, AI-crawler access | [seo-checklists.md](../rules/seo-checklists.md) §6–7 |
| Trust (E-E-A-T) | authors, real reviews, policies, first-hand proof | §8 |
| Internal links | hub/cluster links from strong pages | §11 |
| Off-page | earned links, digital PR, citations, brand mentions | [offpage.md](offpage.md) |
| Social | platform-native distribution that earns visits, mentions and links | [social.md](social.md) |

Order the plan by impact ÷ effort. Each action gets a P0–P3 priority, an R0–R4 risk, an owner,
and a measurable check.

## 4. Measure
- Re-check positions on a schedule (e.g. weekly), using the same source, location and device.
- Report movement per keyword, and don't claim causation from one change without comparison data.
- Typical time to move a competitive term is months; say so plainly.

## Output: [templates/ranking-plan.md](../templates/ranking-plan.md) (+ `rankings[]` in the audit JSON / PDF)

## Never
Guarantee positions · buy links or join link schemes/PBNs · cloaking or hidden text · fake
reviews, fake schema, or mass AI pages with no value · negative SEO.
