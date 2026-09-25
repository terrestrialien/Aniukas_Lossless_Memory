#!/usr/bin/env python3
"""Deterministic synthetic specification fixtures; this is not a memory runtime."""
import argparse
import copy
import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MEM = ROOT / "examples" / "memory"
INSTANCE = "alm.synthetic.example"
SCHEMES = {"record": "mem", "revision": "rev", "evidence-window": "win", "log-manifest": "log", "derivation-map": "map", "proposal": "proposal", "candidate": "candidate", "conflict": "conflict", "commit": "commit", "review-receipt": "review", "outbox-event": "outbox", "audit-run": "audit"}

def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")

def digest(data):
    return hashlib.sha256(data).hexdigest()

def jsonbytes(value):
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False) + "\n").encode("utf-8")

def primary_bytes(scope, entries, records):
    """Render a Primary view: current meaning plus tiny pointers, never the history itself."""
    lines = [f"# Primary: {scope}", ""]
    for entry in entries:
        rec = records[entry["record_id"]]
        current = rec["current"]
        details = [f"status: {current.get('status', 'unknown')}"]
        count = rec.get("revision_count")
        if rec.get("history_ref"):
            noun = "revision" if count == 1 else "revisions"
            details.append(f"history: {count} {noun}, {rec['history_ref']}")
        derivatives = rec.get("registered_derivative_count") or 0
        if derivatives and rec.get("derivation_map_ref"):
            details.append(f"derivatives: {derivatives}, {rec['derivation_map_ref']}")
        lines.append(f"- [{rec['id']} @ {entry['revision_id']}] {current['title']}: {current['statement']} ({'; '.join(details)})")
    return ("\n".join(lines) + "\n").encode("utf-8")

def build():
    objects, files, commits, records, revisions, windows = {}, {}, {}, {}, {}, {}
    def entity(kind, ident, **kw):
        data = dict(format_version="1", instance_id=INSTANCE, kind=kind, id=ident, **kw)
        objects[ident] = data
        return data
    def ref(data):
        return SCHEMES[data["kind"]] + "://" + data["id"]
    def commit(n, scope="GLOBAL", expected=None, reviews=None, caused=None):
        ident = f"TXN-{n:06}"
        principal = "principal:governor" if scope == "GLOBAL" else "principal:library-owner"
        grant = "GRANT-GLOBAL" if scope == "GLOBAL" else "GRANT-LIBRARY"
        c = entity("commit", ident, scope_id=scope, principal_id=principal, grant_id=grant, sequence=n, created_at=f"2026-09-23T12:{n:02}:00Z", idempotency_key=f"synthetic-event-{n}", payload_sha256="0" * 64, caused_by=caused or [], writes=[], expected_revisions=expected or [], source_refs=[], high_impact=bool(reviews), review_receipt_ids=reviews or [])
        commits[ident] = c
        return ident
    def write(tx, data):
        pointer = ref(data)
        if pointer not in commits[tx]["writes"]:
            commits[tx]["writes"].append(pointer)
    def assertion(kind="user-stated", adoption=None):
        speaker = {"user-stated": "principal:synthetic-user", "AI-inferred": "principal:assistant", "document": "source:synthetic-booking-sheet"}[kind]
        return dict(asserted_by=speaker, kind=kind, adoption_evidence=adoption or [], reliability_note="Fictional teaching scenario; these people and documents do not exist.")
    def snap(title, statement, **extra):
        return dict(type="rule", title=title, statement=statement, why="The stated reason is retained with the decision and its exact source.", status="active", importance="high", confidence=1.0, confidence_basis="Clear fictional speaker statement; this score describes interpretation, not factual truth.", assertion=assertion(), valid_from="2026-09-23T00:00:00Z", valid_until=None, valid_time_note=None, edges={}, parent_bases=[], triggers=[], conditions=[], consequences=[]) | extra
    def window(n, tx, start, end=None):
        ident = f"WIN-{n:05}"
        w = entity("evidence-window", ident, scope_id=commits[tx]["scope_id"], log_id="LOG-EXAMPLE", source_digest=source_hash, message_start=start, message_end=end or start, context_before=1, context_after=1, cited_by=[], created_in=tx)
        windows[ident] = w
        write(tx, w)
        return "win://" + ident
    def revise(rid, tx, snapshot, sources, reason, unknown=False):
        previous = records.get(rid)
        number = previous["revision_count"] + 1 if previous else 1
        ident = f"{rid}.r{number}"
        state = copy.deepcopy(snapshot)
        if state["valid_from"] == "2026-09-23T00:00:00Z" and sources:
            first_window = windows[sources[0].removeprefix("win://")]
            state["valid_from"] = timestamps[first_window["message_start"] - 1]
        r = entity("revision", ident, scope_id=commits[tx]["scope_id"], record_id=rid, number=number, predecessor_id=previous["current_revision_id"] if previous else None, snapshot=state, snapshot_sha256=digest(canonical(state)), change=state["statement"], reason=reason, alternatives=["Keep the previous interpretation unchanged."], source_refs=sources, evidence_gap={"reason": "Legacy note has no surviving source; do not manufacture evidence.", "deepest_available": "HISTORY"} if not sources else None, commit_id=tx, created_at=None if unknown else commits[tx]["created_at"], time_note="Original event time is unknown; the enclosing commit records import time." if unknown else None)
        revisions[ident] = r
        rec = entity("record", rid, scope_id=r["scope_id"], current_revision_id=ident, revision_count=number, current=copy.deepcopy(state), history_ref="rev://" + ident, derivation_map_ref=previous["derivation_map_ref"] if previous else None, registered_derivative_count=previous["registered_derivative_count"] if previous else 0, created_in=previous["created_in"] if previous else tx, updated_in=tx)
        records[rid] = rec
        commits[tx]["expected_revisions"].append(dict(record_id=rid, revision_id=r["predecessor_id"]))
        for source in sources:
            windows[source.removeprefix("win://")]["cited_by"].append(ident)
        write(tx, r)
        write(tx, rec)
        return ident
    def review(n, scope, dependencies, sequence):
        reasoning = {
            2: ("Allow people without email to request items while keeping one reservation queue.", ["Keep the email-only pilot."], ["Every phone and email request enters the same queue."], ["More people can request items without volunteers promising one item twice."]),
            3: ("Allow branches to choose a contact method without losing the shared queue.", ["Require every branch to use email only."], ["Local contact options must still enter the shared queue."], ["Branch choices can help members while reservations remain consistent."]),
            5: ("Delay the repair workshop until its room is confirmed.", ["Cancel the workshop permanently.", "Announce an unbooked date."], ["Keep the long-term goal and explain the uncertain room schedule."], ["The workshop remains planned but no date is promised."]),
            6: ("Let Riverside confirm pickups by phone for members without email.", ["Use email confirmations at every branch."], ["The branch must still log confirmations in the shared queue."], ["Other branches keep their own contact rules until their owners decide."]),
            9: ("Add one pickup checklist while keeping local contact methods.", ["Let each branch invent its own pickup check."], ["Do not silently replace Riverside's pinned phone variation."], ["Substitute volunteers can follow the same handoff steps."]),
            15: ("Offer Riverside's phone option as a shared choice for branches.", ["Leave phone confirmation as a Riverside-only variation."], ["The global owner cannot edit Riverside's local history."], ["Branches may adopt the option independently."]),
            16: ("Let Riverside adopt the new shared option and retain its origin.", ["Keep the local variation active beside the shared rule."], ["Only the Riverside owner changes its local status."], ["The branch history still explains why the option began."]),
            21: ("Combine the shared queue, pickup checklist and optional phone confirmation at Riverside.", ["Use only one parent rule."], ["Pin both exact shared-rule revisions; registrations remain pending."], ["No parent map claims the new variant until its owner registers it."]),
        }
        intent, alternatives, constraints, consequences = reasoning[n]
        ident = f"REVIEW-{n:04}"
        receipt = entity("review-receipt", ident, scope_id=scope, principal_id="principal:governor" if scope == "GLOBAL" else "principal:library-owner", grant_id="GRANT-GLOBAL" if scope == "GLOBAL" else "GRANT-LIBRARY", read_sequence=sequence, reviewed=[dict(record_id=revisions[r]["record_id"], revision_id=r) for r in dependencies], sources=[dict(window_id=w, source_digest=source_hash) for w in sorted({s.removeprefix("win://") for r in dependencies for s in revisions[r]["source_refs"]})], intent=intent, alternatives=alternatives, constraints=constraints, consequences=consequences, gaps=[], conflicts=[], outcome="sufficient", created_at=f"2026-09-23T12:{sequence:02}:30Z")
        return receipt["id"]

    for sid, kind, parent, owner in [("GLOBAL", "GLOBAL", None, "principal:governor"), ("USER", "USER", "GLOBAL", "principal:user-owner"), ("PROJECT-LIBRARY", "PROJECT", "GLOBAL", "principal:library-owner"), ("TASK-DESK", "TASK", "PROJECT-LIBRARY", "principal:task-owner")]:
        entity("scope", sid, scope_type=kind, parent_scope_id=parent, owner_principal_id=owner, grant_authorizer_id="principal:human-admin", display_name=sid)
    for gid, sid, principal, role in [("GRANT-GLOBAL", "GLOBAL", "principal:governor", "GOVERNOR"), ("GRANT-LIBRARY", "PROJECT-LIBRARY", "principal:library-owner", "PROJECT_OWNER")]:
        entity("grant", gid, principal_id=principal, scope_id=sid, role=role, generation=1, operations=["commit", "review", "propose", "observe"], issued_by="principal:human-admin", issued_at="2026-09-23T00:00:00Z", revoked_at=None)

    # Every line is original fictional source material with a real example
    # timestamp and speaker. Decisions include reasons and competing options.
    messages = [
        ("user", "For our neighborhood lending library pilot, accept lending requests by email only. Two volunteers can manage one inbox, and we can expand access after we learn the workload."),
        ("user", "People without email still need to borrow items. Accept phone or email requests, but enter both in one shared queue so two volunteers never promise the same item."),
        ("user", "Branches may choose their own contact method. Keep every request in the shared queue; that common step prevents double bookings even when the front desk works differently."),
        ("user", "I want a repair workshop later because members have asked for one. We still need a room and a volunteer instructor, so this is a goal rather than a scheduled event."),
        ("user", "Defer the repair workshop until we confirm the room schedule. Keep it in the plan; I do not want the missing room booking mistaken for a decision to cancel."),
        ("user", "At the Riverside branch, volunteers may confirm pickups by phone for members without email. Enter those confirmations in the shared queue so the branch keeps the common reservation record."),
        ("agent", "I have recorded Riverside's phone-confirmation choice in the branch notebook. I will ask the shared-rule owner to list this local variation in the branch map; recording it locally does not edit the shared rule."),
        ("agent", "The shared-rule owner registered the Riverside variation. The branch owner acknowledges the receipt, keeping the original parent version pinned so later policy edits cannot rewrite why the variation began."),
        ("user", "Add one pickup checklist across branches. Substitute volunteers need a consistent handoff, but each branch can keep its chosen way of contacting members."),
        ("user", "The organizer told me the meeting room seats 30. I had planned the repair workshop around that number, although I have not checked the current booking sheet."),
        ("assistant", "The venue booking sheet lists 20 seats for the same room. I cannot tell whether the sheet or the organizer has the current number, so keep both claims and ask the venue before setting attendance."),
        ("assistant", "What if Riverside stops using the shared queue to save a few volunteer minutes? This is only a suggestion; it could make phone confirmations quicker."),
        ("user", "No. Reject skipping the queue. Without one shared record, two volunteers could promise the same item to different people; the small time saving is not worth that confusion."),
        ("agent", "Riverside's phone option has helped members without email. I propose offering that option to other branches, with the shared queue still required. This proposal does not change those branches."),
        ("agent", "The shared-rule owner accepts a new optional phone-confirmation rule. Riverside keeps its own earlier record and other branches may decide whether the option fits their members."),
        ("user", "Riverside can adopt the shared phone option and keep its original local entry as history. The shared decision must not silently change any other branch's contact practice."),
        ("user", "Our import mentions an old flyer style note about spelling 'résumé' with accents, but the original note and its date are missing. Mark the imported preference's source as unavailable."),
        ("assistant", "Would a large-print weekly lending schedule help members find pickup options and workshop news? I am suggesting it; no one has chosen it yet."),
        ("user", "Yes, adopt the large-print weekly schedule. Members who miss email can read it at the desk, and volunteers answering calls can refer to the same page."),
        ("agent", "A later audit found that the weekly-schedule record cited the suggestion but did not list the user's adoption as direct revision evidence. I will propose an evidence update to the shared-rule owner."),
        ("agent", "The shared-rule owner accepts the audit repair. Add the adoption and audit explanation in a new revision; leave the first revision's evidence exactly as it was."),
        ("agent", "A second Riverside variation combines the shared queue with optional phone confirmation. Both parent versions are pinned; registration is pending, so the shared map must not count this variation yet."),
    ]
    timestamps = [f"2026-09-23T11:{n:02}:00Z" for n in range(1, len(messages) + 1)]
    def source_prefix(n, role):
        return f"{timestamps[n - 1]} | {role} | ".encode("utf-8")
    original = b"".join(source_prefix(n, role) + text.encode("utf-8") + b"\n" for n, (role, text) in enumerate(messages, 1))
    source_hash = digest(original)
    files["logs/original.txt"] = original
    lines, offset = [], 0
    for n, (role, text) in enumerate(messages, 1):
        raw = text.encode("utf-8")
        start = offset + len(source_prefix(n, role))
        speaker = {"user": "principal:synthetic-user", "assistant": "principal:assistant", "agent": "principal:library-agent"}[role]
        msg = dict(format_version="1", instance_id=INSTANCE, kind="log-message", id=f"MSG-{n:04}", log_id="LOG-EXAMPLE", ordinal=n, timestamp=timestamps[n - 1], time_note=None, role=role, identity_note=None, speaker=speaker, text=text, original_byte_start=start, original_byte_end=start + len(raw))
        lines.append(canonical(msg) + b"\n")
        offset = start + len(raw) + 1
    chunk_bytes = b"".join(lines)
    files["logs/c001.jsonl"] = chunk_bytes
    tx = commit(1)
    log = entity("log-manifest", "LOG-EXAMPLE", scope_id="GLOBAL", source="Fictional neighborhood lending library conversation, with source timestamps, speaker labels and reasons.", source_kind="synthetic", original_file="logs/original.txt", original_sha256=source_hash, original_byte_length=len(original), original_encoding="UTF-8", captured_at=commits[tx]["created_at"], started_at=timestamps[0], time_note=None, completeness="complete", missing_ranges=[], chunks=[dict(number=1, file="logs/c001.jsonl", message_start=1, message_end=len(messages), sha256=digest(chunk_bytes), byte_length=len(chunk_bytes))], created_in=tx)
    write(tx, log)
    s = snap("Lending request rule", "Accept lending requests by email during the pilot.", why="Two volunteers can manage one inbox while the pilot begins.")
    r1 = revise("SYS-RULE-0011", tx, s, [window(1, tx, 1)], "Start with one manageable inbox for the pilot.")
    tx = commit(2, reviews=[review(2, "GLOBAL", [r1], 1)])
    s = snap("Lending request rule", "Accept phone and email requests; enter both in one shared queue.", why="Members without email need access, and one queue prevents duplicate promises.")
    r2 = revise("SYS-RULE-0011", tx, s, [window(2, tx, 2)], "Expand access while keeping one reservation record.")
    tx = commit(3, reviews=[review(3, "GLOBAL", [r2], 2)])
    s = snap("Lending request rule", "Branches may choose a contact method, but every request enters the shared queue.", why="Local access can vary while the shared queue prevents double bookings.")
    r3 = revise("SYS-RULE-0011", tx, s, [window(3, tx, 3)], "Allow branch contact choices without losing reservation consistency.")
    tx = commit(4, "PROJECT-LIBRARY")
    workshop = revise("LIB-DEC-0001", tx, snap("Repair workshop", "Hold a repair workshop when a room and instructor are available.", type="decision", why="Members requested it, but the date and resources remain open."), [window(4, tx, 4)], "Record the requested future workshop without inventing a date.")
    tx = commit(5, "PROJECT-LIBRARY", reviews=[review(5, "PROJECT-LIBRARY", [workshop], 4)])
    revise("LIB-DEC-0001", tx, snap("Repair workshop", "Defer the repair workshop until the room schedule is confirmed; keep it planned.", type="decision", status="deferred", why="The room is unconfirmed; the user wants a delay, not cancellation.", triggers=["room schedule confirmed", "instructor available"]), [window(5, tx, 5)], "Deferral preserves the goal while avoiding an unbooked promise.")
    tx6 = commit(6, "PROJECT-LIBRARY", reviews=[review(6, "PROJECT-LIBRARY", [r3], 5)])
    base = dict(record_id="SYS-RULE-0011", revision_id=r3, derivative_kind="specialization", inherited_portion="Every request remains in the shared queue.", differences=["Riverside may confirm pickups by phone for members without email."], reason="Keep the branch reachable without losing reservation records.", registration_state="pending")
    local = snap("Riverside phone confirmation", "At Riverside, volunteers may confirm pickups by phone and enter them in the shared queue.", why="Some members cannot receive email; the shared queue still prevents double promises.", parent_bases=[base])
    child1 = revise("LIB-RULE-0005", tx6, local, [window(6, tx6, 6)], "Keep the shared queue and record the branch's chosen contact method.")
    event = entity("outbox-event", "OUTBOX-REGISTER", scope_id="PROJECT-LIBRARY", source_commit_id=tx6, target_scope_id="GLOBAL", event_type="register-derivation", payload_refs=["rev://" + child1], delivery_state="delivered", ack_commit_id="TXN-000007", attempts=1)
    write(tx6, event)
    tx7 = commit(7, caused=[tx6])
    mp = entity("derivation-map", "MAP-SYS-RULE-0011", scope_id="GLOBAL", parent_id="SYS-RULE-0011", generation=1, watermark=7, registered_count=1, count_filter="registered children whose current status is not superseded", entries=[dict(child_id="LIB-RULE-0005", child_scope_id="PROJECT-LIBRARY", child_revision_id=child1, base_revision_id=r3, derivative_kind="specialization", summary="Riverside phone confirmation; shared queue retained.", reason="Members without email need access.", registered_in=tx7)], updated_in=tx7)
    records["SYS-RULE-0011"].update(derivation_map_ref=ref(mp), registered_derivative_count=1, updated_in=tx7)
    write(tx7, mp)
    write(tx7, records["SYS-RULE-0011"])
    tx = commit(8, "PROJECT-LIBRARY", caused=[tx7])
    local["parent_bases"][0]["registration_state"] = "registered"
    child2 = revise("LIB-RULE-0005", tx, local, [window(8, tx, 8)], "Branch owner acknowledges registration without changing the pinned shared rule.")
    tx = commit(9, reviews=[review(9, "GLOBAL", [r3], 8)])
    r4 = revise("SYS-RULE-0011", tx, snap("Lending request rule", "Every request enters the shared queue; use one pickup checklist while branches choose contact methods.", why="A common checklist helps substitute volunteers without removing local access options."), [window(9, tx, 9)], "Add a shared pickup handoff while preserving Riverside's pinned variation.")
    event = entity("outbox-event", "OUTBOX-PARENT-UPDATE", scope_id="GLOBAL", source_commit_id=tx, target_scope_id="PROJECT-LIBRARY", event_type="parent-updated", payload_refs=["rev://" + r4, "mem://LIB-RULE-0005"], delivery_state="pending", ack_commit_id=None, attempts=0)
    write(tx, event)
    tx = commit(10, "PROJECT-LIBRARY")
    capacity1 = revise("LIB-FACT-0003", tx, snap("Meeting room capacity claim", "The organizer reported that the meeting room seats 30.", type="fact", status="conflicted", why="The workshop plan used this unverified organizer account.", confidence=0.7, confidence_basis="The organizer's number is recalled clearly, but the current room limit is unverified."), [window(10, tx, 10)], "Keep the organizer account as a sourced, unresolved claim.")
    tx = commit(11, "PROJECT-LIBRARY")
    capacity2 = revise("LIB-FACT-0004", tx, snap("Booking sheet capacity claim", "An assistant reports that the venue booking sheet lists 20 seats for the same room.", type="fact", status="conflicted", why="The reported sheet conflicts with the organizer's account; the current capacity must be checked.", confidence=0.8, confidence_basis="The assistant's report is clear, but the original sheet is not captured and the current capacity is unresolved.", assertion=assertion("document") | {"reliability_note": "The retained source is an assistant report about a fictional booking sheet; the sheet itself is not in this fixture."}, edges={"contradicts": ["LIB-FACT-0003"]}), [window(11, tx, 11)], "Retain the reported document claim without choosing a winner or pretending to have the sheet.")
    conflict = entity("conflict", "CONF-0001", scope_id="PROJECT-LIBRARY", subject="Meeting room seating capacity", sides=[dict(record_id="LIB-FACT-0003", revision_id=capacity1, source_refs=["win://WIN-00010"]), dict(record_id="LIB-FACT-0004", revision_id=capacity2, source_refs=["win://WIN-00011"])], state="unresolved", resolution=None, resolved_in=None, created_in=tx)
    write(tx, conflict)
    tx12 = commit(12, "PROJECT-LIBRARY")
    cwin = window(12, tx12, 12)
    candidate = entity("candidate", "CAND-REJECTED", scope_id="PROJECT-LIBRARY", event_types=["IDEA_PROPOSED", "IDEA_REJECTED"], subject="Shared queue removal", candidate_statement="Let Riverside skip the shared request queue.", assertion=assertion("AI-inferred"), confidence=0.6, confidence_basis="Tentative assistant suggestion without user adoption.", source_refs=[cwin], state="open", state_history=[dict(state="open", reason="Tentative time-saving suggestion, not an owner decision.", commit_id=tx12)], resolution_record_id=None, created_in=tx12, updated_in=tx12)
    write(tx12, candidate)
    tx = commit(13, "PROJECT-LIBRARY")
    cwin2 = window(13, tx, 13)
    rejected = revise("LIB-IDEA-0001", tx, snap("Rejected queue removal", "Keep the shared queue at Riverside; skipping it was rejected.", type="idea", status="rejected", why="Without one record, volunteers could promise one item twice."), [cwin, cwin2], "The small time saving did not justify double booking risk.")
    candidate.update(state="rejected", source_refs=[cwin, cwin2], resolution_record_id="LIB-IDEA-0001", updated_in=tx)
    candidate["state_history"].append(dict(state="rejected", reason="Owner rejected the shortcut because duplicate promises would confuse members.", commit_id=tx))
    write(tx, candidate)
    tx14 = commit(14, "PROJECT-LIBRARY")
    proposal = entity("proposal", "SUG-PROMOTION", scope_id="PROJECT-LIBRARY", sender_principal_id="principal:library-owner", target_scope_id="GLOBAL", proposal_kind="promotion", subject_refs=["rev://" + child2], suggestion="Offer phone pickup confirmations to every branch that needs them, while keeping the shared queue.", source_refs=[window(14, tx14, 14)], state="accepted", response_reason="Shared-rule owner accepted an optional branch rule; Riverside's own adoption remains independent.", response_commit_id="TXN-000015", created_in=tx14)
    write(tx14, proposal)
    tx15 = commit(15, reviews=[review(15, "GLOBAL", [child2, r4], 14)], caused=[tx14])
    global2 = revise("SYS-RULE-0020", tx15, snap("Optional phone confirmation", "Branches may confirm pickups by phone when useful, but all confirmations stay in the shared queue.", why="Riverside's experience showed an access benefit without losing one reservation record.", edges={"promoted_from": ["LIB-RULE-0005"]}), [window(15, tx15, 15)], "Shared-rule owner offers the option without editing Riverside or other branches.")
    event = entity("outbox-event", "OUTBOX-PROMOTION", scope_id="GLOBAL", source_commit_id=tx15, target_scope_id="PROJECT-LIBRARY", event_type="promotion-accepted", payload_refs=["proposal://SUG-PROMOTION", "mem://SYS-RULE-0020"], delivery_state="delivered", ack_commit_id="TXN-000016", attempts=1)
    write(tx15, event)
    tx = commit(16, "PROJECT-LIBRARY", reviews=[review(16, "PROJECT-LIBRARY", [child2, global2], 15)], caused=[tx15])
    local.update(status="historical-origin", edges={"promoted_to": ["SYS-RULE-0020"]})
    revise("LIB-RULE-0005", tx, local, [window(16, tx, 16)], "Only Riverside's owner adopts the shared option and preserves its local origin.")
    tx = commit(17, "PROJECT-LIBRARY")
    revise("LIB-PREF-0001", tx, snap("Flyer spelling", "Use the spelling 'résumé' with accents on a future workshop flyer.", type="preference", why="An imported legacy preference mentions this spelling, but its original note was not retained.", valid_from=None, valid_time_note="Original legacy note date unknown."), [], "Legacy source and date are unavailable; do not invent either.", unknown=True)
    tx18 = commit(18)
    suggestion_window = window(18, tx18, 18)
    adoption_window = window(19, tx18, 19)
    schedule = revise("SYS-RULE-0010", tx18, snap("Large-print weekly schedule", "Publish a large-print weekly lending and event schedule at the desk.", why="Members who miss email and volunteers answering calls need the same visible information.", assertion=assertion("AI-inferred", [adoption_window])), [suggestion_window], "Assistant proposal was adopted by the user's next turn; direct revision evidence will be enriched later.")
    cand = entity("candidate", "CAND-CONFIRMED", scope_id="GLOBAL", event_types=["IDEA_PROPOSED", "RULE_CREATED"], subject="Weekly large-print schedule", candidate_statement="Offer a large-print weekly lending schedule at the desk.", assertion=assertion("AI-inferred", [adoption_window]), confidence=0.95, confidence_basis="Explicit user acceptance with reasons in the next turn.", source_refs=[suggestion_window, adoption_window], state="confirmed", state_history=[dict(state="open", reason="Assistant offered a tentative accessibility idea.", commit_id=tx18), dict(state="confirmed", reason="The user adopted it so members and volunteers can share one schedule.", commit_id=tx18)], resolution_record_id="SYS-RULE-0010", created_in=tx18, updated_in=tx18)
    write(tx18, cand)
    tx19 = commit(19, "PROJECT-LIBRARY")
    audit = entity("audit-run", "AUDIT-0001", scope_id="PROJECT-LIBRARY", auditor_principal_id="principal:auditor", source_log_id="LOG-EXAMPLE", message_start=1, message_end=20, auditor_version="synthetic-auditor-1", checkpoint=20, findings=["The schedule revision directly cites the assistant suggestion but omits the user's adoption from its revision evidence list; propose enrichment to the shared-rule owner."], repair_proposal_refs=["proposal://SUG-REPAIR"], created_in=tx19)
    repair = entity("proposal", "SUG-REPAIR", scope_id="PROJECT-LIBRARY", sender_principal_id="principal:library-owner", target_scope_id="GLOBAL", proposal_kind="repair", subject_refs=["rev://" + schedule], suggestion="Append a new weekly-schedule revision that directly cites the user's adoption and the audit explanation.", source_refs=[window(20, tx19, 20)], state="accepted", response_reason="Shared-rule owner adds the missing direct citation without editing the earlier revision.", response_commit_id="TXN-000020", created_in=tx19)
    write(tx19, audit)
    write(tx19, repair)
    tx = commit(20, caused=[tx19])
    revise("SYS-RULE-0010", tx, records["SYS-RULE-0010"]["current"], [suggestion_window, adoption_window, window(21, tx, 21)], "Provenance-only enrichment directly cites the user's reason while preserving the earlier revision.")
    event = entity("outbox-event", "OUTBOX-REPAIR", scope_id="GLOBAL", source_commit_id=tx, target_scope_id="PROJECT-LIBRARY", event_type="repair-proposed", payload_refs=["proposal://SUG-REPAIR", "mem://SYS-RULE-0010"], delivery_state="pending", ack_commit_id=None, attempts=0)
    write(tx, event)
    tx = commit(21, "PROJECT-LIBRARY", reviews=[review(21, "PROJECT-LIBRARY", [r4, global2], 20)])
    bases = [dict(base, revision_id=r4, registration_state="pending", derivative_kind="combination", inherited_portion="Every request enters the shared queue and follows the pickup checklist.", differences=["Riverside may confirm pickups by phone."], reason="Combine the current shared checklist with Riverside contact access."), dict(base, record_id="SYS-RULE-0020", revision_id=global2, registration_state="pending", derivative_kind="combination", inherited_portion="Branches may confirm pickups by phone while retaining the shared queue.", differences=["Riverside commits to this option for its own volunteers."], reason="Members without email need a dependable confirmation path.")]
    pending = revise("LIB-RULE-0006", tx, snap("Combined Riverside variation", "Riverside uses the shared queue and pickup checklist, with optional phone confirmations.", why="Both exact shared rules apply; neither independently specifies the full Riverside handoff.", parent_bases=bases), [window(22, tx, 22)], "Combine two pinned shared rules; register with each parent separately.")
    event = entity("outbox-event", "OUTBOX-COMBINATION", scope_id="PROJECT-LIBRARY", source_commit_id=tx, target_scope_id="GLOBAL", event_type="register-derivation", payload_refs=["rev://" + pending], delivery_state="pending", ack_commit_id=None, attempts=0)
    write(tx, event)

    # Response/delivery fields are projections of scoped historical events.
    # They never authorize a recipient to rewrite the sender's source object.
    for value in objects.values():
        if value["kind"] == "proposal":
            value["response_history"] = [dict(state=value["state"], reason=value["response_reason"], commit_id=value["response_commit_id"])] if value["response_commit_id"] else []
        elif value["kind"] == "outbox-event":
            value["delivery_history"] = [dict(state="pending", reason="Durably queued by source owner.", commit_id=value["source_commit_id"])]
            if value["ack_commit_id"]:
                value["delivery_history"].append(dict(state="delivered", reason="Target owner committed an acknowledgement.", commit_id=value["ack_commit_id"]))
        elif value["kind"] == "conflict":
            value["state_history"] = [dict(state="unresolved", reason="Contradictory sourced claims retained.", commit_id=value["created_in"])]
    for c in commits.values():
        c["payload_sha256"] = digest(canonical({k: v for k, v in c.items() if k != "payload_sha256"}))
    config = entity("config", "CONFIG-EXAMPLE", primary_byte_budgets={sid: 20480 for sid in ["GLOBAL", "USER", "PROJECT-LIBRARY", "TASK-DESK"]}, encoding="UTF-8", line_ending="LF", snapshot_sequence=21, profile="portable-files-alpha", artifact_role="illustrative-fixture", required_extensions=[])
    for scope in config["primary_byte_budgets"]:
        chosen = [r for r in records.values() if r["scope_id"] == scope and r["current"]["status"] not in ["rejected", "historical-origin"]]
        entries = [dict(record_id=r["id"], revision_id=r["current_revision_id"], pinned=r["current"]["importance"] == "critical") for r in sorted(chosen, key=lambda x: x["id"])]
        path = f"primary/{scope}.md"
        raw = primary_bytes(scope, entries, records)
        files[path] = raw
        entity("working-set", f"WORKING-{scope}", scope_id=scope, snapshot_sequence=21, budget_bytes=20480, counting_method="UTF-8 bytes of the named rendered file", token_count=None, tokenizer=None, entries=entries, rendered_file=path, rendered_sha256=digest(raw), actual_bytes=len(raw), overflow=False, omitted_record_ids=[r["id"] for r in records.values() if r["scope_id"] == scope and r not in chosen])
    for value in objects.values():
        files[f"{value['kind']}/{value['id']}.json"] = jsonbytes(value)
    return files

def generate(destination):
    destination.mkdir(parents=True, exist_ok=True)
    for name, data in build().items():
        path = destination / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--output", type=Path, default=MEM)
    args = parser.parse_args()
    expected = build()
    if args.check:
        actual = {p.relative_to(args.output).as_posix(): p.read_bytes() for p in args.output.rglob("*") if p.is_file()}
        mismatch = sorted(set(actual) ^ set(expected) | {n for n in actual.keys() & expected.keys() if actual[n] != expected[n]})
        print("example generation:", "PASS" if not mismatch else "DIFFERENT " + ", ".join(mismatch))
        return bool(mismatch)
    # This generator only replaces its dedicated fixture tree, never a live memory.
    target = args.output.resolve()
    if target != MEM.resolve() and target.exists() and any(target.iterdir()):
        raise SystemExit("custom output must be empty; refusing to overwrite arbitrary files")
    if target == MEM.resolve() and target.exists():
        if target.parent != (ROOT / "examples").resolve() or target.name != "memory":
            raise SystemExit("fixture output containment check failed")
        shutil.rmtree(target)
    generate(target)
    print(f"generated {len(expected)} fixture files (synthetic only)")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
