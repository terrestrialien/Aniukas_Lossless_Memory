# Implementation requirements

The `ALM-001`–`ALM-132` groups define the behavior to build. A group may
contain several detailed clauses. The [machine-readable checklist](requirements.json)
has fields for an implementer to record status, evidence, and notes. The
[build specification](../BUILD_SPEC.md) explains the architecture; the
[acceptance scenarios](ACCEPTANCE.md) describe behavior to demonstrate.

Edit implementation status, evidence, and notes directly in JSON. If you
change normative wording or links there, run
`python tools/check_requirements.py --write-markdown` from the repository root
to refresh this page, then run the ordinary checks.

All clauses below are normative. An acceptance ID is a
verification target, not a claim that a runtime has passed it.

### ALM-001 — Preserve the complete captured conversation, not just a compressed recollection

Spec: §4.1 · Contracts: Source · Acceptance: A01, A03.

Detailed clauses:

- Preserve the complete original conversation/event log. Chunking and archival are permitted; destructive summarization must not replace the source. Source history is immutable/append-only. Chunking and lossless compression do not permit destructive replacement of source material.
- Never rewrite an original captured log because a later interpretation changes. Allow current memory, history, interpretations, rules, importance, and relationships to evolve above that frozen source. Owner-directed erasure, when offered, follows an explicit governed exception and is never ordinary summary compaction.

### ALM-002 — Summaries and useful state accompany the source; recursive summarization must not replace it

Spec: §3.2 · Contracts: WorkingSet · Acceptance: A11, A14.

Detailed clauses:

- Separate persistent storage from active model context. Extract useful operational state into a small memory/index; each extracted claim has a direct pointer to the exact historical evidence and can be revisited if its assumptions change. Operational state remains a derived view with recoverable evidence.

### ALM-003 — The small memory is an index/control panel into durable memory, not the whole memory

Spec: §3.2 · Contracts: WorkingSet · Acceptance: A11, A14.

Detailed clauses:

- Grow from a small working-memory map into category/project files and a hierarchical graph, rather than an endlessly growing in-context RAM file. Category files are maps, not copies of all evidence. Category files are indexes or views; they do not embed all supporting evidence.
- Keep immediate operational entries small, fast, and useful. Expose identity/topic, current state, importance, status, reason and history pointers, revision count, and related-record links; capacity is configured rather than fixed by a sample count.
- Keep concise current system, user, project, and task memory as the starting interface to a large retained archive. Expand into history when reasons, earlier events, certainty, or contradictions matter. No example byte size is a mandatory limit or hardware requirement.
- Store only the current record's necessary meaning and small pointers to deeper material. Support navigation through maps, project rules, reasoning and change history, source windows, and immutable originals. Each layer stays compact relative to its responsibility; deep evidence remains separately retrievable.

### ALM-004 — Each memory points to the exact log and precise relevant location

Spec: §4.2 · Contracts: EvidenceWindow · Acceptance: A03, A14, A18.

Detailed clauses:

- Each memory link identifies the exact log file and exact portion containing the originating discussion. Overrules/expansions retain links to multiple reasoning locations. A change or extension may have multiple evidence locations.
- A decision record must represent identity, topic, status, current meaning, source references, rationale, and superseding relationships. A source locator must identify its log, chunk, and exact message range. Field names and alias formats may vary if these concepts remain interoperable through the declared format.

### ALM-005 — Full logs may be split into archival chunks without losing their content

Spec: §4.1 · Contracts: Source · Acceptance: A01, A03.

### ALM-006 — Every change has its own source; expansion/reversal accumulates evidence, retaining earlier origins

Spec: §4.3 · Contracts: Revision · Acceptance: A02.

Detailed clauses:

- A later changed/expanded decision can contain multiple sources and `extends[]` references. Retain the original record unchanged and express its changed operational meaning through relationships/revisions. New revisions or relationships must not rewrite the original historical record.

### ALM-007 — History records what changed, why, and when; current state alone is insufficient

Spec: §4.3 · Contracts: Revision · Acceptance: A02.

Detailed clauses:

- Decision/reasoning records show a current state and compact revision chronology. Each revision contains when, what changed, why, and its exact source. Preserve evolution of thought rather than only the latest conclusion. Every revision preserves when, what, why, and exact evidence.

### ALM-008 — Later interpretation does not rewrite original events or erase past versions

Preserve immutable source events and prior revisions. Express changed operational state through new authorized revisions or relationships, never by rewriting earlier events.

Spec: §4.1 · Contracts: Source · Acceptance: A01, A03.

### ALM-009 — Navigate adjacent depths in both directions with exact links

Spec: §4.2 · Contracts: EvidenceWindow · Acceptance: A03, A14, A18.

Detailed clauses:

- Adjacent memory depths must have direct, easy, exact links in both directions. A pointer specifies an exact file/location via resolution, and every revision maps to its own originating conversation. Stable resolution may replace literal file paths while preserving exact locations and reverse navigation.

### ALM-010 — Stable identifiers, rather than physical paths, are the fundamental identity

Spec: §4.2 · Contracts: EvidenceWindow · Acceptance: A03, A14, A18.

Detailed clauses:

- Use stable IDs, not physical paths, as fundamental links. Resolve memory IDs, decision revision IDs, and exact log-message range IDs to storage. Moving, splitting, compressing, archiving, or renaming files must preserve historical references. URI syntax is an implementation choice; resolution must remain exact.
- Assign persistent identity to every meaningful memory item, including rules, decisions, observations, and hypotheses, so higher views and histories can refer to it reliably. Human-readable prefixes are aliases, not a mandatory ID format.

### ALM-011 — An index/resolver maps identity to location; filenames are not the authoritative identity

Spec: §4.2 · Contracts: EvidenceWindow · Acceptance: A03, A14, A18.

Detailed clauses:

- Treat filenames as human/agent routing hints, not the authoritative identity index. Maintain an index mapping stable identity to scope, type, status, importance and backend location so renames do not break history. File and offset are example location fields; a backend may use equivalent addresses.

### ALM-012 — Renaming, moving, splitting, compressing, or reorganizing storage must preserve references

Spec: §4.2 · Contracts: EvidenceWindow · Acceptance: A03, A14, A18.

Detailed clauses:

- Permit physical storage to be reorganized without breaking graph references; keep identifiers stable and defer exact physical layout. Storage layout is open; stable identity and resolvability are required.

### ALM-013 — Preserve current meaning, change/reasoning history, exact evidence, and full logs as resolutions of the same memory

Spec: §3.2 · Contracts: WorkingSet · Acceptance: A11, A14.

Detailed clauses:

- Represent current meaning, change and reasoning history, exact evidence windows, and complete sources as increasing resolutions of one memory. The API uses depths 0–3 for current, history, evidence, and reconstruction.
- Keep working-set views separate from canonical current records, revision history, evidence windows, and complete logs. Retrieval must support current, history, evidence, and reconstruction while retaining every conceptual component.
- Allow each scope to have current memory, change and decision history, exact supporting records, and complete immutable logs. Ownership scope is independent of evidence depth: 0=current, 1=history, 2=evidence, 3=full reconstruction.
- Provide global and project primary/secondary views, rules, decisions and indexes, plus scoped histories, exact supporting-source references/windows and immutable original logs. The logical structure is required; literal folders, filenames and the .mem extension are not.

### ALM-014 — Fetch exact evidence windows with surrounding context, expanding or following references when necessary

Spec: §4.2 · Contracts: EvidenceWindow · Acceptance: A03, A14, A18.

Detailed clauses:

- Source retrieval returns precisely the cited message range and can include surrounding messages for context; it must return the actual user/assistant exchange rather than reconstructing it. Evidence excerpts must be source slices, never model reconstructions.
- Evidence windows are separate from full conversations. Retrieve a referenced exact range, then expand outward or follow cited earlier context when needed. Evidence windows represent progressive disclosure of source, not invented summaries. Windows expand to adjacent messages or referenced context when needed.

### ALM-015 — Separate facts, decisions, observations, preferences, goals, constraints, hypotheses, inferences, questions, procedures, and asserted beliefs

Spec: §3.1, §4.3, §5.2 · Contracts: MemoryRecord · Acceptance: A06, A37.

Detailed clauses:

- Represent facts, decisions, beliefs, preferences, observations, hypotheses, goals, constraints, inferences, questions and procedures as distinct concepts. Keep belief explicit or document its mapping without turning it into a verified fact.
- Distinguish facts, rules, decisions, observations, preferences, constraints, hypotheses, inferences, questions, and procedures as record types. Additional types may be added without collapsing these distinctions.

### ALM-016 — Track type, confidence, source authority, and lifecycle separately

Spec: §3.1, §4.3, §5.2 · Contracts: MemoryRecord · Acceptance: A06, A37.

Detailed clauses:

- Track memory `type`, `confidence`, `authority`, and `status` separately. Distinguish observations, inferences, and unknowns; model speculation must not silently become fact. Numerical confidence values require a declared calibration method or must be labelled uncalibrated.
- Track authority independently: user-stated, AI-inferred, document, external source and system-observed. Preserve modality: user wondering whether X must not become “user believes X.” Source categories include user statements, model inference, documents, external sources, and system observations. A question must not become an asserted belief.
- Distinguish human/user statements, authorized governor actions, project-agent actions, external sources and AI/model inferences in provenance and authority metadata. Keep original source attribution separate from the actor who later authorizes adoption. Provenance does not guarantee correctness.

### ALM-017 — AI speculation must not harden into a user statement or verified fact

Spec: §3.1, §4.3, §5.2 · Contracts: MemoryRecord · Acceptance: A06, A37.

### ALM-018 — Use explicit typed relationships: support, contradiction, supersession, extension, cause, and evidence

Spec: §4.4 · Contracts: Relationship · Acceptance: A02, A07.

Detailed clauses:

- Add typed graph relationships: `supports`, `supersedes`, `contradicts`, `caused_by`, and `evidence`, in addition to extension links. Treat the structure as a temporal knowledge graph grounded in immutable evidence. The graph remains grounded in source evidence and revision history.

### ALM-019 — Remember rejected alternatives and reasons, deferred options, experiments, conditions, superseded states, and unknowns

Spec: §5.4 · Contracts: MemoryRecord, Revision · Acceptance: A08.

Detailed clauses:

- Store negative memory: alternatives considered and explicitly rejected, together with reasons; avoid repeatedly proposing previously rejected ideas without context. Changed conditions may justify reconsideration; retaining rejection history prevents uninformed repetition.
- Revision history must distinguish current, past, rejected, deferred, experimental, superseded, conditional, and unknown states. These are semantic concepts; whether they map to one enum or to separate fields is a schema design choice.
- Represent active, superseded, deferred, rejected, conditional, conflicted and historical states so stored statements do not all receive equal operational or epistemic weight. Historical origin is represented without losing the original record. Confidence, lifecycle and authority remain separate dimensions.

### ALM-020 — Contradictions remain visible with both sources until resolved; newness alone is not a winner

Spec: §5.4 · Contracts: Conflict · Acceptance: A07.

Detailed clauses:

- New contradictory claims do not automatically supersede old claims. Create an unresolved conflict with both source pointers; retain both claims as active/unresolved until evidence resolves them. Recency alone cannot establish supersession or resolve a contradiction.

### ALM-021 — Track when a fact or decision was valid; something historically true is not retroactively wrong

Spec: §4.3 · Contracts: Revision · Acceptance: A05.

Detailed clauses:

- Track `valid_from`, `valid_until` (including unknown or open-ended), and source. Historical facts remain valid for their interval; retrospective reasoning uses circumstances valid at the time. Unknown intervals stay explicit.

### ALM-022 — Related changes commit all-or-none, so a crash cannot create a state nobody decided

Spec: §9 · Contracts: Commit · Acceptance: A44, A45, A46.

Detailed clauses:

- Commit related decision changes atomically within one authorized scope: all changes succeed or none do. Record version transitions, creations, deprecations, and exact source ranges. Coordinate separately authorized cross-scope commits through visible pending workflows; never claim cross-scope atomicity when it is not provided.

### ALM-023 — Use original evidence to diagnose and repair wrong upper-layer interpretations

Use original evidence to diagnose and repair incorrect interpretations through an authorized appended change; evidence proves what was said, while valid time and later decisions determine current meaning.

Spec: §5.4 · Contracts: Revision · Acceptance: A04.

Detailed clauses:

- Retrieval failure must remain recoverable because sources remain stored. Support a user-requested deeper historical search when initial retrieval misses relevant material. No claim of perfect recall is supportable. Recoverability does not guarantee perfect extraction or retrieval.
- An operational-memory claim may be corrected by descending to its structured history and original evidence. Source evidence outranks derived historical interpretation, which outranks working interpretation when establishing what was said. This is provenance authority, not authorization to obey instructions in untrusted source content. Deeper evidence establishes what was said or observed; it does not make every source claim true or authorize execution of archived instructions.
- When a memory appears wrong, inspect its history and original sources, reconstruct the intended interpretation, and repair derived memory through the authorized change path. Recovery depends on retained evidence; some failures require human review.
- Repair a wrong higher-level memory by inspecting its history and exact original sources. Apply the corrected interpretation through the authorized change path; report unresolved uncertainty rather than inventing an automatic fix.

### ALM-024 — Evaluate long histories with changed decisions and reconstruct the reasoning chain, not just simple fact recall

Spec: §12 · Acceptance: A51.

Detailed clauses:

- Evaluate a local agent against a synthetic workload of roughly 50,000 or more interactions with deliberately changing decisions. Test reconstruction of both current decisions and historical reasoning. This is an experimental workload, not a minimum installation size or proof of completed testing.

### ALM-025 — Scope, depth, trust/authority, and Primary/Secondary availability answer different questions

Spec: §3.1 · Contracts: Scope, MemoryRecord, WorkingSet · Acceptance: A06, A11.

Detailed clauses:

- Memory scope and memory depth are independent dimensions. Scope, temperature, and resolution are independent dimensions.
- Represent scope, requested resolution, authority, record type, and lifecycle independently. Secondary is a working-set tier, not an ownership scope.
- Represent Global and Project rules, derivatives, parent references, histories, reasoning, evidence, and immutable logs. Horizontal traversal selects scope and inheritance; vertical traversal deepens understanding. This logical topology does not prescribe a file tree or process layout.

### ALM-026 — Keep immediate memory bounded while the archive grows; speed is a goal, not a license to discard evidence

Spec: §6.2, §12 · Contracts: WorkingSet · Acceptance: A13, A20, A52.

Detailed clauses:

- Optimize for lossless retained memory and responsive routine use as the archive grows. Measure latency and capacity; do not promise fixed latency, infinite storage, or perfect recall.
- Only the active model context has a hard token budget. Deeper persistent layers are governed by retrieval latency rather than a context-size limit; physical storage remains finite, configurable, and observable.
- Decouple lifetime storage growth from active-context growth. Routine work should retrieve only a few relevant pages even with a large long-lived archive; multi-decade or multi-terabyte operation is a scale objective, not a hardware prerequisite.
- Preserve the fir-tree design objective: the routinely visible tip of memory stays small as the underlying graph and archive grow. This does not claim infinite capacity or constant-time search on every machine.

### ALM-027 — Primary contains currently relevant/impactful items; Secondary holds valid items not normally loaded

Spec: §6.1, §6.2 · Contracts: WorkingSet · Acceptance: A11, A12, A52.

Detailed clauses:

- Immediate memory holds the most relevant/impactful decisions; a neighboring secondary file holds less important/less used decisions. Secondary is a working-set temperature, not a separate permission scope or automatically injected context.
- Primary holds information worth immediate availability; secondary retains valid information that does not need working-context occupancy. Support later partitions by measured needs without treating demotion as forgetting. Numeric segments, categories, dates and projects are optional partition strategies, not a fixed storage layout.

### ALM-028 — Move items both ways between Primary and Secondary as relevance changes

Spec: §6.1, §6.2 · Contracts: WorkingSet · Acceptance: A11, A12, A52.

Detailed clauses:

- Primary holds information that repeatedly affects reasoning; Secondary holds valid memories not worth immediate tokens. Promote and demote in either direction with relevance and use; demotion does not delete records or history. Physical file layout remains an implementation choice.

### ALM-029 — Demotion and 'garbage collection' mean reorganizing availability, not deleting knowledge

Spec: §6.1, §6.2 · Contracts: WorkingSet · Acceptance: A11, A12, A52.

Detailed clauses:

- Remove inactive information from model context without deleting stored knowledge. Primary and Secondary are availability tiers inside scopes; Secondary is not automatically loaded.

### ALM-030 — Combine persistent Primary entries with a task-specific temporary selection

Spec: §6.1, §6.2 · Contracts: WorkingSet · Acceptance: A11, A12, A52.

Detailed clauses:

- Physical storage may be a graph while the task receives a dynamically assembled relevant tree/working set of pointers. Different task concerns surface different branches. The apparent tree can change with the task while canonical records and relationships persist.

### ALM-031 — Include relevant global/system Primary memory at task startup

Spec: §3.1, §6.1, §7 · Contracts: Scope, WorkingSet · Acceptance: A11, A23.

Detailed clauses:

- Assemble immediate context from system Primary, user Primary, and selected Project memory while keeping Secondary separate. Files or a database may provide equivalent logical views; no specific filename or directory layout is required.
- Normally initialize a project agent with global primary, applicable user-profile primary, project primary and current task state, plus the ability to retrieve deeper memory. Do not ingest years of history at startup. Memory sizes are deployment settings, not fixed limits.
- Compose working context from global primary, the relevant project primary, and current conversation context. Keep older decisions reachable through current record, history, and exact original sources. User-profile and task overlays extend this core composition without requiring the full archive in a model prompt.

### ALM-032 — Include a user-level preference/constraint overlay where applicable

Spec: §3.1, §6.1, §7 · Contracts: Scope, WorkingSet · Acceptance: A11, A23.

### ALM-033 — Project Primary lives at the same immediate depth; changing project details do not burden other projects

Spec: §3.1, §6.1, §7 · Contracts: Scope, WorkingSet · Acceptance: A11, A23.

Detailed clauses:

- Project-specific immediate memory lives at the same depth as primary. Development-dependent project rules remain local and should not affect other projects unless explicitly designated for broader scope per entry. A project's rules do not automatically change other projects or the global scope.

### ALM-034 — Load current task state alongside relevant broader memory

Spec: §3.1, §6.1, §7 · Contracts: Scope, WorkingSet · Acceptance: A11, A23.

### ALM-035 — New project rules stay local unless a specific decision shares or promotes them

Spec: §3.1, §6.1, §7 · Contracts: Scope, WorkingSet · Acceptance: A11, A23.

### ALM-036 — Route to known project/global/user memory deterministically before uncertain discovery search

Spec: §3.1, §6.1, §7 · Contracts: Scope, WorkingSet · Acceptance: A11, A23.

Detailed clauses:

- File naming is part of cheap deterministic sorting/indexing/routing. Obvious scope routing precedes probabilistic retrieval; project work should directly locate system primary, user primary and project-specific memory. Names provide routing hints; stable identity and resolver semantics remain authoritative.

### ALM-037 — Human-readable file names act as cheap sorting/routing hints

Spec: §3.1, §6.1, §7 · Contracts: Scope, WorkingSet · Acceptance: A11, A23.

### ALM-038 — Segment large Secondary/history storage when needed; defer the detailed strategy

Spec: §6.2, §8.2 · Contracts: DerivativeMap · Acceptance: A03, A21.

Detailed clauses:

- Support segmentation of growing Secondary and deeper storage into organized chunks. Choose a partition strategy when measurements justify it; keep stable references throughout any split.
- Begin secondary storage simply and split it only when measured inefficiency warrants partitioning. Permit later subdivisions while preserving all stable references across physical moves. A single file or category directories are possible representations, not required storage formats or a fixed taxonomy.

### ALM-039 — Large derivative maps may gain a hierarchy/category index without changing parent addresses

Support a future hierarchy or category index for large derivative maps without changing parent addresses; defer its exact segmentation and activation thresholds until measured need.

Spec: §6.2, §8.2 · Contracts: DerivativeMap · Acceptance: A03, A21.

Detailed clauses:

- Permit derivative maps to gain hierarchical indexes without changing stable parent addresses. Select categories, segmentation, and activation thresholds from measured scale while preserving extensibility.

### ALM-040 — Start simply when stable addressing permits future growth; no exotic hardware is needed for the core

Keep the core deployable without exotic hardware and allow simple initial storage. Offer a declared capture/manual profile when an extraction model is unavailable; automated extraction remains required for full capability.

Spec: §10 · Acceptance: A49.

Detailed clauses:

- Support interchangeable storage choices: relational metadata and relationships, optional vector retrieval, and compressed files or object storage for immutable chunks. PostgreSQL and pgvector are possible adapters, not prerequisites; local alternatives are allowed.
- Keep the initial implementation simple when stable addressing already permits later storage reorganization without broken references. Add scaling machinery in response to an actual measured need. This does not defer stable identities, provenance, or permissions needed for correctness from the start.

### ALM-041 — Combine keyword/semantic/graph discovery; embeddings and reranking are useful backend options

Spec: §6.1, §6.2, §6.3 · Contracts: WorkingSet · Acceptance: A12, A13, A14, A22.

Detailed clauses:

- Combine semantic discovery with exact provenance. Pipeline: question → memory map → semantic/keyword/graph search → candidate memories → provenance → original chunks → model reasons from actual evidence → answer. Semantic search is a capability adapter; exact provenance is required with or without embeddings.
- Support hybrid retrieval using lexical search, optional embeddings and reranking, and graph traversal. A deterministic lexical and graph baseline must work without a particular model, provider, vector dimension, or service vendor.

### ALM-042 — After finding a record, descend through exact pointers instead of guessing with similarity search

Spec: §6.1, §6.2, §6.3 · Contracts: WorkingSet · Acceptance: A12, A13, A14, A22.

Detailed clauses:

- Once a branch/memory is identified, downward traversal is deterministic. Semantic/vector/graph search discovers branches; fuzzy retrieval is used again only for deliberate lateral discovery of related information. Fuzzy discovery may resume when deliberately searching sideways for related branches.

### ALM-043 — Inspect Secondary and decision indexes on substantial requests; do not search only Primary

Spec: §6.1, §6.2, §6.3 · Contracts: WorkingSet · Acceptance: A12, A13, A14, A22.

Detailed clauses:

- Primary cannot be the only place searched initially. A small retrieval router checks every substantial request against primary, secondary index and decision index; relevant historical branches can be promoted temporarily. Primary combines persistent and dynamically assembled entries. The router considers primary, secondary indexes, and decision/current-record indexes, with temporary promotion of relevant branches.

### ALM-044 — Wake relevant memories through topics, entities, projects, conditions, dependencies, dates, people, hardware, locations, and contradictions

Spec: §6.1, §6.2, §6.3 · Contracts: WorkingSet · Acceptance: A12, A13, A14, A22.

Detailed clauses:

- Retrieval trigger categories: topics, entities, projects, conditions, dependencies, dates, people, hardware, locations and contradictions. Trigger categories include topics, entities, projects, conditions, dependencies, dates, people, hardware, locations, and contradictions.

### ALM-045 — Rare conditional constraints can be critical despite low ordinary frequency

Spec: §6.1, §6.2, §6.3 · Contracts: WorkingSet · Acceptance: A12, A13, A14, A22.

Detailed clauses:

- Importance is multidimensional and conditional, separate from frequency. Track conditional importance and trigger conditions so rarely used but critical memories surface when their conditions occur. A rarely used constraint may be critical under a specific condition.

### ALM-046 — Allow explicit current/explain/verify/reconstruct requests

Spec: §6.3, §6.4 · Contracts: memory.get, memory.get_many · Acceptance: A14, A15, A16, A17, A19, A20, A27.

Detailed clauses:

- Choose retrieval depth according to need: the bounded working set supports routine context; depth 0 provides current records, depth 1 history and reasons, depth 2 exact evidence, and depth 3 full reconstruction. Do not fetch complete histories for every task.
- Support depth-addressed retrieval of current authoritative meaning, concise reasoning and history, relevant exact source excerpts, and full historical reconstruction. Routine work begins with current memory; request type, uncertainty, and impact govern deeper retrieval. Use depths 0–3.
- Expose retrieval by stable record identity and requested evidence depth, plus batch retrieval of multiple identities and branches. Keep each batch branch individually addressable and allow a distinct depth per branch; operation names may vary by adapter.

### ALM-047 — Retrieve several records in one operation or reasoning request

Spec: §6.3, §6.4 · Contracts: memory.get, memory.get_many · Acceptance: A14, A15, A16, A17, A19, A20, A27.

Detailed clauses:

- Retrieve multiple records and branches in one request; fan out across revision and relevant sources and return a combined evidence bundle for joint reasoning. Fan-out is a logical API capability; physical concurrency is optional on constrained hosts.

### ALM-048 — Allow different depths per branch and deepen only the uncertain branches

Spec: §6.3, §6.4 · Contracts: memory.get, memory.get_many · Acceptance: A14, A15, A16, A17, A19, A20, A27.

Detailed clauses:

- Allow one reasoning operation to request multiple memories and histories together, then descend only unresolved branches to differing depths. Logical batch semantics do not require parallel hardware execution.

### ALM-049 — Routine work may rely on a confident current decision without automatically reading all reasoning

Permit routine tasks to use a sufficiently confident current decision without automatically fetching history. Do not forbid extra retrieval when it improves understanding or meets required review.

Spec: §6.3, §6.4 · Contracts: memory.get, memory.get_many · Acceptance: A14, A15, A16, A17, A19, A20, A27.

Detailed clauses:

- Some tasks may rely on a sufficiently confident decision while others retrieve as deeply as needed. Reasoning/full context is demand-driven, not compulsory for every memory read. Adequate confidence is contextual; consequential changes still follow the evidence requirements defined elsewhere.

### ALM-050 — Optimize for informed confidence, not minimum effort or the fewest tokens

Spec: §6.3, §6.4 · Contracts: memory.get, memory.get_many · Acceptance: A14, A15, A16, A17, A19, A20, A27.

Detailed clauses:

- Let a human or agent challenge an unsuitable rule by requesting history or the full deeper record. If the requested level is absent, use the next deeper available record. Retrieve enough reasoning for informed, confident decisions rather than minimizing effort. A justified project-specific exception is a valid investigation outcome; the objective is decision quality.
- Start with authoritative concise understanding, descend when more understanding could materially change the decision, stop at sufficient evidence, and require historical review for consequential changes. Prioritize accuracy, informed reasoning, provenance and recoverability over minimizing retrieval. The user explicitly endorsed this philosophy before adding scope write controls.

### ALM-051 — A challenge normally reads history/reasons first, then original evidence if uncertainty remains

Spec: §6.3, §6.4 · Contracts: memory.get, memory.get_many · Acceptance: A14, A15, A16, A17, A19, A20, A27.

Detailed clauses:

- When an inherited rule materially complicates a task, inspect its revision history and original discussion as needed before challenging it.
- Start with the current rule and use it if suitable. Otherwise inspect change history and reasoning, then exact supporting conversations when required. Stop when understanding is sufficient; deeper information alone is not a reason to retrieve it.
- A historical explanation may be sufficient to accept or design around a rule. When material uncertainty or missing nuance remains, retrieve exact supporting records before deciding whether to challenge it.
- Support current rule → reasoning/history → exact source records → full original conversations when necessary. Stop at sufficient understanding rather than a minimum token count; full reconstruction can be incremental.

### ALM-052 — If an intermediate level is absent, automatically use the next deeper available level

When a requested intermediate depth is genuinely absent, return the next deeper available evidence, with fallback metadata; distinguish absence from a broken pointer or denied access.

Spec: §6.3, §6.4 · Contracts: memory.get, memory.get_many · Acceptance: A14, A15, A16, A17, A19, A20, A27.

Detailed clauses:

- Automatically descend to the next available authoritative evidence level when the requested intermediate history is missing. Clearly identify the deepest available evidence when original sources are absent. Do not fabricate sources. Missing evidence, broken pointers and access denial are distinct outcomes.

### ALM-053 — Know the deepest evidence actually available; disclose genuine gaps

Spec: §6.3, §6.4 · Contracts: memory.get, memory.get_many · Acceptance: A14, A15, A16, A17, A19, A20, A27.

Detailed clauses:

- Addressed records expose stable identity, scope, available evidence resolution, authority/provenance, lifecycle status and confidence. Availability metadata must allow callers to know which depths actually exist. Confidence values have no universal default. Confidence is neither proof of truth nor a permission grant.

### ALM-054 — Require historical review for global reversal/promotion, major dependencies, expensive/irreversible decisions, and contradiction resolution

Spec: §6.3, §6.4 · Contracts: memory.get, memory.get_many · Acceptance: A14, A15, A16, A17, A19, A20, A27.

Detailed clauses:

- Require sufficient supporting history before overturning global rules, making expensive or irreversible decisions, resolving contradictions, changing widely depended-on items, judging an old decision mistaken, or promoting a local rule globally. History can suffice; full conversations are needed only if uncertainty remains.
- Inherit active applicable global rules and inspect the parent's change history/reasoning before making a local exception; descend to original evidence when necessary. This is the minimum evidence procedure for a project override.
- Routine rule following may require no historical retrieval; a project exception requires at least the parent's history/reasoning; a global rule change requires a higher evidentiary standard. Low/moderate/high describe procedural expectations, not fixed token amounts. Apply missing-depth fallback when history is absent.

### ALM-055 — Assess original purpose, solved problem, alternatives, constraints, and consequences before changing a rule

Spec: §6.3, §6.4 · Contracts: memory.get, memory.get_many · Acceptance: A14, A15, A16, A17, A19, A20, A27.

Detailed clauses:

- Before a consequential rule change, establish why the rule exists, the problem it solved, prior alternatives, important constraints, and consequences of change. Continue into relevant sources while material uncertainty persists. This is an evidence standard, not a numeric confidence formula.

### ALM-056 — Do not cap necessary deep understanding at an arbitrary small number of tokens/windows

Spec: §6.3, §6.4 · Contracts: memory.get, memory.get_many · Acceptance: A14, A15, A16, A17, A19, A20, A27.

Detailed clauses:

- Do not stop a consequential investigation merely because a fixed token or source-chunk count is reached. Permit enough historical review for sufficient understanding; handle finite request budgets through resumable retrieval.

### ALM-057 — Do not browse other projects' examples just because they exist; do so when useful

Spec: §6.3, §6.4 · Contracts: memory.get, memory.get_many · Acceptance: A14, A15, A16, A17, A19, A20, A27.

Detailed clauses:

- Expose known derivative summaries from a parent, then allow selective inspection of a variant's reasoning and implementation consequences and creation of a new local derivative from it. Discoverability must follow the configured read policy, including optional restricted-read deployments.
- When precedent helps, read compact map descriptions first, then relevant current derivatives, and only their needed reasoning, history, and source conversation. Do not fetch every derivative's full contents merely because a map exists.
- Support current-meaning-to-source depth traversal and parent-to-relevant-derivative traversal independently. Follow either direction when it improves decision quality or confidence rather than merely because links exist. Required evidence checks for consequential changes still apply.

### ALM-058 — Concise interpretations may be corrected from original evidence while later authorized changes remain meaningful

Spec: §5.4 · Contracts: Revision · Acceptance: A04.

### ALM-059 — Historical reasoning must use the facts/rules valid then, rather than today's circumstances

Spec: §4.3 · Contracts: Revision · Acceptance: A05.

### ALM-060 — An exception whose condition no longer holds may be flagged for owner reconsideration

Spec: §8.1 · Contracts: Derivative, memory.resolve_rule · Acceptance: A28, A29, A30.

Detailed clauses:

- Preserve the conditions that justified Project exceptions and flag them for reconsideration when those conditions no longer hold. A changed condition triggers review, never automatic reversal of the Project rule.

### ALM-061 — Show the effective local rule together with its parent, reason, and unchanged broader default

Spec: §8.1 · Contracts: Derivative, memory.resolve_rule · Acceptance: A28, A29, A30.

Detailed clauses:

- Resolve applicable valid rules deterministically by task override, project rule, global rule and default behavior, with configured user-profile handling. Return effective rule, overridden parent, exception reason and the surviving global default. Most-specific valid rules win; an exception must not masquerade as a universal rule. Ties and incompatible parents require explicit conflict handling.

### ALM-062 — Resolve valid explicit overrides by specificity: task/project/user overlay/global/default; avoid unexplained local shadowing

Resolve applicable valid explicit overrides by task, project, user overlay, global, then defaults. Expose lineage and reasons; unresolved equal-specificity or incompatible combinations remain conflicts.

Spec: §8.1 · Contracts: Derivative, memory.resolve_rule · Acceptance: A28, A29, A30.

Detailed clauses:

- Lower scopes inherit applicable higher-scope rules unless a valid explicit override exists. Every override identifies both what it overrides and why. The original scope terms are normalized into global, user-profile, project and task ownership/overlay rules.

### ALM-063 — Authorized participants may read all memory scopes as needed

Spec: §7, §6.1 · Contracts: Scope · Acceptance: A11, A23.

Detailed clauses:

- Permit project agents to read global primary, secondary, rule histories and evidence, and any project's memories and logs through authorized retrieval. In the default single-owner profile, every authorized agent may read every scope as needed. Read permission never implies automatic context inclusion.
- Support relevant authorized reads, limit agent mutations to currently owned scopes, route cross-scope changes through owner-directed proposals, and preserve the human owner's all-scope authority.

### ALM-064 — Read permission does not mean automatic loading of every scope

Spec: §7, §6.1 · Contracts: Scope · Acceptance: A11, A23.

Detailed clauses:

- Allow relevant authorized reads across global, project, history, and raw-log scopes while retrieving selectively. Do not automatically load other projects merely because access is permitted. The default trusted-agency read profile may be narrowed only through an explicitly documented alternative policy.

### ALM-065 — Project agents write only their assigned project's memory and never global/other-project records

Spec: §7 · Contracts: Scope, PrincipalGrant, Proposal · Acceptance: A23, A24, A32, A33, A34.

Detailed clauses:

- Ordinary project agents must never write global/system memories. They may submit proposals; only the user or an explicitly authorized global agent may modify global-owned memory. The boundary includes metadata, histories and secondary memory as well as rule text.
- Allow project-agent writes to its own project memories, rules and histories, and submission of global-change proposals. Deny direct writes to global primary, secondary, rules and histories. Task writes follow an owning-scope or narrower delegation; ordinary worker roles may have less authority.
- Allow projects to derive, override, experiment, and propose without silently redefining ancestors. Authorized global changes preserve prior versions, reasoning, provenance, and original evidence. A local improvement may be proposed for global adoption; it cannot promote itself.

### ALM-066 — Global governors write global memory, not project memory

Spec: §7 · Contracts: Scope, PrincipalGrant, Proposal · Acceptance: A23, A24, A32, A33, A34.

Detailed clauses:

- Global moderators may suggest project changes but cannot modify project memory. Only the assigned project owner and human owner may write that project; authorized agency agents may read scopes as needed. Universal readability applies within the authorized personal agency, not to anonymous internet users.

### ALM-067 — The human user retains authority to write across all scopes

Spec: §7 · Contracts: Scope, PrincipalGrant, Proposal · Acceptance: A23, A24, A32, A33, A34.

Detailed clauses:

- Give the human owner control over global-memory governance and permit global write authority only through explicit delegation to a governor. Project agents retain proposal authority only. Owner authority is application-scoped and does not bypass operating-system or external service controls.

### ALM-068 — Ownership covers metadata, statuses, history, links, and other indirect changes, not only rule text

Spec: §7 · Contracts: Scope, PrincipalGrant, Proposal · Acceptance: A23, A24, A32, A33, A34.

Detailed clauses:

- Apply scope authorization to changes in metadata, status, reasoning history, exception descriptions, and owned links as well as to rule text. A metadata or projection update cannot be used to bypass the scope owner's authority.

### ALM-069 — All project owners have identical mechanical rights; only their assigned project differs

Spec: §7 · Contracts: Scope, PrincipalGrant, Proposal · Acceptance: A23, A24, A32, A33, A34.

Detailed clauses:

- Apply one symmetric Project-owner access rule: read Global and other Projects; read and write only the assigned Project. Human owners read and write all scopes; Global governors write only Global memory; ungranted workers and researchers are readers.

### ALM-070 — Ordinary worker/research roles are read-only unless separately given a relevant ownership role

Spec: §7 · Contracts: Scope, PrincipalGrant, Proposal · Acceptance: A23, A24, A32, A33, A34.

### ALM-071 — Memory belongs to the project/scope role, not an individual model instance or vendor

Spec: §7, §10 · Contracts: PrincipalGrant · Acceptance: A33.

Detailed clauses:

- Attach write authority to the assigned scope and role rather than a model brand or specific agent instance. A newly assigned owner inherits the existing project authority. Grant replacement and credential revocation are engineering mechanics for current ownership.

### ALM-072 — Replacing an owner preserves memory and full history; the new owner inherits the existing scope

Spec: §7, §10 · Contracts: PrincipalGrant · Acceptance: A33.

Detailed clauses:

- On agent replacement, preserve the scope's existing memory and complete history. Do not replace, fork, summarize away, or reset that memory as a consequence of changing the owner instance. Replacing an owner is an authorization change, not a memory migration that changes meaning.

### ALM-073 — Greater model capability or administrative seniority does not confer write authority

Spec: §7 · Contracts: Scope, PrincipalGrant, Proposal · Acceptance: A23, A24, A32, A33, A34.

Detailed clauses:

- Do not grant write access based on administrative seniority, model capability, or apparent quality of an improvement. A governor can investigate and propose; a project agent can submit evidence; neither can rewrite the other's scope. Inspection of full reasoning and sources remains allowed under the authorized read profile.

### ALM-074 — Enforce permissions technically, not by trusting prompts

Spec: §7 · Contracts: Scope, PrincipalGrant, Proposal · Acceptance: A23, A24, A32, A33, A34.

Detailed clauses:

- Enforce global read-only behavior for ordinary project agents through actual service/storage permissions. Unauthorized global mutation attempts must be rejected even when the agent requests them. An instruction in a prompt is insufficient enforcement.
- Enforce ownership through service and storage authorization. Global governors write global memory; project owners write their assigned project; the human owner may write across scopes. Agent instructions alone are not an access-control boundary.

### ALM-075 — Only the receiving scope's owner applies a cross-scope change

Spec: §7 · Contracts: Proposal · Acceptance: A32.

Detailed clauses:

- Route a requested change outside the actor's scope to that scope's owner. Preserve accept or reject responses, and let only the authorized owner or human apply the target mutation. Proposal delivery must not itself mutate the target's semantic record.

### ALM-076 — Proposals work in both directions: project→global and global→project

Spec: §7 · Contracts: Proposal · Acceptance: A32.

### ALM-077 — Route proposals through a stable operation rather than hardcoding a particular governor agent

Spec: §7 · Contracts: Proposal · Acceptance: A32.

Detailed clauses:

- Expose stable proposal operations that route to the current authorized global custodian or human. Project-agent behavior must not depend on a particular governor identity, and scope write authority remains enforced. propose_global_note is the suggested operation; implementation may provide an equivalent stable interface.

### ALM-078 — Preserve consequential suggestions, acceptance/rejection/defer decisions, reasons, and source discussions

Spec: §7 · Contracts: Proposal · Acceptance: A32.

Detailed clauses:

- Preserve consequential suggestions and responses, including rejected suggestions and reasons. Record stable ID, sender, recipient, subject, proposed change, response, rationale, and precise source references. Prior rejection evidence remains available so later agents can consider changed conditions before repeating a suggestion.

### ALM-079 — The human may initially be the sole global writer; a governor is optional

Spec: §7, §5.2 · Contracts: PrincipalGrant · Acceptance: A23, A37.

Detailed clauses:

- Support an initial deployment where the user is the only global writer, and a later delegated governor that accepts or rejects proposals. Permit policy to authorize automatic change classes while reserving consequential changes for user approval. These are supported deployment/policy choices. An autonomous governor is not a mandatory initial dependency.

### ALM-080 — Explicit user delegation can evolve by change class; consequential changes may need user approval

Spec: §7, §5.2 · Contracts: PrincipalGrant · Acceptance: A23, A37.

### ALM-081 — Rights follow current assigned roles and scopes, not a model name

Spec: §7, §10 · Contracts: PrincipalGrant · Acceptance: A33.

### ALM-082 — Enable cross-project learning through controlled links/proposals without letting projects rewrite one another

Spec: §8.1, §8.2, §8.3 · Contracts: Derivative, DerivativeMap · Acceptance: A25, A26, A27, A28, A29, A30.

Detailed clauses:

- Allow agents to discover and inspect prior project variants, adapt one or produce a new solution, and propose useful local rules for global adoption. Also allow rules to originate globally. An expectation that many rules originate in projects is not a quota or promotion threshold.
- Enable precedent discovery through a project derivative, its global parent, and the parent's derivative index while preserving project isolation and global write restrictions. Discovering another project's precedent grants no authority to modify that project or a global rule.

### ALM-083 — A project may create a justified local exception while the parent rule remains unchanged

Spec: §8.1, §8.2, §8.3 · Contracts: Derivative, DerivativeMap · Acceptance: A25, A26, A27, A28, A29, A30.

Detailed clauses:

- Permit justified project-specific exceptions to inherited rules without altering the global parent. Preserve the overridden parent, conditions/reason, history and supporting sources. The project owner must have local write authority; the exception does not acquire global scope.

### ALM-084 — Parents should lead to every registered project variant, and variants lead back to their ancestry

Spec: §8.1, §8.2, §8.3 · Contracts: Derivative, DerivativeMap · Acceptance: A25, A26, A27, A28, A29, A30.

Detailed clauses:

- Register each local variant with its parent through the authorized parent-scope custodian while leaving parent semantics unchanged. Store descendant details in a separate derivative map and a bounded Primary pointer/count. Project agents never write parent backlinks directly.

### ALM-085 — Rules may originate globally or grow from useful project discoveries

Spec: §8.3 · Contracts: Proposal, Revision · Acceptance: A31.

### ALM-086 — A derivative records parent, project, changed portion, inherited portion, reason, history, and sources

Spec: §8.1, §8.2, §8.3 · Contracts: Derivative, DerivativeMap · Acceptance: A25, A26, A27, A28, A29, A30.

Detailed clauses:

- Store derivative identity, type, parent and pinned base revision, owning Project, effective rule or changes, reasons and conditions, inherited portion, history reference, and source reference. Creating the derivative never mutates parent semantics or silently changes when an ancestor evolves.

### ALM-087 — A project may adapt another project's variant; preserve direct ancestor and global parent genealogy

Spec: §8.1, §8.2, §8.3 · Contracts: Derivative, DerivativeMap · Acceptance: A25, A26, A27, A28, A29, A30.

Detailed clauses:

- Record global parent, immediate derived-from ancestor and modification rationale when a project adapts an existing variant, preserving the complete idea lineage. Suggested fields are global_parent, derived_from and modified_because; exact names may vary.

### ALM-088 — Prefer ancestor references and deltas where practical, avoiding redundant authoritative copies

Prefer pinned ancestor references and explicit deltas wherever practical. Permit a complete local rule with lineage when a delta cannot be applied reliably; caches must not create competing authorities.

Spec: §8.1, §8.2, §8.3 · Contracts: Derivative, DerivativeMap · Acceptance: A25, A26, A27, A28, A29, A30.

Detailed clauses:

- Prefer referencing an ancestor and storing changes where practical rather than duplicating a complete rule. Materialize the full effective rule on request, including changed values, removed restrictions and added requirements. Use a full derived representation with lineage when a delta is unsuitable. Copied caches do not become independent authorities.

### ALM-089 — Materialize a full effective rule when requested

Materialize the complete effective rule on request, using exact base revisions and explicit changes or a complete local meaning; do not guess a natural-language merge.

Spec: §8.1, §8.2, §8.3 · Contracts: Derivative, DerivativeMap · Acceptance: A25, A26, A27, A28, A29, A30.

### ALM-090 — Creating a local derivative emits an event for global registration

Spec: §8.1, §8.2, §8.3 · Contracts: Derivative, DerivativeMap · Acceptance: A25, A26, A27, A28, A29, A30.

Detailed clauses:

- Creating a local derivative emits a registration event or proposal containing parent identity, child identity, Project, and reason for an authorized parent-scope custodian. Processing is transactional, retryable, and idempotent.

### ALM-091 — The authorized parent owner adds the backlink/map entry; the project does not write global metadata

Spec: §8.1, §8.2, §8.3 · Contracts: Derivative, DerivativeMap · Acceptance: A25, A26, A27, A28, A29, A30.

Detailed clauses:

- The authorized parent owner adds child reference, project and concise variant description to the parent's derivative graph without modifying the semantic parent rule. These entries live in a separate, paginated derivative map so the parent's Primary entry stays bounded. Relationship changes require authority and their own revision tracking.

### ALM-092 — Adding knowledge about descendants changes relationships, not the parent's substantive rule

Spec: §8.1, §8.2, §8.3 · Contracts: Derivative, DerivativeMap · Acceptance: A25, A26, A27, A28, A29, A30.

### ALM-093 — Store derivation details in a separate map, outside Global Primary

Spec: §8.1, §8.2, §8.3 · Contracts: Derivative, DerivativeMap · Acceptance: A25, A26, A27, A28, A29, A30.

Detailed clauses:

- Keep project derivative and exception metadata in a separate map outside Global Primary so project variants do not enlarge or alter the parent rule's current meaning.

### ALM-094 — The parent contains only a tiny count and precise map pointer, regardless of descendant count

Spec: §8.1, §8.2, §8.3 · Contracts: Derivative, DerivativeMap · Acceptance: A25, A26, A27, A28, A29, A30.

Detailed clauses:

- Represent descendants on a global current record using a small derivative count and exact map pointer alongside normal status and history references. Omit the annotation when there are no derivatives unless an explicit zero is useful. An explicit zero is an optional display/integrity choice; project-specific details remain outside primary.
- Keep Global Primary compact as descendants accumulate by storing a small count and exact map pointer instead of inline descendant lists. Capacity thresholds and performance targets must be measured for each deployment.

### ALM-095 — With no descendants, omit the field or display zero; either is acceptable

Spec: §8.1, §8.2, §8.3 · Contracts: Derivative, DerivativeMap · Acceptance: A25, A26, A27, A28, A29, A30.

### ALM-096 — Resolve directly to the relevant parent's map entry, not a giant file requiring search

Spec: §8.1, §8.2, §8.3 · Contracts: Derivative, DerivativeMap · Acceptance: A25, A26, A27, A28, A29, A30.

Detailed clauses:

- Resolve parent map pointers directly to that parent's entry and descendant pointers directly to the relevant records. Do not require scanning an entire map file to locate a referenced item. Physical filenames may be routing hints, but stable exact resolution is authoritative.

### ALM-097 — Map entries contain compact project/type/summary/reason and exact child locations

Spec: §8.1, §8.2, §8.3 · Contracts: Derivative, DerivativeMap · Acceptance: A25, A26, A27, A28, A29, A30.

Detailed clauses:

- For each parent, store its ID, derivative total, and compact descendant entries with child identity, Project, relationship type, summary, reason or condition, and exact record location. Specify snapshot watermarks, registration state, and count semantics.

### ALM-098 — Agents may skip precedent browsing when they already understand their local solution

Spec: §8.1, §8.2, §8.3 · Contracts: Derivative, DerivativeMap · Acceptance: A25, A26, A27, A28, A29, A30.

Detailed clauses:

- Permit an agent with an adequately understood parent and supported local solution to create its local derivative without reading existing derivatives from other projects. Skipping other examples does not waive the earlier requirement to understand the inherited rule before changing it.

### ALM-099 — Derivatives include exception, specialization, extension, restriction, override, and combination

Spec: §8.1, §8.2, §8.3 · Contracts: Derivative, DerivativeMap · Acceptance: A25, A26, A27, A28, A29, A30.

Detailed clauses:

- Use derivative as the general relationship term and support exception, specialization, extension, restriction, override, and combination, preserving how a local rule changes its ancestors. A derivative can weaken, strengthen, specialize, extend, combine, partially override, or exempt.

### ALM-100 — Promotion to global requires user/global-owner authority and supporting evidence

Spec: §8.3 · Contracts: Proposal, Revision · Acceptance: A31.

Detailed clauses:

- Useful local rules may be proposed for Global scope with preserved origin and exact links. The Global owner creates the Global record; the Project owner chooses any local adoption or retirement.
- Global promotion retains original scope, originating record, promotion evidence, source identities, and historical Project records. Links connect the records; do not delete or rename the original into another owner's scope.
- Allow useful project discoveries and repeated cross-project experience to produce a global adoption proposal evaluated by the human owner or authorized governor. No particular number of projects is a minimum quorum, automatic trigger or required threshold.

### ALM-101 — Promotion retains project origin and its history; do not destroy the originating record

Spec: §8.3 · Contracts: Proposal, Revision · Acceptance: A31.

Detailed clauses:

- Allow local adoption of a promoted Global rule where appropriate. Preserve the originating local record and its history and promotion links. An exactly redundant active override may be retired through local authority. Promotion alone neither forces local adoption nor retires a needed exception.

### ALM-102 — Promotion respects reciprocal ownership: project adoption and retirement remain project-owned

Preserve project sovereignty during promotion: the global owner commits global adoption; only the project owner or human may adopt, retire, redirect, or annotate its local origin.

Spec: §8.3 · Contracts: Proposal, Revision · Acceptance: A31.

### ALM-103 — Global promotion records first origin, other contributing variants, date, reason, and source decision

Spec: §8.3 · Contracts: Proposal, Revision · Acceptance: A31.

Detailed clauses:

- A promoted Global rule retains its origin, other informing rules, promotion time, rationale, and exact source and promotion-decision references. Record the authorizing actor separately from origin and timestamps.

### ALM-104 — Avoid divergent authoritative duplicates; preserve distinct local variants and canonical global meaning

Keep one canonical identity for equivalent meaning within the same scope and valid time, while retaining justified distinct local derivatives and their origin links.

Spec: §8.3 · Contracts: Proposal, Revision · Acceptance: A31.

Detailed clauses:

- Maintain one canonical identity for each authoritative rule. Permit duplicate representations only as caches so that separate copies do not silently become conflicting authorities. A genuinely different scoped derivative receives its own identity and genealogy; a cache does not.

### ALM-105 — Repeated identical meaning should not automatically create duplicate memories

Spec: §4.4 · Contracts: MemoryRecord · Acceptance: A09.

Detailed clauses:

- Duplicate source statements should not automatically create duplicate memory records. Preserve source events while deduplicating/coalescing equivalent derived memories. Raw repeated source events remain preserved. Equivalence requires compatible meaning, scope, time, and authority.

### ALM-106 — Detect actual decisions even when they are never phrased as 'I decide'

Spec: §5.1, §5.2, §5.3 · Contracts: Candidate, Revision · Acceptance: A35, A36, A37, A38, A39, A41, A42, A43.

Detailed clauses:

- Extract actual decisions during conversations by default, including decisions not phrased explicitly as decisions, with manual confirmation where appropriate. Retrospective auditing supplements live capture; it is not the sole extraction mechanism.
- Detect decisions and revisions from meaning and conversational context, including implicit decisions; distinguish tentative ideas from established decisions. Run a live memory compiler alongside reasoning. Keywords alone are insufficient; classification algorithm and model are implementation choices.

### ALM-107 — Extract during the conversation by default, rather than depending on later manual reconstruction

Spec: §5.1, §5.2, §5.3 · Contracts: Candidate, Revision · Acceptance: A35, A36, A37, A38, A39, A41, A42, A43.

### ALM-108 — Combine automatic capture with manual confirmation where appropriate

Spec: §5.1, §5.2, §5.3 · Contracts: Candidate, Revision · Acceptance: A35, A36, A37, A38, A39, A41, A42, A43.

### ALM-109 — A Memory Observer inspects every turn beside the main reasoner

Spec: §5.1, §5.2, §5.3 · Contracts: Candidate, Revision · Acceptance: A35, A36, A37, A38, A39, A41, A42, A43.

Detailed clauses:

- Inspect every captured user and assistant turn for preservation-worthy creation, modification, rejection, clarification, confirmation, contradiction, deferral, and contextualization. Treat the observer as event detection rather than generic summarization. The observer may be a separate background process or a logical stage.

### ALM-110 — Detect creation, modification, rejection, clarification, confirmation, contradiction, deferral, and contextualization, not general summaries

Spec: §5.1, §5.2, §5.3 · Contracts: Candidate, Revision · Acceptance: A35, A36, A37, A38, A39, A41, A42, A43.

### ALM-111 — Candidate events include transition, scope, subject, proposed meaning, confidence, and exact source

Spec: §5.1, §5.2, §5.3 · Contracts: Candidate, Revision · Acceptance: A35, A36, A37, A38, A39, A41, A42, A43.

Detailed clauses:

- Candidate memory events include event type, scope, subject, proposed content, confidence with its basis, and precise source-message ranges. Identifier formats are implementation choices.

### ALM-112 — Assistant suggestions stay unconfirmed unless adopted; they are not automatically user decisions

Assistant-originated suggestions remain unconfirmed until authorized adoption evidence or an explicit scoped policy activates them. Record the original author separately from the adopting authority; silence alone is not consent.

Spec: §5.1, §5.2, §5.3 · Contracts: Candidate, Revision · Acceptance: A35, A36, A37, A38, A39, A41, A42, A43.

Detailed clauses:

- An authorized, explicit scoped bulk-adoption instruction may accept otherwise unconfirmed suggestions in an imported conversation. Record the adoption event separately from original authorship; do not infer retrospective approval from silence. Adoption applies to proposed decisions; illustrative examples, compliments, background claims, and hypothetical scenarios in an imported conversation do not become requirements merely because they appear there.
- Keep assistant-originated suggestions unconfirmed until authorized adoption evidence or an explicitly preauthorized scoped policy supports activation. Preserve original authorship separately from adopting authority; silence is not universal consent.

### ALM-113 — Clear authorized decisions may auto-commit; ambiguous suggestions remain candidates; exploratory alternatives normally stay exploratory

Spec: §5.1, §5.2, §5.3 · Contracts: Candidate, Revision · Acceptance: A35, A36, A37, A38, A39, A41, A42, A43.

Detailed clauses:

- Allow clear authorized directives and confirmations to commit without repeated save prompts. Evaluate confidence from conversational behavior and evidence rather than a fixed phrase list. Confidence does not itself grant scope authority.
- Keep medium-confidence or ambiguous proposals as candidates or provisional memories until context or confirmation resolves them. Declare any numerical thresholds in policy rather than treating a sample value as a default.
- Treat low-confidence exploratory questions and alternatives as exploration rather than automatically creating active decisions. Raw conversation capture still preserves exploratory material.

### ALM-114 — Avoid interrupting the user to approve every obvious memory event

Spec: §5.1, §5.2, §5.3 · Contracts: Candidate, Revision · Acceptance: A35, A36, A37, A38, A39, A41, A42, A43.

### ALM-115 — Maintain a live decision buffer while tentative ideas develop over several turns

Spec: §5.3 · Contracts: Candidate · Acceptance: A39.

Detailed clauses:

- Maintain confirmed or active decisions, candidate memories, and ignored extraction dispositions. Open candidates persist across turns with stable identity, proposed decision, evidence, and current state. Ignored classification must never discard the captured source event.
- Allow candidates to remain open across a configurable conversational window with no fixed universal turn count. Preserve an archived disposition when they leave the active buffer so they remain recoverable and reviewable.

### ALM-116 — Later reasoning may implicitly confirm an earlier candidate; retain the supporting context

Spec: §5.2, §5.3 · Contracts: Candidate · Acceptance: A38.

Detailed clauses:

- Allow later reasoning that clearly relies on a proposal to support candidate confirmation, preserving the relevant evidence and inference basis. Reliance is evidence of adoption; mere lack of a reply is not the default runtime rule.

### ALM-117 — Distinguish an explored option from the eventual decision; do not store both as equally authoritative

Spec: §5.1, §5.2, §5.3 · Contracts: Candidate, Revision · Acceptance: A35, A36, A37, A38, A39, A41, A42, A43.

Detailed clauses:

- Distinguish earlier exploration from the decision later reached; do not retain both as equally active authority when the conversation clearly resolves the alternative. Preserve historical exploration and its sources rather than deleting it.

### ALM-118 — Recognize the full state-transition vocabulary: rules, decisions, requirements, constraints, preferences, assumptions, questions, ideas, exceptions, facts, priority/feature/scope changes

Recognize RULE_CREATED, RULE_CHANGED, RULE_REJECTED, RULE_CONFIRMED; DECISION_MADE, DECISION_REVISED, DECISION_REVERSED; REQUIREMENT_ADDED, REQUIREMENT_REMOVED, REQUIREMENT_PRIORITY_CHANGED; CONSTRAINT_DISCOVERED; PREFERENCE_ESTABLISHED; ASSUMPTION_CREATED, ASSUMPTION_INVALIDATED; QUESTION_OPENED, QUESTION_RESOLVED; IDEA_PROPOSED, IDEA_REJECTED, IDEA_DEFERRED; EXCEPTION_CREATED; FACT_CORRECTED; FEATURE_DEFERRED; and PROJECT_SCOPE_CHANGED. Equivalent versioned tags must preserve every transition meaning.

Spec: §5.1, §5.3 · Contracts: Candidate · Acceptance: A10, A35.

Detailed clauses:

- Recognize RULE_CREATED, RULE_CHANGED, RULE_REJECTED, DECISION_MADE, DECISION_REVISED, DECISION_REVERSED, REQUIREMENT_ADDED, REQUIREMENT_REMOVED, CONSTRAINT_DISCOVERED, PREFERENCE_ESTABLISHED, ASSUMPTION_CREATED, ASSUMPTION_INVALIDATED, QUESTION_OPENED, QUESTION_RESOLVED, IDEA_PROPOSED, IDEA_REJECTED, IDEA_DEFERRED, EXCEPTION_CREATED, and FACT_CORRECTED. Equivalent versioned schema names are acceptable only if every transition class remains represented.

### ALM-119 — One utterance can have several event tags without producing duplicate memories

Spec: §5.1, §5.3 · Contracts: Candidate · Acceptance: A10, A35.

Detailed clauses:

- Recognize multiple semantic effects from one statement, including REQUIREMENT_PRIORITY_CHANGED, FEATURE_DEFERRED, and PROJECT_SCOPE_CHANGED, without creating duplicate canonical memories for each tag.

### ALM-120 — The exact source pointer is created with the committed memory, not guessed later

Spec: §4.1, §5.3, §9 · Contracts: Source, Commit · Acceptance: A43, A46.

Detailed clauses:

- Persist original conversation promptly and create exact source-window and reasoning/history references when a memory is committed. Source must exist before its referencing authoritative commit; later source reconstruction is not an acceptable default.

### ALM-121 — Capture original conversation immediately so extraction cannot destroy or outrun its source

Spec: §4.1, §5.3, §9 · Contracts: Source, Commit · Acceptance: A43, A46.

### ALM-122 — Retain whole-conversation retrospective auditing alongside live extraction to catch later-revealed significance

Spec: §5.3 · Contracts: AuditRun · Acceptance: A41.

Detailed clauses:

- Retain full-conversation retrospective auditing alongside the live compiler to recover missed state changes and earlier significance revealed by later context. Audit cadence is configurable; conversation completion and user-request triggers are engineering choices.

### ALM-123 — Later auditing can add earlier origins and confirmations without replacing existing provenance

Spec: §5.3 · Contracts: AuditRun · Acceptance: A41.

Detailed clauses:

- Audit already preserved raw conversations to enrich provenance and indexing; never replace original material with audit output or destructive summaries. Derived corrections remain append-only authorized changes.
- Allow retrospective review to add an earlier originating source and later confirmation evidence to an existing record while preserving prior provenance and history. Origin and confirmation evidence have distinct roles even when they support one current rule.

### ALM-124 — If observer and auditor miss something, the source still exists for later mining

Spec: §5.3 · Contracts: Source · Acceptance: A42.

Detailed clauses:

- Combine live capture, retrospective audit, and immutable original logs so missed extraction means unindexed information rather than permanently lost information. No extractor can guarantee perfect detection; retained source permits later repair.

### ALM-125 — Users can inspect decisions so far, revisions, deferrals, rejections, and open candidates with confidence

Spec: §11, §5.3 · Contracts: conversation.state, candidate.review · Acceptance: A40.

Detailed clauses:

- Allow users to inspect actual durable memory state at any time, including active, revised, deferred, rejected, and open-candidate counts. State queries must not depend on the conversational model reconstructing its current working context.

### ALM-126 — Users can confirm/reject selected candidates and return unresolved ideas to exploration without constant interruptions

Spec: §11, §5.3 · Contracts: conversation.state, candidate.review · Acceptance: A40.

Detailed clauses:

- Display addressable candidate records and confidence. Let users confirm, reject, defer, or return selected candidates to exploration while preserving authority and state-transition evidence. Candidate counts and confidence thresholds are policy-specific.

### ALM-127 — Persist durable project state outside the context window so compaction does not erase early decisions

Spec: §3.3, §5.3, §6.1 · Contracts: Candidate, AuditRun · Acceptance: A41, A43.

Detailed clauses:

- Compile durable project state incrementally outside the model's reasoning context so context eviction does not determine what decisions survive. Incremental compilation does not weaken every-turn observation or immediate source capture; batching latency is an implementation choice.

### ALM-128 — Components are capture/log, main reasoner, observer, candidate buffer, compiler, stored state, and retrospective auditor; the storage graph is independent of the processing pipeline

Spec: §3.3, §5.3, §6.1 · Contracts: Candidate, AuditRun · Acceptance: A41, A43.

Detailed clauses:

- Feed captured conversation events to a reasoner and memory observer. Classify preservation events as confirmed, candidate, or ignored; compile rules, decisions, and state into layered memory backed by immutable logs; audit for misses. Capture raw source before classification and keep observer writes within authorized commit paths.

### ALM-129 — Maintain a versioned build specification and distinguish required behavior from demonstrated runtime behavior

Maintain a versioned build specification for the complete memory lifecycle and conformance tests. Report runtime capabilities only when an implementation demonstrates them.

Spec: §1, §13 · Acceptance: A53.

Detailed clauses:

- Specify storage format, traversal rules, Primary/Secondary movement, revision mechanics, and retrieval API; support a small local prototype without requiring particular hardware. A prototype milestone does not demonstrate the complete system.
- Maintain a versioned specification covering layers, Primary and Secondary memory, scopes, inheritance, derivatives, provenance, retrieval, permissions, proposals, promotion, contradictions, immutable logs, and the conversation-to-rule lifecycle. Distinguish specified behavior from behavior demonstrated by a runtime.

### ALM-130 — The overall goal is reconstructing what was and was not decided, why, how it changed, who had authority, and exact evidence without loading the lifetime archive

Spec: §1, §12 · Acceptance: A51.

Detailed clauses:

- At a future date, recover what was decided and undecided, why, how it changed, who had authority, and exact original evidence for each stage without placing the entire archive in active context. Reliable informed decisions take precedence over minimizing the number of memory operations.

### ALM-131 — Provide categorized memory views for decisions, facts, preferences, open questions, current state, important events, people, ideas, architecture, experiments, and hardware without copying all supporting evidence into those views

Spec: §3.1, §3.2, §4.3 · Contracts: MemoryRecord, WorkingSet · Acceptance: A70.

Detailed clauses:

- Support categorized views for decisions, facts, preferences, open questions, current state, important events, people, ideas, architecture, experiments, and hardware as relevant to each scope. Views may be indexes rather than directories and must not bundle private project data.
- Memory maps expose current approach and state, reasons through decision or test IDs, contextual limits with evidence links, and open problems with relevant discussion or test links. Particular project technologies and machine facts are not defaults.

### ALM-132 — Define and enforce a memory constitution covering what becomes memory, revision versus new identity, Primary/Secondary movement, contradictions, and required evidence review

Spec: §5, §6, §7 · Acceptance: A71.

Detailed clauses:

- Define and enforce a memory constitution for when to create memory, how to promote and demote it, how to handle contradictions, when to revise versus create a new identity, and when an answer requires descent to original evidence. Operational thresholds must be declared by the implementation or configuration.
