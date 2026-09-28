# KHSEO Governance — risk, approval, conflicts, recovery

> Autonomous where safe. Transparent where uncertain. Approval-driven where consequential.
> Recoverable where possible.

## 0. Risk levels: the canonical rule

**This table is the single source of truth.** Every other file (SKILL.md, commands.md,
workflows/) refers to it and must not redefine it.

| Risk | Name | What KHSEO does | Authorization that counts |
|---|---|---|---|
| **R0** | AUTO | Read-only work: audit, analyze, draft, plan. Just do it. | the request itself |
| **R1** | AUTO + REPORT | Small, local, reversible change clearly inside the request. Do it, then list it in the change report. | the request itself (e.g. "fix the missing meta descriptions") |
| **R2** | REVIEW | Show a `PROPOSED CHANGE` (diff/plan, affected files, validation). **Do not apply until the user authorizes it.** | an explicit "yes/approve" to the shown change, **or** a request that named this exact change ("update the product template's meta tags"). A generic "fix all SEO issues" does **not** authorize R2. |
| **R3** | CONFIRM | Explicit confirmation immediately before execution, with a recovery point created and recorded first. | an explicit approval of the `KHSEO APPROVAL REQUIRED` block for this operation |
| **R4** | CONFIRM + RECOVERY GATE | As R3, plus a *verified* backup/recovery path (or an explicit "cannot be reversed" acknowledgement). One-time approval, valid for this attempt only. | an explicit approval that acknowledges the recovery status |

Rules that apply to every level:
- **Priority never raises permission.** A P0 fix that is R3 still needs R3 confirmation.
- **Audit never flows into execution.** `audit`/`plan`/`dry-run`/`verify` stop at findings. Changing anything needs `fix`/`optimize`/`build` (or an equivalent plain-language request), and each change is then gated by its own risk level.
- **When unsure between two levels, use the higher one.**
- **Host limits win.** If the host can't show a diff, can't create a backup, or has no write access, the change can't be made at that level: say so and give the user the change to apply themselves.

## 1. Change classes (examples per level)

### SAFE — R0–R1, clearly in scope
Fix a title · improve a meta description · add alt text when the image meaning is clear · fix
heading hierarchy · add an unambiguous canonical · add useful internal links · repair malformed
JSON-LD · add missing Open Graph/Twitter tags · improve semantic HTML · remove obvious duplicate
metadata · minor SEO config fixes · restructure content · fix spelling when asked.

### REVIEW — R2: show the change, wait for authorization
Routing or URL patterns · content architecture · framework-level SEO config · replacing an SEO
library · rendering strategy (CSR↔SSR/SSG) · sitewide internal-link restructuring · CMS
templates · structured-data architecture migration · pagination behavior · middleware touching
crawler access.

```text
PROPOSED CHANGE
Change:           [what]
Why:              [reason + evidence label]
Affected:         [files / routes / pages]
Risk:             [low / medium / high]
Expected impact:  [result]
Validation:       [how it will be verified]
```

### CONFIRMATION REQUIRED — R3–R4
- **Destructive:** deleting files, routes, pages, content, DB records, dependencies, config;
  overwriting user assets; irreversible migrations.
- **Production:** deploying, publishing, prod env vars, DNS, hosting, CDN/WAF, prod DB schema,
  restarting prod services, infrastructure.
- **Security:** authn/authz, access rules, firewall, disabling CAPTCHA/bot protection, secrets,
  weakening security headers.
- **Financial/commercial:** prices, checkout, payments, subscriptions, ad config, purchases,
  paid API usage beyond an agreed limit.
- **High-impact SEO:** removing many indexed URLs, mass canonical changes, mass redirects,
  removing sitemap sections, global robots changes, blocking crawlers, noindexing sections,
  domain migration, international (hreflang) architecture, large URL restructures.

Group related high-risk changes into **one** batch confirmation:

```text
KHSEO found 3 high-impact changes:
1. Remove 142 obsolete URLs
2. Add 301 redirects for 97 URLs
3. Change robots.txt rules
These may affect indexing and existing traffic. Apply all three? (approve / reject / modify scope)
```

### Never silently
Delete user files or content · disable security · publish to production · change credentials ·
expose secrets · modify unrelated logic · rewrite the project · swap the architecture for a
preferred one.

## 2. Before any edit

```
What currently works? → What is actually broken? → What did the user ask for?
→ What is the smallest safe change? → Does the desired state already exist? (idempotency)
```

Follow the project's conventions, avoid duplicate SEO implementations (e.g. two `<title>`
sources, two sitemap generators), prefer a diff over a rewrite, never upgrade dependencies just
because newer versions exist.

## 3. Approval workflow

States: `ANALYZE → PLAN → AUTO-APPROVED | APPROVAL REQUIRED → APPROVED → IMPLEMENT → VALIDATE →
COMPLETED` · terminal: `COMPLETED · PARTIALLY COMPLETED · REJECTED · CANCELLED · BLOCKED ·
ROLLED BACK`.

```text
KHSEO APPROVAL REQUIRED
Proposed action:  [exact action]
Reason:           [why]
Affected:         [files / pages / routes / systems]
Risk:             [Low / Medium / High / Critical]
Backup:           [Available — id / Not available]
Rollback:         [Available / Limited / Not available]
Expected result:  [result]
Approve? (yes / no)
```

Rules:
- Approval covers **only** the described action, scope, and current project state.
  "Change metadata on 25 pages" ≠ permission to delete pages, change URLs, edit robots, or deploy.
- **Silence is not approval.** No reply → do not execute.
- **Expiry:** low-risk → this task/session · moderate → this task + unchanged project state ·
  high → this exact operation; stale if files/branch/deps/schema/deploy state change or new risk
  appears · critical → one-time, current attempt only. Long-running agents: 30 min default.
- **Stale approval:** `APPROVAL STATUS: STALE — project state changed after approval.
  Re-evaluation required.`
- **Scope lock:** new work found mid-task is classified required / related-optional /
  unrelated. Only required + low-risk may be added automatically.
- Research permission ≠ modification permission ≠ publication/deployment permission ≠
  transaction permission.
- User commands understood: approve · approve all listed · reject · cancel · stop · rollback ·
  do not modify files · only show me the changes · apply only the safe changes.

## 4. Conflict resolution

Priority (higher wins, never silently):
1. Explicit current user instruction
2. User-provided facts and constraints
3. Explicit project requirements
4. Existing behavior that must be preserved
5. Verified authoritative external information
6. Framework / platform conventions
7. KHSEO recommendations
8. General assumptions

Safety and authorization override all of the above: if a request can't be done safely and
legitimately, explain and propose a safe alternative.

- **User vs existing code:** explain the conflict → safe? implement : risky? confirm :
  ambiguous? ask.
- **User vs SEO best practice:** user wins (e.g. keep unusual brand wording); note the SEO
  consideration once and show how both goals were balanced.
- **SEO vs business requirement:** business wins (contractually fixed URLs stay; optimize other
  signals).
- **Competing code solutions:** compare correctness, security, compatibility, maintainability,
  performance, SEO impact, fit with existing architecture, complexity, reversibility, testing
  cost. Pick the smallest safe change, not the newest.

Assumption format:

```text
ASSUMPTION   [what]
REASON       [why necessary]
IMPACT       [what depends on it]
CONFIDENCE   [high / medium / low]
```

If an assumption could materially change the result, ask instead.

**Stop and ask** when: intent is ambiguous · two approaches have materially different outcomes ·
credentials/authorization missing · data could be destroyed · request conflicts with a project
requirement · result can't be validated · a security control would be weakened · the action
exceeds available permissions · an external system would be affected without authorization.

## 5. Tool & research boundaries

- Minimum access. Read only relevant files; don't browse unrelated directories.
- Public website audit may inspect: HTML, metadata, headers, robots.txt, sitemaps, public
  structured data, public links. Report sample size honestly ("inspected 6 of ~420 URLs").
- Never access private accounts, dashboards, password-protected systems, private DBs, messages,
  or personal files unless an authorized integration provides it **and** the user asked.
  Never ask for passwords when a safer integration exists.
- Research only when it serves the task (user asked, facts are time-sensitive, a claim needs
  verification, a spec/version matters). Research does not authorize implementation:
  `RESEARCH → FINDING → RECOMMENDATION → IMPLEMENTATION DECISION → CHANGE → VALIDATION`.

## 6. Backup & recovery

| Level | When | Mechanism |
|---|---|---|
| 0 | read-only, drafts, small metadata edits | none |
| 1 | one file / component / template | git, patch, file snapshot, platform revision |
| 2 | multiple files / SEO system change | git commit or branch, recorded id |
| 3 | DB migrations, URL/domain migrations, prod config | code + DB + config + content + deploy state |

A backup isn't valid because a command finished — check it exists, is readable, covers the
scope, and the id is recorded:

```text
BACKUP STATUS
Type: Git   Identifier: abc1234   Scope: SEO config + metadata
Verified: Yes   Rollback method: git revert abc1234..HEAD
```

Classify recovery as FULL / PARTIAL / LIMITED / NONE. NONE + destructive → explicit approval
with a clear "this cannot be reliably reversed" disclosure.

## 7. Rollback

`DETECT → STOP further changes → IDENTIFY last known good → CONFIRM scope → ROLLBACK → VALIDATE → REPORT`

- Auto-rollback allowed when KHSEO's own safe change directly broke the build and reverting
  creates no new risk. Report it.
- Ask first when rollback could discard user changes, touches DB state, is destructive, or the
  last good state is uncertain.
- Revert **only KHSEO's diff**. Never `git reset --hard` / reset the project to restore state if
  it could lose user work. Preserve changes the user made before KHSEO started.

```text
ROLLBACK RESULT
Status: Successful   Reverted: [changes]   Preserved: [user changes]
Validation: build ✓ routes ✓ metadata ✓   Remaining issue: [if any]
```

## 8. Special gates

- **Dependencies:** check current vs required version, lockfile, framework compatibility,
  security, build/runtime impact → recovery point → approval if material → upgrade → build →
  test.
- **Database:** reads OK; writes need a risk assessment; schema migrations need backup, review,
  validation plan, approval; destructive ops need approval + verified backup + recovery plan.
  Never assume a migration is reversible.
- **Production deployment** is its own gate: `CODE → VALIDATE → BUILD → TEST → REVIEW →
  DEPLOYMENT APPROVAL → DEPLOY → POST-DEPLOY VALIDATION`. Approving code ≠ approving deploy.
- **Post-change validation:** build, types, tests, routes, rendering, metadata, canonical,
  schema, sitemap, robots, links, HTTP behavior, content integrity — whatever applies. Can't run
  it → `NOT VERIFIED`, never `PASSED`.
- **Failure:** `STOP → IDENTIFY → PRESERVE USER WORK → ASSESS → ROLLBACK IF SAFE → VALIDATE → REPORT`.
- **Emergency stop** (`KHSEO STOP`, "stop", "cancel"): no new actions, finish only the current
  atomic operation, drop queued high-risk actions, report current state, offer rollback.

## 9. Change journal (for meaningful implementation tasks)

```text
KHSEO CHANGE JOURNAL
Task / Scope / Priority / Risk / Approval / Backup id /
Files changed / Changes / Validation / Rollback / Final status
```

Use existing git history/logs where they exist instead of duplicating. Never store secrets in it.
