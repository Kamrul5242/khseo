# Security policy

## Supported versions

Only the latest release on `main` gets security fixes. See [CHANGELOG.md](CHANGELOG.md).

## Reporting a vulnerability

Please **don't open a public issue**. Report privately through GitHub's private vulnerability
reporting: **<https://github.com/Kamrul5242/khseo/security/advisories/new>**
(Security tab → Report a vulnerability).
Include the affected file/version (`VERSION`), steps to reproduce, and impact. You can expect an
acknowledgement within 7 days and a fix or mitigation plan within 30 days for confirmed issues.

## Scope

In scope: the scripts (`seo_probe.py`, `capture_rendered.py`, `audit_report.py`,
`validate_json.py`, `meta_tags.py`, `clean_text.py`), for example SSRF, network pivots,
decompression bombs, output/HTML injection or unsafe file handling. Also in scope: skill
instructions that could lead an agent to bypass the approval or risk rules, leak secrets, or
follow instructions embedded in fetched content.

Out of scope: vulnerabilities in the host AI or its tools, and the SEO outcome of any advice.

## Repository protections

- Offline test suite, CodeQL (`security-extended`, Python + Actions), dependency review on
  pull requests, and weekly OpenSSF Scorecard.
- All GitHub Actions pinned to full commit SHAs, updated through Dependabot PRs.
- Least-privilege workflow tokens (`contents: read` unless a job needs more).
- Secret scanning and push protection are enabled on the repository.
- No runtime dependencies: every script is Python standard library only.
