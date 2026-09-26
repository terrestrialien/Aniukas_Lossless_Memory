Aniukas Lossless Memory

Your AI should not have to forget in order to think.

Most AI memory systems solve limited context by compressing or discarding history.

ALM separates storage from attention.

Keep the history. Keep working context small. Descend into exact evidence only when needed.

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

Status: ALM is currently a specification and portable conformance contract, not a finished memory library.

Start here: Build Specification · Implementation Plan · Why ALM? · Conformance

The problem ALM-WHY-001

Suppose an AI remembers:

Do not use X.

But the original decision was:

Do not use X because library Y does not support Windows.

Six months later, Y supports Windows.

The memory was not false.

It lost the condition that made it true.

ALM preserves the path from today's conclusion back through its revisions, conditions, rationale, evidence, and original source.

Why this matters →

The idea ALM-WHY-002

Archive size and context size are different problems.

ARCHIVE                         WORKING CONTEXT

████                            ████
████████                        ████
████████████████                ████
████████████████████████        ████

History can grow without requiring the model to carry all of it at once.

Summaries and indexes help navigate memory.

They do not replace the evidence beneath them.

How bounded attention works →

Memory is not truth ALM-WHY-003

ALM does not assume something is correct because it is newer, retrieved first, semantically similar, or confidently stated by a model.

Memory can remain:

current · historical · conditional · rejected · superseded · disputed · unresolved

Sometimes the correct answer is:

We do not currently know which claim is correct.

Why memory needs epistemic state →

Search discovers. Identity governs. ALM-WHY-004

Vector search, embeddings, full-text search and other retrieval systems can help find relevant memory.

Once the memory is identified, ALM uses stable references and deterministic relationships to determine its history, evidence, authority, and current state.

Search finds the filing cabinet. Identity tells you which document governs.

Why ALM separates discovery from authority →

AI reasoning is not authorization ALM-WHY-005

A model can propose a memory change.

That does not mean it is allowed to commit one.

ALM separates reasoning from authority so retrieved text, external content, another agent, or an old conversation cannot grant itself permission to rewrite institutional memory.

Why authorization lives outside the model →

Built for persistent systems ALM-WHY-006

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

Explore temporal memory, ownership, inheritance and multi-agent governance →

Bring your own stack ALM-WHY-007

ALM is not a database, RAG framework, model, programming language, or agent framework.

An implementation might use:

Python      + SQLite
Rust        + PostgreSQL
TypeScript  + graph storage
Local LLMs  + filesystem
Cloud LLMs  + distributed storage

All can implement ALM.

The technology is replaceable. The guarantees are the architecture.

Why ALM is a specification rather than a library →

Build it

The repository contains:

BUILD_SPEC.md — normative architecture
Implementation Plan — staged build path
Data Contracts — records and transaction semantics
Requirements — traceable normative requirements
Reference Format — portable representation
Conformance — language-neutral compatibility cases

Want the reasoning behind all of this?

→ Read WHY_ALM.md

This README is an ALM demo ALM-WHY-008

This file deliberately contains only the information most visitors need.

Each ALM-WHY-* identity maps to a deeper record in WHY_ALM.md.

That document maps onward to the normative specification where appropriate.

README
bounded, current explanation
        ↓
WHY_ALM
deeper reasoning and examples
        ↓
BUILD_SPEC / requirements / contracts
normative detail

You are navigating the documentation using the same principle ALM applies to memory:

Start small. Descend when needed. Preserve the source.

See how the documentation map works →

Keep the evidence. Keep the history. Keep context bounded.

When the AI needs to know why it believes something:

let it look.
