#!/usr/bin/env python3
"""KHSEO meta_tags — build and grade a page's SEO/social <head> tags.

KHSEO (the AI) writes the words; this tool assembles them into correct, escaped HTML and checks
them against search-snippet limits. It never invents content: any field you don't pass is
left out and reported as missing.

Usage:
    python meta_tags.py --title "..." --description "..." --url https://site/page \
        [--site-name "..."] [--image https://...] [--type website|article|product] \
        [--locale en_US] [--twitter-site @handle] [--robots "index, follow"] \
        [--price 24.99 --currency USD] [--keywords "a, b"] [--json]
    python meta_tags.py --spec tags.json [--json]        # same fields as a JSON object
    python meta_tags.py --check page.html [--json]       # grade the tags already in a page

Exit code: 0 no errors (warnings allowed), 1 errors found, 2 usage error.
"""
from __future__ import annotations

import argparse
import html
import json
import sys
from pathlib import Path
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent))

# Arial/Helvetica advance widths (1/1000 em) for ASCII 32..126, used to estimate SERP pixel width.
_W = [278, 278, 355, 556, 556, 889, 667, 191, 333, 333, 389, 584, 278, 333, 278, 278] + [556] * 10 + \
     [278, 278, 584, 584, 584, 556, 1015, 667, 667, 722, 722, 667, 611, 778, 722, 278, 500, 667, 556, 833,
      722, 778, 667, 778, 722, 667, 611, 722, 667, 944, 667, 667, 611, 278, 278, 278, 469, 556, 333, 556,
      556, 500, 556, 556, 278, 556, 556, 222, 222, 500, 222, 833, 556, 556, 556, 556, 333, 500, 278, 556,
      500, 722, 500, 500, 500, 334, 260, 334, 584]
TITLE_PX, TITLE_FONT = 580, 20   # Google desktop title: ~580 px at 20 px Arial (approximate)
DESC_PX, DESC_FONT = 920, 14     # desktop description: ~920 px at 14 px (≈ 2 lines)


def px(text: str, size: int) -> int:
    return round(sum(_W[ord(c) - 32] if 32 <= ord(c) <= 126 else 600 for c in text) * size / 1000)


def grade(spec: dict) -> dict:
    errors, warnings, missing = [], [], []
    t, d, u = spec.get("title"), spec.get("description"), spec.get("url")
    if not t:
        errors.append("title is required")
    else:
        tp = px(t, TITLE_FONT)
        if tp > TITLE_PX:
            warnings.append(f"title ~{tp}px wide (>{TITLE_PX}px): likely truncated in Google; {len(t)} chars")
        if len(t) < 20:
            warnings.append(f"title only {len(t)} chars: probably too vague to match intent")
    if not d:
        missing.append("description")
    else:
        dp = px(d, DESC_FONT)
        if dp > DESC_PX:
            warnings.append(f"description ~{dp}px (>{DESC_PX}px): may be cut off; {len(d)} chars")
        if len(d) < 70:
            warnings.append(f"description only {len(d)} chars: Google is more likely to rewrite it")
    if not u:
        missing.append("url (canonical)")
    else:
        p = urlparse(u)
        if p.scheme not in ("https", "http") or not p.netloc:
            errors.append(f"canonical must be an absolute URL: {u}")
        elif p.scheme == "http":
            warnings.append("canonical uses http://; prefer https://")
        if p.fragment:
            errors.append("canonical must not contain a #fragment")
    img = spec.get("image")
    if img and not urlparse(img).netloc:
        errors.append(f"og:image must be absolute: {img}")
    if not img:
        missing.append("image (social previews will be blank or random)")
    r = (spec.get("robots") or "").lower()
    if "noindex" in r:
        warnings.append("robots contains noindex: this page will be removed from search results")
    if spec.get("keywords"):
        warnings.append("meta keywords are ignored by Google and Bing for ranking; kept only because you asked")
    if spec.get("type") == "product" and not spec.get("price"):
        missing.append("price (product pages)")
    for key in ("title", "description"):
        v = spec.get(key) or ""
        if v and v.upper() == v and any(c.isalpha() for c in v):
            warnings.append(f"{key} is ALL CAPS")
    return {"errors": errors, "warnings": warnings, "missing": missing,
            "title_px": px(t, TITLE_FONT) if t else 0, "description_px": px(d, DESC_FONT) if d else 0}


def build(spec: dict) -> str:
    e = lambda v: html.escape(str(v), quote=True)  # noqa: E731
    L = []
    if spec.get("title"):
        L.append(f"<title>{e(spec['title'])}</title>")
    if spec.get("description"):
        L.append(f'<meta name="description" content="{e(spec["description"])}">')
    L.append(f'<meta name="robots" content="{e(spec.get("robots") or "index, follow, max-image-preview:large")}">')
    if spec.get("keywords"):
        L.append(f'<meta name="keywords" content="{e(spec["keywords"])}">')
    if spec.get("url"):
        L.append(f'<link rel="canonical" href="{e(spec["url"])}">')
    og_type = spec.get("type") or "website"
    L.append(f'<meta property="og:type" content="{e(og_type)}">')
    for prop, key in (("og:title", "title"), ("og:description", "description"), ("og:url", "url"),
                      ("og:site_name", "site_name"), ("og:image", "image"), ("og:locale", "locale")):
        if spec.get(key):
            L.append(f'<meta property="{prop}" content="{e(spec[key])}">')
    if spec.get("image_alt"):
        L.append(f'<meta property="og:image:alt" content="{e(spec["image_alt"])}">')
    if og_type == "product" and spec.get("price"):
        L.append(f'<meta property="product:price:amount" content="{e(spec["price"])}">')
        L.append(f'<meta property="product:price:currency" content="{e(spec.get("currency") or "USD")}">')
    L.append(f'<meta name="twitter:card" content="{"summary_large_image" if spec.get("image") else "summary"}">')
    for name, key in (("twitter:title", "title"), ("twitter:description", "description"),
                      ("twitter:image", "image"), ("twitter:site", "twitter_site")):
        if spec.get(key):
            L.append(f'<meta name="{name}" content="{e(spec[key])}">')
    return "\n".join(L)


def extract(html_text: str) -> dict:
    import seo_probe
    p = seo_probe.analyze_html(html_text, "http://local.invalid/")
    og = p["open_graph"]
    return {"title": p["title"], "description": p["meta_description"],
            "url": (p["canonicals"] or [None])[0], "robots": p["meta_robots"],
            "image": og.get("og:image"), "type": og.get("og:type"), "site_name": og.get("og:site_name"),
            "price": og.get("og:price:amount") or _meta_prop(html_text, "product:price:amount")}


def _meta_prop(html_text: str, prop: str):
    import re
    for m in re.finditer(r"<meta\b[^>]*>", html_text, re.I):
        tag = m.group(0)
        if re.search(r"""property\s*=\s*["']""" + re.escape(prop) + r"""["']""", tag, re.I):
            c = re.search(r"""content\s*=\s*["']([^"']*)["']""", tag, re.I)
            return c.group(1) if c else None
    return None


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Build and grade SEO/social meta tags")
    for f in ("title", "description", "url", "site-name", "image", "image-alt", "type", "locale",
              "twitter-site", "robots", "price", "currency", "keywords"):
        ap.add_argument(f"--{f}")
    ap.add_argument("--spec", help="JSON file with the same fields (snake_case)")
    ap.add_argument("--check", help="grade the tags in an existing HTML file instead of building")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    try:
        if a.check:
            spec = extract(Path(a.check).read_text(encoding="utf-8", errors="replace"))
        elif a.spec:
            spec = json.loads(Path(a.spec).read_text(encoding="utf-8"))
        else:
            spec = {k.replace("-", "_"): v for k, v in vars(a).items()
                    if v is not None and k not in ("spec", "check", "json")}
    except (OSError, ValueError) as ex:
        print(f"meta_tags: {ex}", file=sys.stderr)
        return 2
    g = grade(spec)
    out = {"grade": g} if a.check else {"html": build(spec), "grade": g}
    if a.json:
        print(json.dumps(out, indent=2, ensure_ascii=False))
    else:
        if not a.check:
            print(out["html"] + "\n")
        print(f"Title ~{g['title_px']}px / {TITLE_PX}px   Description ~{g['description_px']}px / {DESC_PX}px")
        for kind in ("errors", "warnings", "missing"):
            for m in g[kind]:
                print(f"[{kind[:-1].upper() if kind != 'missing' else 'MISSING'}] {m}")
        if not any(g[k] for k in ("errors", "warnings", "missing")):
            print("[OK] no issues")
    return 1 if g["errors"] else 0


if __name__ == "__main__":
    sys.exit(main())
