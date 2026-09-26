Aniukas Lossless Memory

Your AI should not have to forget in order to think.

Most AI memory systems solve limited context by throwing information away.

ALM takes a different approach: keep the history losslessly, keep working context small, and let the AI descend into exact evidence only when it needs to.

Working Memory
      ↓
Current State
      ↓
Revision History
      ↓
Exact Evidence
      ↓
Original Source

ALM is an implementation-independent specification for durable, auditable memory for persistent AI and multi-agent systems.

Status: In order to preserve adaptability, ALM is currently a specification and portable conformance contract, not a finished memory library.

Start here: [Build Specification](BUILD_SPEC.md) · [Implementation Plan](docs/IMPLEMENTATION_PLAN.md) · [Why ALM?](docs/WHY_ALM.md) · [Conformance](conformance/README.md)

The problem [WHY_ALM-001](docs/WHY_ALM.md#why_alm-001--lossy-truth)

Suppose an AI remembers:

Do not use X.

But the original decision was:

Do not use X because library Y does not support Windows.

Six months later, Y supports Windows.

The memory was not false.

It lost the condition that made it true.

ALM preserves the path from today's conclusion back through its revisions, conditions, rationale, evidence, and original source.

[Why this matters →](docs/WHY_ALM.md#why_alm-001--lossy-truth)

The idea [WHY_ALM-002](docs/WHY_ALM.md#why_alm-002--storage-is-not-attention)

Archive size and context size are different problems.

ARCHIVE                         WORKING CONTEXT

████                            ████
████████                        ████
████████████████                ████
████████████████████████        ████

History can grow without requiring the model to carry all of it at once.

Summaries and indexes help navigate memory.

They do not replace the evidence beneath them.

[How bounded attention works →](docs/WHY_ALM.md#why_alm-002--storage-is-not-attention)

Memory is not truth [WHY_ALM-003](docs/WHY_ALM.md#why_alm-003--memory-is-not-truth)

ALM does not assume something is correct because it is newer, retrieved first, semantically similar, or confidently stated by a model.

Memory can remain:

current · historical · conditional · rejected · superseded · disputed · unresolved

Sometimes the correct answer is:

We do not currently know which claim is correct.

[Why memory needs epistemic state →](docs/WHY_ALM.md#why_alm-003--memory-is-not-truth)

Search discovers. Identity governs. [WHY_ALM-004](docs/WHY_ALM.md#why_alm-004--discovery-is-not-identity)

Once the memory is identified, ALM uses stable references and deterministic relationships to determine its history, evidence, authority, and current state.

Search finds the filing cabinet. Identity tells you which document governs.

[Why ALM separates discovery from authority →](docs/WHY_ALM.md#why_alm-004--discovery-is-not-identity)

AI reasoning is not authorization [WHY_ALM-005](docs/WHY_ALM.md#why_alm-005--reasoning-is-not-authorization)

A model can propose a memory change.

That does not mean it is allowed to commit one.

ALM separates reasoning from authority so retrieved text, external content, another agent, or an old conversation cannot grant itself permission to rewrite institutional memory.

[Why authorization lives outside the model →](docs/WHY_ALM.md#why_alm-005--reasoning-is-not-authorization)

Built for persistent systems [WHY_ALM-006](docs/WHY_ALM.md#why_alm-006--memory-beyond-one-agent)

ALM is intended for systems that need to remember across:

long-running conversations

changing decisions

multiple agents

multiple projects

model replacements

contradictory evidence

changing conditions

years of accumulated history

Projects can share knowledge without sharing unrestricted write authority.

Historical state can survive without controlling current state.

[Explore temporal memory, ownership, inheritance and multi-agent governance →](docs/WHY_ALM.md#why_alm-006--memory-beyond-one-agent)

Bring your own stack [WHY_ALM-007](docs/WHY_ALM.md#why_alm-007--why-a-specification)

ALM is not a database, RAG framework, model, programming language, or agent framework.

An implementation might use:

Python      + SQLite
Rust        + PostgreSQL
TypeScript  + graph storage
Local LLMs  + filesystem
Cloud LLMs  + distributed storage

All can implement ALM.

The technology is replaceable. The guarantees are the architecture.

[Why ALM is a specification rather than a library →](docs/WHY_ALM.md#why_alm-007--why-a-specification)

Build it

The repository contains:

[BUILD_SPEC.md](BUILD_SPEC.md) — normative architecture
[Implementation Plan](docs/IMPLEMENTATION_PLAN.md) — staged build path
[Data Contracts](docs/DATA_CONTRACTS.md) — records and transaction semantics
[Requirements](docs/REQUIREMENTS.md) — traceable normative requirements
[Reference Format](docs/REFERENCE_FORMAT.md) — portable representation
[Conformance](conformance/README.md) — language-neutral compatibility cases

Want the reasoning behind all of this?

→ [Read WHY_ALM.md](docs/WHY_ALM.md)

This README is in part an ALM demo [WHY_ALM-008](docs/WHY_ALM.md#why_alm-008--this-documentation-is-a-demo)

This file deliberately contains only the information most visitors need.

Each [WHY_ALM-*](docs/WHY_ALM.md) identity maps to a deeper record in [WHY_ALM.md](docs/WHY_ALM.md).

That document maps onward to the normative specification where appropriate.

README
bounded, current explanation
        ↓
[WHY_ALM.md](docs/WHY_ALM.md)
deeper reasoning and examples
        ↓
[BUILD_SPEC.md](BUILD_SPEC.md) / [Requirements](docs/REQUIREMENTS.md) / [Data Contracts](docs/DATA_CONTRACTS.md)
normative detail

You are navigating the documentation using the same principle ALM applies to memory:

Start small. Descend when needed. Preserve the source.

[See how the documentation map works →](docs/WHY_ALM.md#why_alm-008--this-documentation-is-a-demo)

Keep the evidence. Keep the history. Keep context bounded.

When the AI needs to know why it believes something:

let it look.
