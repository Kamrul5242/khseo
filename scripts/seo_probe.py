#!/usr/bin/env python3
"""KHSEO seo_probe — stdlib-only single-page SEO / AI-search probe.

Usage:
    python seo_probe.py https://example.com/            # human-readable report
    python seo_probe.py https://example.com/ --json     # machine-readable
    python seo_probe.py page.html [--base https://example.com/page]   # local file (no network checks)

Everything reported is OBSERVED for the given URL at fetch time only. It does not crawl the site,
does not execute JavaScript, and cannot see what Google has indexed.
"""
from __future__ import annotations

import argparse
import gzip
import json
import re
import sys
import urllib.error
import urllib.request
import urllib.robotparser
import zlib
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse

VERSION = "1.0.0"
UA = "Mozilla/5.0 (compatible; KHSEO-probe/1.0; +https://github.com/Kamrul5242/khseo)"
TIMEOUT = 20
MAX_BYTES = 5_000_000

AI_BOTS = [
    "GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "Claude-SearchBot", "Claude-User",
    "PerplexityBot", "Google-Extended", "Applebot-Extended", "CCBot", "Bytespider", "Meta-ExternalAgent",
]
SEARCH_BOTS = ["Googlebot", "Bingbot"]

CHALLENGE_PATTERNS = [
    r"<title>\s*Just a moment", r"cf-chl-", r"challenge-platform", r"Attention Required! \| Cloudflare",
    r"g-recaptcha", r"h-captcha", r"captcha-delivery\.com", r"_Incapsula_Resource", r"px-captcha",
    r"Access Denied</title>", r"verify you are human",
    r"window\.rbzns", r"rbzid",  # Reblaze
    r"/_Incapsula_", r"ak_bmsc", r"datadome", r"__cf_bm",
]


# ----------------------------------------------------------------------------- HTML parsing
class PageParser(HTMLParser):
    SKIP_TEXT = {"script", "style", "noscript", "template", "svg"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title: str | None = None
        self.title_count = 0
        self.metas: list[dict] = []
        self.links: list[dict] = []
        self.anchors: list[dict] = []
        self.images: list[dict] = []
        self.headings: list[tuple[str, str]] = []
        self.jsonld_raw: list[str] = []
        self.html_lang: str | None = None
        self.text_parts: list[str] = []
        self._stack: list[str] = []
        self._cur_heading: str | None = None
        self._heading_buf: list[str] = []
        self._in_title = False
        self._title_buf: list[str] = []
        self._in_jsonld = False
        self._jsonld_buf: list[str] = []
        self._cur_anchor: dict | None = None

    def handle_starttag(self, tag, attrs):
        a = {k.lower(): (v or "") for k, v in attrs}
        self._stack.append(tag)
        if tag == "html":
            self.html_lang = a.get("lang")
        elif tag == "title":
            self._in_title = True
            self._title_buf = []
            self.title_count += 1
        elif tag == "meta":
            self.metas.append(a)
        elif tag == "link":
            self.links.append(a)
        elif tag == "img":
            self.images.append(a)
        elif tag == "a":
            self._cur_anchor = {"href": a.get("href"), "rel": a.get("rel", ""), "text": []}
        elif tag in ("h1", "h2", "h3"):
            self._cur_heading = tag
            self._heading_buf = []
        elif tag == "script" and a.get("type", "").lower().strip() == "application/ld+json":
            self._in_jsonld = True
            self._jsonld_buf = []

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)

    def handle_endtag(self, tag):
        if tag == "title" and self._in_title:
            self._in_title = False
            if self.title is None:
                self.title = " ".join("".join(self._title_buf).split())
        elif tag == "script" and self._in_jsonld:
            self._in_jsonld = False
            self.jsonld_raw.append("".join(self._jsonld_buf))
        elif tag == self._cur_heading:
            self.headings.append((tag, " ".join("".join(self._heading_buf).split())))
            self._cur_heading = None
        elif tag == "a" and self._cur_anchor is not None:
            self._cur_anchor["text"] = " ".join("".join(self._cur_anchor["text"]).split())
            self.anchors.append(self._cur_anchor)
            self._cur_anchor = None
        # pop to the matching tag (HTML is forgiving)
        if tag in self._stack:
            while self._stack:
                if self._stack.pop() == tag:
                    break

    def handle_data(self, data):
        if self._in_title:
            self._title_buf.append(data)
        if self._in_jsonld:
            self._jsonld_buf.append(data)
            return
        if self._cur_heading:
            self._heading_buf.append(data)
        if self._cur_anchor is not None:
            self._cur_anchor["text"].append(data)
        if not any(t in self.SKIP_TEXT for t in self._stack):
            self.text_parts.append(data)


# ----------------------------------------------------------------------------- fetching
class _RecordingRedirect(urllib.request.HTTPRedirectHandler):
    def __init__(self):
        self.chain: list[tuple[int, str]] = []

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        self.chain.append((code, newurl))
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def fetch(url: str, ua: str = UA) -> dict:
    rec = _RecordingRedirect()
    opener = urllib.request.build_opener(rec)
    # Ask only for encodings the stdlib can decode (no brotli).
    req = urllib.request.Request(url, headers={"User-Agent": ua, "Accept": "text/html,*/*;q=0.8",
                                               "Accept-Encoding": "gzip, deflate"})
    out = {"url": url, "final_url": url, "status": None, "headers": {}, "body": "", "redirects": [], "error": None}
    try:
        with opener.open(req, timeout=TIMEOUT) as r:
            out["status"] = r.status
            out["final_url"] = r.geturl()
            out["headers"] = {k.lower(): v for k, v in r.headers.items()}
            raw = r.read(MAX_BYTES)
    except urllib.error.HTTPError as e:
        out["status"] = e.code
        out["headers"] = {k.lower(): v for k, v in (e.headers or {}).items()}
        try:
            raw = e.read(MAX_BYTES)
        except Exception:
            raw = b""
    except Exception as e:  # DNS, TLS, timeout
        out["error"] = f"{type(e).__name__}: {e}"
        raw = b""
    out["redirects"] = rec.chain
    enc = out["headers"].get("content-encoding", "").lower()
    try:
        if "gzip" in enc or raw[:2] == b"\x1f\x8b":
            raw = gzip.decompress(raw)
        elif "deflate" in enc:
            try:
                raw = zlib.decompress(raw)
            except zlib.error:
                raw = zlib.decompress(raw, -zlib.MAX_WBITS)
    except Exception as e:
        out["error"] = out["error"] or f"could not decode {enc or 'body'}: {e}"
    charset = "utf-8"
    m = re.search(r"charset=([\w-]+)", out["headers"].get("content-type", ""), re.I)
    if m:
        charset = m.group(1)
    out["body"] = raw.decode(charset, errors="replace")
    return out


# ----------------------------------------------------------------------------- analysis
def _meta(parser: PageParser, key: str, attr: str = "name") -> str | None:
    for m in parser.metas:
        if m.get(attr, "").lower() == key.lower():
            return m.get("content")
    return None


def _jsonld_types(obj) -> list[str]:
    types: list[str] = []
    if isinstance(obj, list):
        for o in obj:
            types += _jsonld_types(o)
    elif isinstance(obj, dict):
        t = obj.get("@type")
        if isinstance(t, str):
            types.append(t)
        elif isinstance(t, list):
            types += [x for x in t if isinstance(x, str)]
        if "@graph" in obj:
            types += _jsonld_types(obj["@graph"])
    return types


def analyze_html(html: str, page_url: str) -> dict:
    p = PageParser()
    p.feed(html)
    p.close()
    host = urlparse(page_url).netloc.lower()

    canonicals = [l.get("href") for l in p.links if "canonical" in l.get("rel", "").lower().split()]
    hreflang = [(l.get("hreflang"), l.get("href")) for l in p.links
                if "alternate" in l.get("rel", "").lower().split() and l.get("hreflang")]
    og = {m.get("property"): m.get("content") for m in p.metas if m.get("property", "").startswith("og:")}
    tw = {m.get("name"): m.get("content") for m in p.metas if m.get("name", "").startswith("twitter:")}

    jsonld = []
    for raw in p.jsonld_raw:
        try:
            data = json.loads(raw)
            jsonld.append({"valid": True, "types": _jsonld_types(data)})
        except json.JSONDecodeError as e:
            jsonld.append({"valid": False, "error": f"{e.msg} at line {e.lineno} col {e.colno}", "types": []})

    internal, external, nofollow, empty_anchor = 0, 0, 0, 0
    for a in p.anchors:
        href = (a.get("href") or "").strip()
        if not href or href.startswith(("#", "javascript:", "mailto:", "tel:")):
            continue
        absolute = urljoin(page_url, href)
        if urlparse(absolute).netloc.lower() == host:
            internal += 1
        else:
            external += 1
        if "nofollow" in a.get("rel", "").lower():
            nofollow += 1
        if not a.get("text"):
            empty_anchor += 1

    imgs_missing_alt = [i.get("src", "")[:120] for i in p.images if "alt" not in i]
    text = " ".join(" ".join(p.text_parts).split())
    return {
        "title": p.title,
        "title_count": p.title_count,
        "meta_description": _meta(p, "description"),
        "meta_robots": _meta(p, "robots"),
        "viewport": _meta(p, "viewport"),
        "html_lang": p.html_lang,
        "canonicals": canonicals,
        "hreflang": hreflang,
        "headings": p.headings,
        "h1_count": sum(1 for t, _ in p.headings if t == "h1"),
        "images_total": len(p.images),
        "images_missing_alt": imgs_missing_alt,
        "links_internal": internal,
        "links_external": external,
        "links_nofollow": nofollow,
        "links_without_text": empty_anchor,
        "jsonld": jsonld,
        "open_graph": og,
        "twitter": tw,
        "word_count": len(text.split()),
    }


def analyze_robots(page_url: str) -> dict:
    parts = urlparse(page_url)
    robots_url = f"{parts.scheme}://{parts.netloc}/robots.txt"
    res = fetch(robots_url)
    out = {"url": robots_url, "status": res["status"], "error": res["error"], "sitemaps": [],
           "search_bots": {}, "ai_bots": {}, "disallow_all": False}
    if res["status"] != 200:
        return out
    body = res["body"]
    rp = urllib.robotparser.RobotFileParser()
    rp.parse(body.splitlines())
    for bot in SEARCH_BOTS:
        out["search_bots"][bot] = rp.can_fetch(bot, page_url)
    for bot in AI_BOTS:
        out["ai_bots"][bot] = rp.can_fetch(bot, page_url)
    out["sitemaps"] = re.findall(r"(?im)^\s*sitemap:\s*(\S+)", body)
    out["disallow_all"] = not rp.can_fetch("*", f"{parts.scheme}://{parts.netloc}/")
    return out


def check_sitemap(page_url: str, declared: list[str]) -> dict:
    parts = urlparse(page_url)
    candidates = declared[:3] or [f"{parts.scheme}://{parts.netloc}/sitemap.xml"]
    results = []
    for sm in candidates:
        r = fetch(sm)
        body = r["body"][:200000]
        results.append({
            "url": sm, "status": r["status"],
            "is_xml": body.lstrip().startswith("<?xml") or "<urlset" in body or "<sitemapindex" in body,
            "url_entries": body.count("<loc>"),
            "is_index": "<sitemapindex" in body,
        })
    return {"checked": results}


# ----------------------------------------------------------------------------- findings
def build_findings(fetch_res: dict | None, page: dict, robots: dict | None, sitemap: dict | None) -> list[dict]:
    F: list[dict] = []

    def add(pri, label, msg, evidence=""):
        F.append({"priority": pri, "label": label, "message": msg, "evidence": evidence})

    if fetch_res:
        if fetch_res["error"]:
            add("P0", "OBSERVED", "Page could not be fetched", fetch_res["error"])
            return F
        st = fetch_res["status"]
        if st and st >= 400:
            add("P0", "OBSERVED", f"Page returns HTTP {st}", f"status={st}")
        if len(fetch_res["redirects"]) > 1:
            add("P2", "OBSERVED", f"Redirect chain of {len(fetch_res['redirects'])} hops",
                " -> ".join(f"{c} {u}" for c, u in fetch_res["redirects"]))
        body = fetch_res["body"]
        hits = [pat.replace("\\", "") for pat in CHALLENGE_PATTERNS if re.search(pat, body, re.I)]
        script_shell = (page["word_count"] == 0 and not page["title"] and len(body) < 5000
                        and "<script" in body.lower())
        if (hits and (st in (403, 429, 503) or page["word_count"] < 300)) or script_shell:
            add("P0", "OBSERVED",
                "Bot-challenge / JS shell served instead of content (to this probe's UA and IP; "
                "verify verified-Googlebot access via Search Console URL Inspection)",
                ", ".join(hits[:3]) or f"{len(body)}-byte script-only HTML, 0 words, no <title>")
        elif hits:
            add("P3", "OBSERVED", "Challenge/CAPTCHA script present on page (content still served)", ", ".join(hits[:3]))
        xrt = fetch_res["headers"].get("x-robots-tag", "")
        if "noindex" in xrt.lower():
            add("P0", "OBSERVED", "X-Robots-Tag header contains noindex", f"X-Robots-Tag: {xrt}")
        if urlparse(fetch_res["final_url"]).scheme != "https":
            add("P1", "OBSERVED", "Final URL is not HTTPS", fetch_res["final_url"])

    mr = (page["meta_robots"] or "").lower()
    if "noindex" in mr:
        add("P0", "OBSERVED", "meta robots noindex", f'<meta name="robots" content="{page["meta_robots"]}">')
    if robots:
        if robots["status"] == 200 and robots["disallow_all"]:
            add("P0", "OBSERVED", "robots.txt disallows the whole site for *", robots["url"])
        blocked_search = [b for b, ok in robots["search_bots"].items() if not ok]
        if blocked_search:
            add("P0", "OBSERVED", "robots.txt blocks search crawlers for this URL", ", ".join(blocked_search))
        blocked_ai = [b for b, ok in robots["ai_bots"].items() if not ok]
        if blocked_ai:
            add("P2", "OBSERVED", "robots.txt blocks some AI crawlers (confirm this is intentional)", ", ".join(blocked_ai))
        if robots["status"] not in (200, 404, None):
            add("P1", "OBSERVED", f"robots.txt returns HTTP {robots['status']}", robots["url"])
        if robots["status"] == 200 and not robots["sitemaps"]:
            add("P3", "OBSERVED", "robots.txt does not reference a sitemap", robots["url"])
    if sitemap:
        ok = [s for s in sitemap["checked"] if s["status"] == 200 and s["is_xml"]]
        if not ok:
            add("P1", "OBSERVED", "No reachable XML sitemap found",
                "; ".join(f"{s['url']} -> HTTP {s['status']}" + ("" if s["is_xml"] else " (not XML)")
                          for s in sitemap["checked"]))

    if not page["title"]:
        add("P1", "OBSERVED", "Missing <title>")
    else:
        n = len(page["title"])
        if n < 15 or n > 65:
            add("P3", "OBSERVED", f"Title length {n} chars (aim ~50-60, judged by pixels)", page["title"])
    if page["title_count"] > 1:
        add("P2", "OBSERVED", f"{page['title_count']} <title> tags on the page")
    md = page["meta_description"]
    if not md:
        add("P2", "OBSERVED", "Missing meta description")
    elif len(md) < 70 or len(md) > 170:
        add("P3", "OBSERVED", f"Meta description length {len(md)} chars (aim ~140-160)", md[:170])
    if not page["canonicals"]:
        add("P2", "OBSERVED", "No rel=canonical")
    elif len(set(page["canonicals"])) > 1:
        add("P1", "OBSERVED", "Multiple conflicting canonicals", " | ".join(page["canonicals"]))
    elif fetch_res:
        can = urljoin(fetch_res["final_url"], page["canonicals"][0])
        if can.rstrip("/") != fetch_res["final_url"].split("#")[0].rstrip("/"):
            add("P2", "OBSERVED", "Canonical points to a different URL (fine if intentional)",
                f"final={fetch_res['final_url']} canonical={can}")
    if page["h1_count"] == 0:
        add("P2", "OBSERVED", "No <h1> in raw HTML")
    elif page["h1_count"] > 1:
        add("P3", "OBSERVED", f"{page['h1_count']} <h1> elements")
    if not page["viewport"]:
        add("P1", "OBSERVED", "No viewport meta (mobile rendering)")
    if not page["html_lang"]:
        add("P3", "OBSERVED", "<html> has no lang attribute")
    if page["images_missing_alt"]:
        add("P3", "OBSERVED", f"{len(page['images_missing_alt'])}/{page['images_total']} images without alt attribute",
            ", ".join(page["images_missing_alt"][:3]))
    bad_ld = [j for j in page["jsonld"] if not j["valid"]]
    if bad_ld:
        add("P1", "OBSERVED", f"{len(bad_ld)} JSON-LD block(s) fail to parse", bad_ld[0]["error"])
    if not page["jsonld"]:
        add("P2", "OBSERVED", "No JSON-LD structured data")
    if not page["open_graph"]:
        add("P3", "OBSERVED", "No Open Graph tags (social previews)")
    if page["word_count"] < 150:
        add("P1", "INFERRED", f"Only {page['word_count']} words of text in raw HTML — content may be JS-rendered or thin",
            "compare with the rendered page in a browser")
    order = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
    F.sort(key=lambda f: order[f["priority"]])
    return F


# ----------------------------------------------------------------------------- output
def run(target: str, base: str | None = None, network: bool = True) -> dict:
    is_url = target.startswith(("http://", "https://"))
    fetch_res = robots = sitemap = None
    if is_url:
        fetch_res = fetch(target)
        page_url = fetch_res["final_url"]
        html = fetch_res["body"]
    else:
        with open(target, encoding="utf-8", errors="replace") as fh:
            html = fh.read()
        page_url = base or "http://local.invalid/"
    page = analyze_html(html, page_url)
    if is_url and network and not fetch_res["error"]:
        robots = analyze_robots(page_url)
        sitemap = check_sitemap(page_url, robots.get("sitemaps", []))
    findings = build_findings(fetch_res, page, robots, sitemap)
    not_tested = ["JavaScript rendering", "Core Web Vitals", "index coverage (needs Search Console)",
                  "other pages of the site"]
    if not is_url:
        not_tested = ["HTTP status/headers", "robots.txt", "sitemap"] + not_tested
    return {
        "tool": "khseo-seo_probe", "version": VERSION, "target": target,
        "fetch": None if not fetch_res else {k: fetch_res[k] for k in ("url", "final_url", "status", "redirects", "error")}
                 | {"x_robots_tag": fetch_res["headers"].get("x-robots-tag"),
                    "server": fetch_res["headers"].get("server"),
                    "content_type": fetch_res["headers"].get("content-type")},
        "page": page, "robots": robots, "sitemap": sitemap,
        "findings": findings, "not_tested": not_tested,
    }


def render_text(r: dict) -> str:
    L = [f"KHSEO PROBE v{r['version']} — {r['target']}", "=" * 60]
    f = r["fetch"]
    if f:
        L.append(f"Status: {f['status']}  Final URL: {f['final_url']}  Server: {f.get('server')}")
        if f["redirects"]:
            L.append("Redirects: " + " -> ".join(f"{c} {u}" for c, u in f["redirects"]))
        if f["error"]:
            L.append(f"Fetch error: {f['error']}")
    p = r["page"]
    L += [
        f"Title ({len(p['title'] or '')}): {p['title']}",
        f"Meta description ({len(p['meta_description'] or '')}): {p['meta_description']}",
        f"Meta robots: {p['meta_robots']}   Canonical: {', '.join(p['canonicals']) or '-'}",
        f"Lang: {p['html_lang']}   Viewport: {'yes' if p['viewport'] else 'no'}   Words (raw HTML): {p['word_count']}",
        f"H1 x{p['h1_count']}: " + " | ".join(t for h, t in p["headings"] if h == "h1")[:200],
        f"Images: {p['images_total']} (missing alt: {len(p['images_missing_alt'])})   "
        f"Links: {p['links_internal']} internal / {p['links_external']} external",
        "JSON-LD: " + (", ".join(("OK " if j["valid"] else "INVALID ") + "/".join(j["types"] or ["?"]) for j in p["jsonld"]) or "none"),
        f"Open Graph: {len(p['open_graph'])} tags   Twitter: {len(p['twitter'])} tags   hreflang: {len(p['hreflang'])}",
    ]
    if r["robots"]:
        rb = r["robots"]
        L.append(f"robots.txt: HTTP {rb['status']}   sitemaps declared: {len(rb['sitemaps'])}")
        if rb["ai_bots"]:
            L.append("  AI bots allowed: " + ", ".join(f"{b}={'Y' if ok else 'N'}" for b, ok in rb["ai_bots"].items()))
    if r["sitemap"]:
        for s in r["sitemap"]["checked"]:
            L.append(f"Sitemap {s['url']}: HTTP {s['status']} xml={s['is_xml']} locs={s['url_entries']}")
    L += ["", "FINDINGS"]
    for x in r["findings"]:
        L.append(f"[{x['priority']}] [{x['label']}] {x['message']}" + (f"\n        evidence: {x['evidence']}" if x["evidence"] else ""))
    if not r["findings"]:
        L.append("(none)")
    L += ["", "NOT TESTED: " + ", ".join(r["not_tested"])]
    return "\n".join(L)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="KHSEO single-page SEO/AI-search probe (stdlib only)")
    ap.add_argument("target", help="URL (http/https) or path to a local .html file")
    ap.add_argument("--json", action="store_true", help="emit JSON")
    ap.add_argument("--base", help="page URL to resolve links against when target is a local file")
    ap.add_argument("--no-network-extras", action="store_true", help="skip robots.txt and sitemap checks")
    a = ap.parse_args(argv)
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    result = run(a.target, a.base, network=not a.no_network_extras)
    print(json.dumps(result, indent=2, ensure_ascii=False, default=list) if a.json else render_text(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
