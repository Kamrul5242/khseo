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

### `KHSEO help`
Prints this compact card, not the whole specification:

```text
KHSEO: just type  KHSEO <what you want>  in plain words.

Optional commands
  audit     analyze, change nothing          fix       find + apply safe fixes
  write     create content / social posts    optimize  improve existing content/site/code
  build     add SEO features to a codebase   verify    check what's really implemented
  research  sourced research                 plan      plan only, no changes
  dry-run   show exact changes, no writes    status    task, tools, risk, progress
  approve   approve pending action           reject    reject pending action
  rollback  undo KHSEO's own changes         stop      emergency stop

Examples
  KHSEO audit https://example.com
  KHSEO fix the SEO in this Next.js app
  KHSEO write a 1500-word blog about travel insurance
  KHSEO optimize this product page
  KHSEO dry-run fix all SEO issues
```

## Precedence
1. `stop` always wins, even mid-task.
2. Read-only commands (`audit`, `verify`, `research`, `plan`, `dry-run`, `status`, `help`)
   **never** modify anything, even if the text after them says "and fix it". In that case
   KHSEO finishes the read-only work and offers the modifying command.
3. `approve`/`reject` apply only to the currently pending request.
4. A command word inside normal prose ("can you audit and then write…") is treated as natural
   language, and the universal mode handles it.
