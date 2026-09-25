"""Mutation tests for contracts that previously escaped the artifact checks."""
import copy
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from check_pointers import check
from gen_examples import build, canonical, digest, generate, jsonbytes, primary_bytes
from validate_examples import inspect


class PortableContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.workspace = tempfile.TemporaryDirectory(prefix="alm-contract-tests-")
        cls.base = Path(cls.workspace.name) / "baseline"
        generate(cls.base)

    @classmethod
    def tearDownClass(cls):
        cls.workspace.cleanup()

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="case-", dir=self.workspace.name)
        self.memory = Path(self.temp.name) / "memory"
        shutil.copytree(self.base, self.memory)

    def tearDown(self):
        self.temp.cleanup()

    def file(self, kind, ident):
        return self.memory / kind / (ident + ".json")

    def get(self, kind, ident):
        return json.loads(self.file(kind, ident).read_text(encoding="utf-8"))

    def put(self, data):
        self.file(data["kind"], data["id"]).write_bytes(jsonbytes(data))

    def mutate(self, kind, ident, change):
        data = self.get(kind, ident)
        change(data)
        self.put(data)
        return data

    def resign_commit(self, ident, change):
        data = self.get("commit", ident)
        change(data)
        data["payload_sha256"] = digest(canonical({k: v for k, v in data.items() if k != "payload_sha256"}))
        self.put(data)

    def mutate_snapshot(self, rid, change, revision_id=None):
        record = self.get("record", rid)
        revision = self.get("revision", revision_id or record["current_revision_id"])
        change(revision["snapshot"])
        revision["snapshot_sha256"] = digest(canonical(revision["snapshot"]))
        self.put(revision)
        if revision["id"] == record["current_revision_id"]:
            record["current"] = copy.deepcopy(revision["snapshot"])
            self.put(record)
            for path in (self.memory / "working-set").glob("*.json"):
                working = json.loads(path.read_text(encoding="utf-8"))
                records = {p.stem: json.loads(p.read_text(encoding="utf-8")) for p in (self.memory / "record").glob("*.json")}
                raw = primary_bytes(working["scope_id"], working["entries"], records)
                (self.memory / working["rendered_file"]).write_bytes(raw)
                working.update(rendered_sha256=digest(raw), actual_bytes=len(raw))
                self.put(working)

    def rewrite_chunk(self, change):
        path = self.memory / "logs/c001.jsonl"
        messages = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
        change(messages)
        data = b"".join(canonical(m) + b"\n" for m in messages)
        path.write_bytes(data)
        self.mutate("log-manifest", "LOG-EXAMPLE", lambda m: m["chunks"][0].update(sha256=digest(data), byte_length=len(data)))

    def assert_problem(self, expected, baseline=None):
        errors = check(self.memory, baseline)
        self.assertTrue(any(expected in e for e in errors), f"Expected {expected!r}; got {errors}")

    def test_baseline_complete_example_passes(self):
        self.assertEqual([], check(self.memory))

    def test_generators_are_deterministic_and_use_actual_lf_bytes(self):
        expected = build()
        self.assertEqual(expected, build())
        actual = {p.relative_to(self.memory).as_posix(): p.read_bytes() for p in self.memory.rglob("*") if p.is_file()}
        self.assertEqual(expected, actual)
        for name, data in actual.items():
            if name.endswith((".json", ".jsonl")):
                self.assertNotIn(b"\r", data, name)
        self.assertIn("résumé".encode(), actual["logs/original.txt"])

    def test_teaching_source_has_distinct_timestamps_speakers_and_reasons(self):
        messages = [json.loads(line) for line in (self.memory / "logs/c001.jsonl").read_bytes().splitlines()]
        original = (self.memory / "logs/original.txt").read_bytes()
        self.assertEqual(22, len(messages))
        self.assertEqual(22, len({m["timestamp"] for m in messages}))
        self.assertEqual({"user", "assistant", "agent"}, {m["role"] for m in messages})
        for message in messages:
            self.assertIsNone(message["time_note"])
            prefix = f'{message["timestamp"]} | {message["role"]} | '.encode("utf-8")
            self.assertEqual(prefix, original[message["original_byte_start"] - len(prefix):message["original_byte_start"]])
            self.assertEqual(message["text"], original[message["original_byte_start"]:message["original_byte_end"]].decode("utf-8"))
        self.assertIn("missing room booking mistaken for a decision to cancel", messages[4]["text"])
        self.assertIn("two volunteers could promise the same item", messages[12]["text"])
        self.assertIn("Members who miss email", messages[18]["text"])

    def test_dangling_bare_graph_id_rejected(self):
        self.mutate_snapshot("SYS-RULE-0011", lambda s: s["edges"].update(related=["MISSING-RECORD"]))
        self.assert_problem("missing record MISSING-RECORD")

    def test_empty_evidence_requires_declared_gap(self):
        self.mutate("revision", "SYS-RULE-0011.r1", lambda r: r.update(source_refs=[]))
        self.assert_problem("evidence_gap")

    def test_evidence_ranges_logs_and_backlinks_are_validated(self):
        for mutation, expected in [(lambda w: w.update(log_id="LOG-MISSING"), "missing log-manifest"), (lambda w: w.update(message_start=999, message_end=1), "evidence range"), (lambda w: w.update(cited_by=["MISSING-REVISION"]), "backlinks")]:
            with self.subTest(expected=expected):
                original = self.get("evidence-window", "WIN-00001")
                self.mutate("evidence-window", "WIN-00001", mutation)
                self.assert_problem(expected)
                self.put(original)

    def test_duplicate_identity_in_second_file_rejected(self):
        source = self.file("record", "SYS-RULE-0011")
        shutil.copyfile(source, source.parent / "duplicate.json")
        self.assert_problem("duplicate entity ID")

    def test_duplicate_json_keys_rejected(self):
        path = self.file("record", "SYS-RULE-0011")
        data = path.read_text(encoding="utf-8").replace('"kind": "record"', '"kind": "record", "kind": "record"')
        path.write_bytes(data.encode("utf-8"))
        self.assert_problem("duplicate JSON key")

    def test_primary_content_and_byte_ceiling_checked(self):
        (self.memory / "primary/GLOBAL.md").write_bytes(b"x" * 30000)
        self.assert_problem("primary budget exceeded")
        self.assert_problem("rendered primary differs")

    def test_ambiguous_parent_array_rejected(self):
        self.mutate_snapshot("LIB-RULE-0006", lambda s: s["edges"].update(parent=["SYS-RULE-0011", "SYS-RULE-0020"]))
        self.assert_problem("Additional properties")

    def test_multi_parent_bases_are_supported(self):
        rec = self.get("record", "LIB-RULE-0006")
        self.assertEqual(2, len(rec["current"]["parent_bases"]))
        self.assertEqual([], check(self.memory))

    def test_derivative_requires_its_reason_and_differences(self):
        self.mutate_snapshot("LIB-RULE-0006", lambda s: s["parent_bases"][0].pop("reason"))
        self.assert_problem("'reason' is a required property")

    def test_high_impact_requires_review(self):
        self.resign_commit("TXN-000006", lambda c: c.update(review_receipt_ids=[]))
        self.assert_problem("review_receipt_ids")

    def test_review_requires_reasoning_not_empty_object(self):
        self.mutate("review-receipt", "REVIEW-0006", lambda r: r.update(intent="", alternatives=[]))
        self.assert_problem("intent")

    def test_stale_review_dependency_rejected(self):
        self.mutate("review-receipt", "REVIEW-0009", lambda r: r["reviewed"][0].update(revision_id="SYS-RULE-0011.r2"))
        self.assert_problem("stale reviewed dependency")

    def test_unconfirmed_inference_cannot_claim_confidence_one(self):
        self.mutate_snapshot("SYS-RULE-0011", lambda s: s["assertion"].update(kind="AI-inferred", adoption_evidence=[]))
        self.assert_problem("confidence")

    def test_promotion_state_and_owner_split_are_representable(self):
        record = self.get("record", "LIB-RULE-0005")
        self.assertEqual("historical-origin", record["current"]["status"])
        for n, expected in [(14, "PROJECT-LIBRARY"), (15, "GLOBAL"), (16, "PROJECT-LIBRARY")]:
            self.assertEqual(expected, self.get("commit", f"TXN-{n:06}")["scope_id"])
        self.assertEqual([], check(self.memory))

    def test_project_owner_cannot_write_global_map(self):
        self.resign_commit("TXN-000006", lambda c: c["writes"].append("map://MAP-SYS-RULE-0011"))
        self.assert_problem("unauthorized cross-scope write")

    def test_payload_actor_cannot_override_granted_principal(self):
        self.resign_commit("TXN-000006", lambda c: c.update(principal_id="principal:governor"))
        self.assert_problem("grant does not authorize")

    def test_agent_cannot_issue_its_own_grant(self):
        self.mutate("grant", "GRANT-LIBRARY", lambda g: g.update(issued_by="principal:library-owner"))
        self.assert_problem("unauthorized grant issuer")

    def test_revocation_evaluated_at_commit_time(self):
        self.mutate("grant", "GRANT-LIBRARY", lambda g: g.update(revoked_at="2026-09-23T12:05:00Z"))
        self.assert_problem("grant inactive")

    def test_trusted_human_user_grant_can_authorize_scope(self):
        self.mutate("grant", "GRANT-LIBRARY", lambda g: g.update(role="USER"))
        self.assertEqual([], check(self.memory))

    def test_source_paths_cannot_escape_export(self):
        self.mutate("log-manifest", "LOG-EXAMPLE", lambda m: m.update(original_file="../outside.txt"))
        self.assert_problem("unsafe portable path")

    def test_chunk_hashes_are_for_bytes_read_from_disk(self):
        path = self.memory / "logs/c001.jsonl"
        path.write_bytes(path.read_bytes().replace(b"accept lending requests by email", b"accept lending requests by phone"))
        self.assert_problem("chunk hash/byte length mismatch")

    def test_duplicate_message_ordinals_rejected(self):
        self.rewrite_chunk(lambda messages: messages[1].update(ordinal=1))
        self.assert_problem("duplicate message ordinal")

    def test_manifest_ranges_match_actual_chunk(self):
        self.mutate("log-manifest", "LOG-EXAMPLE", lambda m: m["chunks"][0].update(message_end=999))
        self.assert_problem("chunk bounds/order")

    def test_unknown_speaker_is_preserved_without_invention(self):
        self.rewrite_chunk(lambda messages: messages[0].update(speaker=None, role="unknown", identity_note="Original importer had no speaker metadata."))
        self.assertEqual([], check(self.memory))

    def test_original_byte_selectors_are_verified(self):
        self.rewrite_chunk(lambda messages: messages[0].update(original_byte_end=messages[0]["original_byte_start"] + 1))
        self.assert_problem("original bytes do not match")

    def test_recomputed_historical_snapshot_still_fails_baseline(self):
        self.mutate_snapshot("SYS-RULE-0011", lambda s: s.update(statement="Rewritten history."), "SYS-RULE-0011.r1")
        self.assertEqual([], check(self.memory))
        self.assert_problem("immutable entity changed", self.base)

    def test_prior_candidate_transition_cannot_be_rewritten(self):
        self.mutate("candidate", "CAND-REJECTED", lambda c: c["state_history"][0].update(reason="Rewritten earlier reason."))
        self.assert_problem("historical transitions changed", self.base)

    def test_mixed_instance_ids_rejected(self):
        self.mutate("record", "SYS-RULE-0011", lambda r: r.update(instance_id="another.instance"))
        self.assert_problem("mixed instance namespaces")

    def test_unknown_required_extension_rejected(self):
        self.mutate("config", "CONFIG-EXAMPLE", lambda c: c.update(required_extensions=["org.example.unsupported"]))
        self.assert_problem("unsupported required extensions")

    def test_optional_extension_is_preserved_without_shape_loss(self):
        data = self.mutate("record", "SYS-RULE-0011", lambda r: r.update(extensions={"org.example.note": {"literal": "keep this", "data": [1, 2]}}))
        self.assertEqual(data["extensions"], self.get("record", "SYS-RULE-0011")["extensions"])
        self.assertEqual([], check(self.memory))

    def test_revision_count_and_current_snapshot_are_checked(self):
        self.mutate("record", "SYS-RULE-0011", lambda r: r.update(revision_count=999))
        self.assert_problem("revision count mismatch")
        self.mutate("record", "SYS-RULE-0011", lambda r: r["current"].update(statement="Wrong current meaning."))
        self.assert_problem("current projection disagrees")

    def test_pinned_base_must_belong_to_named_parent(self):
        self.mutate_snapshot("LIB-RULE-0006", lambda s: s["parent_bases"][0].update(revision_id="SYS-RULE-0020.r1"))
        self.assert_problem("pinned base is unrelated")

    def test_map_entry_must_be_reciprocal(self):
        self.mutate("derivation-map", "MAP-SYS-RULE-0011", lambda m: m["entries"][0].update(base_revision_id="SYS-RULE-0011.r4"))
        self.assert_problem("nonreciprocal or stale child/base")

    def test_registered_child_requires_map_entry(self):
        self.mutate("derivation-map", "MAP-SYS-RULE-0011", lambda m: m.update(entries=[], registered_count=0))
        self.assert_problem("registered derivative missing")

    def test_map_project_label_is_verified(self):
        self.mutate("derivation-map", "MAP-SYS-RULE-0011", lambda m: m["entries"][0].update(child_scope_id="GLOBAL"))
        self.assert_problem("child scope")

    def test_conflict_lifecycle_retains_origin(self):
        self.mutate("conflict", "CONF-0001", lambda c: c["state_history"][0].update(commit_id="TXN-000010"))
        self.assert_problem("invalid conflict transition order/origin")

    def test_confirmed_candidate_needs_adoption_evidence(self):
        self.mutate("candidate", "CAND-CONFIRMED", lambda c: c["assertion"].update(adoption_evidence=[]))
        self.assert_problem("confirmation lacks adopted evidence")

    def test_adoption_evidence_cannot_be_a_current_memory_pointer(self):
        self.mutate("candidate", "CAND-CONFIRMED", lambda c: c["assertion"].update(adoption_evidence=["mem://SYS-RULE-0010"]))
        self.assert_problem("adoption_evidence")

    def test_review_cannot_read_a_future_window(self):
        self.mutate("review-receipt", "REVIEW-0002", lambda r: r["sources"][0].update(window_id="WIN-00021"))
        self.assert_problem("not available at read snapshot")

    def test_audit_coverage_is_not_an_unchecked_claim(self):
        self.mutate("audit-run", "AUDIT-0001", lambda a: a.update(message_end=999, checkpoint=999))
        self.assert_problem("invalid audit coverage")

    def test_unknown_historical_times_require_notes(self):
        self.mutate("revision", "LIB-PREF-0001.r1", lambda r: r.update(time_note=None))
        self.assert_problem("time_note")

    def test_fractional_time_is_explicitly_outside_fixed_precision_profile(self):
        self.resign_commit("TXN-000001", lambda c: c.update(created_at="2026-09-23T12:01:00.1Z"))
        self.assert_problem("does not match")

    def test_revision_commit_must_authorize_its_write(self):
        self.resign_commit("TXN-000003", lambda c: c["writes"].remove("rev://SYS-RULE-0011.r3"))
        self.assert_problem("authoritative writes")

    def test_stale_expected_revision_rejected(self):
        self.resign_commit("TXN-000003", lambda c: c["expected_revisions"][0].update(revision_id="SYS-RULE-0011.r1"))
        self.assert_problem("stale expected revision")

    def test_low_budget_blocks_even_with_matching_rendered_hash(self):
        self.mutate("config", "CONFIG-EXAMPLE", lambda c: c["primary_byte_budgets"].update(GLOBAL=8))
        self.mutate("working-set", "WORKING-GLOBAL", lambda w: w.update(budget_bytes=8))
        self.assert_problem("primary budget exceeded")

    def test_missing_chunk_is_reported_without_crashing(self):
        (self.memory / "logs/c001.jsonl").unlink()
        self.assert_problem("missing/unsafe file")

    def test_crlf_changes_canonical_jsonl_bytes(self):
        path = self.memory / "logs/c001.jsonl"
        path.write_bytes(path.read_bytes().replace(b"\n", b"\r\n"))
        self.assert_problem("JSON bytes must be UTF-8")

    def test_source_only_review_can_cover_first_decision(self):
        self.mutate("review-receipt", "REVIEW-0002", lambda r: r.update(reviewed=[]))
        self.assertEqual([], check(self.memory))
        self.mutate("review-receipt", "REVIEW-0002", lambda r: r.update(sources=[]))
        self.assert_problem("not valid under any")


if __name__ == "__main__":
    unittest.main()
