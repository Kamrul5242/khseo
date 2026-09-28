#!/usr/bin/env python3
"""Run KHSEO behavior scenarios against a real agent and check its replies.

Usage:
    python tests/behavior/run_live.py --cmd "claude -p" [--only id1,id2] [--timeout 300]

For each scenario the runner builds a prompt (the scenario context + request), pipes it to
`--cmd` on stdin, and checks the agent's reply against the scenario's `expect.must` /
`expect.must_not` regexes (case-insensitive). The agent must already have KHSEO loaded (e.g.
installed as a skill), because this runner tests the host + skill together, not the model alone.

This is a *live* check: it costs model calls and depends on the host. The offline suite
(tests/run_tests.py) only proves every scenario is covered by the spec.
Exit code: 0 all passed, 1 any failed, 2 usage/host error.
"""
from __future__ import annotations

import argparse
import json
import re
import shlex
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROMPT = """You are being evaluated on KHSEO behavior. Treat the CONTEXT as true facts about the
current environment (you cannot inspect it; reason from it). Respond exactly as KHSEO would to
the REQUEST. Do not actually run tools.

CONTEXT: {context}

REQUEST: {request}
"""


def check(reply: str, expect: dict) -> list[str]:
    errs = []
    for pat in expect.get("must", []):
        if not re.search(pat, reply, re.I | re.S):
            errs.append(f"missing expected /{pat}/")
    for pat in expect.get("must_not", []):
        if re.search(pat, reply, re.I | re.S):
            errs.append(f"contains forbidden /{pat}/")
    return errs


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--cmd", required=True, help='agent command that reads a prompt on stdin, e.g. "claude -p"')
    ap.add_argument("--only", help="comma-separated scenario ids")
    ap.add_argument("--timeout", type=int, default=300)
    a = ap.parse_args(argv)
    scenarios = json.loads((HERE / "scenarios.json").read_text(encoding="utf-8"))["scenarios"]
    if a.only:
        wanted = set(a.only.split(","))
        scenarios = [s for s in scenarios if s["id"] in wanted]
    failed = 0
    for s in scenarios:
        prompt = PROMPT.format(context=s["context"], request=s["request"])
        try:
            p = subprocess.run(shlex.split(a.cmd), input=prompt, capture_output=True, text=True,
                               encoding="utf-8", timeout=a.timeout)
        except (OSError, subprocess.TimeoutExpired) as e:
            print(f"HOST ERROR  {s['id']}: {e}")
            return 2
        if p.returncode != 0:
            print(f"HOST ERROR  {s['id']}: exit {p.returncode}: {p.stderr.strip()[:200]}")
            return 2
        errs = check(p.stdout, s["expect"])
        failed += bool(errs)
        print(("FAIL" if errs else "PASS") + f"  {s['id']}" + "".join(f"\n      - {e}" for e in errs))
    print(f"\n{len(scenarios) - failed}/{len(scenarios)} scenarios passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
