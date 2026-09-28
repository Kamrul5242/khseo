#!/usr/bin/env python3
"""KHSEO audit_report — turn a KHSEO audit JSON into a professional HTML + PDF report.

Usage:
    python audit_report.py audit.json -o report.pdf                  # PDF (+ report.html next to it)
    python audit_report.py audit.json -o report.pdf --engine builtin # no browser needed
    python audit_report.py audit.json --html-only -o report.html

Input must validate against schemas/audit-report.schema.json (including the honesty lint);
invalid input is refused rather than rendered. Produce the JSON by hand/agent, or from the
probe: python seo_probe.py https://site/ --audit-json > audit.json

Engines:
  auto     (default) headless Chromium-family browser if found (Edge, Chrome, Chromium, Brave),
           else the built-in writer
  browser  require a browser; fail if none is found
  builtin  stdlib-only PDF writer (Helvetica; non-Latin-1 text is transliterated)

Security: every value is HTML-escaped (audit text often comes from untrusted web pages), and the
HTML carries a CSP that blocks scripts and all network loads, so printing it can't fetch or run anything.
"""
from __future__ import annotations

import argparse
import html
import json
import os
import shutil
import subprocess
import sys
import tempfile
import zlib
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import validate_json  # noqa: E402

VERSION = "1.2.0"
PRI_COLOR = {"P0": "#b71c1c", "P1": "#d84315", "P2": "#b8860b", "P3": "#455a64"}
PRI_NAME = {"P0": "Critical", "P1": "High", "P2": "Medium", "P3": "Enhancement"}
STATUS_COLOR = {"critical": "#b71c1c", "needs_work": "#d84315", "healthy": "#2e7d32"}
STATUS_NAME = {"critical": "Critical", "needs_work": "Needs work", "healthy": "Healthy"}
LAYER_NAME = {
    "crawlability": "Crawlability", "indexability": "Indexability", "technical": "Technical SEO",
    "on_page": "On-page", "entity": "Entity SEO", "semantic": "Semantic SEO", "aeo": "AEO",
    "geo": "GEO", "llm": "LLM / AI search", "eeat": "E-E-A-T", "information_gain": "Information gain",
    "structured_data": "Structured data", "internal_links": "Internal linking", "reputation": "Reputation",
    "ai_readiness": "AI-search readiness",
}
DISCLAIMER = ("Findings reflect only the URLs and data listed under Scope at the time of the audit. "
              "Items under 'Not tested' were not checked. No ranking, traffic or AI-citation outcome is "
              "guaranteed. Evidence labels: VERIFIED = tested and confirmed; OBSERVED = seen directly; "
              "INFERRED = concluded from evidence; UNKNOWN / NOT TESTED = not established.")


# =============================================================================== HTML
def _e(v) -> str:
    return html.escape(str(v if v is not None else ""), quote=True)


def build_html(a: dict) -> str:
    findings = sorted(a["findings"], key=lambda f: (f["priority"], f.get("id", "")))
    counts = {p: sum(1 for f in findings if f["priority"] == p) for p in PRI_COLOR}
    status = a["overall_status"]
    title = a.get("site_name") or a["target"]
    rows = []
    for f in findings:
        meta = [f'<span class="chip" style="background:{PRI_COLOR[f["priority"]]}">{_e(f["priority"])} · '
                f'{_e(PRI_NAME[f["priority"]])}</span>',
                f'<span class="chip ghost">{_e(f["label"])}</span>',
                f'<span class="layer">{_e(LAYER_NAME.get(f["layer"], f["layer"]))}</span>']
        if f.get("fix_risk"):
            meta.append(f'<span class="chip ghost">fix risk {_e(f["fix_risk"])}</span>')
        if f.get("owner"):
            meta.append(f'<span class="owner">owner: {_e(f["owner"])}</span>')
        body = [f'<div class="f-msg">{_e(f["message"])}</div>']
        if f.get("url"):
            body.append(f'<div class="f-row"><b>URL</b> <span class="mono">{_e(f["url"])}</span></div>')
        if f.get("evidence"):
            body.append(f'<div class="f-row"><b>Evidence</b> {_e(f["evidence"])}</div>')
        if f.get("fix"):
            body.append(f'<div class="f-row"><b>Fix</b> {_e(f["fix"])}</div>')
        rows.append(f'<div class="finding" style="border-left-color:{PRI_COLOR[f["priority"]]}">'
                    f'<div class="f-meta"><span class="fid">{_e(f.get("id", ""))}</span>{"".join(meta)}</div>'
                    f'{"".join(body)}</div>')

    def ul(items):
        return "<ul>" + "".join(f"<li>{_e(i)}</li>" for i in items) + "</ul>" if items else "<p class='muted'>None.</p>"

    plan = "".join(
        f'<tr><td class="num">{_e(s["step"])}</td><td>{_e(s["action"])}</td>'
        f'<td><span class="chip" style="background:{PRI_COLOR[s["priority"]]}">{_e(s["priority"])}</span></td>'
        f'<td>{_e(s.get("risk", ""))}</td><td>{_e(s.get("owner", ""))}</td></tr>'
        for s in a.get("action_plan", []))
    ready = "".join(f'<tr><td>{_e(r["area"])}</td><td><b>{_e(r["status"])}</b></td><td>{_e(r.get("evidence", ""))}</td></tr>'
                    for r in a.get("ai_search_readiness", []))
    caps = "".join(f'<span class="cap {"on" if v == "AVAILABLE" else "off"}">{_e(k.replace("_", " "))}: {_e(v)}</span>'
                   for k, v in (a.get("capabilities") or {}).items())
    scope = a["scope"]
    kpis = "".join(f'<div class="kpi" style="border-top-color:{PRI_COLOR[p]}"><div class="kpi-n">{counts[p]}</div>'
                   f'<div class="kpi-l">{p} {PRI_NAME[p]}</div></div>' for p in PRI_COLOR)

    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; img-src data:">
<title>KHSEO Audit — {_e(title)}</title>
<style>
@page {{ size: A4; margin: 16mm 14mm 18mm 14mm;
  @bottom-left {{ content: "KHSEO audit · {_e(title)}"; font: 8pt Arial, sans-serif; color: #888; }}
  @bottom-right {{ content: "Page " counter(page) " of " counter(pages); font: 8pt Arial, sans-serif; color: #888; }} }}
* {{ box-sizing: border-box; }}
body {{ font: 10pt/1.45 "Segoe UI", Arial, Helvetica, sans-serif; color: #1c2430; margin: 0; }}
.cover {{ border-bottom: 3px solid #1c2430; padding-bottom: 10px; margin-bottom: 14px; }}
.brand {{ font-size: 9pt; letter-spacing: .12em; text-transform: uppercase; color: #5b6573; }}
h1 {{ font-size: 21pt; margin: 4px 0 2px; }}
.target {{ font-family: Consolas, monospace; color: #3d4a5c; font-size: 9.5pt; }}
.status {{ display: inline-block; color: #fff; padding: 3px 10px; border-radius: 3px; font-weight: 700; font-size: 9.5pt; }}
.meta-line {{ color: #5b6573; font-size: 9pt; margin-top: 6px; }}
h2 {{ font-size: 12.5pt; border-bottom: 1px solid #d6dbe2; padding-bottom: 3px; margin: 18px 0 8px; break-after: avoid; }}
.summary {{ background: #f3f5f8; border-left: 4px solid #1c2430; padding: 9px 12px; }}
.kpis {{ display: flex; gap: 8px; margin: 12px 0 4px; }}
.kpi {{ flex: 1; border: 1px solid #d6dbe2; border-top: 4px solid; padding: 6px 8px; }}
.kpi-n {{ font-size: 18pt; font-weight: 700; line-height: 1.1; }}
.kpi-l {{ font-size: 8.5pt; color: #5b6573; }}
.finding {{ border: 1px solid #e1e5ea; border-left: 5px solid; padding: 7px 10px; margin: 0 0 7px; break-inside: avoid; }}
.f-meta {{ display: flex; flex-wrap: wrap; gap: 6px; align-items: center; margin-bottom: 3px; }}
.fid {{ font-weight: 700; color: #5b6573; font-size: 9pt; }}
.chip {{ color: #fff; font-size: 7.5pt; font-weight: 700; padding: 1px 6px; border-radius: 2px; }}
.chip.ghost {{ color: #3d4a5c; background: #e8ecf1; }}
.layer, .owner {{ font-size: 8.5pt; color: #5b6573; }}
.f-msg {{ font-weight: 600; }}
.f-row {{ font-size: 9pt; margin-top: 2px; }}
.f-row b {{ display: inline-block; min-width: 56px; color: #5b6573; font-weight: 600; }}
.mono {{ font-family: Consolas, monospace; font-size: 8.5pt; word-break: break-all; }}
table {{ width: 100%; border-collapse: collapse; font-size: 9pt; break-inside: auto; }}
th, td {{ text-align: left; border-bottom: 1px solid #e1e5ea; padding: 5px 6px; vertical-align: top; }}
th {{ background: #f3f5f8; font-weight: 600; }}
td.num {{ width: 26px; font-weight: 700; }}
.caps {{ display: flex; flex-wrap: wrap; gap: 5px; }}
.cap {{ font-size: 8pt; padding: 1px 6px; border-radius: 2px; }}
.cap.on {{ background: #e3f1e5; color: #1b5e20; }} .cap.off {{ background: #fbe9e7; color: #8d2a14; }}
.cols {{ display: flex; gap: 16px; }} .cols > div {{ flex: 1; }}
ul {{ margin: 4px 0; padding-left: 18px; }}
.muted {{ color: #5b6573; }}
.endblock {{ break-inside: avoid; }}
.disclaimer {{ break-inside: avoid; margin-top: 18px; font-size: 8pt; color: #5b6573; border-top: 1px solid #d6dbe2; padding-top: 6px; }}
</style></head><body>
<section class="cover">
  <div class="brand">KHSEO · SEO &amp; AI-search audit</div>
  <h1>{_e(title)}</h1>
  <div class="target">{_e(a["target"])}</div>
  <div class="meta-line"><span class="status" style="background:{STATUS_COLOR[status]}">{_e(STATUS_NAME[status])}</span>
   &nbsp; Date: {_e(a.get("date") or date.today().isoformat())} &nbsp;·&nbsp; Depth: {_e(scope["depth"])}
   &nbsp;·&nbsp; URLs inspected: {len(scope["urls_inspected"])}{(" &nbsp;·&nbsp; " + _e(a["prepared_by"])) if a.get("prepared_by") else ""}</div>
</section>
<h2>Executive summary</h2>
<div class="summary">{_e(a["summary"])}</div>
<div class="kpis">{kpis}</div>
<h2>Findings</h2>
{"".join(rows) or "<p class='muted'>No findings.</p>"}
{"<h2>Action plan</h2><table><tr><th>#</th><th>Action</th><th>Priority</th><th>Risk</th><th>Owner</th></tr>" + plan + "</table>" if plan else ""}
{"<h2>AI-search readiness</h2><table><tr><th>Area</th><th>Status</th><th>Evidence</th></tr>" + ready + "</table>" if ready else ""}
<div class="cols">
  <div><h2>What KHSEO can do next</h2>{ul(a.get("what_khseo_can_do", []))}</div>
  <div><h2>Uncertain</h2>{ul(a.get("uncertain", []))}</div>
</div>
<h2>Scope &amp; method</h2>
<p>{_e(scope.get("note", ""))}</p>
{ul(scope["urls_inspected"])}
{"<p><b>Host capabilities:</b></p><div class='caps'>" + caps + "</div>" if caps else ""}
<div class="endblock"><h2>Not tested</h2>
{ul(a["not_tested"])}
<p class="disclaimer">{_e(DISCLAIMER)} Generated by KHSEO audit_report v{VERSION}.</p></div>
</body></html>"""


# =============================================================================== browser engine
def find_browser() -> str | None:
    env = os.environ.get("KHSEO_BROWSER")
    if env and Path(env).exists():
        return env
    for name in ("msedge", "google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "chrome", "brave"):
        p = shutil.which(name)
        if p:
            return p
    pf = [os.environ.get(k, "") for k in ("PROGRAMFILES", "PROGRAMFILES(X86)", "LOCALAPPDATA")]
    candidates = [Path(b) / rel for b in pf if b for rel in (
        "Microsoft/Edge/Application/msedge.exe", "Google/Chrome/Application/chrome.exe",
        "Chromium/Application/chrome.exe", "BraveSoftware/Brave-Browser/Application/brave.exe")]
    candidates += [Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
                   Path("/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"),
                   Path("/Applications/Chromium.app/Contents/MacOS/Chromium")]
    for c in candidates:
        if c.exists():
            return str(c)
    return None


def pdf_via_browser(html_path: Path, pdf_path: Path, browser: str) -> None:
    with tempfile.TemporaryDirectory() as prof:
        cmd = [browser, "--headless=new", "--disable-gpu", "--no-first-run", "--no-default-browser-check",
               f"--user-data-dir={prof}", "--no-pdf-header-footer", f"--print-to-pdf={pdf_path}",
               html_path.resolve().as_uri()]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=120, check=False)
    if not pdf_path.exists() or pdf_path.read_bytes()[:5] != b"%PDF-":
        raise RuntimeError(f"browser did not produce a PDF ({browser})")


# =============================================================================== builtin engine
_W = {
    "F1": [278, 278, 355, 556, 556, 889, 667, 191, 333, 333, 389, 584, 278, 333, 278, 278] + [556] * 10 +
          [278, 278, 584, 584, 584, 556, 1015, 667, 667, 722, 722, 667, 611, 778, 722, 278, 500, 667, 556, 833,
           722, 778, 667, 778, 722, 667, 611, 722, 667, 944, 667, 667, 611, 278, 278, 278, 469, 556, 333, 556,
           556, 500, 556, 556, 278, 556, 556, 222, 222, 500, 222, 833, 556, 556, 556, 556, 333, 500, 278, 556,
           500, 722, 500, 500, 500, 334, 260, 334, 584],
    "F2": [278, 333, 474, 556, 556, 889, 722, 238, 333, 333, 389, 584, 278, 333, 278, 278] + [556] * 10 +
          [333, 333, 584, 584, 584, 611, 975, 722, 722, 722, 722, 667, 611, 778, 722, 278, 556, 722, 611, 833,
           722, 778, 667, 778, 722, 667, 611, 722, 667, 944, 667, 667, 611, 333, 278, 333, 584, 556, 333, 556,
           611, 556, 611, 556, 333, 611, 611, 278, 278, 556, 278, 889, 611, 611, 611, 611, 389, 556, 333, 611,
           556, 778, 556, 556, 500, 389, 280, 389, 584],
}
_TRANSLIT = {"—": "-", "–": "-", "‘": "'", "’": "'", "“": '"', "”": '"', "…": "...", "•": "*", "·": "-",
             "→": "->", "←": "<-", "≠": "!=", "≤": "<=", "≥": ">=", "×": "x", "✓": "v", "✗": "x", " ": " "}


def _latin(s: str) -> str:
    s = "".join(_TRANSLIT.get(c, c) for c in str(s))
    return s.encode("latin-1", "replace").decode("latin-1")


def _width(s: str, font: str, size: float) -> float:
    w = _W[font]
    return sum(w[ord(c) - 32] if 32 <= ord(c) <= 126 else 556 for c in s) * size / 1000


def _wrap(text: str, font: str, size: float, maxw: float) -> list[str]:
    lines, cur = [], ""
    for word in _latin(text).split():
        trial = f"{cur} {word}".strip()
        if _width(trial, font, size) <= maxw:
            cur = trial
            continue
        if cur:
            lines.append(cur)
        while _width(word, font, size) > maxw:  # hard-break very long tokens (URLs)
            cut = max(1, int(len(word) * maxw / _width(word, font, size)) - 1)
            lines.append(word[:cut])
            word = word[cut:]
        cur = word
    if cur:
        lines.append(cur)
    return lines or [""]


def _hex(color: str) -> str:
    c = color.lstrip("#")
    return " ".join(f"{int(c[i:i + 2], 16) / 255:.3f}" for i in (0, 2, 4))


class _PDF:
    W, H, M = 595.28, 841.89, 42.0

    def __init__(self, footer: str):
        self.pages: list[list[str]] = []
        self.footer = footer
        self.new_page()

    def new_page(self):
        self.ops: list[str] = []
        self.pages.append(self.ops)
        self.y = self.H - self.M

    def need(self, h: float):
        if self.y - h < self.M + 18:
            self.new_page()

    @staticmethod
    def _esc(s: str) -> str:
        return s.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")

    def text(self, x, y, s, font="F1", size=10, color="#1c2430"):
        self.ops.append(f"BT {_hex(color)} rg /{font} {size} Tf {x:.2f} {y:.2f} Td ({self._esc(_latin(s))}) Tj ET")

    def rect(self, x, y, w, h, color):
        self.ops.append(f"{_hex(color)} rg {x:.2f} {y:.2f} {w:.2f} {h:.2f} re f")

    def line(self, x1, y1, x2, y2, color="#d6dbe2", width=0.8):
        self.ops.append(f"{_hex(color)} RG {width} w {x1:.2f} {y1:.2f} m {x2:.2f} {y2:.2f} l S")

    def para(self, s, font="F1", size=10, color="#1c2430", indent=0.0, gap=3.0, lead=1.35):
        maxw = self.W - 2 * self.M - indent
        for ln in _wrap(s, font, size, maxw):
            self.need(size * lead)
            self.y -= size * lead
            self.text(self.M + indent, self.y, ln, font, size, color)
        self.y -= gap

    def heading(self, s):
        self.need(46)
        if self.y < self.H - self.M - 1:  # not at the top of a fresh page
            self.y -= 12
        self.y -= 14
        self.text(self.M, self.y, s, "F2", 12.5)
        self.y -= 5
        self.line(self.M, self.y, self.W - self.M, self.y)
        self.y -= 6

    def save(self, path: Path):
        n = len(self.pages)
        objs = ["<< /Type /Catalog /Pages 2 0 R >>", None,
                "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>",
                "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>"]
        kids = []
        for i, ops in enumerate(self.pages, 1):
            foot = (f"BT {_hex('#888888')} rg /F1 8 Tf {self.M:.2f} 24 Td ({self._esc(_latin(self.footer))}) Tj ET "
                    f"BT {_hex('#888888')} rg /F1 8 Tf {self.W - self.M - 60:.2f} 24 Td (Page {i} of {n}) Tj ET")
            stream = zlib.compress(("\n".join(ops) + "\n" + foot).encode("latin-1"))
            objs.append(f"<< /Length {len(stream)} /Filter /FlateDecode >>".encode() + b"\nstream\n" + stream + b"\nendstream")
            content_id = len(objs)
            objs.append(f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {self.W} {self.H}] "
                        f"/Resources << /Font << /F1 3 0 R /F2 4 0 R >> >> /Contents {content_id} 0 R >>")
            kids.append(f"{len(objs)} 0 R")
        objs[1] = f"<< /Type /Pages /Kids [{' '.join(kids)}] /Count {n} >>"
        out = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
        offsets = []
        for i, o in enumerate(objs, 1):
            offsets.append(len(out))
            body = o if isinstance(o, bytes) else o.encode("latin-1")
            out += f"{i} 0 obj\n".encode() + body + b"\nendobj\n"
        xref = len(out)
        out += f"xref\n0 {len(objs) + 1}\n0000000000 65535 f \n".encode()
        out += "".join(f"{o:010d} 00000 n \n" for o in offsets).encode()
        out += f"trailer\n<< /Size {len(objs) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode()
        path.write_bytes(bytes(out))


def pdf_builtin(a: dict, pdf_path: Path) -> None:
    title = a.get("site_name") or a["target"]
    d = _PDF(f"KHSEO audit - {title}")
    L, R = d.M, d.W - d.M
    d.text(L, d.y - 10, "KHSEO  -  SEO & AI-SEARCH AUDIT", "F1", 8.5, "#5b6573")
    d.y -= 34
    for ln in _wrap(title, "F2", 20, R - L):
        d.text(L, d.y, ln, "F2", 20)
        d.y -= 24
    d.text(L, d.y, a["target"], "F1", 9.5, "#3d4a5c")
    d.y -= 20
    st = a["overall_status"]
    d.rect(L, d.y - 4, 78, 16, STATUS_COLOR[st])
    d.text(L + 6, d.y + 1, STATUS_NAME[st], "F2", 9.5, "#ffffff")
    d.text(L + 88, d.y + 1, f"Date: {a.get('date') or date.today().isoformat()}   Depth: {a['scope']['depth']}   "
                            f"URLs inspected: {len(a['scope']['urls_inspected'])}", "F1", 9, "#5b6573")
    d.y -= 14
    d.line(L, d.y, R, d.y, "#1c2430", 2)
    d.heading("Executive summary")
    d.para(a["summary"], size=10)
    counts = {p: sum(1 for f in a["findings"] if f["priority"] == p) for p in PRI_COLOR}
    d.need(46)
    bw = (R - L - 18) / 4
    for i, p in enumerate(PRI_COLOR):
        x = L + i * (bw + 6)
        d.rect(x, d.y - 46, bw, 3, PRI_COLOR[p])
        d.text(x + 4, d.y - 24, str(counts[p]), "F2", 16)
        d.text(x + 4, d.y - 36, f"{p} {PRI_NAME[p]}", "F1", 8, "#5b6573")
    d.y -= 52
    d.heading("Findings")
    for f in sorted(a["findings"], key=lambda f: (f["priority"], f.get("id", ""))):
        d.need(52)
        top = d.y
        chip = f"{f['priority']} {PRI_NAME[f['priority']]}"
        d.y -= 12
        d.rect(L + 8, d.y - 2, _width(chip, "F2", 7.5) + 8, 11, PRI_COLOR[f["priority"]])
        d.text(L + 12, d.y + 0.5, chip, "F2", 7.5, "#ffffff")
        meta = f"{f.get('id', '')}   {f['label']}   {LAYER_NAME.get(f['layer'], f['layer'])}"
        if f.get("fix_risk"):
            meta += f"   fix risk {f['fix_risk']}"
        if f.get("owner"):
            meta += f"   owner: {f['owner']}"
        d.text(L + 20 + _width(chip, "F2", 7.5), d.y + 0.5, meta, "F1", 8, "#5b6573")
        d.y -= 2
        d.para(f["message"], "F2", 10, indent=8, gap=1)
        for key, label in (("url", "URL"), ("evidence", "Evidence"), ("fix", "Fix")):
            if f.get(key):
                d.para(f"{label}: {f[key]}", "F1", 9, "#3d4a5c", indent=8, gap=1)
        bottom = d.y - 2
        if d.pages[-1] is d.ops and top > bottom:
            d.rect(L, bottom, 3, top - bottom, PRI_COLOR[f["priority"]])
        d.y -= 6
    if a.get("action_plan"):
        d.heading("Action plan")
        for s in a["action_plan"]:
            d.para(f"{s['step']}. [{s['priority']}{' / ' + s['risk'] if s.get('risk') else ''}] {s['action']}"
                   f"{'  (owner: ' + s['owner'] + ')' if s.get('owner') else ''}", size=9.5, gap=2)
    if a.get("ai_search_readiness"):
        d.heading("AI-search readiness")
        for r in a["ai_search_readiness"]:
            d.para(f"{r['area']}: {r['status']}" + (f"  ({r['evidence']})" if r.get("evidence") else ""), size=9.5, gap=2)
    for head, key in (("What KHSEO can do next", "what_khseo_can_do"), ("Uncertain", "uncertain")):
        if a.get(key):
            d.heading(head)
            for item in a[key]:
                d.para(f"* {item}", size=9.5, gap=1)
    d.heading("Scope & method")
    if a["scope"].get("note"):
        d.para(a["scope"]["note"], size=9.5)
    for u in a["scope"]["urls_inspected"]:
        d.para(f"* {u}", size=9, color="#3d4a5c", gap=1)
    if a.get("capabilities"):
        d.para("Host capabilities: " + ", ".join(f"{k.replace('_', ' ')}: {v}" for k, v in a["capabilities"].items()),
               size=9, color="#3d4a5c")
    d.heading("Not tested")
    for item in a["not_tested"]:
        d.para(f"* {item}", size=9.5, gap=1)
    d.y -= 8
    d.para(DISCLAIMER + f" Generated by KHSEO audit_report v{VERSION} (built-in engine).", size=8, color="#5b6573")
    d.save(pdf_path)


# =============================================================================== CLI
def render(audit: dict, out: Path, engine: str = "auto", html_only: bool = False) -> dict:
    errs = validate_json.check("audit-report", audit)
    if errs:
        raise ValueError("audit JSON is invalid:\n" + "\n".join(f"  - {e}" for e in errs))
    out = Path(out)
    html_path = out if html_only else out.with_suffix(".html")
    html_path.write_text(build_html(audit), encoding="utf-8")
    result = {"html": str(html_path), "pdf": None, "engine": None}
    if html_only:
        return result
    browser = find_browser() if engine in ("auto", "browser") else None
    if engine == "browser" and not browser:
        raise RuntimeError("no Chromium-family browser found (set KHSEO_BROWSER to its path)")
    if browser:
        try:
            pdf_via_browser(html_path, out, browser)
            result.update(pdf=str(out), engine=f"browser ({Path(browser).name})")
            return result
        except (RuntimeError, OSError, subprocess.SubprocessError) as e:
            if engine == "browser":
                raise
            print(f"audit_report: browser engine failed ({e}); using built-in engine", file=sys.stderr)
    pdf_builtin(audit, out)
    result.update(pdf=str(out), engine="builtin")
    return result


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Render a KHSEO audit JSON to HTML + PDF")
    ap.add_argument("audit", help="audit JSON (schemas/audit-report.schema.json)")
    ap.add_argument("-o", "--out", required=True, help="output .pdf (or .html with --html-only)")
    ap.add_argument("--engine", choices=["auto", "browser", "builtin"], default="auto")
    ap.add_argument("--html-only", action="store_true")
    a = ap.parse_args(argv)
    try:
        audit = json.loads(Path(a.audit).read_text(encoding="utf-8"))
        r = render(audit, Path(a.out), a.engine, a.html_only)
    except (OSError, ValueError, RuntimeError) as e:
        print(f"audit_report: {e}", file=sys.stderr)
        return 1 if isinstance(e, (ValueError, RuntimeError)) else 2
    print(f"HTML: {r['html']}" + (f"\nPDF:  {r['pdf']}  [{r['engine']}]" if r["pdf"] else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
