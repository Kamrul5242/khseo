#!/usr/bin/env python3
"""KHSEO validate_json — stdlib validator for KHSEO's JSON contracts + honesty lint.

Usage:
    python validate_json.py <schema-name|schema-path> <document.json> [--capabilities caps.json]

    schema-name: audit-report | approval | change-set | validation | capabilities

Supports the JSON Schema subset KHSEO's schemas use: type, required, properties,
additionalProperties:false, enum, const, items, minItems, minLength, minimum, pattern, $ref
(local #/$defs/...). Unknown keywords (format, description, $schema…) are ignored.

Honesty lint (always on), the rule "can't test → NOT VERIFIED, never PASSED":
  * validation: a PASSED check must carry both `method` and `evidence`.
  * validation + --capabilities: a check that `requires` an UNAVAILABLE capability can't be PASSED/FAILED.
  * audit-report: a VERIFIED finding must carry `evidence`; findings about something listed in
    `not_tested` can't be VERIFIED.
  * change-set: `deployed` must be false (deployment is a separate gate).
Exit code: 0 valid, 1 invalid, 2 usage error.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

SCHEMA_DIR = Path(__file__).resolve().parent.parent / "schemas"
_TYPES = {"object": dict, "array": list, "string": str, "boolean": bool, "null": type(None)}


def _type_ok(value, t) -> bool:
    if t == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if t == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    return isinstance(value, _TYPES[t])


def validate(doc, schema: dict, root: dict | None = None, path: str = "$") -> list[str]:
    root = root or schema
    errs: list[str] = []
    if "$ref" in schema:
        ref = schema["$ref"]
        if not ref.startswith("#/"):
            return [f"{path}: unsupported $ref {ref}"]
        target = root
        for part in ref[2:].split("/"):
            target = target[part]
        return validate(doc, target, root, path)
    t = schema.get("type")
    if t is not None:
        types = t if isinstance(t, list) else [t]
        if not any(_type_ok(doc, x) for x in types):
            return [f"{path}: expected {'/'.join(types)}, got {type(doc).__name__}"]
    if "const" in schema and doc != schema["const"]:
        errs.append(f"{path}: must be {json.dumps(schema['const'])}")
    if "enum" in schema and doc not in schema["enum"]:
        errs.append(f"{path}: {json.dumps(doc)} not one of {schema['enum']}")
    if isinstance(doc, str):
        if "minLength" in schema and len(doc) < schema["minLength"]:
            errs.append(f"{path}: shorter than {schema['minLength']}")
        if "pattern" in schema and not re.search(schema["pattern"], doc):
            errs.append(f"{path}: does not match {schema['pattern']}")
    if isinstance(doc, (int, float)) and not isinstance(doc, bool) and "minimum" in schema:
        if doc < schema["minimum"]:
            errs.append(f"{path}: below minimum {schema['minimum']}")
    if isinstance(doc, dict):
        for key in schema.get("required", []):
            if key not in doc:
                errs.append(f"{path}: missing required '{key}'")
        props = schema.get("properties", {})
        for key, val in doc.items():
            extra = schema.get("additionalProperties")
            if key in props:
                errs += validate(val, props[key], root, f"{path}.{key}")
            elif extra is False:
                errs.append(f"{path}: unexpected property '{key}'")
            elif isinstance(extra, dict):
                errs += validate(val, extra, root, f"{path}.{key}")
    if isinstance(doc, list):
        if "minItems" in schema and len(doc) < schema["minItems"]:
            errs.append(f"{path}: needs at least {schema['minItems']} item(s)")
        if "items" in schema:
            for i, item in enumerate(doc):
                errs += validate(item, schema["items"], root, f"{path}[{i}]")
    return errs


def honesty_lint(kind: str, doc, caps: dict | None = None) -> list[str]:
    errs: list[str] = []
    if not isinstance(doc, dict):
        return errs
    if kind == "validation":
        unavailable = set()
        if caps:
            unavailable = {k for k, v in caps.get("capabilities", {}).items() if v == "UNAVAILABLE"}
        for i, c in enumerate(doc.get("checks", [])):
            if not isinstance(c, dict):
                continue
            where = f"$.checks[{i}] ({c.get('name')})"
            if c.get("status") == "PASSED" and not (c.get("method") and c.get("evidence")):
                errs.append(f"{where}: PASSED without method + evidence. Use NOT_VERIFIED if it wasn't run")
            missing = unavailable.intersection(c.get("requires", []))
            if missing and c.get("status") != "NOT_VERIFIED":
                errs.append(f"{where}: needs unavailable {sorted(missing)} so it must be NOT_VERIFIED")
    elif kind == "audit-report":
        not_tested = [s.lower() for s in doc.get("not_tested", []) if isinstance(s, str)]
        for i, f in enumerate(doc.get("findings", [])):
            if not isinstance(f, dict) or f.get("label") != "VERIFIED":
                continue
            if not f.get("evidence"):
                errs.append(f"$.findings[{i}]: VERIFIED finding without evidence")
            text = (f.get("message", "") + " " + f.get("layer", "")).lower()
            for nt in not_tested:
                key = nt.split("(")[0].strip()
                if key and key in text:
                    errs.append(f"$.findings[{i}]: VERIFIED, but '{nt}' is listed as not tested")
    elif kind == "change-set":
        if doc.get("deployed") is True:
            errs.append("$.deployed: a change set can't imply deployment (separate gate)")
    return errs


def load_schema(name_or_path: str) -> tuple[str, dict]:
    p = Path(name_or_path)
    if not p.suffix:
        p = SCHEMA_DIR / f"{name_or_path}.schema.json"
    kind = p.name.replace(".schema.json", "")
    return kind, json.loads(p.read_text(encoding="utf-8"))


def check(kind_or_path: str, doc, caps: dict | None = None) -> list[str]:
    kind, schema = load_schema(kind_or_path)
    return validate(doc, schema) + honesty_lint(kind, doc, caps)


def main(argv=None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    caps = None
    if "--capabilities" in args:
        i = args.index("--capabilities")
        caps = json.loads(Path(args[i + 1]).read_text(encoding="utf-8"))
        del args[i:i + 2]
    if len(args) != 2:
        print(__doc__, file=sys.stderr)
        return 2
    try:
        doc = json.loads(Path(args[1]).read_text(encoding="utf-8"))
        errs = check(args[0], doc, caps)
    except (OSError, ValueError, KeyError) as e:
        print(f"validate_json: {e}", file=sys.stderr)
        return 2
    if errs:
        print("INVALID\n" + "\n".join(f"  - {e}" for e in errs))
        return 1
    print("VALID")
    return 0


if __name__ == "__main__":
    sys.exit(main())
