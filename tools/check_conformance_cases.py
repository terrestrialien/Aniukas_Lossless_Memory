#!/usr/bin/env python3
"""Run language-neutral conformance cases against the reference fixture checker.

The cases are portable data. This Python program is one reference adapter, not the
required implementation language for a memory system.
"""
import copy
import ast
import json
from pathlib import Path
import re
import shutil
import sys
import tempfile

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from check_pointers import check
from gen_examples import build, canonical, digest, jsonbytes, primary_bytes
from validate_examples import decode

CASES = ROOT / "conformance" / "cases.json"
MEMORY = ROOT / "examples" / "memory"

# A type is assigned only after the exact expected diagnostic is observed. These
# prefixes are intentionally more specific than a generic "validation failed".
DIAGNOSTIC_CODES = (
    ("missing/unsafe file:", "SOURCE_UNAVAILABLE"),
    ("chunk hash/byte length mismatch", "SOURCE_UNAVAILABLE"),
    ("original bytes do not match", "SOURCE_UNAVAILABLE"),
    ("unsafe portable path:", "FORBIDDEN"),
    ("unauthorized cross-scope write", "FORBIDDEN"),
    ("grant does not authorize", "FORBIDDEN"),
    ("unauthorized grant issuer", "FORBIDDEN"),
    ("grant inactive", "FORBIDDEN"),
    ("stale reviewed dependency", "STALE_REVIEW"),
    ("reviewed source was not available", "STALE_REVIEW"),
    ("not available at read snapshot", "STALE_REVIEW"),
    ("stale expected revision", "STALE_REVISION"),
    ("primary budget exceeded", "BUDGET_EXCEEDED"),
    ("rendered primary differs", "PROJECTION_STALE"),
    ("current projection disagrees", "PROJECTION_STALE"),
    ("historical transitions changed", "SNAPSHOT_UNAVAILABLE"),
    ("immutable entity changed", "SNAPSHOT_UNAVAILABLE"),
    ("unsupported required extensions", "UNSUPPORTED_FORMAT"),
    ("duplicate JSON key", "UNSUPPORTED_FORMAT"),
    ("JSON bytes must be UTF-8", "UNSUPPORTED_FORMAT"),
    ("does not match", "UNSUPPORTED_FORMAT"),
    ("Additional properties", "UNSUPPORTED_FORMAT"),
    ("'reason' is a required property", "UNSUPPORTED_FORMAT"),
    ("evidence_gap", "EVIDENCE_INSUFFICIENT"),
    ("review_receipt_ids", "EVIDENCE_INSUFFICIENT"),
    ("intent", "EVIDENCE_INSUFFICIENT"),
    ("confidence", "EVIDENCE_INSUFFICIENT"),
    ("confirmation lacks adopted evidence", "EVIDENCE_INSUFFICIENT"),
    ("adoption_evidence", "EVIDENCE_INSUFFICIENT"),
    ("time_note", "EVIDENCE_INSUFFICIENT"),
    ("not valid under any", "EVIDENCE_INSUFFICIENT"),
    ("missing record", "BROKEN_REFERENCE"),
    ("missing log-manifest", "BROKEN_REFERENCE"),
    ("evidence range", "BROKEN_REFERENCE"),
    ("backlinks", "BROKEN_REFERENCE"),
    ("duplicate entity ID", "BROKEN_REFERENCE"),
    ("duplicate message ordinal", "BROKEN_REFERENCE"),
    ("chunk bounds/order", "BROKEN_REFERENCE"),
    ("revision count mismatch", "BROKEN_REFERENCE"),
    ("pinned base is unrelated", "BROKEN_REFERENCE"),
    ("nonreciprocal or stale child/base", "BROKEN_REFERENCE"),
    ("registered derivative missing", "BROKEN_REFERENCE"),
    ("child scope", "BROKEN_REFERENCE"),
    ("invalid conflict transition order/origin", "BROKEN_REFERENCE"),
    ("invalid audit coverage", "BROKEN_REFERENCE"),
    ("authoritative writes", "BROKEN_REFERENCE"),
    ("mixed instance namespaces", "BROKEN_REFERENCE"),
)

def diagnose_code(message):
    matches = [(len(phrase), code) for phrase, code in DIAGNOSTIC_CODES if phrase in message]
    if not matches:
        raise ValueError(f"diagnostic has no unambiguous typed mapping: {message}")
    longest = max(length for length, _ in matches)
    codes = {code for length, code in matches if length == longest}
    if len(codes) != 1:
        raise ValueError(f"diagnostic has no unambiguous typed mapping: {message}")
    return codes.pop()

def safe_file(memory, name):
    path = (memory / name).resolve()
    if Path(name).is_absolute() or not path.is_relative_to(memory.resolve()):
        raise ValueError(f"case path escapes fixture: {name}")
    return path

def pointer_tokens(pointer):
    if not pointer.startswith("/"):
        raise ValueError(f"JSON Pointer must begin with /: {pointer}")
    return [part.replace("~1", "/").replace("~0", "~") for part in pointer[1:].split("/")]

def at(value, pointer):
    for part in pointer_tokens(pointer):
        value = value[int(part)] if isinstance(value, list) else value[part]
    return value

def parent_at(value, pointer):
    tokens = pointer_tokens(pointer)
    for part in tokens[:-1]:
        value = value[int(part)] if isinstance(value, list) else value[part]
    return value, tokens[-1]

def load_document(path, line=None):
    if line is None:
        return json.loads(path.read_bytes())
    return [json.loads(row) for row in path.read_bytes().splitlines()]

def save_document(path, value, line=None):
    if line is None:
        path.write_bytes(jsonbytes(value))
    else:
        path.write_bytes(b"".join(canonical(row) + b"\n" for row in value))

def edit_json(memory, operation):
    path = safe_file(memory, operation["file"])
    line = operation.get("line")
    document = load_document(path, line)
    target = document if line is None else document[line]
    container, key = parent_at(target, operation["pointer"])
    action = operation["op"]
    if action == "set":
        if isinstance(container, list):
            container[int(key)] = operation["value"]
        else:
            container[key] = operation["value"]
    elif action == "remove":
        if isinstance(container, list):
            container.pop(int(key))
        else:
            del container[key]
    elif action == "append":
        array = at(target, operation["pointer"])
        if not isinstance(array, list):
            raise ValueError("append target is not an array")
        array.append(operation["value"])
    else:
        raise ValueError(f"unknown JSON operation: {action}")
    save_document(path, document, line)

def recompute(memory, operation):
    mode = operation["kind"]
    path = safe_file(memory, operation["file"])
    if mode == "commit_digest":
        value = load_document(path)
        value["payload_sha256"] = digest(canonical({k: v for k, v in value.items() if k != "payload_sha256"}))
        save_document(path, value)
    elif mode == "revision_snapshot":
        revision = load_document(path)
        revision["snapshot_sha256"] = digest(canonical(revision["snapshot"]))
        save_document(path, revision)
        record_path = memory / "record" / (revision["record_id"] + ".json")
        record = load_document(record_path)
        if record["current_revision_id"] == revision["id"]:
            record["current"] = copy.deepcopy(revision["snapshot"])
            save_document(record_path, record)
            records = {p.stem: load_document(p) for p in (memory / "record").glob("*.json")}
            for work_path in (memory / "working-set").glob("*.json"):
                working = load_document(work_path)
                raw = primary_bytes(working["scope_id"], working["entries"], records)
                safe_file(memory, working["rendered_file"]).write_bytes(raw)
                working.update(rendered_sha256=digest(raw), actual_bytes=len(raw))
                save_document(work_path, working)
    elif mode == "chunk_digest":
        manifest = load_document(path)
        index = operation.get("index", 0)
        chunk = manifest["chunks"][index]
        raw = safe_file(memory, chunk["file"]).read_bytes()
        chunk.update(sha256=digest(raw), byte_length=len(raw))
        save_document(path, manifest)
    else:
        raise ValueError(f"unknown recomputation: {mode}")

def apply(memory, operation):
    action = operation["op"]
    if action in {"set", "remove", "append"}:
        edit_json(memory, operation)
    elif action == "recompute":
        recompute(memory, operation)
    elif action == "copy_file":
        shutil.copyfile(safe_file(memory, operation["from"]), safe_file(memory, operation["to"]))
    elif action == "delete_file":
        safe_file(memory, operation["file"]).unlink()
    elif action == "replace_utf8":
        path = safe_file(memory, operation["file"])
        raw = path.read_bytes()
        old = operation["old"].encode("utf-8")
        if raw.count(old) != operation.get("count", 1):
            raise ValueError(f"replace count differed for {path}")
        path.write_bytes(raw.replace(old, operation["new"].encode("utf-8")))
    elif action == "repeat_byte":
        value = operation["byte"]
        if not isinstance(value, int) or not 0 <= value <= 255:
            raise ValueError("byte must be an integer from 0 to 255")
        safe_file(memory, operation["file"]).write_bytes(bytes([value]) * operation["count"])
    elif action == "lf_to_crlf":
        path = safe_file(memory, operation["file"])
        raw = path.read_bytes()
        if b"\r" in raw or b"\n" not in raw:
            raise ValueError("input must contain LF with no CR")
        path.write_bytes(raw.replace(b"\n", b"\r\n"))
    else:
        raise ValueError(f"unknown operation: {action}")

def assert_data(memory, assertion):
    mode = assertion["op"]
    if mode == "equals":
        path = safe_file(memory, assertion["file"])
        doc = load_document(path, assertion.get("line"))
        if "line" in assertion:
            doc = doc[assertion["line"]]
        actual = at(doc, assertion["pointer"])
        assert actual == assertion["value"], f"expected {assertion['value']!r}; got {actual!r}"
    elif mode == "length":
        doc = load_document(safe_file(memory, assertion["file"]), assertion.get("line"))
        if "line" in assertion:
            doc = doc[assertion["line"]]
        actual = len(at(doc, assertion["pointer"]))
        assert actual == assertion["value"], f"expected length {assertion['value']}; got {actual}"
    elif mode == "generated_bytes_match":
        expected = build()
        actual = {p.relative_to(memory).as_posix(): p.read_bytes() for p in memory.rglob("*") if p.is_file()}
        assert expected == actual, "generated bytes differ from reference fixture"
        assert all(b"\r" not in data for name, data in actual.items() if name.endswith((".json", ".jsonl"))), "CR in JSON"
    elif mode == "source_byte_selectors_match":
        lines = safe_file(memory, assertion["file"]).read_bytes().splitlines()
        messages = [json.loads(line) for line in lines]
        source = safe_file(memory, assertion["source_file"]).read_bytes()
        assert len(messages) == assertion["message_count"]
        assert len({m["timestamp"] for m in messages}) == assertion["message_count"]
        assert {m["role"] for m in messages} == set(assertion["roles"])
        for message in messages:
            assert message["time_note"] is None
            prefix = f'{message["timestamp"]} | {message["role"]} | '.encode("utf-8")
            start, end = message["original_byte_start"], message["original_byte_end"]
            assert source[start-len(prefix):start] == prefix
            assert source[start:end].decode("utf-8") == message["text"]
        for phrase in assertion["reason_phrases"]:
            assert any(phrase in m["text"] for m in messages), f"missing example rationale: {phrase}"
    else:
        raise ValueError(f"unknown assertion: {mode}")

def run_case(case, baseline, temp_root):
    memory = temp_root / case["id"]
    shutil.copytree(baseline, memory)
    for operation in case["operations"]:
        apply(memory, operation)
    for assertion in case.get("assertions", []):
        assert_data(memory, assertion)
    errors = check(memory, baseline if case.get("compare_baseline") else None)
    expected = case["expect"]
    if expected["result"] == "valid":
        if errors:
            raise AssertionError(f"expected valid fixture; got {errors}")
    else:
        needle = expected["diagnostic_contains"]
        matches = [error for error in errors if needle in error]
        if not matches:
            raise AssertionError(f"expected diagnostic {needle!r}; got {errors}")
        if not any(diagnose_code(message) == expected["error_code"] for message in matches):
            raise AssertionError(f"wrong typed error for {needle!r}: {matches}")
    return len(errors)

def main():
    suite = decode(CASES.read_bytes())
    schema = decode((ROOT / "conformance" / "cases.schema.json").read_bytes())
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.Draft202012Validator(schema).validate(suite)
    ids = [case["id"] for case in suite["cases"]]
    if len(ids) != len(set(ids)) or not all(re.fullmatch(r"[a-z0-9-]+", ident) for ident in ids):
        raise ValueError("case IDs must be unique lowercase slugs")
    tree = ast.parse((ROOT / "tests" / "test_contracts.py").read_text(encoding="utf-8"))
    reference_tests = {node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef) and node.name.startswith("test_")}
    covered_tests = {case["source_test"] for case in suite["cases"]}
    if covered_tests != reference_tests:
        raise ValueError(f"conformance coverage mismatch: missing={sorted(reference_tests - covered_tests)}, unknown={sorted(covered_tests - reference_tests)}")
    errors = check(MEMORY)
    if errors:
        raise ValueError(f"reference fixture is invalid: {errors}")
    # The normative type vocabulary comes from DATA_CONTRACTS, not this runner.
    contract = (ROOT / "docs" / "DATA_CONTRACTS.md").read_text(encoding="utf-8")
    available_codes = set(re.findall(r"`([A-Z][A-Z_]+)`", contract.split("## Error semantics", 1)[1]))
    with tempfile.TemporaryDirectory(prefix="alm-portable-cases-") as scratch:
        for case in suite["cases"]:
            if case["expect"]["result"] == "error" and case["expect"]["error_code"] not in available_codes:
                raise ValueError(f"{case['id']}: undeclared error code")
            try:
                run_case(case, MEMORY, Path(scratch))
            except Exception as exc:
                raise AssertionError(f"{case['id']}: {exc}") from exc
            print(f"PASS {case['id']}")
    print(f"portable conformance cases: {len(ids)} passed")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
