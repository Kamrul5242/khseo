# Mode C — Content Writer (blog, article, website copy, product copy)

**Trigger:** write / rewrite / humanize / optimize an article, blog, guide, tutorial, landing
page, product or category description, buying guide, FAQ, about/service page, email/newsletter.

```
TOPIC → AUDIENCE → SEARCH INTENT → TOPIC MAP → INFORMATION GAIN → ORIGINAL DRAFT
→ HUMANIZATION → SEO → AEO → GEO → E-E-A-T → FACT CHECK → FINAL QUALITY CHECK
```

## 1. Understand
Primary topic · intent (informational / commercial / transactional / navigational / local) ·
audience and their skill level · market & language (don't default silently — label `ASSUMED`) ·
content type · reader's problem · desired outcome/CTA · requested length and tone.

**Intent → format:** "what is" → definition + explainer · "how to" → numbered steps · "best X" →
comparison with criteria + table · "X vs Y" → side-by-side table + verdict by use case · "X price"
→ ranges with date and source · local → location specifics, hours, service area.

## 2. Topic map
Primary topic, secondary topics, related entities, the real questions people ask (PAA-style),
comparisons, examples, attributes, objections, supporting concepts. Research current facts when
tools allow; otherwise write only what's reliably known and mark `[VERIFY: …]` where freshness
matters.

## 3. Information gain
Ask the user (once, briefly) for anything first-hand that would lift the piece: their data,
photos, test results, customer questions, prices, local details, opinions. If they have none,
use better structure, clearer explanation, worked examples, and decision frameworks — never fake
experience ("I tested…") on their behalf.

## 4. Draft
Natural structure that serves the reader. Default skeleton (break it when another shape fits):

```
Title
Intro: hook + direct answer in the first 2–3 sentences
Main sections (H2 = a question or clear sub-topic; answer first, then depth)
Examples / table / steps where they help
Evidence and sources where claims need them
Practical advice / decision guide
FAQ (only real questions not already answered above)
Short close with next step or CTA (not "In conclusion")
```

## 5. Humanize (see ban list in [rules/core-rules.md](../rules/core-rules.md))
Vary sentence length. Cut throat-clearing openers. Replace abstractions with specifics. Use
second person where it helps. Allow a clear, labeled opinion. Remove repeated conclusions. Read
it as the target reader: would they finish it?

## 6. Optimize
- **SEO:** title (intent + primary topic early), meta description, slug, H1, outline, primary
  topic in the first 100 words naturally, semantic coverage via entities/attributes — not
  keyword density.
- **AEO:** question headings + 40–60 word direct answers; lists/tables for steps & comparisons.
- **GEO:** standalone passages, consistent entity names, crisp factual sentences, attribution.
- **E-E-A-T:** author/expert placeholders, sources, dates, experience from the user only.
- **Internal links:** 3–6 suggestions with anchor text and target (existing URLs if known,
  otherwise described).

## 7. Fact check
Every number, date, spec, price, claim: sourced, user-supplied, or removed/flagged. List
anything uncertain under "Missing information".

## Rewrite / humanize existing content
1. Extract the facts first (names, prices, specs, dates, claims, CTAs) → these are preserved
   unless the user says otherwise.
2. Diagnose: intent mismatch, weak intro, thin sections, missing FAQs, poor headings, filler,
   unsupported claims, weak entity signals, weak conversion messaging.
3. Rewrite; then output with [templates/rewrite-output.md](../templates/rewrite-output.md) —
   including FACTS PRESERVED and MISSING INFORMATION. Never silently change a factual claim.

## Product & category content
Evaluate/produce: name · short benefit summary · who it's for · key attributes (material, size,
color, dimensions, compatibility, care) · use cases · specifications table · what's included ·
shipping/returns pointers · FAQs from real objections · related products/categories.
Schema: Product + Offer (+ AggregateRating only from genuine reviews) + BreadcrumbList — only
with accurate values. Missing attribute → `[ADD: …]`, never guessed.

## Output
Full writing package: [templates/writing-output.md](../templates/writing-output.md). If the user
asked for "just the article", give just the article (plus a one-line note of any `[VERIFY]` items).
