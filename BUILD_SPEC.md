# Aniukas Lossless Memory — build specification

Status: implementation specification, not a running service · Short name: ALM

## 1. Objective, scope, and requirement language

Build a memory subsystem that can determine what was decided, what remains undecided, why a decision exists, how it changed, who had authority, and which original evidence produced each stage, without keeping the lifetime archive in active model context.

The central optimization is **informed, confident decisions with recoverable evidence**. Efficiency follows from avoiding unnecessary retrieval. It must not come from hiding uncertainty, silently discarding source material, or imposing a small retrieval cap that makes a consequential decision inadequately informed.

MUST and MUST NOT define required behavior. SHOULD is a default with a documented reason for exceptions. MAY identifies an allowed choice or extension. Required capabilities remain on the delivery plan even when not included in the first milestone. A baseline build must identify which later capabilities it has not implemented.

The system is the durable memory component of an AI agency, not an entire agency framework. Agent scheduling, business workflows, user interfaces, and model hosting integrate through adapters. No particular CPU, GPU, operating system, model, provider, agent framework, or filesystem layout is required by the logical design.

The complete requirements checklist uses `ALM-001` through `ALM-132` in [REQUIREMENTS.md](docs/REQUIREMENTS.md). Each entry identifies its specification section and acceptance scenarios. A release identifies any requirement it has not implemented.

This specification and every clause in the [requirements checklist](docs/REQUIREMENTS.md) jointly define required behavior. The [logical data contracts](docs/DATA_CONTRACTS.md) define service semantics, and the versioned [portable reference format](docs/REFERENCE_FORMAT.md) fixes interoperable exchange fields. Schemas, examples, and acceptance checks must agree with all of them. A contradiction is a specification defect to resolve, never permission to choose the easier behavior. Alternative internal databases and physical layouts remain allowed.

## 2. Non-negotiable invariants

1. Retain every captured source message and tool event in its original form. Derived summaries and indexes must never replace the source archive.
2. Give every meaningful memory, revision, source, relationship, proposal, and commit a stable identity. Physical location is not identity.
3. Preserve prior revisions and their reasoning when state changes. A correction appends evidence and a new interpretation; it does not rewrite the past.
4. Connect current records, history, evidence windows, and original logs through exact resolvable references, with reverse navigation.
5. Keep primary context bounded. Archive size, history length, and descendant count must not directly increase the amount of injected primary context.
6. Make deterministic traversal authoritative once a record is identified. Semantic search discovers candidates; it does not guess which historical source an existing pointer means.
7. Enforce write authority in the memory service and storage boundary. A prompt telling an agent to behave is insufficient.
8. Preserve unresolved contradictions and rejected alternatives. A newer assertion does not automatically supersede an older one.
9. Commit related authoritative changes atomically, with concurrency checks. Never expose half of a decision update.
10. Represent missing evidence, extraction delay, stale indexes, and incomplete retrieval explicitly. Failure to retrieve is not proof that nothing exists.
11. Memory belongs to a scope and survives reassignment of agents, models, or providers.
12. Public repository contents and a person's private operational memory are separate artifacts.

## 3. Logical architecture

### 3.1 Independent dimensions

| Dimension | Meaning | Values |
| --- | --- | --- |
| Scope | Who owns the record and where it applies | Global/system, user profile, project, task |
| Temperature | Whether it belongs in the current working set | Primary, secondary, temporary task selection |
| Resolution | How much supporting understanding is requested | Current, history, evidence, full source |
| Record type | What kind of knowledge this is | Rule, fact, decision, observation, belief, preference, goal, constraint, hypothesis, inference, question, procedure, idea, state/event |
| Authority | Who asserted and who authorized it | Human, delegated scope owner/governor, project agent, observed system event, external source, model inference |
| Lifecycle | Its present standing | Candidate, active, deferred, rejected, experimental, conditional, conflicted, superseded, historical, unknown |

Secondary is a temperature, not a separate permission scope. A global secondary record is still global-owned. A task is nested in its project or global scope. A user profile is logically distinct but follows the configured global ownership policy; a separate owner may be assigned explicitly. The memory service must never infer extra authority from a scope's display name.

### 3.2 Canonical layers

The design is a fir tree: a small working set at the tip, progressively deeper history and evidence below it, and the complete source archive at the base. Physical storage may be any graph. The logical components are:

| Component | Content | Context behavior |
| --- | --- | --- |
| Working set | Compact primary entries plus temporary relevant records and task state | Explicit token budget |
| Current records | Canonical current meaning, status, scope, small pointers | Fetch selected records |
| Revision history | Dated changes, rationale, alternatives, sources, actors | Fetch relevant revisions |
| Evidence windows | Exact bounded ranges from source records | Fetch and expand as needed |
| Immutable source archive | Complete conversations and captured events | Stream/page; retain original bytes |
| Derivative maps | Compact descriptions and exact links for descendants of one parent | Separate from primary, paginated |

The public API uses `depth=0` for current, `1` for history, `2` for evidence, and `3` for full reconstruction. The working set is a cache/view, not another truth source. A depth request can differ for every branch in a batch.

Primary and secondary files MAY be human-readable materialized views. A logical global primary, user primary, project primary, and task state must exist even if a database implements them. Histories, sources, and maps must not be embedded wholesale into these views. Scope filenames provide deterministic routing hints; a stable-ID resolver remains the authoritative index.

Provide categorized views for decisions, facts, preferences, open questions, current state, important events, people, ideas, project architecture, experiments, and hardware. Categories are navigable indexes/views over canonical records, not additional authoritative copies or new permission scopes. A record may appear in several views with the same stable identity and exact history/evidence pointers. Operators may extend categories for their own projects without copying the underlying archive into Primary.

### 3.3 Components and trust boundaries

Implement capture adapters, immutable source storage, an identity resolver, a transactional record store, a retrieval router, lexical/graph search, an authorization service, a live observer, a memory compiler, a candidate buffer, a proposal router, a retrospective auditor, and rebuildable projections.

Embedding and reranking adapters, additional storage backends, and a visual explorer are separable capabilities. The observer can be a background worker or a logical stage in one process; physical parallelism is optional. It MUST inspect every captured turn, including user and assistant turns, with durable checkpoints.

Only the authorized commit path may mutate owned semantic records. Model output is a proposed structured event, not a database instruction. A read tool, search result, imported chat, or source document cannot change permissions or issue service commands merely by containing instructions.

## 4. Storage, identity, provenance, and time

### 4.1 Source retention

Capture incoming messages before extraction. Append completed assistant messages and available tool events as delivered by the host. Record conversation ID, event ID, role, content, ordering, attachments or attachment references, capture time, original time when available, and source identity. If an adapter lacks message metadata, preserve the imported file bytes and identify exact byte/line spans without inventing speakers or timestamps.

Source chunks are sealed immutable units. Lossless compression, object-store relocation, and splitting at stable message boundaries are allowed through the resolver. Store a content digest, encoding, length, and chunk manifest. Verify content before declaring a restore or migration complete. Edits, corrections, and revised user messages become new linked source events; the originally captured version remains.

Hash the exact bytes actually retained, not text before newline or encoding conversion. Imported CRLF, LF, byte-order marks, Unicode and legacy encodings remain recoverable byte for byte. A normalized display/search view must carry a deterministic mapping to the original bytes. New portable synthetic fixtures use explicit UTF-8/LF bytes; a host's default text-writing behavior must not change their digest.

“Complete” always means complete relative to what the adapter captured. Export omissions and attachment gaps must be represented. SHA-256 or equivalent integrity checks detect changes relative to stored digests; they do not prove who originally authored a statement.

### 4.2 Exact references

Use opaque persistent IDs; human-friendly aliases such as `SYS-RULE-001` are optional. Native adapters may expose logical addresses such as `memory://<id>`, `history://<id>/<revision>`, and `source://<id>/<window>` with versioned parsing. Portable interchange uses the exact reference conventions in [REFERENCE_FORMAT.md](docs/REFERENCE_FORMAT.md), including its evidence-window references. Logical addresses are not operating-system paths; aliases must resolve to the same stable instance/entity/revision identity.

An evidence window identifies its source, exact start/end message IDs or byte range, context padding policy, and digest. Line numbers in an imported document are allowed when tied to a fixed source version. A displayed excerpt must be an exact decoded slice, not an LLM paraphrase. Expansion follows adjacent messages or referenced sources and reports additional sources separately.

Reverse indexes must support source → revisions → current record and child → parent → derivative map. Indexes may be rebuildable; committed source and revision references may not be guessed during reconstruction.

### 4.3 Current records and revision chains

Each record stores identity, scope, type, current revision, concise meaning, lifecycle status, confidence with its basis, source/authority metadata, importance and triggers, relationships, validity interval, and small history/derivative pointers. Current views also expose a revision count without loading the history. Put long reasoning in revision records. Source metadata and authorizing actor must be distinct: a user's decision adopting an assistant suggestion does not make the assistant its original human author.

Each revision stores a unique revision ID, prior revision IDs, before/after change, concise rationale, changed-at/recorded-at times, effective validity, authorizing actor and grant, evidence references, rejected/deferred alternatives where applicable, conditions, consequences, and commit ID. Unknown times remain null/unknown. Confidence is not a permission grant or a guarantee of truth.

Every revision MUST preserve the complete normalized state after that revision, or an exactly reversible machine-defined patch with a pinned base and verified resulting state. The portable reference format stores a complete immutable `snapshot`. A natural-language change description alone is insufficient to reconstruct a past rule. Current projections must equal their referenced revision's snapshot. Advancing the current pointer does not mutate the old revision's status from current to past; whether a revision is current is a query result. Historical-origin, rejected, and superseded meanings are represented through later snapshots, not retroactive edits.

Distinguish valid time (when the claim applied) from recorded time (when the system learned it). Historical questions resolve records using the relevant time, not today's hardware, rule version, or preferences. A valid old fact is historical, not retroactively false.

Historical reads identify both an effective time and a committed snapshot watermark: "what applied then, using what we knew by this commit." Recorded commit order is always known, even when the original event's timestamp is unknown. A late correction may change today's understanding of an earlier interval while the earlier recorded snapshot remains reproducible. An authorized successor can explicitly supersede its predecessor over a declared valid interval without editing that predecessor; derive interval boundaries from those transitions. Overlapping incompatible claims without such resolution return a conflict; unknown times return uncertainty rather than an invented ordering. Rules, grants, relationships, and pinned ancestors used for a reconstruction must resolve at the same declared snapshot.

### 4.4 Relationships and canonical identity

Support `supports`, `contradicts`, `supersedes`, `extends`, `caused_by`, `evidence`, `related_to`, `derived_from`, `overrides`, `promoted_to`, `origin`, and `informed_by`. Store direction, endpoints, relevant revisions, owning scope, and provenance. Derived reverse links are read projections, not permission to alter the opposite endpoint.

Repeated statements attach corroborating sources to a canonical record where meaning, scope, time, and authority match. Identical text alone does not establish duplication. Different projects and changed meanings can require distinct records. Repeated processing of the same source event must be idempotent.

## 5. Memory constitution and lifecycle

The **memory constitution** is the explicit versioned policy governing what becomes memory, revision versus new identity, Primary/Secondary movement, contradictions, and required descent toward evidence. Sections 5–8 define its required behavior; instance configuration selects permitted thresholds and schedules. Record the active policy version on extraction, selection and commit outcomes so changed tuning remains explainable. Configuration cannot weaken source retention, scope ownership, required review or explicit uncertainty; human-authorized policy changes preserve their own history.

### 5.1 What becomes memory

Preserve meaningful state transitions: creation, change, rejection, clarification, confirmation, contradiction, deferral, contextualization, changed priorities, and resolved questions. Do not store every conversational sentence as an authoritative decision. Raw conversation capture still preserves those sentences.

Recognize indirect language and context. A decision need not contain the word “decide.” A tentative idea remains a candidate until authorized evidence or configured adoption policy supports a transition. Later reasoning that clearly relies on an earlier proposal can be evidence of implicit confirmation; record both source locations and the inference basis.

A new record is appropriate for a distinct subject, scope-specific derivative, independent conflicting assertion, or independently governed rule. A revision is appropriate when the same canonical subject changes under its owner. Uncertain equivalence becomes a candidate for review; it must not silently merge histories.

### 5.2 Authority and confirmation

By default, clear statements or confirmations by an authorized human/owner can commit automatically. Ambiguous statements remain provisional; exploratory alternatives do not become decisions merely because they were discussed. Confidence thresholds are configurable policy, with calibrated evidence rather than universal magic numbers.

Assistant-originated suggestions require adoption evidence or an explicit preauthorized adoption policy. Asking confirmation for every clear decision is prohibited as the default user experience. Queue consequential ambiguous candidates for batched review or request clarification when an immediate dependent decision needs it.

The human owner may explicitly enable a bounded acceptance policy for imported or future conversations. The policy specifies conversations, scopes, excluded classes, duration, and authorizing actor; it does not grant cross-scope write access. Each adopted suggestion retains its original assertion and separate adoption evidence, with the actual times of both. Silence alone is not consent under the default policy.

### 5.3 Observer, buffer, compiler, and audit

1. Durably capture the source event and assign its identity.
2. Enqueue observation with a replay-safe event key. Track observed-through and committed-through watermarks.
3. Compare the new turn with relevant recent turns, pending candidates, and affected current records. Recover prior context through source pointers when needed.
4. Produce events and candidates with exact source ranges, confidence basis, subject, scope, proposed transition, and required authority.
5. Validate identity, schema, source existence, scope, permissions, expected revisions, contradictions, and adoption evidence.
6. Commit the authorized transition or retain it as a candidate/proposal. Record `ignored` as an extraction disposition when useful for audit; raw source remains.
7. Refresh current/primary/search projections and publish durable notification events.

Candidate states include open, needs-review, confirmed, rejected, deferred, exploratory, and superseded. Window length and review scheduling are configuration choices. Aging removes a candidate from the active buffer but preserves it durably with its disposition. Reclassification later must remain possible.

The compiler recognizes at least the event families in [DATA_CONTRACTS.md](docs/DATA_CONTRACTS.md). One utterance may carry multiple event tags while producing a single canonical decision, avoiding duplicate memories.

Live capture/extraction is the default. Retrospective auditing complements it at conversation completion, user request, and configurable checkpoints. Audits revisit the entire relevant source with continuation checkpoints, find missed state changes and earlier origins, and propose corrections through the same authority checks. An auditor cannot silently obtain global or project write authority. Missing discoveries remain recoverable in the archive.

Provenance enrichment appends a new authorized revision or immutable enrichment event with its own evidence and recording time. It MUST NOT edit the source list, authorizer, status, or rationale in an old revision. Candidate and proposal decisions also retain transition history. An extraction checkpoint advances only after the captured range and every resulting disposition are durably recorded; a failed batch resumes without skipping candidates.

### 5.4 Contradiction, repair, and negative memory

Store conflicting assertions separately and create an unresolved conflict with both sources. Do not choose a winner solely by recency, similarity score, or higher model confidence. Resolution requires authorized reasoning, a new revision/decision, and evidence; retain losing assertions and the conflict history.

Keep alternatives that were rejected, deferred, superseded, conditional, experimental, or unknown, including why. Retrieval of a proposed approach should surface relevant prior rejections so the system can reconsider changed conditions rather than repeat old mistakes.

When current memory and source disagree, inspect the source and repair the derived interpretation through an authorized append-only correction. Source is authoritative evidence of what was said or observed, not automatic proof that the statement is true or still effective. Later authorized revisions and temporal validity determine current operational meaning.

## 6. Retrieval and bounded working memory

### 6.1 Initial context and routing

Start with global primary, applicable user-profile primary, project primary, and task state alongside the current conversation context. Reserve room for host instructions, current input, and response generation before assigning the memory budget. Build one combined working set under the configured model context budget. Allow pinned critical constraints plus task-relevant temporary entries. Do not automatically include other projects or all secondary memory merely because read access exists.

Route by explicit IDs, scope, project identity, and deterministic indexes before semantic search. On each substantial request, also inspect relevant secondary/current-record indexes; primary must not be the only discovery surface. Support keyword/BM25, graph links, temporal filters, and optional embedding/reranking adapters. Provide deeper-search retry when ordinary discovery misses something.

Selection considers relevance, recurrence, authority, recency/validity, conditional criticality, dependencies, and task impact. Store triggers for topics, entities, projects, conditions, dependencies, dates, people, hardware, locations, and contradictions. Rare but critical conditional constraints must not disappear merely because they are seldom used.

### 6.2 Promotion, demotion, and overflow

Promote secondary records into the working set when relevant; demote inactive primary entries while preserving the canonical record and history. Temporary task promotion expires after its task or policy window. Canonical scope promotion is a different operation governed by section 8.

The active-context budget is hard for a single model request. It is not a limit on the evidence a decision may examine across multiple retrieval calls. Count actual model tokens when possible; otherwise use a conservative estimate and expose it. If required constraints exceed the budget, return an explicit overflow and continuation/partition strategy. Do not silently omit a mandatory constraint and claim the context is complete.

The sum includes all global, user, project and task entries, pinned constraints, temporary retrieval, serialization/tool overhead, and current host context after reserving output capacity. Per-scope caps are subordinate allocations, not separate permission to exceed the combined budget. An overflow result must identify the mandatory items that could not fit and which partition or next step is required. The caller must not proceed as if it received a complete applicable constraint set. Summarizing mandatory items is allowed only when their meaning and exact pointers remain intact; it does not waive the overflow check.

Secondary memory, histories, and maps are paginated and partitionable. Select segmentation using measured workload rather than imposing an elaborate taxonomy in advance. Stable IDs must survive reorganizations. Operational capacity limits must be observable; never describe disk or RAM as unlimited.

### 6.3 Procedural depth

Use `get(id, depth)`, `get_many(requests)`, and `search(query, scope, filters)`.

At depth 0, use a valid authoritative current record for routine work. When its suitability is questioned, retrieve history/rationale. If this leaves material uncertainty, read exact evidence, then expand windows or reconstruct the relevant full conversations. Each branch may stop at a different depth. Fetch independent branches in one request, concurrently where supported, or sequentially on constrained machines with the same result semantics.

If a requested intermediate layer is missing, use the next deeper available layer and report the fallback. If deeper evidence does not exist, return the deepest available layer, the missing ranges, and the uncertainty; do not fabricate evidence. Broken pointers and access denial are distinct from “no supporting evidence exists.”

For example, a request for depth 1 with depths 0, 2 and 3 available returns depth 2 first, not depth 3. A request for depth 2 with only 0 and 1 available returns depth 1 with `EVIDENCE_INSUFFICIENT`; it cannot claim verification. Routine access MAY read deeper when useful: current-only operation is permitted, not an absolute prohibition on history.

Inspect sufficient supporting history before a project override, global promotion, global rule change, contradiction resolution, expensive or irreversible decision, change affecting many dependents, or conclusion that an earlier decision was mistaken. Ask whether the original purpose, constraints, alternatives, and consequences are understood. History may be sufficient; source retrieval is necessary when it is not. A known local solution can skip browsing other projects' derivatives, but it does not bypass this evidence requirement for changing an inherited rule.

Persist an immutable review receipt for such a change. It identifies the reviewer authenticated by the service, grant, read snapshot, exact revisions and evidence inspected, target change, purpose, alternatives, constraints, consequences, unresolved gaps/conflicts, and conclusion. The resulting commit references that receipt and rechecks affected/dependency revision preconditions. An empty list or the statement "reviewed" is insufficient. If a material revision changed after review, the commit must return a stale-review conflict and require renewed review. A receipt makes review auditable; it cannot prove that a model understood the evidence.

Operational deadlines and resource limits may pause reconstruction with a resumable cursor. They may not cause a silently incomplete answer labelled verified. “Full reconstruction” means complete access to the selected evidence chain with a manifest and explicit omissions, not one giant prompt containing every historical token.

### 6.4 Retrieval result contract

Return record and revision IDs, requested/returned depths, available depths and deepest available evidence, snapshot/commit watermark, current status/validity, confidence basis, effective rule lineage, evidence windows, missing/stale/conflicted flags, continuation cursors, and token/latency estimates. Distinguish exact-ID resolution from search ranking. A cached result identifies its source revision and policy generation.

## 7. Reciprocal scope ownership

The default is a single owner's trusted personal agency: all authenticated, authorized agency agents may read any memory scope as necessary. This is not anonymous/public read access. Readability does not cause automatic context inclusion.

| Actor | Global memory | Assigned project | Other projects |
| --- | --- | --- | --- |
| Human owner | Read/write | Read/write | Read/write |
| Global governor | Read/write | Read | Read |
| Project owner agent | Read | Read/write | Read |
| Worker/research agent | Read | Read | Read |

Every project owner follows the same mechanics. The assigned project ID is the only difference. A task may use the same owner identity as its project/global parent, but writes to a separate task scope still require an explicit task-scope grant issued under the human-authorized assignment/delegation policy. Scope ancestry alone grants no authority. User-profile writes likewise follow an exact recorded owner grant. Workers may submit candidates but cannot commit semantic records without a grant.

A global governor is optional: the human can initially be the sole global writer. Later delegation may authorize specific automatic change classes while reserving consequential changes for the human; grants must represent that distinction explicitly.

Writes include meaning, status, confidence, metadata, reasoning, owned links, owned histories, deletions, and changes to materialized views that would change effective meaning. A global governor cannot “repair” a project's metadata as a backdoor. A project agent cannot update a global derivative count directly.

Route cross-scope changes through stable operations such as `propose_global_note` and `propose_change(target_scope, ...)`, not a hardcoded agent name. Resolve the current owner at delivery time. Consequential proposals and their accept/reject/defer responses remain permanent evidence, including rationale and sources. Only the target scope owner may apply a proposed change.

Ownership attaches to roles and scopes, not model brands or particular model instances. On reassignment, preserve memory and full history, revoke the old grant, issue a new grant, and invalidate stale credentials. Policy changes themselves require the human owner's authority. Administrative hierarchy and model capability grant no extra writes.

The service must validate principal identity outside model-provided payloads. Agents must not receive unrestricted filesystem/database credentials that defeat these rules. A local process with the same unrestricted OS identity as the database owner is not a strong security boundary. A conforming deployment must isolate credentials/processes or otherwise prevent its agents from bypassing service authorization. An unsecured prototype must document that limitation and must not claim conformance to the enforced-permissions requirement.

Bind the authenticated session to the recorded principal and grant at commit time. Reject a payload that claims another principal, role, scope, or grant; possessing an evidence pointer or quoting a human does not impersonate that human. Historical grants are evidence for past authorization, never live credentials. Role revocation and owner generation changes take effect before the next write, including queued observation, import, replay, registration, and projection work. A scope parameter, administrative worker, unrestricted import, or generic file-edit operation must not create an authorization bypass.

Optional restricted-read or multi-owner deployments are separate policy profiles. They must document how they restrict the default authorized agency-read model and filter all indexes and reverse links. The default profile does not provide cross-owner read isolation.

## 8. Inheritance, derivatives, and promotion

### 8.1 Effective rules

Resolve applicable authorized rules deterministically from task → project → user-profile overlay, where configured → global → implementation default. Most-specific valid override wins only when its lineage explicitly identifies the inherited rule and applicable conditions. Arbitrary local text cannot override another subject or the service authorization policy. Ties and incompatible multiple parents create a conflict requiring resolution, not nondeterministic selection.

Evaluate every condition as satisfied, not satisfied, or unknown against the query context and declared snapshot. Unknown conditions that could change the result produce `CONDITIONAL_AMBIGUITY`; they do not silently evaluate to false. Precedence selects among authorized overrides of the same subject; compatible constraints on different subjects accumulate. Multiple equally specific rules require an explicit authorized precedence or merge decision. User-profile overlays do not grant permission to bypass a global safety/ownership policy enforced by the service.

Show the effective rule alongside parent identities, parent versions, inherited portions, modified portions, exception reason, and original default. An exception must never look like a universal rule. Reevaluate conditional exceptions when their reason ceases to hold, proposing reconsideration to the project owner.

### 8.2 Derivative records and maps

A project owner can create a derivative after adequate review of its parent. Record global parent(s), direct ancestor(s), exact base revisions, derivative type, local conditions, inherited portion, changes/delta, rationale, and sources. Types include exception, specialization, extension, restriction, override, and combination.

Prefer revision-pinned deltas plus lineage when practical. Materialize the full effective rule on request. Store a full derived rule with lineage when a delta is ambiguous or expensive to apply; copied text is not an independently authoritative duplicate of the parent. Reject inheritance cycles. Preserve an ambiguous combination as an inactive conflicted candidate/record with its evidence; reject activation or materialization as an applicable rule until the merge is resolved. A changed ancestor must not silently rewrite an established project rule; mark it for owner review.

Each parent in a combination has its own exact base revision, inherited portion, changed portion, and rationale. A deterministic machine-applicable delta names its patch format and resulting digest. A prose delta requires a stored complete local snapshot; an LLM must not generate a different authoritative rule on each read. Materialization verifies all pinned bases and returns the stored or deterministically computed result with the full ancestry. A missing pinned base is a broken reference, not permission to substitute the parent's latest revision.

Creating a derivative emits `DERIVATION_CREATED`. Its authorized parent-scope owner registers it in a separate map. The child-scope commit and event are atomic; parent registration is a separately authorized idempotent commit. Until registered, show `registration_pending`, not a false claim of a complete parent map. Reconciliation must retry and surface durable failures.

Registration updates a separately versioned relationship/map entity. It does not mutate the immutable child revision to change a stored pending flag. The child's effective registration status is the projection of its immutable creation event and subsequent parent-authorized registration receipt. The same rule applies to delivery attempts and acknowledgments: append or version workflow state, preserving earlier outcomes.

Later child revision, retirement or supersession emits the corresponding durable map-refresh event under the child owner's commit. The parent owner authorizes any resulting map change. Until processed, expose the map's older watermark and pending update; never present its old count as an up-to-date complete census. Historical map snapshots and superseded children remain navigable.

A primary entry contains only a derivative count and exact map pointer, plus its usual small history pointer. With no derivatives, omit the display field or show zero. The map contains the parent ID, entries with child ID/project/type/summary/reason/exact pointer/status, count semantics, and a watermark. The default count is registered non-superseded derivatives; historical descendants remain accessible through a filter. Counts and pages must refer to the same snapshot.

Read compact map entries first, then only relevant derivatives. Browsing other examples is optional when the agent already has an adequately supported local solution. Maps can become hierarchical/paginated at scale without changing the parent's address. A map update changes relationships, not the parent rule's semantic version; track its own revision.

### 8.3 Global promotion

A useful project rule may be proposed for global adoption. The user or authorized global governor evaluates the original rationale, observed successes, variants, and relevant conflicts. Record the promotion decision, source/origin, informed-by records, time, reason, and authorizer.

Do not destroy, relocate away, or silently overwrite the project-owned origin. Create an authorized global canonical rule with explicit genealogy; local owners may retire redundant active overrides and point to the global rule while preserving historical records. Identical inherited meaning has one current canonical global rule; distinct local variants retain their own identities.

Global promotion does not compel a governor to change projects. Adoption notices go to project owners, who retain their authority to accept, reject, or maintain a justified exception.

## 9. Transactions, concurrent agents, and recovery

Canonical updates require the following transaction and recovery rules.

Use a commit envelope with actor, grant, target scopes, expected revisions, idempotency key, source/event IDs, proposed changes, and related outbox events. Validate all mutations before writing. A single-scope multi-record change commits all or none. A human authorized for every touched scope may use a true multi-scope transaction only when the backend can provide it; otherwise expose a coordinated workflow with separate commits and pending state. Never call a multi-step saga globally atomic.

The portable reference profile requires scope-local commits, immutable revision snapshots, a monotonic committed `sequence`, authenticated principal/grant references, and review receipt references. It represents multi-scope work as separately authorized commits joined by durable workflow identities. A runtime may additionally expose stronger atomic capabilities, but its portable export must preserve every authorization boundary and historical result.

Concurrent edits use compare-and-swap revision preconditions or equivalent optimistic concurrency. The same transaction checks current grant/owner policy generations so a revocation racing with validation cannot authorize a later write. A stale writer receives a conflict and re-reads; last-write-wins is not acceptable for semantic decisions. Duplicate delivery returns the existing result without a second revision, subject to the caller's current read authority. Reusing an idempotency key for a different payload is an error.

Store a source durably before its referencing commit. If blob storage and the database lack a shared transaction, finalize immutable blobs first, then commit their manifest/references. Failed commits may leave unreferenced blobs, which must be reconciled without deleting captured source. Never expose a committed pointer to an unfinalized blob.

Write projections and an outbox within the appropriate local transaction or tag async projections with a watermark. Reads needing current authoritative state bypass lagging indexes. Derived search embeddings and rendered primary files may lag; canonical records and commit history may not pretend they did not. After restart, replay the outbox and observation checkpoints idempotently.

If the implementation makes files its canonical store, it must specify a write-ahead journal or staged immutable generation protocol: all source/entity bytes durably finalized first, one durable commit marker publishing the generation, reads following committed markers only, and deterministic restart reconciliation. Several independent file renames are not a transaction. Database-backed implementations must validate their actual durability settings and filesystem guarantees. The reference JSON export is an interchange snapshot, not an alternative permission-enforcing transaction engine.

Back up raw logs, record/revision/commit manifests, permissions, schema versions, and durable proposals/candidates. Indexes are rebuildable. Verify restore by hashes, reference traversal, permissions, and selected historical queries. Provide complete portable export/import with IDs preserved and collision detection. A rollback is a new corrective commit; history is not rewritten to conceal failure.

An export manifest names the instance namespace, format version, snapshot sequence, entity counts, source digests, coverage and any omissions. Restore includes pending outbox work, capture/observer/audit checkpoints, review receipts, owner generations, conflicts and candidate/proposal transition histories. Rebuild projections against the restored watermark. Import validates namespace collisions and every reference before activation, preserves original lineage, and stages changes without partially publishing the instance. Imported grant records describe history; new live credential bindings require the receiving human owner's explicit authorization. Never import secrets or automatically grant a remote author control of the destination.

## 10. Hardware independence and agency integration

Expose capabilities rather than machine assumptions. Required baseline capabilities are persistent storage, reliable source capture/import, transactions, exact resolution, lexical search, scoped authorization, and an integration path for manual or model-assisted event extraction. No CUDA, GPU, cloud account, containers, vector database, or always-on second machine is mandatory.

A capability probe reports storage capacity, backend readiness, context limits, tokenizer availability, extraction/embedding/reranking adapters, supported concurrency, and network policy. Missing optional capabilities select deterministic fallbacks with visible status. Never silently send private memory to a remote provider because a local adapter is unavailable. A configured external provider must be explicitly enabled and receive only the required authorized context.

Use bounded queues and worker counts. On slow hardware, archive capture has priority; extraction backlog remains durable and visible. Never drop old events to keep a dashboard looking live. Backpressure must be observable to the host. A baseline process can perform steps sequentially while preserving logical `get_many` behavior.

Recommended adapter boundaries: capture host, source store, metadata/transaction store, search, embedding, reranking, extraction model, authentication/policy, and presentation. A framework-specific tool protocol is an adapter, not the canonical data model. Replacing a model must preserve histories, permissions, sources, candidates, and canonical IDs.

A local implementation may use a transactional SQLite database and source directory. PostgreSQL, optional pgvector, and object storage are scalable adapter choices where needed. None is a mandatory installation. See the [adaptation guide](docs/ADAPTATION.md) for deployment profiles and integration boundaries.

Every conforming backend must support the [portable reference profile](docs/REFERENCE_FORMAT.md) conventions, preserving additional runtime semantics through versioned extension data and a complete export manifest. The included 17-kind fixture profile fixes namespace, revision, evidence and commit examples; it is not by itself a complete operational backup or a mandate to use files as the live authoritative store. Full export includes the additional state required by §9 and the logical contracts. An unsupported required extension must produce a visible compatibility failure, not silent data loss. Changing language, model, operating system or database must not change stable IDs or current/historical answers.

## 11. User-facing and operator functions

Provide tools or CLI operations to list decisions so far with counts of active, revised, deferred, rejected items and open candidates; show candidate confidence and its basis. Support confirming, rejecting, deferring, or returning selected candidates to exploratory status in a batch, viewing provenance, comparing revisions, resolving conflicts, inspecting proposals, following derivations, and requesting deeper historical searches. A revised count is a change-history metric and may overlap active status; label the count definitions.

The interface should display concise current meaning first, then offer history, source, and related variants. Users and agents must be able to traverse in both directions. A graphical tree explorer is optional; functional navigation is required.

Report capture/observer/audit watermarks, backlog age, failed events, stale projections, broken links, unregistered derivatives, ownership grants, memory-context usage, and available storage. Audit logs record actor, scope, action, outcome, related commit, and source references without copying secrets into general telemetry.

## 12. Scale, performance, and limitations

Bound working-set tokens independently of lifetime corpus size. Index by identity/scope/status/time, fetch ranges instead of complete conversations for ordinary evidence requests, cache by revision, and split secondary/map storage when measured latency warrants it.

Benchmark capture durability, current-record lookup, evidence-window fetch, history traversal, multi-branch retrieval, working-set assembly, extraction backlog, discovery recall, revision reconstruction accuracy, and permission failures. Report p50/p95 latency, corpus size, warm/cold cache, hardware, backend, and model configuration. Compare growth on the same host. Set local latency objectives before implementing an optimization and publish results rather than claiming every machine meets one universal millisecond target.

The long-horizon benchmark must include at least 50,000 synthetic interactions, repeated changed decisions, rejected alternatives, temporal facts, missing summaries, and source-based repair. Run a larger generated metadata/derivative-count test to verify that primary payload size remains bounded as the archive grows. These are acceptance workloads, not claims of completed tests.

The design cannot guarantee perfect extraction, perfect retrieval, infinite physical capacity, constant-time semantic discovery, or correctness of every source claim. It makes errors diagnosable and repairable by retaining evidence. A required evidence gap may prevent a confident decision even when the service is working correctly.

## 13. Publication and implementation completion

Keep private conversations, embeddings, indexes, credentials, instance configurations, real user/project directories, and generated logs out of public distributions. Ship synthetic fixtures and portable configuration examples.

Default source retention is indefinite while capacity permits; never silently purge to make space. An optional explicit owner-directed erasure process must document that it breaks lossless retention for the selected content, remove governed copies/indexes/backups according to its declared scope, and leave a non-sensitive tombstone. This is an engineering privacy extension, not a normal compaction feature.

The build is complete only when all required behaviors in this specification and [the requirements checklist](docs/REQUIREMENTS.md) are implemented and their corresponding [acceptance scenarios](docs/ACCEPTANCE.md) pass with recorded results. A partial release must clearly identify unimplemented requirements and must not present itself as the complete design. Optional reference backends are evaluated when shipped; supporting a portable deployment does not require installing every backend alternative.

Reference schemas, fixtures, and artifact checks verify portable data contracts. A runtime release must separately demonstrate live authentication, crash durability, extraction accuracy, and installation on each claimed operating system. It must provide reproducible setup, pinned dependencies, one working live host adapter and a transcript importer, with observed results for its supported operating-system/backend matrix.
