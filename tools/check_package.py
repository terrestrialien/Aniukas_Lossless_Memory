#!/usr/bin/env python3
"""Check public-package links, names, license and accidental local artifacts.

This is a release hygiene check, not a secret scanner or a legal assessment.
"""
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parent.parent
SKIP = {".git", ".venv", "venv", "__pycache__", ".pytest_cache", "dist", "build", "bin", "obj"}
REQUIRED = (
    "README.md", "BUILD_SPEC.md", "LICENSE", "ATTRIBUTION.md", "CONTRIBUTING.md",
    "requirements-dev.txt", ".gitattributes", ".gitignore", "docs/REQUIREMENTS.md",
    "docs/requirements.json", "docs/REFERENCE_FORMAT.md", "docs/ACCEPTANCE.md",
    "docs/ADAPTATION.md", "conformance/README.md",
    ".github/workflows/validate.yml", "tools/check_all.py",
    "tools/check_requirements.py", "tools/check_conformance_cases.py",
    "examples/WALKTHROUGH.md",
    "examples/REFERENCE_IMPLEMENTATIONS.md", ".github/workflows/reference-examples.yml",
    "examples/reference-js/evidence.mjs", "examples/reference-js/evidence.test.mjs",
    "examples/reference-csharp/Program.cs", "examples/reference-csharp/ReferenceEvidence.csproj",
)


def source_files():
    return [p for p in ROOT.rglob("*") if p.is_file() and not SKIP.intersection(p.relative_to(ROOT).parts)]


def correct_case(path):
    current = ROOT
    for part in path.relative_to(ROOT).parts:
        if part not in {p.name for p in current.iterdir()}:
            return False
        current /= part
    return True


def main():
    problems = []
    for name in REQUIRED:
        if not (ROOT / name).is_file():
            problems.append("missing " + name)
    license_path = ROOT / "LICENSE"
    if license_path.exists():
        license_text = license_path.read_text(encoding="utf-8")
        if "MIT License" not in license_text or "Copyright (c) 2026 Andrius Cincys" not in license_text:
            problems.append("root MIT license or author notice missing")
    link_count = 0
    names = {}
    for path in source_files():
        rel = path.relative_to(ROOT).as_posix()
        folded = rel.casefold()
        if folded in names:
            problems.append("case-insensitive path collision: " + rel)
        names[folded] = rel
        if path.is_symlink():
            problems.append("symlink needs release review: " + rel)
        if path.suffix in {".sqlite", ".sqlite3", ".db", ".pyc", ".zip"} or path.name.startswith(".env"):
            problems.append("unexpected local/private artifact: " + rel)
        if path.suffix not in {".md", ".json", ".txt", ".yml", ".yaml"}:
            continue
        text = path.read_text(encoding="utf-8")
        if re.search(r"(?i)\b[A-Z]:[\\/](?:Users|Memory)[\\/]", text):
            problems.append("machine-specific path in " + rel)
        if path.suffix != ".md":
            continue
        # Ignore illustrative Markdown inside fenced code blocks.
        prose = re.sub(r"(?ms)^```.*?^```[^\n]*", "", text)
        for match in re.finditer(r"\[[^\]\n]+\]\(([^)\n]+)\)", prose):
            href = match.group(1).strip().strip("<>")
            parsed = urlsplit(href)
            if parsed.scheme or not parsed.path:
                continue
            target = (path.parent / unquote(parsed.path)).resolve()
            link_count += 1
            try:
                target.relative_to(ROOT)
            except ValueError:
                problems.append(f"link escapes package: {rel}: {href}")
                continue
            if not target.exists():
                problems.append(f"broken local link: {rel}: {href}")
            elif not correct_case(target):
                problems.append(f"link case mismatch: {rel}: {href}")
    print(f"Package: {len(names)} files, {link_count} local links checked")
    for problem in problems:
        print("ERROR: " + problem)
    if not problems:
        print("Public-package checks passed (not a comprehensive privacy audit).")
    return bool(problems)


if __name__ == "__main__":
    raise SystemExit(main())
