# Glossary

Terms used in [BUILD_SPEC.md](../BUILD_SPEC.md), the [logical contracts](DATA_CONTRACTS.md), and the [portable format](REFERENCE_FORMAT.md).

| Term | Meaning |
|---|---|
| Archive / source | The original captured conversation or other evidence. Its retained bytes do not change when an interpretation changes. |
| Assertion | What someone or something stated, including whether it is a human statement, observation, document claim, or model inference. |
| Authorization | Permission for an authenticated principal to perform a particular operation in a scope. Confidence and quoted speaker labels are not authorization. |
| Auditor | A retrospective process that revisits complete captured source to find missed changes, earlier origins, or inconsistencies. Its proposals pass the usual ownership checks. |
| Candidate | A proposed state change awaiting adequate evidence or adoption. Its review history and source remain durable even if it leaves the active buffer. |
| Commit | An authorized atomic change inside its declared transaction boundary, with evidence, expected versions, recording order, and replay identity. |
| Compiler | Validates candidate events and turns authorized decisions into durable revisions or routes them into review/proposals. |
| Confidence | A qualified estimate with a basis. It neither proves a statement true nor grants write rights. |
| Conflict | Unresolved incompatible claims or rules whose competing evidence must remain visible until an authorized resolution. |
| Current record | A compact view of the selected complete revision, with identity, current meaning, status, and pointers. |
| Depth | Resolution of a read: 0 current; 1 history/reasons; 2 exact evidence; 3 reconstruction from full relevant source. |
| Deepest available | The deepest support actually retained. If a requested intermediate depth is absent, first use the nearest deeper available depth, not automatically the deepest. |
| Derivative | A local rule with explicit pinned ancestry, inherited and changed portions, reason, and evidence. It may be an exception, specialization, extension, restriction, override, or combination. |
| Derivation map | A separate, precisely addressable collection of compact references to a parent's variants. The parent's Primary entry retains only a count/pointer. |
| Effective rule | The valid applicable rule after evaluating explicit scope overrides, conditions, and pinned ancestry; unresolved ambiguity remains visible. |
| Evidence window | An exact selector into identified source bytes or mapped messages, with integrity and reverse-reference information. Context expansion is separately identified. |
| Fir tree | The design's mental picture: a small current tip above progressively deeper explanations and, at the base, the original conversations. It describes logical layers; physical storage may be any graph. |
| Governor | A human-delegated owner of global memory. It can suggest project changes but cannot edit project-owned records. User-profile authority requires the recorded grant policy. |
| Grant | A versioned assignment of operations, principal, role, and scope, including its issuance and revocation. Exported historical grants do not automatically create live credentials elsewhere. |
| History | Ordered immutable revisions and related workflow evidence. Advancing the current pointer does not edit earlier revisions. |
| Index / projection | Rebuildable derived data for locating, searching, or presenting authoritative records. Freshness is declared; lost indexes must not mean lost evidence. |
| Instance namespace | The declared identity boundary within which entity IDs are unique; moves preserve it and merges detect collisions. |
| Memory constitution | Versioned rules governing extraction, adoption, authority, lifecycle, contradiction, promotion, and sufficient evidence. |
| Negative memory | Preserved rejected alternatives and their reasons, allowing informed reconsideration rather than repeated rediscovery. |
| Observer | A live process or logical stage inspecting every captured turn for meaningful state transitions rather than merely summarizing it. |
| Outbox | Durable events committed with local changes and delivered idempotently to the appropriate scope owner, with pending/failure state visible. |
| Primary / Secondary | Availability tiers inside each scope. Primary contributes relevant concise entries to bounded context; Secondary is retrieved when needed. Moving tiers is not forgetting. |
| Promotion | Either a relevance change into Primary, or separately authorized adoption of a project idea into a global canonical rule. The second does not automatically retire the local origin. |
| Proposal | A durable request for another scope owner to consider a change; the receiving owner applies or rejects it under its own authority. |
| Provenance | The exact trail from a claim through each change and authorizer to its evidence, preserving origins and later adoption. |
| Review receipt | A record of inspected versions/evidence, rationale, gaps, and reviewer identity for a proposed consequential change. It makes review auditable, without proving comprehension. |
| Revision / snapshot | A complete immutable historical state with its predecessor, reason, evidence, and authorizing commit. A short change note alone is not a snapshot. |
| Scope | Ownership and applicability boundary: global/system, user profile, project, or task. Secondary is not a scope. |
| Sovereignty | All authorized participants may read as relevant; each agent writes only its owned scope; cross-scope changes are proposals; memory survives owner replacement. The human retains authority across scopes. |
| Stable ID | An entity's persistent identity independent of filename, folder, model, or machine. Historical references additionally pin revisions where necessary. |
| Trigger | A topic, entity, condition, dependency, date, or other relevance signal that makes a memory worth inspecting, including rare critical constraints. |
| Valid time / recorded time | When a claim applies versus when the system learned/committed it. Historical queries specify their effective time and knowledge snapshot. |
| Watermark / snapshot sequence | The committed point to which a read or projection refers. Paged/batched results cannot silently switch knowledge snapshots. |
| Working set | The actual combined selected context—applicable global/user/project/task information and temporary relevant entries—within the host/model budget and reserves. |

For exact interchange field names, use the [reference format](REFERENCE_FORMAT.md) and its schemas.
