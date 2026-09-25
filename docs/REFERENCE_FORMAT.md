# Portable reference format: profile 1

This is the executable **illustrative fixture profile** for Aniukas Lossless Memory. Its `format_version` is the string `"1"`; release and storage-format versions are separate. The 17 schemas, generators and validators define concrete examples of the core contracts. They are not a memory server, complete backup format, authentication system, observer, importer or proof that every acceptance scenario passes.

[DATA_CONTRACTS.md](DATA_CONTRACTS.md) defines the complete logical implementation/export requirements. A production export must also preserve every logical entity and required state omitted from this bounded example: effective policy and grant history, jobs/checkpoints, attachment bytes, search/projection configuration, ownership transfer, historical delivery attempts, category definitions, extension declarations and the complete `ExportManifest`. A developer must implement and version those extensions before claiming complete backup/restore. Silently dropping them to fit these fixtures is forbidden. The supplied config explicitly declares `artifact_role: illustrative-fixture`.

## Encoding and identities

Each JSON object has `format_version`, `instance_id`, `kind`, and `id`. IDs are opaque, case-sensitive, unique across **all entity kinds within one instance** and retained during migration. Names such as `SYS-RULE-0011` are readable fixture IDs, not a required production allocation algorithm. A production deployment should allocate collision-resistant IDs. References in this profile are local to the declared instance; cross-instance merge must detect collisions and use an explicit namespaced mapping rather than silently reinterpret IDs.

All generated JSON and JSONL uses UTF-8 without BOM, LF line endings, and a final LF. Original imported source bytes remain exactly as supplied, regardless of encoding or line endings. Hashes cover actual bytes. Original text is never re-encoded merely to fit this JSON convention. Paths are slash-separated relative paths inside the snapshot; absolute paths, escaping paths and symbolic links are rejected. Git attributes protect hash-bearing fixtures from line-ending conversion.

For structured payload hashes, canonical bytes are `json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")`. This is the exact fixture algorithm, not a claim of RFC 8785 compliance. Implementations must match it for this profile or negotiate a different versioned production canonicalization contract. `snapshot_sha256` hashes `snapshot`; `payload_sha256` hashes the commit envelope with only `payload_sha256` omitted. The latter protects envelope consistency; it is **not a signature** and does not authenticate an untrusted export or commit payload files.

Unknown fields are rejected except in `extensions`, an object of namespaced keys such as `org.example.feature`. Optional extensions must survive import/export unchanged. Config `required_extensions` names mandatory semantics. This checker supports no extra required extensions and rejects a nonempty list; production importers must reject unknown required semantics instead of silently ignoring them. Incrementing `format_version` requires an explicit migration with preservation checks; schemas must never silently reinterpret an old enum or ID.

## Entity and reference map

Entities are stored at `<kind>/<percent-encoded-id>.json` (encode characters such as colon that are not portable in Windows filenames); logs have separately named raw/chunk files. Location is not identity. A production index may locate these IDs differently.

| Kind | Reference | Purpose |
| --- | --- | --- |
| `record` | `mem://ID` | Current projection and the current immutable revision ID/count. |
| `revision` | `rev://ID` | Full immutable semantic snapshot, rationale, alternatives and evidence. |
| `evidence-window` | `win://ID` | Exact inclusive message range into a digest-identified source. |
| `log-manifest` | `log://ID`, `log://ID/m1-3` | Original bytes and mapped normalized message chunks. |
| `log-message` | Through its log/ordinal | Stable message ID, role, speaker, exact decoded text and original byte selector. |
| `derivation-map` | `map://ID` | Parent-owner projection of separately registered local derivatives. |
| `proposal` | `proposal://ID` | Sender-owned request plus recipient-response projection. |
| `candidate` | `candidate://ID` | Tentative extracted event with retained lifecycle and confirmation basis. |
| `conflict` | `conflict://ID` | Competing exact revisions, evidence, status and resolution history. |
| `commit` | `commit://ID` | Scope-local authenticated-authority receipt and ordered change envelope. |
| `review-receipt` | `review://ID` | Exact read snapshot, dependencies, sources, reasoning and review outcome. |
| `outbox-event` | `outbox://ID` | Source-owner durable event and derived delivery/acknowledgement state. |
| `audit-run` | `audit://ID` | Declared source range/checkpoint and proposed repairs. |
| `scope`, `grant` | ID fields | Ownership and trusted administrative grant metadata. |
| `working-set`, `config` | ID fields | Bounded rebuildable Primary projection and fixture settings. |

This concrete profile uses `rev://current-revision-ID` as `record.history_ref`; follow `predecessor_id` for earlier revisions. It has no `hist://` shorthand and no Markdown-front-matter canonical records. Schemas reject obsolete fields and aliases so two implementations cannot accidentally select different meanings.

## Revisions and current meaning

`record.current` must equal its latest `revision.snapshot` exactly. `current_revision_id` and `revision_count` must agree with that record's complete history. The profile uses a **linear per-record history**, numbered from 1, with a scalar nullable `predecessor_id`. Multiple source origins and combined rules are represented through edges and pinned bases, not branched predecessor chains. A richer implementation can use a declared extension for branching while exporting an unambiguous selected history and preserving the other branches.

Snapshots contain type, status, title, statement, concise reason, importance, confidence and `confidence_basis`, assertion provenance, effective interval, trigger/condition/consequence lists, graph edges and pinned parent bases. `confidence` describes confidence in the stated interpretation; it is not factual certainty or permission. `assertion.asserted_by`, `assertion.kind`, `reliability_note` and `adoption_evidence` describe source authority. Adoption evidence must name exact `win://` source windows, never an ordinary current-memory pointer. They are independent of the commit principal and grant. An unconfirmed `AI-inferred` assertion cannot have confidence 1.

`created_at` on a historical revision and message/source times may be null only with a meaningful time note. Profile timestamps use fixed whole-second UTC RFC 3339, such as `2026-09-23T12:00:00Z`; production precision extensions must not silently truncate original times. Unknown effective time requires `valid_time_note`; do not invent historical dates. `commit.created_at` is a known recording time, and `commit.sequence` supplies strict ordering for the exported snapshot. Effective time and recorded time answer different questions.

Historical revisions retain the status they had when created. They are never rewritten to `PAST`. Currentness is determined by record pointers and commit sequence. `historical-origin` is a supported lifecycle state when the local owner accepts a promotion. Provenance enrichment appends a new revision even when semantic meaning is unchanged. `--baseline` detects removed/changed immutable revisions, commits, source messages/manifests and review receipts; The baseline keeps fixture manifest file mappings fixed; a production resolver may relocate source files while preserving identity, exact bytes and explicit old-to-new physical location projections. A one-snapshot check cannot establish that maliciously recomputed hashes were never altered.

Every revision has at least one precise `win://` source or an explicit `evidence_gap` reason/deepest-available marker. The synthetic legacy preference illustrates a legitimate gap. Adding an arbitrary valid pointer to prose does not satisfy these canonical fields. Window `cited_by` is a rebuildable reciprocal list of citing revision IDs; selectors themselves are immutable. Extending the backlink projection must not mutate the original source or revision.

## Scope, grants and transactions

A `scope` names its owner and separately its trusted `grant_authorizer_id`. Fixture grants are issued by `principal:human-admin`; a governor or project agent does not authorize itself. The root administrative identity and grants must come from a trusted authenticated installation boundary, not from importing arbitrary attacker-controlled JSON. Each grant declares principal, exact scope, role, operations, generation, issuance and optional revocation time. Permission inheritance across parent scopes is forbidden. A governor has no project-write authority merely because GLOBAL is a project's parent scope.

A commit declares one `scope_id`, principal/grant, sequence, known recording time, idempotency key, causal predecessors, explicit object writes, expected record revisions, sources and review receipt IDs. `writes` is an envelope of changed entity identities, **not an executable replay journal containing complete before/after file bytes**. Production atomic commit/recovery needs the transaction journal/generation protocol or database transaction equivalent in DATA_CONTRACTS. Each immutable revision must be included in its commit together with its current record update and expected predecessor; stale expectations reject the commit. Metadata writes, maps, windows and conflicts are subject to the same scope rule.

Commit principals are authenticated by the future runtime; the checker tests only internal consistency of the supplied grant receipts. It cannot establish external identity, enforce filesystem ACLs, prevent a process from bypassing a server or prove crash atomicity. Those are mandatory implementation acceptance gates.

High-impact commits require nonempty `review_receipt_ids`. The structured receipt records actor/grant, `read_sequence`, exact reviewed record/revision pairs, source-window digests, intent, alternatives, constraints, consequences, gaps, conflicts and outcome. A sufficient outcome is required. Reviewed dependencies must still be current immediately before the commit; a parent/dependency change invalidates the old review. Review records must precede the commit in recording order. A receipt is evidence of a review process, not proof of model comprehension.

## Derivation and promotion

There is exactly one representation of inheritance: `snapshot.parent_bases`, an array. Each entry contains parent record ID, exact base revision ID, derivative kind, inherited portion, differences, reason and registration state. Single and multiple parents use the same form. Generic edges are arrays of record IDs; `edges.parent` is rejected so inheritance has one unambiguous representation. All targets resolve, pinned bases belong to the named parent and existed before the child commit, and current inheritance is acyclic.

Registration requires separate scoped commits. `TXN-000006` creates the project derivative and durable outbox event. `TXN-000007` is the governor-owned map/count update. `TXN-000008` is the project-owned acknowledgement. The child keeps its exact old base after the parent changes in `TXN-000009`. A pending registration can be valid local memory when its durable event remains pending; it is excluded from the parent's registered count. A registered child requires a reciprocal map entry.

Map entries include child scope for selection without fetching every child, and name the child revision **at registration**, the pinned parent base, kind and registering commit. Current child lineage must still match the registered entry; a later rebase must update registration through the owner workflow. The example child later becomes historical origin while retaining its ancestry. Map count filter is explicitly `registered children whose current status is not superseded`, including that historical-origin record. Superseded children leave this current map projection; immutable registration history must remain available. Counts describe registered derivatives under the filter; they do not claim all possible/pending children.

Promotion uses a project proposal (`TXN-000014`), independent global creation with `promoted_from` (`TXN-000015`), and independent project adoption with `promoted_to` (`TXN-000016`). The governor never writes the originating project. The accepted `proposal.state/response_*` fields are **read-model projections** of the target-owned outbox response event/commit; target acceptance does not authorize changing the immutable sender request. Outbox identity/payload fields are immutable; delivery fields/history are projections of source/recipient-owned events. Production exports must retain all immutable transitions and attempts, not just these final projections.

Candidate, conflict, proposal-response and delivery histories are append-only arrays in this small fixture profile. The checker verifies lifecycle consistency and baseline-prefix preservation. Production implementations must store authorized immutable lifecycle events and preserve them in export; an array alone is not a concurrency or authorization mechanism. Rejected candidates remain retrievable; assistant speculation is not silently promoted to user authority. The confirmed candidate includes its contextual adoption evidence. Audit repairs are proposals to the owning scope, and accepted provenance repair appends a revision.

## Evidence bytes and bounded Primary

The synthetic log retains `logs/original.txt` exactly, including its fictional timestamps, speaker labels and reasoning. Normalized JSONL messages map their text to half-open original byte ranges (`original_byte_start`, `original_byte_end`) and carry the same time and speaker as fields. The known times in this fixture are examples; a real import must preserve unavailable metadata as unknown. Missing identities use `role: unknown`, `speaker: null` and an `identity_note`, never fabricated people. The checker verifies the original digest/byte length, chunk digest/length, ordered nonoverlapping chunk ranges, unique messages, decoded byte selectors, complete/partial declarations and evidence/backlink agreement. Window start/end are inclusive message ordinals; before/after context is requested padding, not a change to cited boundaries.

Primary is explicitly derived from current selected records using `primary_bytes()` in the generator. Each rendered entry shows only current meaning, status, the revision count with a history pointer and, when a rule has registered derivatives, their count with the exact map pointer; the history and derivative details themselves stay outside Primary. Each working set contains exact record/revision IDs, snapshot watermark, pinned flags, omitted record IDs, rendered path/hash, counted bytes and ceiling. This profile counts **UTF-8 bytes**, not model tokens. Optional token measurements require both token count and tokenizer identity. A production working set must also honor the model/token budget and policy rules in DATA_CONTRACTS. A too-large Primary fails even if a caller sets `overflow: true`; a production implementation must return a blocked/minimal overflow result under its separate response contract, without deleting canonical memories.

## Running the artifact checks

From the package root, after installing `requirements-dev.txt`:

```sh
python tools/gen_schemas.py --check
python tools/gen_examples.py --check
python tools/validate_examples.py
python tools/check_pointers.py
python -m unittest discover -s tests
```

Both generators use actual UTF-8 byte writes on every OS. `--check` compares expected bytes without changing files. `gen_examples.py --output EMPTY_DIRECTORY` creates a separate synthetic snapshot; it refuses a nonempty custom output. Default generation replaces only the checked, dedicated `examples/memory` tree. Do not point a generator at real memory.

`check_pointers.py PATH --baseline PREVIOUS_PATH` additionally checks historical preservation. The negative tests deliberately break evidence, permissions, bytes, histories, maps, reviews and budgets. Passing tests demonstrates these finite artifact invariants, not extraction quality, real hardware portability, complete production conformance or a running memory service.
