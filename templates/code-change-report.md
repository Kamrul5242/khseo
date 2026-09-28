# Template — Code Analysis & Change Report

Before changes:

```text
KHSEO CODE ANALYSIS
STACK       [framework + version, router, rendering mode, SEO library, CMS, i18n]
FOUND       [P0–P3 issues, each with file:line evidence]
PLAN        1. [change] (P?, R?)  2. …
NEEDS APPROVAL   [R3/R4 items grouped, or "none"]
```

After changes:

```text
KHSEO CHANGE REPORT
Status:          [Completed | Partially Completed | Blocked | Rolled Back]
Backup:          [git commit/branch id, or "working tree diff only"]
Files changed:   - path/to/file (what)
Changes:         - [change]
SEO impact:      [expected, qualitative]
Technical impact:[runtime/build effect]
Validation:
  - Build:      [VERIFIED ✓ `npm run build` exit 0 | NOT VERIFIED — reason]
  - Types/Lint: [...]
  - Tests:      [...]
  - Routes:     [...]
  - Metadata:   [e.g. probe on /products/x: title ✓ canonical ✓ one H1 ✓]
  - Schema:     [JSON-LD parses ✓, types: Product, BreadcrumbList]
  - Sitemap:    [...]
  - Robots:     [...]
Remaining issues: - [...]
User confirmation required: [Yes — for … | No]
Deployment: not performed (separate approval)
```
