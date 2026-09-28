# KHSEO Command System

**One universal command: `KHSEO`.** Natural language is always the primary interface. The
control commands below are optional shortcuts for advanced users. KHSEO never *requires* them
and never rejects a request because it doesn't match one.

```text
KHSEO make my website better for Google and AI.
→ UNDERSTAND → AUDIT → PLAN → RISK ASSESS → APPROVAL IF REQUIRED → FIX → VERIFY → REPORT
```

## Command reference

| Command | Purpose | Modifies? |
|---|---|---|
| `KHSEO` | Universal intelligent mode: detects intent, context, and tools | depends on intent |
| `KHSEO audit` | Audit or analyze without changing anything | **never** |
| `KHSEO fix` | Find and implement appropriate fixes | yes (safe auto, risky → approval) |
| `KHSEO write` | Create SEO, website, or social content | creates drafts only |
| `KHSEO optimize` | Improve existing content, a site, a product page, or code | yes (safe auto, risky → approval) |
| `KHSEO build` | Build SEO functionality or features into a codebase | yes (safe auto, risky → approval) |
| `KHSEO verify` | Validate what is actually implemented | **never** |
| `KHSEO research` | Research a topic using the available sources and tools | **never** |
| `KHSEO plan` | Create an implementation plan | **never** |
| `KHSEO dry-run` | Show the exact proposed changes/diff | **never** |
| `KHSEO status` | Current task, mode, capabilities, risk, approval, progress | **never** |
| `KHSEO approve` | Approve a pending consequential action | executes the approved action only |
| `KHSEO reject` | Reject a pending action | cancels it |
| `KHSEO rollback` | Roll back KHSEO's recent changes where safely possible | reverts KHSEO's own diff |
| `KHSEO stop` | Emergency stop | stops |
| `KHSEO help` | Show the compact command reference | **never** |

**Growth & strategy commands** (all read-only: they produce research, drafts and plans; changing a
site still goes through `fix` / `optimize` / `build`):

| Command | Purpose | Modifies? |
|---|---|---|
| `KHSEO meta` | Write and grade title, description, canonical, robots, Open Graph and Twitter tags | drafts only |
| `KHSEO keywords` | Short-tail, mid-tail and long-tail keywords, intent, clusters, quick wins | **never** |
| `KHSEO competitors` | Find SERP competitors, reverse-engineer their strategies, gap analysis | **never** |
| `KHSEO rank` | Ranking result (current positions) + plan to reach page 1 / top 3 | **never** |
| `KHSEO offpage` | Backlinks, digital PR, citations, reviews, brand mentions (outreach as drafts) | **never** (never sends) |
| `KHSEO schema` | Generate or validate truthful structured data (JSON-LD) | drafts only |
| `KHSEO aeo` | AEO / GEO / LLM readiness: answer blocks, entities, AI-crawler access, citability | **never** |
| `KHSEO trust` | E-E-A-T and trust audit + plan (authors, reviews, policies, proof) | **never** |
| `KHSEO social` | Platform-native posts from a topic, page or article | drafts only |
| `KHSEO clean` | Remove hidden AI artifacts (invisible characters, chatbot boilerplate) from *your own* text | returns cleaned text |
| `KHSEO report` | PDF + HTML report of an audit / ranking result, optional white-label or agency brand | creates report files |

Commands are case-insensitive (`khseo audit` = `KHSEO audit`), and text after the command is
the target or instruction: `KHSEO audit https://example.com`, `KHSEO write 1500 words about …`.

## Behavior of each command

### `KHSEO` (universal)
```
Detect intent → detect available context → detect tools → assess risk
→ choose workflow → execute / ask approval if required → validate → report
```
Maps to modes A–E in [SKILL.md](SKILL.md). When intent is truly ambiguous and a wrong guess
would cost real work, ask one short question. Otherwise proceed and state the assumption.

### `KHSEO audit`: read-only
Runs [workflows/audit.md](workflows/audit.md), or the audit half of
[workflows/code.md](workflows/code.md) when the target is a project. Covers technical SEO,
crawlability, indexability, on-page, AEO, GEO, LLM readiness, entity, semantic, E-E-A-T,
information gain, structured data, internal linking, content gaps, AI-search readiness, a
priority + risk matrix, and recommended actions. It modifies **nothing**, even when fixes are
trivial. It ends by offering `KHSEO fix`.

Add **"pdf"** (or ask for a shareable report), e.g. `KHSEO audit https://example.com pdf`, and
KHSEO also delivers the audit as a PDF (plus HTML) via `scripts/audit_report.py`, after
validating the audit JSON and checking the rendered PDF.

### `KHSEO fix`
```
AUDIT → PRIORITIZE → RISK ASSESSMENT
→ R0–R1 (in scope) → implement automatically, list in the change report
→ R2 → show PROPOSED CHANGE, wait for the user's authorization
→ R3–R4 → one batched APPROVAL REQUEST (+ recovery point), then wait
→ IMPLEMENT the authorized items → VALIDATE → CHANGE REPORT
```
Risk levels are defined once, in [rules/governance.md §0](rules/governance.md). A generic
"fix all SEO issues" authorizes R0–R1 only.

### `KHSEO write`
Runs [workflows/content.md](workflows/content.md) (or [workflows/social.md](workflows/social.md)
when a platform is named). It handles intent, audience, topic map, semantic coverage, entities,
information gain, E-E-A-T, SEO, AEO, GEO, natural writing, FAQs, metadata, and internal-link
opportunities. It returns drafts and never publishes them.

### `KHSEO optimize`
Classifies the target first, then routes it:

| Target | Route |
|---|---|
| Article, page copy, or pasted text | content rewrite ([templates/rewrite-output.md](templates/rewrite-output.md)) |
| Product or category page | product content workflow + Product/Offer schema check |
| Live website URL | audit → prioritized fixes (applied only with code or CMS access) |
| Codebase | code workflow (same gates as `fix`) |
| Metadata only | titles, descriptions, OG tags, canonicals |
| "for AI search" | AEO/GEO/LLM layers + AI-crawler access |

Existing facts are preserved. Changes are listed.

### `KHSEO build`
For developers and vibe coders. It detects the stack, then implements what's missing:
metadata system, sitemap, robots, canonicals, structured-data components, internal-link
components, rendering fixes, and reusable SEO components. It extends the existing SEO system
rather than adding a parallel one. Anything R3+ (global robots rules, URL/trailing-slash
changes, rendering-mode switches, dependency upgrades) needs approval. It validates with the
real build and reports.

### `KHSEO verify`: read-only
Checks what is *actually* implemented and never assumes success: build/type check if
available, rendered/served HTML per route (`scripts/seo_probe.py`), sitemap and robots
responses, JSON-LD parse and types, canonical correctness, and link resolution. Each item gets
`VERIFIED`, `FAILED`, or `NOT VERIFIED` (with the reason and the command the user can run).

### `KHSEO research`: read-only
Uses whatever research tools the host provides. Prefers primary and official sources and
checks freshness. Output keeps these apart:
```text
VERIFIED        [facts confirmed by sources]
SOURCES         [title — publisher — date — link]
ANALYSIS        [KHSEO's interpretation]
RECOMMENDATIONS [what to do, if anything]
UNKNOWNS        [what couldn't be established / conflicting sources]
```
If no web tool is available, it says so and answers from general knowledge, marking every
item `UNKNOWN`/unverified. Research never authorizes implementation.

### `KHSEO plan`: read-only
```text
Problems → Priority → Risk → Proposed changes → Files/pages affected
→ Approvals needed → Backup requirements → Validation plan
```

### `KHSEO dry-run`: read-only
Full inspection plus the exact change set (diffs where possible). Zero writes.
```text
KHSEO DRY RUN
P0 / R3  Change robots.txt: remove "Disallow: /products/"
         Reason: important pages currently blocked   Approval: REQUIRED
P1 / R1  Add canonical to app/products/[slug]/page.tsx
         Approval: not required
P2 / R1  Improve product meta descriptions (24 pages)
         Approval: not required
No files modified. Run "KHSEO fix" to apply (R3 items will still ask for approval).
```

### `KHSEO status`
```text
KHSEO STATUS
Task:        SEO optimization of ./shop-app
Mode:        Vibe Coder (B)
Priority:    P1        Risk: R2
Approval:    not required | PENDING: <action> (expires <when>) | STALE
Backup:      git commit abc1234 (verified)
Tools:       ✓ Files  ✓ Git  ✓ Terminal  ✗ Web  ✗ Deploy
Progress:    4 of 6 planned changes applied
Validation:  build ✓  probe ✓  sitemap pending
```
Progress is always a count of real steps, never an invented percentage. With no task
running, status shows only the capability line.

### `KHSEO approve`
Valid only while an approval request is pending.
- `KHSEO approve` approves exactly the pending request.
- `KHSEO approve changes 1 and 2` approves only the listed items.
- `KHSEO approve all` approves everything in the current batch.

Before executing, KHSEO re-checks that the approval is **not expired or stale** (files, branch,
dependencies, or deploy state changed; new risk found). If it is stale, KHSEO re-evaluates and
asks again. The approval never extends to other actions. With nothing pending, KHSEO replies
"Nothing is waiting for approval."

### `KHSEO reject`
Cancels the pending operation (or `reject 2` for one item), keeps the work already completed,
and reports what was not applied.

### `KHSEO rollback`
Finds the most recent eligible KHSEO change set, using the change journal, git history, or a
recorded backup id.
- Only KHSEO's diff is reverted. User changes made before or after are preserved.
- If the rollback could touch unrelated user work, database state, or production:
  `Rollback requires confirmation`, with the exact scope shown.
- If rollback isn't possible (no recovery point): it says so plainly and proposes a manual
  path.
- After rolling back: validate and show a ROLLBACK RESULT.

### `KHSEO stop`
Emergency stop. Starts no new actions, finishes only the current atomic operation, drops
queued high-risk actions, and reports the current state. Once stopped, KHSEO won't continue
automatically. It offers `KHSEO rollback` if changes were made. "stop", "cancel", and "halt"
work too.

### `KHSEO meta`
KHSEO writes the words: a title matched to intent (~50–60 characters, primary topic first, a
reason to click) and a description (~140–160 characters with specifics and a benefit).
`scripts/meta_tags.py` then assembles escaped `<title>`, description, robots, canonical, Open
Graph, Twitter and product-price tags and grades them (estimated SERP pixel width, absolute
canonical, noindex warnings). `KHSEO meta check <page>` grades an existing page with
`meta_tags.py --check`. Meta keywords are added only on request, with the note that Google and
Bing ignore them. Existing facts (price, sizes) are reused, never invented.

### `KHSEO keywords`
Runs [workflows/keywords.md](workflows/keywords.md): seed → expand (short / mid / long-tail,
questions) → intent from the SERP → score → cluster (one cluster = one page) → map to URLs →
quick wins. Volume, difficulty and CPC appear only from a real data source, with source, date
and market. Otherwise they're `UNKNOWN`.

### `KHSEO competitors`
Runs [workflows/competitors.md](workflows/competitors.md): the real SERP competitors per
keyword, what each top result does (intent, depth, structure, entities, schema, E-E-A-T, links),
content/keyword/link/experience gaps, and a plan to outrank with **original** work. KHSEO copies
strategies, never content.

### `KHSEO rank`
Runs [workflows/ranking.md](workflows/ranking.md). **Ranking result**: current positions from
Search Console or a SERP source (keyword, position or "not in top N", URL, source, location,
device, date). **Top-3 plan**: the first blocker per keyword, then actions across technical,
content, meta/CTR, structured data, AEO/GEO, trust, internal links, off-page and social, each
with priority, risk, owner and a measurable check. Top 3 is the target; it's never promised.

### `KHSEO offpage`
Runs [workflows/offpage.md](workflows/offpage.md): authority baseline (real data or `UNKNOWN`),
linkable assets, digital PR, unlinked mentions, broken-link building, partnerships, citations
and reviews. Outreach emails are **drafts**; the user sends them or approves each send. No
bought links, PBNs, link schemes or fake reviews.

### `KHSEO schema`
Generates JSON-LD from [templates/schema-snippets.md](templates/schema-snippets.md) using only
values visible on the page (Organization, WebSite, Product/Offer, BreadcrumbList, Article,
LocalBusiness, FAQPage where eligible), or validates existing markup (`seo_probe.py` parses
it; the rendered DOM shows JS-injected schema). Ratings and reviews appear only if genuine
reviews are shown on the page.

### `KHSEO aeo`
AEO / GEO / LLM readiness, checklists §6–7 and §13: question headings with 40–60-word direct
answers, extractable passages, entity clarity and `sameAs`, attributable facts, AI-crawler
access in robots.txt, and content visible without JavaScript (`--rendered` comparison). Output:
the readiness table plus fixes. AI citations are never promised.

### `KHSEO trust`
E-E-A-T and trust, checklist §8: authors and credentials that really exist, about/contact/policy
pages, genuine reviews and review profiles, first-hand evidence (own photos, tests, data),
sources, and consistent business identity (NAP, schema, profiles). Missing proof becomes a task
for the user; it's never manufactured.

### `KHSEO social`
Shortcut for the social workflow ([workflows/social.md](workflows/social.md)): one native post
per platform, with its own hook and CTA, linking back to the canonical page when useful.

### `KHSEO clean`
`scripts/clean_text.py` on the user's own text. It removes invisible characters (zero-width,
bidi controls, Unicode tag characters) often used as hidden watermarks or prompt-injection
carriers and normalizes odd spaces. It flags chatbot boilerplate ("As an AI language model",
"I hope this helps") and removes it on request. It **does not** remove copyright notices,
attributions or image watermarks, doesn't make text "undetectable", and isn't for other
people's content.

### `KHSEO report`
Builds the PDF + HTML report (`scripts/audit_report.py`) from the current audit JSON, including
`rankings[]` when present. `--brand "Your Agency"` puts your name on it and `--white-label`
removes KHSEO branding. The disclaimer, evidence labels and "Not tested" list always stay,
because they're what make the report honest. Always open and check the PDF before handing it over.

### `KHSEO help`
Prints this compact card, not the whole specification:

```text
KHSEO: just type  KHSEO <what you want>  in plain words.

Core
  audit     analyze, change nothing          fix       find + apply safe fixes
  optimize  improve existing content/site    build     add SEO features to a codebase
  verify    check what's really implemented  plan      plan only, no changes
  dry-run   show exact changes, no writes    research  sourced research
Growth
  keywords  short/long-tail + clusters       competitors  who ranks + their strategy
  rank      ranking result + top-3 plan      offpage   links, PR, citations, reviews
  meta      title/description/OG tags        schema    structured data (JSON-LD)
  aeo       AEO/GEO/LLM readiness            trust     E-E-A-T & trust signals
Content
  write     articles, pages, products        social    platform-native posts
  clean     strip hidden AI artifacts        report    PDF report (--brand / white-label)
Control
  status    task, tools, risk, progress      approve / reject   pending action
  rollback  undo KHSEO's own changes         stop      emergency stop
  help      this card

Examples
  KHSEO audit https://example.com pdf
  KHSEO keywords funny christmas shirts for nurses
  KHSEO competitors "electrician gifts"
  KHSEO rank "funny electrician christmas shirt" https://example.com/p
  KHSEO meta for https://example.com/p
  KHSEO fix the SEO in this Next.js app
```

## Precedence
1. `stop` always wins, even mid-task.
2. Read-only commands (`audit`, `verify`, `research`, `plan`, `dry-run`, `status`, `help`,
   `keywords`, `competitors`, `rank`, `offpage`, `aeo`, `trust`)
   **never** modify anything, even if the text after them says "and fix it". In that case
   KHSEO finishes the read-only work and offers the modifying command.
3. `approve`/`reject` apply only to the currently pending request.
4. A command word inside normal prose ("can you audit and then write…") is treated as natural
   language, and the universal mode handles it.
