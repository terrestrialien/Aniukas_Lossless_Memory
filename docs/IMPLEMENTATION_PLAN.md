# Implementation plan

This is an ordered build backlog. Phase completion does not mean the entire specification is implemented. Use [the acceptance plan](ACCEPTANCE.md) as release evidence and [the requirements checklist](REQUIREMENTS.md) to track implementation coverage.

Documenting a contract does not complete an implementation phase. Every implementation release publishes a feature matrix against `ALM-001`–`ALM-132`, its supported deployment profiles, and actual acceptance results.

## Phase 0 — contracts and deployment policy

Choose the reference language/runtime and service transport and record versioned decisions. Implement the [portable reference format](REFERENCE_FORMAT.md) and [logical data contracts](DATA_CONTRACTS.md), rather than inventing an incompatible serialization. Define the human identity, authenticated grants, global/project/task ownership, capability report, and private data locations. Select local performance objectives, model-evaluation thresholds and fixture ground truth. The human may be the only global writer initially.

Deliverables: interface contracts, private instance configuration, synthetic fixture/ground truth, schema migration policy, threat/trust boundary statement for the selected deployment, reproducible dependency setup and CI. Gate: no ambiguous scope ownership or permission bypass through direct storage access; independent invalid fixtures fail usefully. Pin dependency/runtime versions for the chosen implementation and declare supported operating systems; the specification does not require a particular language.

## Phase 1 — durable core and manual decisions

Implement append-only capture/import, stable IDs, source manifests/digests, exact windows and reverse links, canonical current records, immutable complete revision snapshots, typed records/statuses and valid/recorded-time queries, transactions, idempotency, optimistic concurrency, and scope-enforced manual commits. Provide human-readable exports, exact current/history/evidence reads, lexical and relationship traversal, nearest-depth fallback, and substantive review receipts for consequential manual changes. Source hashes operate on exact bytes; unknown historical times remain unknown while commit ordering stays deterministic.

Deliverables: runnable capture/manual profile, transcript importer and complete round-trip export/restore. Gate: A01–A10, A14–A16, A18–A20, A22–A24, A33–A34, A44–A50, A53, A55–A58, A63–A64, A67, A69, with A54/A66 when applicable as defined in [the profile matrix](ACCEPTANCE.md#applicability-by-setup-type). Do not defer provenance or permissions until after an ungoverned prototype; those are foundations.

First end-to-end demonstration: import a synthetic conversation; commit one sourced decision; retrieve current/history/evidence; revise it; reconstruct the original state; reject a foreign-scope write; restart; export/import into a fresh instance; verify identical IDs, bytes and answers. This is a vertical milestone, not completion of automatic memory.

## Phase 2 — bounded context and deterministic retrieval

Implement separate primary/secondary and categorized views, global/user/project/task routing, richer lexical and graph discovery, trigger-aware working-set assembly, promotion/demotion, one combined model-context budget, fan-out bundles, exact expansion, conflict visibility, and resumable reconstruction. Extend the Phase 1 depth and review tools to batch retrieval and full working-set use. Include temporal queries, rare conditional constraints and negative-memory retrieval. Version the explicit memory constitution governing these choices and retain that version on outcomes.

Deliverables: host retrieval tools and evidence navigation. Gate: A11–A13, A17, A21, A62, A70–A71, with regression checks for exact retrieval, permissions and review. Working-set limits must be independent of archive size, and necessary evidence cannot be silently cut off by a retrieval budget.

## Phase 3 — inheritance and reciprocal governance

Implement effective-rule resolution, revision-pinned derivatives, deterministic delta/materialized rules, separate exact-address derivative maps, idempotent outbox registration, proposal routing, durable responses, promotion genealogy, and owner-controlled adoption. Prevent cycles, ambiguous combinations, unknown-condition fall-through and silent descendant rebasing. Registration, global promotion and local adoption each require separate scope authorization; no workflow changes immutable historical snapshots.

Deliverables: cross-project precedent workflow and global/project proposal review. Gate: A25–A32, A59–A61, with regression checks for A23–A24 and A57–A58 after new write paths. Registration failures and cross-scope pending state must be observable; A65 tests their complete restore after the live pipeline is added.

## Phase 4 — live memory compiler and retrospective audit

Connect one real live-conversation host adapter and replaceable extraction adapters. Document capture coverage for user/assistant/tool turns, edits and attachments; report unavailable hooks. Inspect all captured turns, track sources/checkpoints, detect the full transition vocabulary, maintain a durable decision buffer, implement explicit/implicit adoption policies, batch human review, and publish live state/count queries. Add full-conversation audits that append provenance enrichment and propose repairs through normal ownership checks.

Deliverables: complete automatic profile with visible backlog, host integration walkthrough, confidence calibration report, and source-grounded extraction evaluations against held-out human-reviewed cases. Gate: A35–A43, A65, A68, with regression checks for permission, transactions, and source integrity. The compiler never receives implicit global write authority. Capture/manual remains useful on constrained hosts but is explicitly a reduced profile; this phase is required for the full live-memory purpose.

## Phase 5 — retrieval enrichment and long-horizon scaling

Add capability-gated embedding and reranking adapters, tunable hybrid discovery, temporal relevance, and measured segmentation. Provide PostgreSQL/pgvector and object-storage pathways where deployment needs justify shipping those adapters; a conforming portable deployment may use another backend. Evaluate 50,000+ interactions and growing derivative/record counts, including changing decisions and deep historical reconstruction.

Deliverables: adapter capability matrix, benchmark report, published limitations, and measured segmentation thresholds. Gate: A22, A49–A52. Missing optional adapters must preserve core deterministic/lexical operation. Declare any planned but unshipped enrichment capability as unimplemented. Semantic discovery, server backends and a graphical explorer remain available adaptation pathways; no baseline host must install every pathway, and UI polish must not block functional bidirectional navigation.

## Phase 6 — integration and public release

Document agency hooks, CLI/API usage, backups/recovery, owner transfer, privacy controls, schema migrations, and resource tuning. Verify the implementation with synthetic data from a clean checkout on every claimed supported operating system. Keep private histories outside the repository and include the applicable license and attribution notices in distributions.

Deliverables: user integration guide, example configuration, reproducible setup and migration commands, acceptance report, feature matrix, license, public-safe artifacts, and maintained CI. Gate: A53, A69 and A54 if erasure is implemented, plus all required earlier cases. Cross-platform fixture checks alone do not prove a service supports an operating system; publish runtime installation/recovery results separately. Optional UI polish follows working navigation and correctness.

## Dependency summary

```mermaid
flowchart LR
  P0[Contracts and policy] --> P1[Durable scoped core]
  P1 --> P2[Bounded retrieval]
  P1 --> P3[Governance and derivatives]
  P2 --> P4[Live compiler and audit]
  P3 --> P4
  P4 --> P5[Enrichment and scaling]
  P5 --> P6[Integration and release]
```

## Mechanisms this spec adds

Use complete immutable snapshots, valid/recorded-time queries, transaction envelopes, review receipts, optimistic revision checks, replay keys, source-finalization ordering, outbox delivery, projection watermarks, grant revocation, cycle checks, pinned inheritance versions, portable export, integrity/backup verification, and explicit resource failure states. The portable profile makes these mechanisms concrete enough for independent implementations to exchange data without imposing one physical backend.
