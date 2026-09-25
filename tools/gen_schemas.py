#!/usr/bin/env python3
"""Generate the strict, bounded Aniukas Lossless Memory portable profile 1."""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DRAFT = "https://json-schema.org/draft/2020-12/schema"
S = {"type": "string", "minLength": 1}
ID = {"type": "string", "pattern": r"^[A-Za-z][A-Za-z0-9_.:-]{1,127}$"}
TIME = {"type": "string", "format": "date-time", "pattern": r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$"}
NULLTIME = {"anyOf": [TIME, {"type": "null"}]}
HASH = {"type": "string", "pattern": r"^[a-f0-9]{64}$"}
REF = {"type": "string", "pattern": r"^(mem|rev|win|log|map|proposal|candidate|conflict|commit|review|outbox|audit)://[A-Za-z][A-Za-z0-9_.:-]{1,127}(?:/m[1-9][0-9]*(?:-[1-9][0-9]*)?)?$"}
WINREF = {"type": "string", "pattern": r"^win://[A-Za-z][A-Za-z0-9_.:-]{1,127}$"}
NAT = {"type": "integer", "minimum": 0}
POS = {"type": "integer", "minimum": 1}
BOOL = {"type": "boolean"}

def arr(item, minimum=0):
    return {"type": "array", "items": item, "minItems": minimum, "uniqueItems": True}

def obj(props, required=None):
    return {"type": "object", "properties": props, "required": list(props) if required is None else required, "additionalProperties": False}

def enum(*values):
    return {"enum": list(values)}

STATUS = enum("candidate", "active", "deferred", "rejected", "experimental", "conditional", "conflicted", "superseded", "historical", "historical-origin", "unknown", "open", "resolved")
TYPES = enum("rule", "fact", "decision", "observation", "belief", "preference", "goal", "constraint", "hypothesis", "inference", "question", "procedure", "idea", "state_event")
KINDS = enum("exception", "specialization", "extension", "restriction", "override", "combination")
CONF = {"type": "number", "minimum": 0, "maximum": 1}
ASSERTION = obj({"asserted_by": ID, "kind": enum("user-stated", "AI-inferred", "document", "external-source", "system-observed"), "adoption_evidence": arr(WINREF), "reliability_note": S})
BASE = obj({"record_id": ID, "revision_id": ID, "derivative_kind": KINDS, "inherited_portion": S, "differences": arr(S, 1), "reason": S, "registration_state": enum("pending", "registered", "rejected")})
EDGES = obj({key: arr(ID) for key in ("supersedes", "superseded_by", "extends", "supports", "contradicts", "caused_by", "related", "promoted_from", "promoted_to", "resolves", "responds_to")}, [])
SNAPSHOT = obj({"type": TYPES, "title": S, "statement": S, "why": S, "status": STATUS, "importance": enum("critical", "high", "medium", "low"), "confidence": CONF, "confidence_basis": S, "assertion": ASSERTION, "valid_from": NULLTIME, "valid_until": NULLTIME, "valid_time_note": {"type": ["string", "null"]}, "edges": EDGES, "parent_bases": arr(BASE), "triggers": arr(S), "conditions": arr(S), "consequences": arr(S)})
SNAPSHOT["allOf"] = [{"if": {"properties": {"assertion": {"properties": {"kind": {"const": "AI-inferred"}, "adoption_evidence": {"maxItems": 0}}}}}, "then": {"properties": {"confidence": {"exclusiveMaximum": 1}}}}]
GAP = {"anyOf": [{"type": "null"}, obj({"reason": S, "deepest_available": enum("CURRENT", "HISTORY", "EVIDENCE", "FULL_LOG")})]}

def schemas():
    result = {}
    def add(kind, props, extra=None):
        common = {"format_version": {"const": "1"}, "instance_id": ID, "kind": {"const": kind}, "id": ID, "extensions": {"type": "object", "propertyNames": {"pattern": r"^[a-z0-9]+[.][a-z0-9_.-]+$"}}}
        value = obj(common | props, ["format_version", "instance_id", "kind", "id"] + list(props))
        value.update({"$schema": DRAFT, "$id": f"urn:aniukas-lossless-memory:format:1:{kind}", "title": f"Aniukas Lossless Memory profile 1: {kind}"})
        if extra:
            value.update(extra)
        result[kind] = value

    add("config", {"primary_byte_budgets": {"type": "object", "additionalProperties": POS}, "encoding": {"const": "UTF-8"}, "line_ending": {"const": "LF"}, "snapshot_sequence": NAT, "profile": {"const": "portable-files-alpha"}, "artifact_role": {"const": "illustrative-fixture"}, "required_extensions": arr(S)})
    add("scope", {"scope_type": enum("GLOBAL", "USER", "PROJECT", "TASK"), "parent_scope_id": {"anyOf": [ID, {"type": "null"}]}, "owner_principal_id": ID, "grant_authorizer_id": ID, "display_name": S})
    add("grant", {"principal_id": ID, "scope_id": ID, "role": enum("USER", "GOVERNOR", "PROJECT_OWNER", "TASK_OWNER", "WORKER", "AUDITOR"), "generation": POS, "operations": arr(enum("commit", "review", "propose", "observe"), 1), "issued_by": ID, "issued_at": TIME, "revoked_at": NULLTIME})
    add("record", {"scope_id": ID, "current_revision_id": ID, "revision_count": POS, "current": SNAPSHOT, "history_ref": REF, "derivation_map_ref": {"anyOf": [REF, {"type": "null"}]}, "registered_derivative_count": NAT, "created_in": ID, "updated_in": ID})
    add("revision", {"scope_id": ID, "record_id": ID, "number": POS, "predecessor_id": {"anyOf": [ID, {"type": "null"}]}, "snapshot": SNAPSHOT, "snapshot_sha256": HASH, "change": S, "reason": S, "alternatives": arr(S), "source_refs": arr(REF), "evidence_gap": GAP, "commit_id": ID, "created_at": NULLTIME, "time_note": {"type": ["string", "null"]}}, {"allOf": [{"if": {"properties": {"source_refs": {"maxItems": 0}}}, "then": {"properties": {"evidence_gap": {"type": "object"}}}}, {"if": {"properties": {"created_at": {"type": "null"}}}, "then": {"properties": {"time_note": S}}}]})
    add("evidence-window", {"scope_id": ID, "log_id": ID, "source_digest": HASH, "message_start": POS, "message_end": POS, "context_before": NAT, "context_after": NAT, "cited_by": arr(ID), "created_in": ID})
    chunk = obj({"number": POS, "file": S, "message_start": POS, "message_end": POS, "sha256": HASH, "byte_length": NAT})
    add("log-manifest", {"scope_id": ID, "source": S, "source_kind": enum("synthetic", "live", "import"), "original_file": S, "original_sha256": HASH, "original_byte_length": NAT, "original_encoding": S, "captured_at": TIME, "started_at": NULLTIME, "time_note": {"type": ["string", "null"]}, "completeness": enum("complete", "partial"), "missing_ranges": arr(S), "chunks": arr(chunk, 1), "created_in": ID})
    add("log-message", {"log_id": ID, "ordinal": POS, "timestamp": NULLTIME, "time_note": {"type": ["string", "null"]}, "role": enum("user", "assistant", "system", "tool", "agent", "human", "unknown"), "speaker": {"anyOf": [ID, {"type": "null"}]}, "identity_note": {"type": ["string", "null"]}, "text": {"type": "string"}, "original_byte_start": NAT, "original_byte_end": NAT})
    entry = obj({"child_id": ID, "child_scope_id": ID, "child_revision_id": ID, "base_revision_id": ID, "derivative_kind": KINDS, "summary": S, "reason": S, "registered_in": ID})
    add("derivation-map", {"scope_id": ID, "parent_id": ID, "generation": POS, "watermark": NAT, "registered_count": NAT, "count_filter": {"const": "registered children whose current status is not superseded"}, "entries": arr(entry), "updated_in": ID})
    transition = obj({"state": S, "reason": S, "commit_id": ID})
    add("proposal", {"scope_id": ID, "sender_principal_id": ID, "target_scope_id": ID, "proposal_kind": enum("promotion", "derivation-registration", "rule-change", "repair", "other"), "subject_refs": arr(REF, 1), "suggestion": S, "source_refs": arr(REF, 1), "state": enum("open", "accepted", "rejected", "deferred"), "response_history": arr(transition), "response_reason": {"type": ["string", "null"]}, "response_commit_id": {"anyOf": [ID, {"type": "null"}]}, "created_in": ID})
    add("candidate", {"scope_id": ID, "event_types": arr(S, 1), "subject": S, "candidate_statement": S, "assertion": ASSERTION, "confidence": CONF, "confidence_basis": S, "source_refs": arr(REF, 1), "state": enum("open", "needs-review", "confirmed", "rejected", "deferred", "exploratory", "expired", "superseded"), "state_history": arr(transition, 1), "resolution_record_id": {"anyOf": [ID, {"type": "null"}]}, "created_in": ID, "updated_in": ID})
    add("conflict", {"scope_id": ID, "subject": S, "sides": arr(obj({"record_id": ID, "revision_id": ID, "source_refs": arr(REF, 1)}), 2), "state": enum("unresolved", "resolved"), "state_history": arr(transition, 1), "resolution": {"type": ["string", "null"]}, "resolved_in": {"anyOf": [ID, {"type": "null"}]}, "created_in": ID})
    reviewed = obj({"record_id": ID, "revision_id": ID})
    add("review-receipt", {"scope_id": ID, "principal_id": ID, "grant_id": ID, "read_sequence": NAT, "reviewed": arr(reviewed), "sources": arr(obj({"window_id": ID, "source_digest": HASH})), "intent": S, "alternatives": arr(S, 1), "constraints": arr(S, 1), "consequences": arr(S, 1), "gaps": arr(S), "conflicts": arr(ID), "outcome": enum("sufficient", "blocked"), "created_at": TIME}, {"anyOf": [{"properties": {"reviewed": {"minItems": 1}}}, {"properties": {"sources": {"minItems": 1}}}]})
    add("commit", {"scope_id": ID, "principal_id": ID, "grant_id": ID, "sequence": POS, "created_at": TIME, "idempotency_key": S, "payload_sha256": HASH, "caused_by": arr(ID), "writes": arr(REF, 1), "expected_revisions": arr(obj({"record_id": ID, "revision_id": {"anyOf": [ID, {"type": "null"}]}})), "source_refs": arr(REF), "high_impact": BOOL, "review_receipt_ids": arr(ID)}, {"if": {"properties": {"high_impact": {"const": True}}}, "then": {"properties": {"review_receipt_ids": {"minItems": 1}}}})
    add("outbox-event", {"scope_id": ID, "source_commit_id": ID, "target_scope_id": ID, "event_type": enum("register-derivation", "refresh-derivation", "retire-derivation", "promotion-accepted", "parent-updated", "repair-proposed"), "payload_refs": arr(REF, 1), "delivery_state": enum("pending", "delivered", "rejected"), "delivery_history": arr(transition, 1), "ack_commit_id": {"anyOf": [ID, {"type": "null"}]}, "attempts": NAT})
    add("audit-run", {"scope_id": ID, "auditor_principal_id": ID, "source_log_id": ID, "message_start": POS, "message_end": POS, "auditor_version": S, "checkpoint": POS, "findings": arr(S), "repair_proposal_refs": arr(REF), "created_in": ID})
    add("working-set", {"scope_id": ID, "snapshot_sequence": NAT, "budget_bytes": POS, "counting_method": {"const": "UTF-8 bytes of the named rendered file"}, "token_count": {"anyOf": [NAT, {"type": "null"}]}, "tokenizer": {"type": ["string", "null"]}, "entries": arr(obj({"record_id": ID, "revision_id": ID, "pinned": BOOL})), "rendered_file": S, "rendered_sha256": HASH, "actual_bytes": NAT, "overflow": BOOL, "omitted_record_ids": arr(ID)})
    return result

def rendered():
    return {f"{name}.schema.json": (json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8") for name, data in schemas().items()}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    output = ROOT / "schemas"
    expected = rendered()
    if args.check:
        actual = {p.name: p.read_bytes() for p in output.glob("*.schema.json")}
        mismatches = sorted(set(actual) ^ set(expected) | {n for n in actual.keys() & expected.keys() if actual[n] != expected[n]})
        print("schema generation:", "PASS" if not mismatches else "DIFFERENT " + ", ".join(mismatches))
        return bool(mismatches)
    output.mkdir(exist_ok=True)
    for path in output.glob("*.schema.json"):
        if path.name not in expected:
            path.unlink()
    for name, data in expected.items():
        (output / name).write_bytes(data)
    print(f"generated {len(expected)} schemas")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
