#!/usr/bin/env python3
"""Run all specification-kit checks; never starts a memory service."""
from pathlib import Path
import os
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent


def main():
    checks = [
        ["tools/check_requirements.py"],
        ["tools/gen_schemas.py", "--check"],
        ["tools/gen_examples.py", "--check"],
        ["tools/validate_examples.py"],
        ["tools/check_pointers.py"],
        ["tools/check_conformance_cases.py"],
        ["tools/check_package.py"],
        ["-m", "unittest", "discover", "-s", "tests", "-v"],
    ]
    failures = []
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONUTF8="1")
    for arguments in checks:
        label = " ".join(arguments)
        print("\nCHECK: " + label, flush=True)
        result = subprocess.run([sys.executable, *arguments], cwd=ROOT, env=env)
        if result.returncode:
            failures.append(label)
    if failures:
        print("\nFAILED: " + "; ".join(failures))
        return 1
    print("\nAll specification-kit checks passed. Runtime conformance is not established.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
