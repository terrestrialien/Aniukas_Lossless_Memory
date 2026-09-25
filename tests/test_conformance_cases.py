"""Guard against false positives in the portable conformance adapter."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from check_conformance_cases import CASES, MEMORY, diagnose_code, run_case


class ConformanceAdapterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases = {case["id"]: case for case in json.loads(CASES.read_text(encoding="utf-8"))["cases"]}

    def test_wrong_typed_code_cannot_pass(self):
        case = copy.deepcopy(self.cases["stale-expected-revision"])
        case["expect"]["error_code"] = "FORBIDDEN"
        with tempfile.TemporaryDirectory(prefix="alm-case-guard-") as scratch:
            with self.assertRaisesRegex(AssertionError, "wrong typed error"):
                run_case(case, MEMORY, Path(scratch))

    def test_unrelated_failure_cannot_pass(self):
        case = copy.deepcopy(self.cases["stale-expected-revision"])
        case["operations"] = [{"op": "set", "file": "record/SYS-RULE-0011.json", "pointer": "/instance_id", "value": "unrelated"}]
        with tempfile.TemporaryDirectory(prefix="alm-case-guard-") as scratch:
            with self.assertRaisesRegex(AssertionError, "expected diagnostic"):
                run_case(case, MEMORY, Path(scratch))

    def test_unknown_diagnostic_has_no_invented_type(self):
        with self.assertRaisesRegex(ValueError, "no unambiguous typed mapping"):
            diagnose_code("unrelated validator failure")


if __name__ == "__main__":
    unittest.main()
