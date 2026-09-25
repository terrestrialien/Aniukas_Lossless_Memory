# Data contracts and operations

An implementation may choose its programming language, transport and physical backend, but must preserve these semantics and provide the versioned [portable reference format](REFERENCE_FORMAT.md). This document is normative alongside [the build specification](../BUILD_SPEC.md). The reference format specifies exact JSON names and schema constraints; tables here describe logical entities, including capabilities that a runtime still needs to implement.

The included 17-kind profile is a **bounded reference-fixture snapshot format**, not a complete operational backup format or running API. Its strict fields and semantic checks are concrete interoperability examples. A full runtime exporter must additionally carry every logical entity/history/checkpoint and required extension in this document, with a versioned manifest and migration rules. Namespaced `extensions` preserve additional data; required extension semantics must be declared and supported before import activation. Do not strip unrecognized data or label a fixture-only export a complete backup. The profile's rendered-byte budget checks are not proof of the combined runtime model-token budget, and static principal/grant records are not authentication.

## Shared conventions

Every persisted entity is versioned, has an opaque stable `id`, and records creation/commit provenance where applicable. The portable envelope uses `format_version` and `instance_id`; do not add a competing `schema_version` convention to its files. Times use UTC RFC 3339 in exports. Unknown historical event timestamps are null with a time note; local capture, receipt and commit recording timestamps and commit order are always recorded. IDs are unique inside a declared instance namespace and remain unchanged during migration. A merge of instances checks collisions and never silently reassigns identities. Display aliases are not keys.

References identify stable entity IDs and, when historical meaning matters, exact revision IDs. Lists are paginated with a snapshot watermark. Default responses contain small summaries and pointers; larger content is explicitly requested. The implementation validates both field structure and referential/permission invariants; JSON validation alone is insufficient.

The reference profile uses immutable revision `snapshot` values, a linear per-record `predecessor_id` chain, and a strictly ordered committed `sequence`. Other lineage, combinations and promoted origins use explicit relationships and `parent_bases`; they must not overload the linear history link. A backend with revision branches must preserve those branches in a versioned extension and expose unresolved conflicts rather than flattening them silently. Every export identifies which profile and required extensions it needs.

## Entity inventory

| Entity | Required information beyond shared fields | Validation and behavior |
| --- | --- | --- |
| `Scope` | kind, parent_scope_id, name, owner_role/grants, policy_version | No cyclic scope ancestry; display names grant no authority. |
| `PrincipalGrant` | authenticated principal_id, role, scope_id, operations, issued/revoked times, issuer | Only owner-authorized administration can grant rights; evaluate at commit time. |
| `MemoryPolicy` | immutable version, authorizing commit, adoption/extraction rules, identity/revision criteria, selection/aging rules, contradiction/review rules, allowed tuning | Explicit memory constitution; outcomes identify the version used. Policy changes cannot silently weaken invariants or rewrite earlier decisions. |
| `Source` | conversation/external ID, capture adapter, media/encoding, byte length, digest, original/capture times, chunk manifest, completeness | Exact bytes retained; unavailable portions explicitly marked. |
| `Message` | source_id, message ID, ordinal, role, content or exact byte range, timestamp if available, attachment refs | Preserve ordering and original content, including repeated text. |
| `EvidenceWindow` | source_id, source digest/version, selector, padding, unavailable ranges | Selectors use exact IDs or half-open offsets into the identified original source bytes, decoded using its recorded encoding; imported lines are one-based inclusive. A canonical decoded view requires an explicit mapping back to the original bytes. A selector never points at an unversioned moving file. |
| `MemoryRecord` | scope_id, type, subject, current_revision_id, revision_count, concise meaning, status, confidence/basis, authority/provenance, valid interval, importance/triggers, available depths/deepest evidence, small pointers | Its current pointer resolves to its own authorized committed revision. No long history embedded in primary. |
| `Revision` | record_id, predecessor IDs, complete resulting snapshot, semantic change, concise rationale, alternatives, source refs, effective interval, assertion/adoption, authorizing commit, conditions/consequences | Immutable; revisions form an acyclic history. Reference profile uses `predecessor_id` and full `snapshot`. Source gaps permitted only as explicit legacy gaps. Current record content must equal its selected snapshot. |
| `Relationship` | type, endpoint IDs/revisions, owner_scope, rationale/evidence, validity | Only endpoint metadata owned by the committing scope can be altered; reverse links may be projections. |
| `Conflict` | subject/record IDs, competing revision/evidence refs, scope, status, resolving commit/rationale | An unresolved conflict is visible during relevant reads. Resolution preserves prior claims. |
| `Candidate` | proposed event(s), subject, target_scope, draft change, source refs, authority/adoption basis, confidence, state, observer version/checkpoint | Candidate status never equals write authority. It may be reviewed, confirmed, rejected, deferred, or reclassified. |
| `Proposal` | sender principal/scope, target owner scope, subject, proposed changes, rationale, sources, status, target-owner response | Cross-scope communication only; acceptance applies through the recipient's authorized commit. |
| `Derivative` | child record/revision, parent record(s)/base revision(s), direct ancestors, type, delta or complete local meaning, inherited portion, conditions | Reject cycles; preserve ambiguous combinations as inactive conflicted candidates/records. Activation as an applicable effective rule requires a resolved merge. |
| `DerivativeMap` | parent_id, map_revision, watermark, registered count, compact paginated entries, count filter | Separate storage/projection from primary; precisely addressable for one parent. |
| `ReviewReceipt` | authenticated principal/grant, scope, read sequence, exact reviewed record/revision refs and source-window digests, change intent, alternatives, constraints, consequences, gaps, conflicts, outcome, recorded time | Immutable, nonempty substantive review for consequential changes; commit checks freshness against affected dependencies. This records review evidence, not proof of comprehension. |
| `Commit` | authenticated principal/grant, idempotency key/payload digest, sequence, scope, expected revisions, changed entity IDs, source refs, review receipt IDs, timestamp, outcome | All authoritative changes in its supported transaction boundary succeed or none do. The portable profile uses scope-local commits; foreign-scope workflows require separate authorization. |
| `OutboxEvent` | event type, source commit, target scope, payload refs, delivery attempts/state | Durable at commit; retried idempotently, not silently dropped. |
| `WorkingSet` | scope/task, policy generation, token budget/count method, selected record/revision IDs, pinned/temporary state, omitted/overflow status | Rebuildable; never the only copy of memory. |
| `CategoryView` | category identity/query definition, scope filter, snapshot watermark, paginated canonical record/revision refs | Rebuildable index/view for required categories; no copied authority, extra ownership scope or embedded full histories. |
| `AuditRun` | source range/manifest, auditor version, checkpoint, findings, proposed/accepted repairs, coverage | A completed run declares exactly what it inspected. |
| `ExportManifest` | namespace, format/extension versions, committed snapshot sequence, entity/source file inventory and digests, counts, omissions | Restore verifies all hashes and references, stages before activation, and preserves pending work. Historical grant data does not create live credentials. |

Record types include `rule`, `fact`, `decision`, `observation`, `belief`, `preference`, `goal`, `constraint`, `hypothesis`, `inference`, `question`, `procedure`, `idea`, and `state_event`. Keep asserted belief separate from verified fact.

Do not overload a single `authority` string. At minimum distinguish `asserted_by`, `assertion_kind` (user-stated, AI-inferred, document, external-source, system-observed), `authorized_by`, `authorization_grant`, and `adoption_evidence`. Record type, source reliability, extraction confidence, and write authority answer different questions.

Lifecycle values include `candidate`, `active`, `deferred`, `rejected`, `experimental`, `conditional`, `conflicted`, `superseded`, `historical`, `historical-origin`, and `unknown`. Additional stable enums represent question states and proposal states. A migration must preserve old enum meanings. `historical-origin` is available only through an authorized later snapshot; a global promotion cannot use it to rewrite a project-owned origin.

The portable revision's `snapshot.assertion` distinguishes `asserted_by`, `kind` and `adoption_evidence` from its commit's authenticated `principal_id` and `grant_id`. A quoted human decision is source evidence, not a transport identity. Confidence records its calibration/basis and never substitutes for either adoption evidence or authorization. A source-reliability note and an extraction-confidence explanation are distinct; neither field establishes a live grant.

Evidence windows identify sealed source bytes and digest, using exact message IDs, half-open byte offsets or fixed-version inclusive line spans as the profile specifies. Validate range order, source membership, boundaries, declared encoding and unavailable ranges. A byte slice must not split a multi-byte character when displayed as text; binary content remains exact bytes. Persist the selected evidence before its referencing revision. Platform line-ending conversion must not alter stored/imported source hashes.

Derivative `parent_bases` is always an array, including a single parent. Each entry pins the parent record and revision, inherited/changed portions, type and rationale. Natural-language differences alone do not compute authoritative state; a complete immutable local snapshot is required. Stored creation-time registration status is historical. Current pending/registered status comes from separately authorized registration events/maps, without editing the old snapshot.

## Required event vocabulary

The observer/compiler must detect these transition families, even if the implementation uses a more generic event format with semantic tags:

| Family | Transitions |
| --- | --- |
| Rules | `RULE_CREATED`, `RULE_CHANGED`, `RULE_REJECTED`, `RULE_CONFIRMED` |
| Decisions | `DECISION_MADE`, `DECISION_REVISED`, `DECISION_REVERSED` |
| Requirements | `REQUIREMENT_ADDED`, `REQUIREMENT_REMOVED`, `REQUIREMENT_PRIORITY_CHANGED` |
| Constraints/preferences | `CONSTRAINT_DISCOVERED`, `PREFERENCE_ESTABLISHED` |
| Assumptions | `ASSUMPTION_CREATED`, `ASSUMPTION_INVALIDATED` |
| Questions | `QUESTION_OPENED`, `QUESTION_RESOLVED` |
| Ideas | `IDEA_PROPOSED`, `IDEA_REJECTED`, `IDEA_DEFERRED` |
| Project scope | `EXCEPTION_CREATED`, `FEATURE_DEFERRED`, `PROJECT_SCOPE_CHANGED` |
| Facts | `FACT_CORRECTED` |
| Graph/ownership workflows | `DERIVATION_CREATED`, promotion proposals and scope-owner responses |

Workflow events should additionally identify source capture, candidate reclassification, conflict opening/resolution, derivative revision/retirement map refresh, projection updates, grant revocation, and ownership transfer. These event types do not change the provenance or authorizer of the underlying decision.

## Required logical operations

These are service contracts, not claims that a CLI or SDK already exists.

| Operation | Inputs | Required result |
| --- | --- | --- |
| `capture.append` | host source identity, event key, original bytes/message metadata | Durable source/message IDs, capture watermark, duplicate disposition |
| `capture.import` | complete source file/stream, metadata, adoption policy if any | Immutable manifest, exact locations, import/observation job IDs |
| `memory.get` | record ID, depth 0–3, effective time, snapshot | Current meaning plus requested resolution, gaps/fallbacks, evidence and cursors |
| `memory.get_many` | list of ID/depth/time requests | Snapshot-consistent bundle, independently returned depth/status per branch |
| `memory.search` | query, scopes, type/status/time/trigger/category filters, cursor | Ranked candidates with ranking method and exact canonical references |
| `memory.resolve_rule` | subject, task/project/user scope, effective time | Effective rule, pinned bases, explicit lineage, conflicts |
| `memory.build_working_set` | task context, scope, token budget, model/tokenizer metadata | Bounded relevant entries, required constraints, overflow/gap status |
| `memory.history` | record ID, time filter, cursor | Ordered immutable revisions and evidence pointers |
| `source.read_window` | evidence window ID or exact selector | Exact text/content, digest, padding boundaries, expansion cursor |
| `source.follow_backlinks` | source/window ID, snapshot | Citing revisions/records and their scopes |
| `memory.propose` | target scope, proposed changes, rationale, source refs | Durable routed proposal, current owner, status |
| `memory.commit` | validated envelope with expected revisions/idempotency key | Atomic commit result or typed failure; actor from authenticated session |
| `memory.record_review` | change intent, read sequence, inspected revision/window refs, reasoning, gaps/conflicts, conclusion | Immutable review receipt tied to the authenticated reviewer; no record writes or authority expansion |
| `memory.derive` | parent/base revisions, target project, delta/rule, rationale, sources | Authorized local record, outbox event, registration status |
| `memory.derivatives` | parent ID, filters, cursor | Compact map page, count/filter/watermark and precise child pointers |
| `memory.propose_promotion` | origin/variant IDs, rationale/evidence | Global adoption proposal; does not write projects or global rules directly |
| `candidate.review` | candidate IDs, approve/reject/defer/return-to-exploratory/reopen decisions, rationale | Authorized transitions or proposals routed to correct owners, preserving prior candidate history |
| `conversation.state` | conversation ID, snapshot | Active, revised, deferred, rejected, conflicted items and open candidates; labelled counts, candidate confidence/basis, and explicit definitions for overlapping count categories |
| `audit.run` | source manifest/range, incremental or complete mode | Checkpointed coverage and findings; repairs use ordinary commit policy |
| `admin.transfer_owner` | scope, current generation, new principal/grant | New owner generation, revoked prior rights, intact scope history |
| `archive.export/import` | selection/manifest, portable destination/input | Versioned complete records, IDs, evidence, grants policy, integrity report |
| `maintenance.rebuild` | projection kinds, source watermark | Rebuilt indexes/views plus validation; canonical history unchanged |

`propose_global_note` is a convenience alias for a proposal targeted at the global scope. Agents use the operation rather than knowing a particular governor's identity.

### Snapshot and retrieval response semantics

`memory.get`, `get_many`, `history`, `resolve_rule` and cursor continuations use one committed `snapshot_sequence`, plus an `effective_at` when asking historical questions. Omission means the latest committed snapshot and current effective time; echo the resolved values. A continuation cannot silently move to a new snapshot. An expired live cursor returns an explicit error and a way to restart against the same retained committed history; cursor expiry must not erase historical reconstructability. Missing/corrupt historical data or a deliberate declared erasure is an evidence gap, not ordinary cursor expiry.

Temporal resolution first excludes commits later than the requested recorded snapshot, then evaluates the authorized revision/supersession transitions whose valid intervals cover the effective time. A declared successor replaces its predecessor only over the affected interval; derive the predecessor's effective boundary rather than modifying its immutable `valid_until`. Revision-chain succession is not a license to suppress an independently recorded conflicting assertion. If no authorized resolution orders overlapping incompatible claims, return the conflict. When event validity is unknown, expose the uncertainty; never substitute capture time for the original event time. A current-pointer query can still identify the latest recorded state while declaring its uncertain historical applicability.

Return requested depth, returned depth, available depths, deepest available evidence, record/revision IDs, validity, confidence basis, exact source references, lineage, conflict/gap/staleness flags, fallback reason, continuation and token-count basis. Fall forward to the nearest deeper available depth, never automatically to the deepest. If none is deeper, return the deepest available evidence with insufficiency. `get_many` permits mixed depths but uses a consistent snapshot and gives a result or typed error for every requested branch.

Record lookup and search are different contracts. Search returns ranked discoverable records and a declared ranking method; once the record is known, provenance uses exact references. A failed/unavailable search index is not an empty result. A stable source selector returns original content; presentation summaries are separately labelled derived content.

Working-set output declares the combined model context limit, host/output reserve, memory allocation, serialized token count or conservative estimate, mandatory entries, selected temporary/persistent entries, omitted optional entries, missing mandatory entries and overflow continuation. Never report `complete=true` when required items are missing, denied, conflicted or over budget. A lower per-scope limit cannot hide combined overflow.

### Review receipt and proposal workflow

The reference receipt uses `principal_id`, `grant_id`, `scope_id`, `read_sequence`, `reviewed` entries containing exact `record_id`/`revision_id`, `sources` containing `window_id`/`source_digest`, `intent`, `alternatives`, `constraints`, `consequences`, `gaps`, `conflicts`, `outcome`, and non-null `created_at`. The commit's `review_receipt_ids` must refer to valid receipts for its intent and scope. A high-impact flag does not replace the semantic classification of changes that require review under BUILD_SPEC §6.3; callers cannot disable review by setting the flag false.

Creating a cross-scope proposal preserves sender identity and source without writing the recipient's canonical records. A recipient response is a separately authorized event. Parent registration, global promotion and local adoption each use their own scope-local commit and current grant, linked by a durable workflow ID. Reject/defer responses and failures are retained; a successful global promotion does not imply accepted local adoption.

## Commit checks, in order

1. Authenticate the actual caller and load current grants.
2. Resolve target entities/scopes and expected revisions.
3. Validate idempotency key and payload digest.
4. Check schema, exact source availability, adoption evidence, required review receipts and their exact revision/evidence dependencies.
5. Validate every mutation's scope, including metadata, links, statuses, and derived primary changes.
6. Check contradictions, inheritance cycles, valid-time consistency, and referential integrity.
7. Commit canonical records, revisions, owned links, and outbox atomically.
8. Return a stable commit identity; advance projections/watermarks through authorized workers.

Even a high-confidence observer event fails step 5 without authority. A proposal sender cannot supply the recipient's identity in a payload to pass authorization.

Check authorization against the current policy/owner generation, including replays queued before revocation. Enforce expected revisions for touched records, reviewed dependencies and current grant/owner generations inside the transaction so concurrent revocation cannot race validation. Source-only or provenance-enrichment changes remain writes requiring the relevant scope grant. Return the existing committed result only for an identical replay digest and a currently authorized reader; do not apply old authorization to new data under a reused key.

## Error semantics

Implement equivalents of `NOT_FOUND`, `FORBIDDEN`, `STALE_REVISION`, `STALE_REVIEW`, `IDEMPOTENCY_CONFLICT`, `SOURCE_UNAVAILABLE`, `BROKEN_REFERENCE`, `UNRESOLVED_CONFLICT`, `CONDITIONAL_AMBIGUITY`, `EVIDENCE_INSUFFICIENT`, `DEPTH_FALLBACK`, `BUDGET_EXCEEDED`, `CAPACITY_EXCEEDED`, `PROJECTION_STALE`, `ADAPTER_UNAVAILABLE`, `SNAPSHOT_UNAVAILABLE`, and `UNSUPPORTED_FORMAT`.

Partial batch success must identify each item's result. `NOT_FOUND` must not masquerade as `FORBIDDEN`, and an unavailable index must not masquerade as no relevant memories. Optional restricted-read deployments may deliberately use a non-disclosing external error while retaining the actual cause in authorized audit telemetry.
