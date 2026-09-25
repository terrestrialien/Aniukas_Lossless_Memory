#!/usr/bin/env python3
"""Validate every JSON/JSONL object in a portable fixture snapshot."""
import argparse
import json
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples" / "memory"

def no_duplicates(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result

def decode(data):
    return json.loads(data.decode("utf-8"), object_pairs_hook=no_duplicates, parse_constant=lambda value: (_ for _ in ()).throw(ValueError(f"invalid JSON number: {value}")))

def load_schema(name):
    return decode((ROOT / "schemas" / f"{name}.schema.json").read_bytes())

def inspect(memory):
    """Return [(path, object)] and diagnostics, preserving duplicate identities."""
    memory = Path(memory)
    rows, errors, validators = [], [], {}
    if not memory.is_dir():
        return [], [f"memory root is not a directory: {memory}"]
    for path in sorted(memory.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(memory).as_posix()
        if path.is_symlink():
            errors.append(f"{relative}: symlink is not permitted in portable fixtures")
            continue
        if path.suffix not in (".json", ".jsonl"):
            if path.suffix not in (".md", ".txt"):
                errors.append(f"{relative}: unknown artifact format")
            continue
        try:
            data = path.read_bytes()
            if b"\r" in data or not data.endswith(b"\n") or data.startswith(b"\xef\xbb\xbf"):
                errors.append(f"{relative}: JSON bytes must be UTF-8 without BOM and with LF final newline")
            chunks = data.splitlines() if path.suffix == ".jsonl" else [data]
            for n, raw in enumerate(chunks, 1):
                value = decode(raw)
                if not isinstance(value, dict):
                    raise ValueError("object required")
                kind = value.get("kind")
                if kind not in validators:
                    if not isinstance(kind, str) or not kind.replace("-", "").isalpha():
                        raise ValueError("invalid or missing kind")
                    schema = load_schema(kind)
                    jsonschema.Draft202012Validator.check_schema(schema)
                    validators[kind] = jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker())
                for failure in validators[kind].iter_errors(value):
                    location = "/".join(map(str, failure.absolute_path)) or "root"
                    errors.append(f"{relative}:{n}:{location}: {failure.message}")
                rows.append((path, value))
        except (ValueError, OSError, UnicodeError, jsonschema.SchemaError) as exc:
            errors.append(f"{relative}: {exc}")
    if not rows:
        errors.append("snapshot contains no JSON entities")
    return rows, errors

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("memory", nargs="?", type=Path, default=EXAMPLES)
    args = parser.parse_args()
    rows, errors = inspect(args.memory)
    for error in errors:
        print(error)
    print(f"shape validation: {len(rows)} objects, {len(errors)} errors")
    return bool(errors)

if __name__ == "__main__":
    raise SystemExit(main())
