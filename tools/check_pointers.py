#!/usr/bin/env python3
"""Check semantic integrity of the bounded portable snapshot (not runtime auth)."""
import argparse
import collections
import hashlib
from pathlib import Path

from gen_examples import SCHEMES, canonical, primary_bytes
from validate_examples import EXAMPLES, decode, inspect

def sha(data):
    return hashlib.sha256(data).hexdigest()

def check(memory=EXAMPLES, baseline=None):
    memory = Path(memory).resolve()
    rows, errors = inspect(memory)
    if errors:
        return errors
    by_id, kinds, paths = {}, collections.defaultdict(dict), {}
    for path, value in rows:
        ident = value["id"]
        if ident in by_id:
            errors.append(f"duplicate entity ID: {ident}")
        by_id[ident] = value
        kinds[value["kind"]][ident] = value
        paths[ident] = path
    if errors:
        return errors
    instances = {v["instance_id"] for _, v in rows}
    if len(instances) != 1:
        errors.append("mixed instance namespaces in one snapshot")
    def issue(message):
        errors.append(message)
    def need(ident, kind, context):
        value = kinds[kind].get(ident)
        if value is None:
            issue(f"{context}: missing {kind} {ident}")
        return value
    def path_for(name):
        path = (memory / name).resolve()
        if not path.is_relative_to(memory) or Path(name).is_absolute() or "\\" in name:
            issue(f"unsafe portable path: {name}")
            return None
        if not path.is_file() or path.is_symlink():
            issue(f"missing/unsafe file: {name}")
            return None
        return path
    def pointer(value, context):
        scheme, _, suffix = value.partition("://")
        ident, _, range_text = suffix.partition("/")
        kind = {v: k for k, v in SCHEMES.items()}.get(scheme)
        target = need(ident, kind, context) if kind else None
        if not kind:
            issue(f"{context}: unknown reference scheme {scheme}")
        if range_text:
            if scheme != "log" or not range_text.startswith("m"):
                issue(f"{context}: range only allowed on log references")
            else:
                try:
                    start, _, end = range_text[1:].partition("-")
                    a, b = int(start), int(end or start)
                    present = messages.get(ident, {})
                    if a > b or any(n not in present for n in range(a, b + 1)):
                        issue(f"{context}: invalid log message range {value}")
                except ValueError:
                    issue(f"{context}: invalid log reference {value}")
        return target
    scopes = kinds["scope"]
    commits = kinds["commit"]
    records = kinds["record"]
    revisions = kinds["revision"]
    windows = kinds["evidence-window"]
    maps = kinds["derivation-map"]
    config = list(kinds["config"].values())
    if len(config) != 1:
        issue("exactly one config is required")
        return errors
    config = config[0]
    if config["required_extensions"]:
        issue("unsupported required extensions: " + ", ".join(config["required_extensions"]))
    def sequence(tx):
        return commits.get(tx, {}).get("sequence", -1)
    def latest(rid, seq):
        candidates = [r for r in revisions.values() if r["record_id"] == rid and sequence(r["commit_id"]) <= seq]
        return max(candidates, key=lambda r: sequence(r["commit_id"]))["id"] if candidates else None
    def authorize(principal, gid, scope, operation, when, context):
        grant = need(gid, "grant", context)
        if not grant:
            return
        owner = scopes.get(scope)
        if not owner or grant["scope_id"] != scope or grant["principal_id"] != principal or operation not in grant["operations"]:
            issue(f"{context}: grant does not authorize {operation} for this principal and scope")
        if owner and grant["issued_by"] != owner["grant_authorizer_id"]:
            issue(f"{context}: grant issuer is not the trusted scope authorizer")
        if when < grant["issued_at"] or (grant["revoked_at"] and when >= grant["revoked_at"]):
            issue(f"{context}: grant inactive at commit/review time")
        if operation == "commit" and owner:
            expected_role = {"GLOBAL": "GOVERNOR", "USER": "USER", "PROJECT": "PROJECT_OWNER", "TASK": "TASK_OWNER"}[owner["scope_type"]]
            if grant["role"] not in (expected_role, "USER"):
                issue(f"{context}: role {grant['role']} cannot commit in {owner['scope_type']}")

    for sid, scope in scopes.items():
        seen, parent = {sid}, scope["parent_scope_id"]
        while parent:
            if parent in seen:
                issue(f"scope ancestry cycle: {sid}")
                break
            seen.add(parent)
            target = need(parent, "scope", sid)
            parent = target["parent_scope_id"] if target else None
    for gid, grant in kinds["grant"].items():
        scope = need(grant["scope_id"], "scope", gid)
        if scope and grant["issued_by"] != scope["grant_authorizer_id"]:
            issue(f"{gid}: unauthorized grant issuer")
        if grant["revoked_at"] and grant["revoked_at"] < grant["issued_at"]:
            issue(f"{gid}: revocation predates issuance")

    messages = collections.defaultdict(dict)
    for msg in kinds["log-message"].values():
        logid, n = msg["log_id"], msg["ordinal"]
        if n in messages[logid]:
            issue(f"{logid}: duplicate message ordinal {n}")
        messages[logid][n] = msg
        need(logid, "log-manifest", msg["id"])
        if msg["timestamp"] is None and not msg["time_note"]:
            issue(f"{msg['id']}: unknown timestamp lacks explanation")
        if (msg["role"] == "unknown" or msg["speaker"] is None) and not msg["identity_note"]:
            issue(f"{msg['id']}: unknown identity lacks explanation")
    referenced_files = set()
    for lid, log in kinds["log-manifest"].items():
        original_path = path_for(log["original_file"])
        referenced_files.add(log["original_file"])
        original = original_path.read_bytes() if original_path else b""
        if sha(original) != log["original_sha256"] or len(original) != log["original_byte_length"]:
            issue(f"{lid}: original byte digest/length mismatch")
        if log["started_at"] is None and not log["time_note"]:
            issue(f"{lid}: unknown source time lacks explanation")
        if (log["completeness"] == "complete") == bool(log["missing_ranges"]):
            issue(f"{lid}: completeness and missing ranges disagree")
        chunk_numbers, covered = [], []
        for chunk in log["chunks"]:
            chunk_numbers.append(chunk["number"])
            path = path_for(chunk["file"])
            referenced_files.add(chunk["file"])
            if not path:
                continue
            data = path.read_bytes()
            if sha(data) != chunk["sha256"] or len(data) != chunk["byte_length"]:
                issue(f"{lid}: chunk hash/byte length mismatch")
            entries = [decode(line) for line in data.splitlines()]
            numbers = [m["ordinal"] for m in entries]
            a, b = chunk["message_start"], chunk["message_end"]
            if a > b or numbers != list(range(a, b + 1)):
                issue(f"{lid}: chunk bounds/order do not match its messages")
            if any(m["log_id"] != lid for m in entries):
                issue(f"{lid}: chunk contains another log's messages")
            covered.extend(numbers)
            for message in entries:
                a, b = message["original_byte_start"], message["original_byte_end"]
                if a > b or b > len(original):
                    issue(f"{message['id']}: invalid original byte selector")
                else:
                    try:
                        if original[a:b].decode(log["original_encoding"]) != message["text"]:
                            issue(f"{message['id']}: original bytes do not match decoded message")
                    except (UnicodeError, LookupError):
                        issue(f"{message['id']}: original byte selector/encoding cannot decode")
        if chunk_numbers != list(range(1, len(chunk_numbers) + 1)):
            issue(f"{lid}: chunk numbers must be contiguous and ordered")
        if len(covered) != len(set(covered)) or set(covered) != set(messages[lid]):
            issue(f"{lid}: chunk coverage is overlapping or incomplete")
        if log["completeness"] == "complete" and covered != list(range(1, len(covered) + 1)):
            issue(f"{lid}: complete log has missing message ordinals")

    for wid, window in windows.items():
        log = need(window["log_id"], "log-manifest", wid)
        a, b = window["message_start"], window["message_end"]
        if a > b or any(n not in messages[window["log_id"]] for n in range(a, b + 1)):
            issue(f"{wid}: evidence range is reversed or unavailable")
        if log and log["original_sha256"] != window["source_digest"]:
            issue(f"{wid}: source digest mismatch")
        actual = sorted(r["id"] for r in revisions.values() if "win://" + wid in r["source_refs"])
        if sorted(window["cited_by"]) != actual:
            issue(f"{wid}: revision backlinks disagree with source references")
        for rev in window["cited_by"]:
            need(rev, "revision", wid)

    for rid, record in records.items():
        history = sorted([r for r in revisions.values() if r["record_id"] == rid], key=lambda r: r["number"])
        if not history:
            issue(f"{rid}: record without revisions")
            continue
        if [r["number"] for r in history] != list(range(1, len(history) + 1)):
            issue(f"{rid}: revision numbers are not contiguous and unique")
        if len(history) != record["revision_count"]:
            issue(f"{rid}: revision count mismatch")
        if record["current_revision_id"] != history[-1]["id"] or record["current"] != history[-1]["snapshot"]:
            issue(f"{rid}: current projection disagrees with latest immutable snapshot")
        if record["history_ref"] != "rev://" + record["current_revision_id"]:
            issue(f"{rid}: history reference must name current revision")
        if record["created_in"] != history[0]["commit_id"] or sequence(record["updated_in"]) < sequence(history[-1]["commit_id"]):
            issue(f"{rid}: record commit provenance inconsistent")
        for previous, revision in zip([None] + history[:-1], history):
            if revision["predecessor_id"] != (previous["id"] if previous else None):
                issue(f"{rid}: broken predecessor chain")
            if previous and sequence(previous["commit_id"]) >= sequence(revision["commit_id"]):
                issue(f"{rid}: revision order disagrees with recorded commit sequence")
        mapref = record["derivation_map_ref"]
        if mapref:
            target = pointer(mapref, rid)
            if target and (target["kind"] != "derivation-map" or target["parent_id"] != rid or target["registered_count"] != record["registered_derivative_count"]):
                issue(f"{rid}: derivation map/count mismatch")
        elif record["registered_derivative_count"]:
            issue(f"{rid}: derivative count without a map")
    for rid, revision in revisions.items():
        rec = need(revision["record_id"], "record", rid)
        if rec and revision["scope_id"] != rec["scope_id"]:
            issue(f"{rid}: revision crosses record scope")
        if sha(canonical(revision["snapshot"])) != revision["snapshot_sha256"]:
            issue(f"{rid}: immutable snapshot digest mismatch")
        snap = revision["snapshot"]
        if snap["valid_from"] is None and not snap["valid_time_note"]:
            issue(f"{rid}: unknown effective time requires a note")
        if snap["valid_from"] and snap["valid_until"] and snap["valid_from"] > snap["valid_until"]:
            issue(f"{rid}: reversed effective interval")
        for source in revision["source_refs"]:
            if not source.startswith("win://"):
                issue(f"{rid}: revision evidence must use precise windows")
            pointer(source, rid)
        for source in snap["assertion"]["adoption_evidence"]:
            pointer(source, rid)
        for targets in snap["edges"].values():
            for target in targets:
                need(target, "record", rid)
        parent_ids = []
        for base in snap["parent_bases"]:
            parent_ids.append(base["record_id"])
            parent = need(base["record_id"], "record", rid)
            parent_rev = need(base["revision_id"], "revision", rid)
            if parent_rev and (parent_rev["record_id"] != base["record_id"] or sequence(parent_rev["commit_id"]) >= sequence(revision["commit_id"])):
                issue(f"{rid}: pinned base is unrelated or did not yet exist")
        if len(parent_ids) != len(set(parent_ids)):
            issue(f"{rid}: repeated parent in a combined derivative")
    def visit(rid, visiting, done):
        if rid in visiting:
            issue(f"derivation cycle at {rid}")
            return
        if rid in done or rid not in records:
            return
        visiting.add(rid)
        for base in records[rid]["current"]["parent_bases"]:
            visit(base["record_id"], visiting, done)
        visiting.remove(rid)
        done.add(rid)
    done = set()
    for rid in records:
        visit(rid, set(), done)

    parent_maps = collections.defaultdict(list)
    for mid, mp in maps.items():
        parent_maps[mp["parent_id"]].append(mp)
        parent = need(mp["parent_id"], "record", mid)
        if parent and (parent["scope_id"] != mp["scope_id"] or parent["derivation_map_ref"] != "map://" + mid):
            issue(f"{mid}: parent/map owner or pointer mismatch")
        if mp["registered_count"] != len(mp["entries"]) or len({e["child_id"] for e in mp["entries"]}) != len(mp["entries"]):
            issue(f"{mid}: map count or unique children mismatch")
        if mp["watermark"] > config["snapshot_sequence"] or mp["watermark"] < sequence(mp["updated_in"]):
            issue(f"{mid}: invalid map watermark")
        for entry in mp["entries"]:
            child = need(entry["child_id"], "record", mid)
            if child and (entry["child_scope_id"] != child["scope_id"] or child["current"]["status"] == "superseded"):
                issue(f"{mid}: child scope or default status filter mismatch")
            at_registration = need(entry["child_revision_id"], "revision", mid)
            registration = need(entry["registered_in"], "commit", mid)
            if registration and (registration["scope_id"] != mp["scope_id"] or "map://" + mid not in registration["writes"]):
                issue(f"{mid}: registration commit lacks parent-owner map write")
            if at_registration and at_registration["record_id"] != entry["child_id"]:
                issue(f"{mid}: entry names another child's revision")
            for state in [child["current"] if child else None, at_registration["snapshot"] if at_registration else None]:
                if state and not any(b["record_id"] == mp["parent_id"] and b["revision_id"] == entry["base_revision_id"] and b["derivative_kind"] == entry["derivative_kind"] for b in state["parent_bases"]):
                    issue(f"{mid}: nonreciprocal or stale child/base map entry")
    for rid, rec in records.items():
        if len(parent_maps[rid]) > 1:
            issue(f"{rid}: more than one current derivation map")
        for base in rec["current"]["parent_bases"]:
            registered = any(e["child_id"] == rid for mp in parent_maps[base["record_id"]] for e in mp["entries"])
            if base["registration_state"] == "registered" and not registered and rec["current"]["status"] != "superseded":
                issue(f"{rid}: registered derivative missing from parent map")
            if base["registration_state"] == "pending" and not registered:
                if not any(e["event_type"] == "register-derivation" and ("rev://" + rec["current_revision_id"]) in e["payload_refs"] and e["delivery_state"] == "pending" for e in kinds["outbox-event"].values()):
                    issue(f"{rid}: pending derivation lacks durable registration event")

    seqs = [c["sequence"] for c in commits.values()]
    if len(seqs) != len(set(seqs)) or (seqs and max(seqs) != config["snapshot_sequence"]):
        issue("commit sequence collision or snapshot watermark mismatch")
    keys = set()
    for cid, commit in commits.items():
        authorize(commit["principal_id"], commit["grant_id"], commit["scope_id"], "commit", commit["created_at"], cid)
        if sha(canonical({k: v for k, v in commit.items() if k != "payload_sha256"})) != commit["payload_sha256"]:
            issue(f"{cid}: commit payload digest mismatch")
        key = (commit["principal_id"], commit["scope_id"], commit["idempotency_key"])
        if key in keys:
            issue(f"{cid}: duplicate committed idempotency key")
        keys.add(key)
        for previous in commit["caused_by"]:
            cause = need(previous, "commit", cid)
            if cause and cause["sequence"] >= commit["sequence"]:
                issue(f"{cid}: invalid causal order")
        for p in commit["writes"]:
            target = pointer(p, cid)
            if target and target.get("scope_id") != commit["scope_id"]:
                issue(f"{cid}: unauthorized cross-scope write to {p}")
        for source in commit["source_refs"]:
            pointer(source, cid)
        expected_ids = [e["record_id"] for e in commit["expected_revisions"]]
        if len(expected_ids) != len(set(expected_ids)):
            issue(f"{cid}: repeated expected record")
        for expected in commit["expected_revisions"]:
            if latest(expected["record_id"], commit["sequence"] - 1) != expected["revision_id"]:
                issue(f"{cid}: stale expected revision for {expected['record_id']}")
        for revision in revisions.values():
            if revision["commit_id"] == cid:
                if revision["record_id"] not in expected_ids or "rev://" + revision["id"] not in commit["writes"] or "mem://" + revision["record_id"] not in commit["writes"]:
                    issue(f"{cid}: revision is not covered by expected state and authoritative writes")
        for receipt_id in commit["review_receipt_ids"]:
            receipt = need(receipt_id, "review-receipt", cid)
            if not receipt:
                continue
            if receipt["principal_id"] != commit["principal_id"] or receipt["scope_id"] != commit["scope_id"] or receipt["outcome"] != "sufficient" or receipt["created_at"] > commit["created_at"]:
                issue(f"{cid}: review actor/scope/outcome/time invalid")
            if receipt["read_sequence"] >= commit["sequence"]:
                issue(f"{cid}: review watermark is not earlier than commit")
            for read in receipt["reviewed"]:
                if latest(read["record_id"], commit["sequence"] - 1) != read["revision_id"]:
                    issue(f"{cid}: stale reviewed dependency {read['record_id']}")
    for rid, receipt in kinds["review-receipt"].items():
        authorize(receipt["principal_id"], receipt["grant_id"], receipt["scope_id"], "review", receipt["created_at"], rid)
        for read in receipt["reviewed"]:
            rev = need(read["revision_id"], "revision", rid)
            if rev and (rev["record_id"] != read["record_id"] or latest(read["record_id"], receipt["read_sequence"]) != rev["id"]):
                issue(f"{rid}: reviewed revision inconsistent with read snapshot")
        for source in receipt["sources"]:
            window = need(source["window_id"], "evidence-window", rid)
            if window and window["source_digest"] != source["source_digest"]:
                issue(f"{rid}: reviewed source digest mismatch")
            if window and sequence(window["created_in"]) > receipt["read_sequence"]:
                issue(f"{rid}: reviewed source was not available at read snapshot")
        for conflict in receipt["conflicts"]:
            need(conflict, "conflict", rid)

    for ident, value in by_id.items():
        scope = value.get("scope_id")
        if scope:
            need(scope, "scope", ident)
        for field in ("created_in", "updated_in", "commit_id", "source_commit_id"):
            if field in value:
                c = need(value[field], "commit", ident)
                scheme = SCHEMES.get(value["kind"])
                if c and (c["scope_id"] != scope or (scheme and scheme + "://" + ident not in c["writes"])):
                    issue(f"{ident}: {field} does not authorize/contain this object's write")
    for pid, proposal in kinds["proposal"].items():
        need(proposal["target_scope_id"], "scope", pid)
        creation = commits.get(proposal["created_in"])
        if creation and creation["principal_id"] != proposal["sender_principal_id"]:
            issue(f"{pid}: sender does not match authenticated creation principal")
        for p in proposal["subject_refs"] + proposal["source_refs"]:
            pointer(p, pid)
        response = proposal["response_commit_id"]
        history = proposal["response_history"]
        if history and (history[-1]["state"] != proposal["state"] or history[-1]["commit_id"] != response or history[-1]["reason"] != proposal["response_reason"]):
            issue(f"{pid}: response projection differs from response history")
        if proposal["state"] != "open" and not history:
            issue(f"{pid}: missing response history")
        for transition in history:
            c = need(transition["commit_id"], "commit", pid)
            if c and c["scope_id"] != proposal["target_scope_id"]:
                issue(f"{pid}: response history crosses recipient ownership")
        if proposal["state"] != "open":
            c = need(response, "commit", pid)
            if not proposal["response_reason"] or not c or c["scope_id"] != proposal["target_scope_id"] or sequence(response) <= sequence(proposal["created_in"]):
                issue(f"{pid}: proposal response lacks target-owner decision and rationale")
            if not any(e["source_commit_id"] == response and "proposal://" + pid in e["payload_refs"] for e in kinds["outbox-event"].values()):
                issue(f"{pid}: projected response lacks immutable target-owned event")
    for cid, candidate in kinds["candidate"].items():
        for p in candidate["source_refs"] + candidate["assertion"]["adoption_evidence"]:
            pointer(p, cid)
        history = candidate["state_history"]
        if history[-1]["state"] != candidate["state"] or history[0]["commit_id"] != candidate["created_in"] or history[-1]["commit_id"] != candidate["updated_in"]:
            issue(f"{cid}: candidate lifecycle projection inconsistent")
        order = [sequence(h["commit_id"]) for h in history]
        if order != sorted(order):
            issue(f"{cid}: candidate lifecycle is out of order")
        for h in history:
            c = need(h["commit_id"], "commit", cid)
            if c and (c["scope_id"] != candidate["scope_id"] or "candidate://" + cid not in c["writes"]):
                issue(f"{cid}: unauthorized candidate transition")
        if candidate["resolution_record_id"]:
            need(candidate["resolution_record_id"], "record", cid)
        if candidate["state"] == "confirmed" and (not candidate["resolution_record_id"] or not candidate["assertion"]["adoption_evidence"]):
            issue(f"{cid}: confirmation lacks adopted evidence/record")
        if candidate["assertion"]["kind"] == "AI-inferred" and not candidate["assertion"]["adoption_evidence"] and candidate["confidence"] >= 1:
            issue(f"{cid}: unconfirmed AI inference claims certainty")
    for fid, conflict in kinds["conflict"].items():
        if conflict["state_history"][-1]["state"] != conflict["state"]:
            issue(f"{fid}: conflict projection differs from lifecycle history")
        history = conflict["state_history"]
        order = [sequence(h["commit_id"]) for h in history]
        if order != sorted(order) or history[0]["commit_id"] != conflict["created_in"] or history[0]["state"] != "unresolved":
            issue(f"{fid}: invalid conflict transition order/origin")
        if conflict["state"] == "resolved" and history[-1]["commit_id"] != conflict["resolved_in"]:
            issue(f"{fid}: resolution commit differs from lifecycle history")
        for transition in conflict["state_history"]:
            c = need(transition["commit_id"], "commit", fid)
            if c and (c["scope_id"] != conflict["scope_id"] or "conflict://" + fid not in c["writes"]):
                issue(f"{fid}: unauthorized conflict transition")
        for side in conflict["sides"]:
            rev = need(side["revision_id"], "revision", fid)
            if rev and rev["record_id"] != side["record_id"]:
                issue(f"{fid}: conflict side mismatches record/revision")
            for p in side["source_refs"]:
                pointer(p, fid)
        if conflict["state"] == "resolved":
            c = need(conflict["resolved_in"], "commit", fid)
            if not conflict["resolution"] or not c or c["scope_id"] != conflict["scope_id"] or "conflict://" + fid not in c["writes"]:
                issue(f"{fid}: resolution lacks authorized write/rationale")
    for eid, event in kinds["outbox-event"].items():
        history = event["delivery_history"]
        if history[0]["state"] != "pending" or history[0]["commit_id"] != event["source_commit_id"] or history[-1]["state"] != event["delivery_state"]:
            issue(f"{eid}: delivery projection differs from event history")
        if event["ack_commit_id"] and history[-1]["commit_id"] != event["ack_commit_id"]:
            issue(f"{eid}: delivery history lacks acknowledgement")
        need(event["target_scope_id"], "scope", eid)
        for p in event["payload_refs"]:
            pointer(p, eid)
        if event["delivery_state"] == "delivered":
            ack = need(event["ack_commit_id"], "commit", eid)
            if not ack or ack["scope_id"] != event["target_scope_id"] or event["source_commit_id"] not in ack["caused_by"] or not event["attempts"]:
                issue(f"{eid}: delivery lacks scoped causal acknowledgement")
        elif event["ack_commit_id"] is not None:
            issue(f"{eid}: pending/rejected event has an acknowledgement")
    for aid, audit in kinds["audit-run"].items():
        log = need(audit["source_log_id"], "log-manifest", aid)
        a, b = audit["message_start"], audit["message_end"]
        if a > b or audit["checkpoint"] != b or any(n not in messages[audit["source_log_id"]] for n in range(a, b + 1)):
            issue(f"{aid}: invalid audit coverage/checkpoint")
        for p in audit["repair_proposal_refs"]:
            pointer(p, aid)

    working_scopes = set()
    for wid, working in kinds["working-set"].items():
        scope = working["scope_id"]
        if scope in working_scopes:
            issue(f"{scope}: duplicate current working set")
        working_scopes.add(scope)
        if working["snapshot_sequence"] != config["snapshot_sequence"] or working["budget_bytes"] != config["primary_byte_budgets"].get(scope):
            issue(f"{wid}: budget/snapshot disagrees with config")
        selected = [e["record_id"] for e in working["entries"]]
        if len(selected) != len(set(selected)):
            issue(f"{wid}: duplicate primary entry")
        can_render = True
        for e in working["entries"]:
            r = need(e["record_id"], "record", wid)
            if not r:
                can_render = False
            elif r["scope_id"] != scope or r["current_revision_id"] != e["revision_id"]:
                issue(f"{wid}: stale or cross-scope primary projection")
        owned = {r["id"] for r in records.values() if r["scope_id"] == scope}
        omitted = set(working["omitted_record_ids"])
        if omitted & set(selected) or omitted | set(selected) != owned:
            issue(f"{wid}: incomplete/overlapping working-set coverage")
        path = path_for(working["rendered_file"])
        referenced_files.add(working["rendered_file"])
        if path:
            data = path.read_bytes()
            if can_render and data != primary_bytes(scope, working["entries"], records):
                issue(f"{wid}: rendered primary differs from declared current projection")
            if len(data) != working["actual_bytes"] or sha(data) != working["rendered_sha256"]:
                issue(f"{wid}: primary byte count/hash mismatch")
            if len(data) > working["budget_bytes"]:
                issue(f"{wid}: primary budget exceeded; overflow must return blocked/minimal working set")
        if working["overflow"]:
            issue(f"{wid}: this ready fixture profile requires nonoverflowing primary")
        if (working["token_count"] is None) != (working["tokenizer"] is None):
            issue(f"{wid}: token measurement lacks tokenizer/count pair")
    if working_scopes != set(config["primary_byte_budgets"]):
        issue("working sets and configured scopes disagree")
    for path in memory.rglob("*"):
        if path.is_file() and path.suffix in (".md", ".txt", ".jsonl") and path.relative_to(memory).as_posix() not in referenced_files:
            issue(f"unreferenced artifact file: {path.relative_to(memory)}")

    if baseline:
        old_rows, old_errors = inspect(Path(baseline))
        if old_errors:
            issue("baseline is not a valid shaped snapshot")
        else:
            immutable = {"revision", "commit", "log-message", "log-manifest", "review-receipt"}
            for old_path, old in old_rows:
                if old["kind"] in ("candidate", "proposal", "conflict", "outbox-event") and old["id"] not in by_id:
                    issue(f"historical lifecycle object removed: {old['id']}")
                if old["kind"] in immutable and (old["id"] not in by_id or canonical(old) != canonical(by_id[old["id"]])):
                    issue(f"immutable entity changed or removed since baseline: {old['id']}")
                if old["kind"] == "evidence-window":
                    current = by_id.get(old["id"], {})
                    if any(old[k] != current.get(k) for k in ("log_id", "source_digest", "message_start", "message_end")):
                        issue(f"immutable evidence selector changed: {old['id']}")
                for history_field in ("state_history", "response_history", "delivery_history"):
                    if history_field in old:
                        current = by_id.get(old["id"], {})
                        if current.get(history_field, [])[:len(old[history_field])] != old[history_field]:
                            issue(f"historical transitions changed or removed: {old['id']}")
                if old["kind"] == "outbox-event":
                    current = by_id.get(old["id"], {})
                    if any(old[k] != current.get(k) for k in ("scope_id", "source_commit_id", "target_scope_id", "event_type", "payload_refs")):
                        issue(f"immutable source event changed: {old['id']}")
    return errors

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("memory", nargs="?", type=Path, default=EXAMPLES)
    parser.add_argument("--baseline", type=Path)
    args = parser.parse_args()
    errors = check(args.memory, args.baseline)
    for error in errors:
        print(error)
    print(f"semantic validation: {len(errors)} errors")
    return bool(errors)

if __name__ == "__main__":
    raise SystemExit(main())
