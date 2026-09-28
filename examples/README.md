# KHSEO examples

Short, realistic request → behavior pairs. They show *how KHSEO decides*, not canned outputs.

## 1. Audit (Mode A)
**User:** `KHSEO audit https://myshop.example`

**KHSEO does:** capability check → runs `seo_probe.py` on home + one product + one category →
finds the product page returns a JS challenge shell to non-browser clients →

```text
CRITICAL (P0)
- Bot-challenge served instead of product HTML — OBSERVED (probe UA, 2026-09-28)
  evidence: 509-byte script-only response, window.rbzns
  Fix: allowlist verified search/AI crawlers in the WAF, then confirm with Search Console
  URL Inspection (R3 — WAF change needs your approval; KHSEO cannot access the WAF).
```
…and deliberately puts meta-description advice under P3, because nothing else matters until
crawlers can read the page.

## 2. Vibe coding (Mode B)
**User:** `KHSEO fix the SEO in this Next.js app`

**KHSEO does:** reads `package.json` (next 15, App Router) → finds `layout.tsx` sets one static
title for every route, no `sitemap.ts`, product JSON-LD built in `useEffect` (invisible in server
HTML) → auto-applies R1 fixes (per-route `generateMetadata`, `app/sitemap.ts`, server-rendered
JSON-LD) → runs `npm run build` and probes `.next` output for two routes → reports. A proposed
`trailingSlash: true` change is **R3** (every URL changes) → asks first.

## 3. Blog writing (Mode C)
**User:** `KHSEO write a 1500-word blog about choosing t-shirt fabric for hot weather, for my store's customers in Bangladesh`

**KHSEO does:** intent = informational with commercial follow-up; audience = shoppers in a
hot-humid climate; asks once for first-hand material (the store's actual fabrics/GSM) → writes
with question H2s + direct answers, a fabric comparison table, care tips, FAQ → marks
`[VERIFY: …]` on any humidity/breathability figure it couldn't source → gives SEO title, meta,
slug, internal-link suggestions to the store's product categories.

## 4. Rewrite (Mode C)
**User:** `KHSEO humanize this product description and improve SEO: "Our premium high quality tee is the best choice for everyone who wants quality..."`

**KHSEO does:** extracts facts (there are none beyond "tee") → rewrites around benefits it can
state honestly → leaves `[ADD: fabric weight]`, `[ADD: fit]`, `[ADD: sizes]` rather than
inventing them → lists them under MISSING INFORMATION.

## 5. Social (Mode D)
**User:** `KHSEO turn this blog into posts for Facebook, LinkedIn and an Instagram carousel`

**KHSEO does:** three different angles (Facebook: the common mistake story; LinkedIn: the
sourcing decision as a founder insight; Instagram: 7-slide checklist) with one CTA each, no
copy-pasted text.

## 6. General user (Mode E)
**User:** `KHSEO make my website better for Google and ChatGPT`

**KHSEO does:** asks only for the URL → audits quietly → explains the top 3 problems in plain
words with who fixes each → offers to do the ones it can (copy, schema, blog plan) right now.

## 7. Dry run & stop
- `KHSEO show me what you'd change in this repo, don't modify anything` → plan + diff, zero writes.
- `KHSEO STOP` → finishes only the current atomic edit, starts nothing new, reports state and
  offers to roll back its own changes.
