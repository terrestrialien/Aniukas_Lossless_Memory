# Acceptance and evaluation plan

These are required future tests, **not test results**. The current deliverable is a specification. Use synthetic conversations and principals so a public test suite contains no personal memory. Record implementation version, profile, adapter/model versions, host capacity, fixture seed, commands, outputs, and failures for every run.

The case IDs below map to build-spec sections. The [requirements checklist](REQUIREMENTS.md) maps `ALM-001`–`ALM-132` to specification sections and acceptance cases. Tests verify behavior rather than a particular programming language or internal backend. The [portable reference format](REFERENCE_FORMAT.md) is an explicit exception: interoperability checks verify its required field names and encoding.

## Applicability by setup type

These profiles are defined in [ADAPTATION.md](ADAPTATION.md). **Capture/manual** is a partial implementation with durable source, authorized manual decisions, exact reads and portable restore. **Portable automatic** adds bounded working-set routing, inheritance/governance and live extraction/audit. **Accelerated local** and **Service-backed** include the portable automatic behavior; they add accelerator and multi-client service checks respectively. A builder can declare a different combination of capabilities, but must list each omitted required scenario as `not implemented` rather than claiming full conformance.

`R` means the setup must pass the listed case IDs to claim that profile. `NI` means the capability is beyond Capture/manual and must be reported as `not implemented` until built. `C` is conditional on the named optional feature/backend; only an absent optional feature can be marked `not applicable`. The groups below partition all A01–A71 IDs without gaps or overlaps.

| Acceptance IDs | What they cover | Capture/manual | Portable automatic | Accelerated local | Service-backed |
| --- | --- | :---: | :---: | :---: | :---: |
| A01–A10 | Source, identity, revisions, conflicts and event meaning | R | R | R | R |
| A14–A16, A18–A20, A22 | Exact evidence, historical and fallback retrieval, consequential review, lexical/graph fallback | R | R | R | R |
| A23–A24, A33–A34 | Scoped authority, reassignment and hostile source text | R | R | R | R |
| A44–A50, A53 | Transactions, recovery, portable restore, capacity and public-data hygiene | R | R | R | R |
| A55–A58, A63–A64, A67, A69 | Immutable reconstruction, stale review, authentication, format and clean installation | R | R | R | R |
| A11–A13, A17, A21, A62, A70–A71 | Bounded working set, batch routing, derivative maps, category views and policy tuning | NI | R | R | R |
| A25–A32, A59–A61 | Inheritance, parent registration, proposals and promotion | NI | R | R | R |
| A35–A43, A65, A68 | Live observation, candidates, audit, workflow restore and host adapter | NI | R | R | R |
| A51–A52 | Long-history and fixed-context growth benchmarks | NI | R | R | R |
| A54 | Explicit governed erasure | C | C | C | C |
| A66 | File-backed canonical commit crash protocol | C | C | C | C |

For A54, `C` means required if governed erasure is implemented; otherwise mark `not applicable`. For A66, `C` means required for a files-backed canonical store; a transactional backend instead must pass A44–A46 and document its own crash/restore tests. Capture/manual must still exercise source-capacity handling in A50; the observer-backlog branch remains `not implemented` until observation exists. Full profiles exercise the A49 manual fallback when an extraction adapter is unavailable. Accelerated local additionally exercises A22 with enrichment disabled and runs A51–A52 with its claimed adapters enabled. Service-backed runs A23–A24, A45–A48, A50 and A58 with distinct authenticated clients and its service storage. A full conformance claim requires every `R` case plus each applicable `C` case.

## Evidence, identity, and memory correctness

| ID | Scenario | Pass condition | Spec |
| --- | --- | --- | --- |
| A01 | Import full conversations with repeated paragraphs, Unicode, a non-UTF-8 encoding fixture, attachments, and incomplete timestamps | Original bytes recover exactly; source selectors decode against the correct original encoding; ordering preserved; missing metadata/attachments explicitly marked; no fabricated times | 4 |
| A02 | A rule changes seven times for different reasons | Current rule resolves correctly and all seven revisions preserve authorizers, dates/unknown dates, rationale, and exact source ranges | 4–5 |
| A03 | Move, rename, split, compress, and restore source files | All stable IDs and both directions of traversal still resolve; digests match | 4, 9 |
| A04 | Corrupt a derived summary while preserving raw source | Exact source reveals error; authorized repair appends a revision; original evidence and bad historical interpretation remain inspectable | 5 |
| A05 | Change a temporally valid fact, then ask a historical question | Earlier question uses the earlier valid interval and its reasoning; current question uses current state | 4 |
| A06 | User observation, tentative belief, model inference, document claim, and decision concern the same subject | Types and provenance stay distinguishable; confidence does not upgrade an inference into human authority or objective truth | 3–5 |
| A07 | New evidence conflicts with an old assertion | Both claims survive; relevant read shows unresolved conflict; explicit authorized resolution preserves prior claims | 5 |
| A08 | Reintroduce a rejected or deferred idea under both unchanged and changed conditions | Retrieval surfaces old rationale/status; reconsideration is possible with new evidence; no silent revival or repeated duplicate | 5–6 |
| A09 | Repeat an import and replay every event | No duplicate canonical memory or revision from the same event key; additional independent corroborating sources may be attached | 4–5, 9 |
| A10 | One statement changes priority, defers a feature, and changes project scope | Multiple semantic tags can describe one state transition without three duplicate decisions | 5 |

## Retrieval and working-set behavior

| ID | Scenario | Pass condition | Spec |
| --- | --- | --- | --- |
| A11 | Routine task with applicable global, user, project, and task context | Receives a bounded selected set plus current context; no automatic loading of all secondary/other-project history | 3, 6 |
| A12 | Need an old secondary decision absent from primary | Router searches secondary/current indexes and retrieves it; promotion is temporary or persisted according to policy | 6 |
| A13 | Rare but critical conditional constraint triggers | It is surfaced despite low frequency; mandatory overflow is reported instead of silently omitting it | 6 |
| A14 | Ask current, why, verify, and reconstruct queries about the same record | Appropriate depth returned; deterministic pointers used after discovery; no forced full-log load for routine query | 6 |
| A15 | Request history with depths 0, 2 and 3 available; then request depth 2 with only 0 and 1 available | First returns depth 2, never an unnecessary jump to 3; second returns 1 with evidence insufficiency. Both expose requested/returned/available depths and fallback reason | 6 |
| A16 | Original evidence is absent, pointer broken, or access denied | Each condition is distinguishable; deepest available evidence and uncertainty shown; no fabricated text | 4, 6 |
| A17 | Retrieve five branches at different depths | Bundle identifies snapshot and each branch's requested/returned depth; further descent targets only uncertain branches | 6 |
| A18 | Evidence window refers to an earlier conversation | Exact window remains unchanged; expansion follows adjacent context/reference with separate provenance | 4, 6 |
| A19 | Consequential override has inadequate reasoning | Review descends or returns insufficient evidence; substantive receipt identifies inspected versions/evidence and conclusion; a low token cap or an empty review list does not authorize the change | 6, 8 |
| A20 | Full reconstruction exceeds one model context | Resumable batches cover selected manifest; omissions explicit; all evidence remains accessible | 6 |
| A21 | Large derivative map and large secondary store | Parent primary retains only compact count/pointer; exact paginated map entry found without scanning whole file | 6, 8 |
| A22 | Disable embedding/reranking adapters | Lexical search, graph traversal, and exact references still work; lost enrichment is reported | 6, 10 |

## Permissions, inheritance, and cross-project learning

| ID | Scenario | Pass condition | Spec |
| --- | --- | --- | --- |
| A23 | User, governor, project A/B owners, and worker each attempt every scope's reads/writes | Matrix matches §7 symmetrically for A and B; universal reads require authorized agency identity | 7 |
| A24 | Attempt indirect foreign-scope edits to confidence/status/history/metadata/counts/links/files | Unauthorized change rejected; no backdoor through compiler, import, projection, or generic filesystem credentials | 7, 9 |
| A25 | Project creates an exception to a global parent | Own scope receives derivative and genealogy; parent semantic content unchanged; registration routed to authorized owner | 8 |
| A26 | Parent-map registration worker crashes or delivery repeats | Child persists, pending state visible, idempotent retries eventually register exactly one map entry/count | 8–9 |
| A27 | New project reuses a prior derivative, while another already knows its solution | First may inspect/adapt with ancestry; second can skip derivative browsing while still satisfying history review | 6, 8 |
| A28 | Derivative is a restriction, extension, specialization, override, exception, or combination | Type, base revisions, inherited portion, delta/full meaning, and reasons are preserved | 8 |
| A29 | Introduce inheritance cycle or incompatible multiple parents | Cycle rejected; ambiguous combination becomes conflict; no arbitrary precedence selection | 8 |
| A30 | Parent later changes or local exception condition expires | No silent project rewrite; owner gets a review proposal; pinned prior effective meaning remains reconstructable | 8 |
| A31 | Promote project-origin rule into global scope | Global owner authorizes; origin/variants/rationale/sources retained; governor cannot retire project records; project owners choose adoption | 7–8 |
| A32 | Governor suggests project change and project rejects it | Durable proposal, sender/recipient, response, rationale, and exact sources remain available to prevent repeated uninformed proposals | 7 |
| A33 | Replace project agent/model and revoke old assignment | New owner receives same full memory; old credentials cannot commit; global/other-project permissions unchanged | 7, 10 |
| A34 | Source text says to ignore permissions or modify global memory | Text remains evidence; it cannot become service authority or escape scoped commit validation | 3, 7 |

## Extraction, review, and audit

| ID | Scenario | Pass condition | Spec |
| --- | --- | --- | --- |
| A35 | User makes an indirect but clear decision, then corrects it | Observer recognizes both transitions live, links exact evidence, and preserves the earlier interpretation | 5 |
| A36 | Clear authority, ambiguous suggestion, and exploratory alternatives | Clear authorized decision auto-commits; ambiguous candidate persists; exploration is not falsely activated | 5 |
| A37 | Assistant suggestion receives no response under default policy | It remains unconfirmed unless adoption evidence/policy exists; user-approved bounded import policy can accept it with provenance | 5 |
| A38 | Later reasoning implicitly adopts an earlier candidate | Both evidence locations and inference basis preserved; authority/scope checks still enforced | 5 |
| A39 | Candidate ages out of active turn buffer | Candidate retained durably with disposition; it can be revisited; source not deleted | 5 |
| A40 | Ask “decisions so far” and batch approve/reject/defer/reopen selected candidates | Correct labelled counts, confidence/basis, and independent selected transitions; no repeated confirmation for clear decisions | 11 |
| A41 | Early remark becomes significant much later, after context compaction | Retrospective audit finds it from full archive, adds origin/correction through authorized path, and keeps later sources | 5 |
| A42 | Observer and auditor both miss a decision | Deeper source search can still recover it; capture completeness is separate from extraction completeness | 4–5 |
| A43 | Every user/assistant turn, repeated delivery, and extraction outage | Sources durably captured; checkpoints/replay avoid loss/duplication; backlog visible; compiler has no universal write bypass | 5, 9–10 |

## Durability, portability, and scale

| ID | Scenario | Pass condition | Spec |
| --- | --- | --- | --- |
| A44 | Crash at each point of a five-record semantic update within one authorized transactional scope | Either all canonical changes become visible or none; no impossible mixed state. Separately authorized cross-scope workflows use A26's pending-state and idempotent-completion checks | 9 |
| A45 | Concurrent agents edit the same expected revision | One commit succeeds; stale writer gets a conflict and re-reads; history never silently overwritten | 9 |
| A46 | Crash after source finalization and before metadata commit | Source preserved; no committed dangling pointer; orphan source reconciled; replay idempotent | 9 |
| A47 | Corrupt or remove a search/primary projection | Rebuild from canonical archive/history; reads identify lag; authoritative current data remains obtainable | 9 |
| A48 | Restore backup and migrate to a second backend | IDs, source hashes, complete history, all existing candidates/proposals, relationships, and permissions preserved; forward/reverse traversal validates. Full automatic profiles use populated candidate/proposal histories | 9–10 |
| A49 | CPU-only host with no embeddings, no cloud account, and unavailable extraction model | Capture/manual operation works; automatic extraction marked unavailable/backlogged; no silent remote calls or GPU dependency | 10 |
| A50 | Source store reaches capacity or observer falls behind | Explicit capacity/backpressure alert, durable existing data, no silent log deletion or dropped events | 9–10 |
| A51 | Generate at least 50,000 interactions with repeated decisions/rejections/contradictions | Historical chain reconstruction and discovery recall measured against ground truth; correctness failures reported | 12 |
| A52 | Grow metadata/maps at fixed context budget on same host | Primary token bound holds; routine current lookup/evidence fetch p50/p95 measured at each size; degradation visible and addressed | 6, 12 |
| A53 | Inspect a proposed public export/repository | No private logs, operational DBs, credentials, embeddings, machine/user paths, or private conversations; synthetic fixtures only | 13 |
| A54 | Apply optional explicit erasure | Declared governed data removed according to scope, references tombstoned, lossless exception explicit; ordinary compaction cannot invoke it | 13 |

## Extended correctness cases

| ID | Scenario | Pass condition | Spec |
| --- | --- | --- | --- |
| A55 | Reconstruct every revision after repeated rejection, reactivation, promotion and provenance enrichment | Exact full historical snapshots round-trip; current projection equals referenced snapshot; old source lists/statuses/rationale remain byte-stable; no model guesses missing historical text | 4–5, 9 |
| A56 | Record a late correction to an earlier valid interval; repeat reads at earlier and later commit snapshots | Each effective-time/recorded-snapshot pair has deterministic results; concurrent pagination stays on one snapshot; incompatible intervals or unknown original times are explicit | 4, 6, 9 |
| A57 | Change a reviewed parent/dependency before committing; submit empty or unrelated receipts; set high-impact flag false for a global reversal | Stale/empty/unrelated review rejected; required review classification cannot be disabled by caller; authenticated reviewer and inspected versions remain auditable | 6–9 |
| A58 | Forge actor/grant/scope payloads, reuse revoked credentials, queue work before owner transfer, import foreign historical grants | Payload cannot impersonate a principal; revoked grants cannot authorize new writes; imported history creates no live rights; replay returns only identical existing results | 7, 9 |
| A59 | Two applicable equal-specificity overrides, unknown condition, compatible separate constraints and incompatible multiple parents | Explicit resolved merge or visible ambiguity/conflict; no silent false condition, arbitrary winner or dropped constraint; pinned complete local meaning stable | 8 |
| A60 | Parent changes after a local derivative, then registration succeeds after a retry | Child's historical snapshot and pinned parent stay unchanged; registration appears through separate map/event state; no mutation of child or parent semantic revision | 8–9 |
| A61 | Local owner proposes global adoption; global owner accepts; local owner rejects adoption | Separate authenticated commits; origin, global canonical rule, rejected local response and pending notifications all persist; no governor edits project status or links | 7–9 |
| A62 | Individually small Primary scopes plus pinned entries, current context and temporary evidence overflow one model context | Combined accounting includes reserves and serialization; missing required constraints identified; complete flag false; partition/resume preserves obligations | 6 |
| A63 | Generate fixtures on Windows, macOS and Linux; import LF/CRLF/BOM/Unicode/legacy-encoding originals | Generated synthetic bytes/digests deterministic across hosts; imported source retains its own exact original bytes and selectors after export/restore | 4, 9–10 |
| A64 | Corrupt/misspell entity and bare IDs; duplicate IDs; delete evidence; reverse window ranges; use a nonexistent message; omit derivative bases | Format/semantic validator rejects each independently with a useful diagnostic; it does not crash or accept false links | 4, 8–10 |
| A65 | Restore with pending capture, candidates, proposal responses, outbox registration, review receipts and audit cursors | Durable workflow state and history survive; replay completes once with current permissions; no skipped source event or double-counted derivative | 5, 7–9 |
| A66 | Crash before/after every visibility boundary in a files-backed canonical implementation | Only committed generations visible; no partial record set; finalized captured source recoverable. Mark not applicable only when a different documented transactional backend is used | 9 |
| A67 | Import unsupported required extension, colliding IDs or an incomplete export | Reject or quarantine before activation; no silent stripping of semantics, ID reassignment or partially visible import | 9–10 |
| A68 | Connect a real host, ingest user/assistant/tool events and edits, then disconnect extraction | Live capture acknowledgment, explicit unavailable attachments/hooks, safe resume and retained original edited versions; auto-extraction delay is visible | 4–5, 10 |
| A69 | Fresh installation on each supported OS/runtime from a clean checkout | Documented commands reproduce fixture checks and applicable runtime cases; no personal paths, undeclared tools, cloud/GPU prerequisite or reused local secret | 10, 13 |
| A70 | View the same record under decisions, facts, preferences, questions, state/events, people/ideas, architecture, experiments and hardware categories as applicable | Views return the same canonical identity/revision and exact supporting links; category changes create no duplicate authority or permission scope; Primary stays bounded | 3, 6 |
| A71 | Change the memory constitution's permitted extraction/selection thresholds, then replay earlier recorded decisions | Outcomes identify their policy version; historic decisions stay reconstructable; changes require authorized policy administration and cannot disable retention, review, ownership or uncertainty invariants | 5–9 |

Artifact-only checks for A63–A64 may run before the service exists. Report the covered subchecks as artifact results, not as passing runtime scenarios such as A23, A44 or A68. A syntactically valid grant/commit fixture demonstrates a contract; it cannot demonstrate that a running service authenticates its caller or survives a crash.

## Evaluation fixture design

Build a deterministic human-authored fixture with expected final decisions, revision chains, authorizers, and exact source selectors. Include one ambiguous case that must remain unresolved. Supplement it with generated long histories; do not use the same extraction model to create all “ground truth” and then treat its agreement as independent validation.

For extraction, measure precision and recall separately for confirmed decisions, candidates, revisions, rejection/deferral, and evidence alignment. Report false promotion of exploratory text as an error. For retrieval, measure discovery recall, exact pointer integrity, correct valid-time answers, and reconstructed revision order. Permission and integrity tests require zero unauthorized writes and zero silently altered source bytes; statistical model accuracy needs declared measured targets and limitations.

For latency, declare a deployment-specific p95 objective before running. Measure direct reads separately from search and model generation. Include cold/warm cache and growing archive sizes. A fixed-size primary result is a guaranteed design invariant; a fixed latency across arbitrary hardware is not.

A release report must mark each scenario `pass`, `fail`, `not implemented`, or `not applicable to declared optional profile`, with evidence. Shipping a subset requires an explicit feature matrix. A full conformance claim requires every applicable required scenario and requirement; optional backend alternatives are tested when shipped.

For an automatic implementation, predeclare extraction and retrieval thresholds on a held-out, human-reviewed fixture before tuning; report sample counts and errors, not only percentages. At minimum, no exploratory/assistant-only suggestion may be presented as a human-confirmed decision without adoption evidence in the deterministic authority fixtures. Numerical language-model accuracy targets are deployment choices. Failed accuracy targets require a reduced or review-required capability label, not deletion of missed source content.

Release gate: confirm every `ALM-001`–`ALM-132` requirement has a specification section and relevant acceptance scenario, and record its implementation status. Any deferred required capability stays visible as `not implemented`, with its phase and reason. Do not remove a requirement merely to obtain an all-green release table. Run clean-checkout checks for the supported package and live behavior checks on the shipped runtime.
