# Template — KHSEO Audit

Include only relevant sections. Every finding: priority · evidence label · evidence · fix.

```text
KHSEO AUDIT
───────────
Target:          [URL / project]
Scope:           [Quick | Standard | Deep | Full] — inspected [N] URLs: [list or pattern]
Date:            [YYYY-MM-DD]
Overall status:  [Critical | Needs Work | Healthy]
Not tested:      [what couldn't be checked and why]

EXECUTIVE SUMMARY
[3–5 sentences: the single biggest blocker, the biggest opportunity, what to do first.]

CRITICAL (P0)
- [Finding] — [OBSERVED] [evidence: line/header/status] → Fix: [action] (Risk R?, Who: KHSEO/user/dev)

HIGH (P1)
- …

MEDIUM (P2)
- …

ENHANCEMENTS (P3)
- …
```

Then the relevant layer sections, each a short bullet list or table:

`TECHNICAL SEO` · `CONTENT / ON-PAGE` · `AEO` · `GEO` · `LLM / AI SEARCH` · `ENTITY SEO` ·
`SEMANTIC SEO` · `E-E-A-T` · `INFORMATION GAIN` · `STRUCTURED DATA` · `INTERNAL LINKING` ·
`REPUTATION` · `AI SEARCH READINESS` (table: area · status · evidence)

```text
ACTION PLAN
1. [P0] [action] — [where] — [expected effect, qualitative] — [who]
2. …

WHAT KHSEO CAN DO NOW
- [e.g. rewrite homepage hero copy, generate Product JSON-LD, fix titles in repo]

UNCERTAIN / UNKNOWN
- [e.g. index coverage — needs Search Console data]
```
