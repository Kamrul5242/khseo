# Release policy

KHSEO ships **behavior**, not just code. A change to what KHSEO does without asking can matter
more than a Python bug fix, so versions track governance semantics as well as code.

## Version numbers

| Number | Where | Meaning |
|---|---|---|
| **KHSEO** `MAJOR.MINOR.PATCH` | [VERSION](VERSION) | the package release (tag `vX.Y.Z`) |
| **Spec** `MAJOR.MINOR` | `scripts/khseo_version.py` | the behavior/governance contract: rules, risk levels, approvals, commands, workflows |
| **Schema** `MAJOR.MINOR` | `scripts/khseo_version.py` + `x-khseo-schema-version` in each schema | the JSON contracts in `schemas/` |
| **Probe** `X.Y.Z` | `scripts/seo_probe.py` | the crawler-view probe component |

Probe output, audit JSON and PDF reports all state these versions. A test fails if `VERSION`, the
newest CHANGELOG entry, the report engine and the schema files disagree.

## What bumps what

| Change | KHSEO | Spec | Schema |
|---|---|---|---|
| KHSEO can now act with **less** permission (e.g. an R3 action becomes R2, auto-apply widened, a "never" relaxed) | **MAJOR** | **MAJOR** | – |
| Removing or renaming a command, or changing what an existing command modifies | **MAJOR** | **MAJOR** | – |
| Breaking JSON change (field removed or renamed, enum value removed, new required field) | **MAJOR** | – | **MAJOR** |
| **Stricter** governance (more approval, new "never" rule, new honesty check) | MINOR | MINOR | – |
| New command, workflow, tool or optional JSON field | MINOR | MINOR (if behavior) | MINOR (if JSON) |
| Bug fix, security fix, docs, tests, CI | PATCH | – | – |

When in doubt, choose the bigger bump. Loosening a safety rule is never a patch.

## CHANGELOG format

Each release in [CHANGELOG.md](CHANGELOG.md) uses these sections (omit empty ones):

```text
## X.Y.Z — YYYY-MM-DD   (spec A.B, schema C.D)
### Breaking behavior   anything that changes what KHSEO does or asks permission for, or breaks JSON
### Governance          risk levels, approvals, honesty rules, "never" rules
### Security            vulnerabilities fixed, hardening
### Added / Changed / Fixed
```

## Release checklist

1. Update `VERSION` (and `SPEC_VERSION` / `SCHEMA_VERSION` if they changed).
2. Add the CHANGELOG entry (newest first; its version must equal `VERSION`).
3. `python tests/run_tests.py` passes (offline contract tests).
4. Optional but recommended for governance changes: run the live behavior scenarios against a
   real host (`tests/behavior/run_live.py`) and note the result in the release.
5. Commit, push, wait for CI (tests, CodeQL) to go green.
6. Tag `vX.Y.Z` and create a GitHub Release with the CHANGELOG entry as its notes.
