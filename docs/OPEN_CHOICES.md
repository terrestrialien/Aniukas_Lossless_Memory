# Implementation choices

Each implementation must choose and document the items below for its own hardware, agents and privacy needs. These choices configure the [required behavior](../BUILD_SPEC.md); they do not remove it. Record the selected values and supported setup type before claiming an implementation passes the [acceptance tests](ACCEPTANCE.md).

| Choice | Normative boundary / current treatment | Who decides / when |
| --- | --- | --- |
| Language and transport | Logical API and versioned portable format are fixed; runtime language, CLI/RPC/HTTP bindings are open | Implementer at phase 0, recording a versioned decision. |
| Physical storage | No files-first mandate. SQLite is a recommended portable transactional starting point; PostgreSQL/pgvector and object storage are accepted optional pathways | Implementer; demonstrate durability, permissions and round-trip export for each shipped backend. |
| Authentication mechanism | Actual principal identity must be outside model payloads, with enforceable storage isolation and revocation | Deployment implementer before any conformance claim. |
| Models/providers | No mandatory model/vendor/GPU/cloud account; capture/manual profile remains available | Instance operator; remote calls require explicit configuration. |
| Automatic-extraction thresholds | Clear/ambiguous/exploratory/adoption behavior fixed; numeric thresholds and held-out accuracy targets need calibration | Operator/implementer before automatic extraction release. |
| Context budgets and latency targets | One combined context limit including reserves, pinned items and temporary retrieval; overflow explicit | Calibrate per host/model, report tokenizer or conservative estimate. |
| Segmentation and map hierarchy | Start simply; stable IDs/pointers survive repartitioning; measured growth determines further hierarchy | Maintainer when measured thresholds justify it. |
| Governor delegation | Human may be sole global writer initially; additional change classes require explicit grants | Human owner. |
| User/task ownership | User profile follows recorded ownership policy; task normally uses its parent's owner identity, with an explicit exact-scope grant; workers and scope ancestry gain no automatic write rights | Human owner at setup. |
| Audit cadence | Completion and on-demand audits supported; periodic checkpoints configurable; coverage and backlog visible | Instance operator. |
| Candidate aging | Active buffer may expire; durable candidate and transition history must remain | Operator policy. |
| Ancestor updates | Pinned bases and explicit owner adoption; no silent rebase | Normative engineering rule; alternative behavior requires a versioned contract change and migration. |
| Derivative counts | Registered non-superseded derivatives by default; historical filter and snapshot watermark retained | Normative engineering default; compatible alternative filters must be explicitly named. |
| Condition language and patch syntax | Unknown conditions are explicit ambiguity; prose deltas require a complete stored local rule | Implementer selects versioned representation; no model-dependent materialization on read. |
| Restricted reads/multiple owners | Default: every authenticated agent of the single owner may read any scope as needed; stricter isolation is an optional profile with explicit read grants | Deployment owner; extra isolation tests required. |
| Erasure/encryption/remote storage | Explicit privacy extensions; captured-source retention is the default and normal compaction cannot erase evidence | Instance owner before enabling the extension. |
| Graphical explorer | Functional bidirectional navigation required; graphical polish optional | Maintainer after core correctness. |
| Supported platforms | Declare tested OS/runtime/backend combinations; no claim of identical speed or automatic installation everywhere | Release maintainer, based on observed clean-checkout tests. |

Numeric thresholds, buffer lifetime, retention and demotion schedules, and token budgets must be calibrated for the selected setup. Document why each value works on the supported machines. Assistant suggestions become authoritative only with adoption evidence or an explicitly scoped adoption policy.
