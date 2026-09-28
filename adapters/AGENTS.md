# KHSEO (for AGENTS.md-aware coding agents)

When the user's request starts with `KHSEO` or concerns SEO, AI-search readiness, structured
data, or SEO content, follow the KHSEO skill in `./khseo/` (adjust the path to where you placed
this folder):

- Entry point and mode detection: `khseo/SKILL.md`
- Safety, approvals, rollback: `khseo/rules/governance.md`
- Codebase workflow: `khseo/workflows/code.md`
- Probe a URL or built HTML file: `python khseo/scripts/seo_probe.py <url-or-file> [--json]`

Do not deploy, change robots.txt globally, add mass redirects, or delete content without explicit
approval. Report validation you actually ran; mark the rest NOT VERIFIED.
