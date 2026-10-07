# Mode G — Freelancer Gig SEO (Fiverr, Upwork, Freelancer.com, other marketplaces)

**Trigger:** `KHSEO gig …`, "optimize my Fiverr gig", "Upwork profile SEO", "rank my gig".
**Load:** this file + [core-rules](../rules/core-rules.md). Marketplace search is internal search,
not Google, so the website workflows don't apply. Reuse, don't repeat: data tiers in
[keywords.md](keywords.md), "copy strategies, never content" in [competitors.md](competitors.md).

## Assets
Gig/service (Fiverr gig, Upwork Project Catalog project, Freelancer.com service) · freelancer
profile · portfolio items · packages · FAQ · category/subcategory · tags/skills.

## Steps
1. **Platform + asset + inputs.** Use only what the user provides: the service, deliverables,
   turnaround, real portfolio and reviews, prices. Anything missing becomes `[ADD: …]`.
2. **Keywords (marketplace-native).** Use the marketplace's own search autocomplete, category and
   subcategory names, the phrases top-ranking gigs use (`OBSERVED`), and buyer wording from
   briefs. No invented search volumes; the marketplace exposes none publicly, so mark them `UNKNOWN`.
   Pick 1 primary and 3–5 secondary terms; match buyer intent ("logo design for restaurant").
3. **Category/subcategory.** Choose the most specific one that matches the deliverable, because
   search filters by it. A wrong category hides the gig whatever the keywords.
4. **Title (CTR).** Primary keyword first, a specific outcome or niche, no stuffing. Fiverr starts
   with "I will …". Example pattern: `I will design a [deliverable] for [niche] [differentiator]`.
5. **Description (conversion).** Hook (buyer problem, then outcome), what's included, process,
   why you (real proof only), who it's for and not for, CTA to order or message *on-platform*.
   Primary keyword in the first sentence and 2–3 natural variants; short scannable lines.
6. **Tags/skills.** Use every allowed slot with distinct, relevant terms: synonyms, niche terms
   and tools. Don't repeat the title verbatim, and don't use competitor brand names.
7. **Packages.** A clear Basic → Standard → Premium value ladder (scope, revisions, delivery
   time). Package names should be searchable and descriptive, never vague. Only offer what you'll deliver.
8. **FAQ.** Answer real pre-sale objections (scope, revisions, files, timeline, what the buyer
   provides) in natural, keyword-aware language.
9. **Profile SEO.** Headline or title with the core service plus niche, an overview that leads
   with the buyer outcome (the first lines show in search), skills that match the gigs, and
   languages and certifications that really exist.
10. **Portfolio SEO.** Descriptive titles and descriptions per item (service + niche + result).
    Only the user's own work, with client work shown only with permission or anonymized.
11. **Competitor gigs.** Analyze the top results for the primary term: title patterns, package
    pricing spread, what they include, review volume and gaps. Build an *original*, better offer.
12. **Validate.** Count characters against the limits below. Every claim must be backed by the
    user's facts, and nothing may violate the platform's terms (see *Never*).

## Platform limits (last known: verify in the live editor, which is the source of truth)
| Platform | Field | Limit (last known) |
|---|---|---|
| Fiverr | gig title | 80 characters, starts "I will" |
| Fiverr | search tags | 5 tags |
| Fiverr | gig description | 1,200 characters |
| Fiverr | packages | up to 3 (Basic / Standard / Premium) |
| Upwork | profile overview | 5,000 characters (the opening lines show in search) |
| Upwork | profile skills | up to 15 |
| Freelancer.com / others | all fields | check the editor's counter; no fixed values assumed |

Limits change. If the editor disagrees, the editor wins, and the draft gets updated.

## Marketplace ranking factors (`INFERRED`: platforms don't fully publish them)
Relevance (title, tags, description, category) plus performance (CTR, conversion, response time,
on-time delivery, completion, ratings, repeat buyers). KHSEO can improve relevance, CTR and
conversion copy. Performance comes from real delivery, and positions are never guaranteed.

## Output
```text
KHSEO GIG: [platform] · [service]   Primary: [term]   Secondary: [terms]   Data: [observed sources | UNKNOWN]
CATEGORY:     [category > subcategory]
TITLE:        [text]  ([n]/[limit] chars)
DESCRIPTION:  [text]  ([n]/[limit] chars)
TAGS/SKILLS:  [t1] · [t2] · [t3] · [t4] · [t5]
PACKAGES:     Basic [name · scope · delivery · revisions] | Standard […] | Premium […]
FAQ:          Q/A ×3–5
PROFILE:      [headline] · [overview opening lines] · [skills]
PORTFOLIO:    [item title → description] …
COMPETITOR NOTES: [patterns, gaps, our angle]
MISSING:      [ADD: …]
```
Return only the assets the user asked for.

## Never
Fake reviews, orders or ratings · keyword stuffing in titles or tags · misrepresented skills,
credentials or portfolio (including AI images shown as client work) · copying competitor gig
text or images · steering buyers to off-platform contact or payment (it breaks marketplace terms)
· logging into or editing the user's marketplace account. KHSEO drafts, and the user publishes.
