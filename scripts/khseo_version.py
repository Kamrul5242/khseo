"""Single source of truth for KHSEO version numbers.

KHSEO_VERSION  release of the whole skill package, read from the VERSION file at the repo root
SPEC_VERSION   the behavior/governance contract (rules, commands, workflows); bumped whenever
               what KHSEO does or asks permission for changes (see RELEASING.md)
SCHEMA_VERSION the JSON contracts in schemas/ (each schema carries x-khseo-schema-version)
Component tools (seo_probe.py, …) keep their own VERSION constants.
"""
from __future__ import annotations

from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent

try:
    KHSEO_VERSION = (_ROOT / "VERSION").read_text(encoding="utf-8").strip()
except OSError:  # scripts copied without the package root
    KHSEO_VERSION = "unknown"
SPEC_VERSION = "1.4"
SCHEMA_VERSION = "1.1"


def versions(probe: str | None = None) -> dict:
    v = {"khseo": KHSEO_VERSION, "spec": SPEC_VERSION, "schema": SCHEMA_VERSION}
    if probe:
        v["probe"] = probe
    return v


def banner(v: dict, brand: bool = True) -> str:
    parts = [f"{'KHSEO' if brand else 'engine'} {v.get('khseo', '?')}", f"spec {v.get('spec', '?')}",
             f"schema {v.get('schema', '?')}"]
    if v.get("probe"):
        parts.append(f"probe {v['probe']}")
    return " · ".join(parts)
