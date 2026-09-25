#!/usr/bin/env python3
"""Check the public requirement checklist against the specification and tests.

This is a documentation consistency check. It does not prove that an
implementation satisfies the requirements or that the clauses are complete.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys


FIRST_ID = 1
LAST_ID = 132
MINIMUM_DETAILED_CLAUSES = 164
STATUSES = {"not_reported", "not_implemented", "in_progress", "implemented", "not_applicable"}


def unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def render_requirements(requirements: list[dict]) -> str:
    lines = [
        "# Implementation requirements",
        "",
        "The `ALM-001`–`ALM-132` groups define the behavior to build. A group may",
        "contain several detailed clauses. The [machine-readable checklist](requirements.json)",
        "has fields for an implementer to record status, evidence, and notes. The",
        "[build specification](../BUILD_SPEC.md) explains the architecture; the",
        "[acceptance scenarios](ACCEPTANCE.md) describe behavior to demonstrate.",
        "",
        "Edit implementation status, evidence, and notes directly in JSON. If you",
        "change normative wording or links there, run",
        "`python tools/check_requirements.py --write-markdown` from the repository root",
        "to refresh this page, then run the ordinary checks.",
        "",
        "All clauses below are normative. An acceptance ID is a",
        "verification target, not a claim that a runtime has passed it.",
        "",
    ]
    for req in requirements:
        lines.extend((f"### {req['id']} — {req['title']}", ""))
        if req["statement"].rstrip(".") != req["title"].rstrip("."):
            lines.extend((req["statement"], ""))
        refs = ", ".join(f"§{item}" for item in req["spec_sections"])
        targets = f"Spec: {refs}"
        if req["contract_refs"]:
            targets += " · Contracts: " + ", ".join(req["contract_refs"])
        targets += " · Acceptance: " + ", ".join(req["acceptance_ids"]) + "."
        lines.extend((targets, ""))
        if req["clauses"]:
            lines.extend(("Detailed clauses:", ""))
            lines.extend(f"- {clause}" for clause in req["clauses"])
            lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    checklist_path = root / "docs" / "requirements.json"
    requirements_doc = root / "docs" / "REQUIREMENTS.md"
    try:
        data = json.loads(checklist_path.read_text(encoding="utf-8"), object_pairs_hook=unique_object)
        spec = (root / "BUILD_SPEC.md").read_text(encoding="utf-8")
        contracts = (root / "docs" / "DATA_CONTRACTS.md").read_text(encoding="utf-8")
        acceptance = (root / "docs" / "ACCEPTANCE.md").read_text(encoding="utf-8")
        document = requirements_doc.read_text(encoding="utf-8")
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        return [str(exc)]

    if not isinstance(data, dict) or set(data) != {"schema_version", "requirements"}:
        return ["requirements.json must contain only schema_version and requirements"]
    if data["schema_version"] != "2.0.0":
        errors.append("unsupported checklist schema_version")
    requirements = data["requirements"]
    if not isinstance(requirements, list):
        return errors + ["requirements must be an array"]
    expected_ids = [f"ALM-{index:03d}" for index in range(FIRST_ID, LAST_ID + 1)]
    actual_ids = [item.get("id") if isinstance(item, dict) else None for item in requirements]
    if actual_ids != expected_ids:
        errors.append("requirement IDs must be unique and ordered ALM-001 through ALM-132")

    spec_sections = re.findall(r"^#{2,4}\s+(\d+(?:\.\d+)*)(?:\.\s|\s)", spec, re.M)
    # The applicability matrix also names case IDs. Count only four-column
    # scenario definitions, so a profile row is not mistaken for a duplicate.
    acceptance_ids = re.findall(r"^\|\s*(A\d+)\s*\|[^|\n]*\|[^|\n]*\|[^|\n]*\|\s*$", acceptance, re.M)
    if len(spec_sections) != len(set(spec_sections)):
        errors.append("duplicate BUILD_SPEC section number")
    if len(acceptance_ids) != len(set(acceptance_ids)):
        errors.append("duplicate ACCEPTANCE case ID")
    section_set = set(spec_sections)
    acceptance_set = set(acceptance_ids)
    clause_count = 0
    expected_fields = {"id", "title", "statement", "clauses", "spec_sections",
                       "contract_refs", "acceptance_ids", "implementation"}
    for number, item in enumerate(requirements, start=FIRST_ID):
        if not isinstance(item, dict):
            errors.append(f"entry {number}: requirement must be an object")
            continue
        rid = str(item.get("id", f"entry {number}"))
        if set(item) != expected_fields:
            errors.append(f"{rid}: unexpected or missing fields")
            continue
        for field in ("title", "statement"):
            if not isinstance(item[field], str) or not item[field].strip():
                errors.append(f"{rid}: {field} must be nonempty text")
        for field in ("clauses", "spec_sections", "contract_refs", "acceptance_ids"):
            if not isinstance(item[field], list) or any(not isinstance(x, str) or not x.strip() for x in item[field]):
                errors.append(f"{rid}: {field} must be an array of nonempty strings")
        if any(message.startswith(f"{rid}:") for message in errors):
            continue
        clause_count += len(item["clauses"])
        if len(item["clauses"]) != len(set(item["clauses"])):
            errors.append(f"{rid}: duplicate detailed clause")
        if not item["spec_sections"] or len(item["spec_sections"]) != len(set(item["spec_sections"])):
            errors.append(f"{rid}: missing or repeated specification section")
        if not item["acceptance_ids"] or len(item["acceptance_ids"]) != len(set(item["acceptance_ids"])):
            errors.append(f"{rid}: missing or repeated acceptance ID")
        for section in item["spec_sections"]:
            if section not in section_set:
                errors.append(f"{rid}: missing BUILD_SPEC section {section}")
        for case in item["acceptance_ids"]:
            if case not in acceptance_set:
                errors.append(f"{rid}: missing ACCEPTANCE case {case}")
        for symbol in item["contract_refs"]:
            if not re.search(r"(?<![\w.])" + re.escape(symbol) + r"(?![\w.])", contracts):
                errors.append(f"{rid}: missing DATA_CONTRACTS symbol {symbol}")
        report = item["implementation"]
        if not isinstance(report, dict) or set(report) != {"status", "evidence", "notes"}:
            errors.append(f"{rid}: implementation report needs status, evidence, and notes")
        elif not isinstance(report["status"], str) or report["status"] not in STATUSES or \
                not isinstance(report["evidence"], list) or \
                any(not isinstance(x, str) or not x.strip() for x in report["evidence"]) or \
                not isinstance(report["notes"], str):
            errors.append(f"{rid}: invalid implementation report")
        elif report["status"] == "implemented" and not report["evidence"]:
            errors.append(f"{rid}: implemented requires evidence")
        elif report["status"] == "not_applicable" and not report["notes"].strip():
            errors.append(f"{rid}: not_applicable requires a reason in notes")

    if clause_count < MINIMUM_DETAILED_CLAUSES:
        errors.append(f"detailed clauses fell below the {MINIMUM_DETAILED_CLAUSES}-clause baseline")
    if not errors:
        expected_doc = render_requirements(requirements)
        if document.replace("\r\n", "\n") != expected_doc:
            errors.append("REQUIREMENTS.md differs from requirements.json; regenerate the document")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--write-markdown", action="store_true", help="Refresh REQUIREMENTS.md from the checklist")
    args = parser.parse_args(argv)
    root = args.root.resolve()
    if args.write_markdown:
        try:
            data = json.loads((root / "docs" / "requirements.json").read_text(encoding="utf-8"),
                              object_pairs_hook=unique_object)
            document = render_requirements(data["requirements"])
            (root / "docs" / "REQUIREMENTS.md").write_text(document, encoding="utf-8", newline="\n")
        except (OSError, UnicodeError, json.JSONDecodeError, ValueError, KeyError, TypeError) as exc:
            print("REQUIREMENTS FAIL: " + str(exc), file=sys.stderr)
            return 1
    errors = validate(root)
    if errors:
        for error in errors:
            print("REQUIREMENTS FAIL: " + error, file=sys.stderr)
        return 1
    print("REQUIREMENTS PASS: 132 groups, at least 164 detailed clauses, and all specification and acceptance links resolve.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
