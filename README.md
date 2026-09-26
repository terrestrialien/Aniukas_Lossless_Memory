Aniukas Lossless Memory

Your AI should not have to forget in order to think.

Most AI memory systems solve limited context by throwing information away.

Conversations are summarized. Summaries are summarized again. Decisions lose their rationale. Rejected alternatives disappear. Conditions disappear. Contradictions get resolved implicitly. Eventually the system remembers a clean version of the past that may never have existed.

That is an attention solution disguised as a storage solution.

Aniukas Lossless Memory (ALM) separates the two.

Storage can grow.

Working context stays bounded.

The original evidence remains recoverable.

---

The basic idea

An AI does not need its entire history in context.

It needs a small representation of what matters now, with deterministic paths back to why it matters.

ALM therefore separates:

CURRENT WORKING MEMORY
        ↓
CURRENT CANONICAL STATE
        ↓
IMMUTABLE REVISION HISTORY
        ↓
EXACT EVIDENCE
        ↓
ORIGINAL SOURCE

Most interactions stop near the top.

When uncertainty, contradiction, audit, or consequential change requires more context, the system can descend.

The archive may contain 10,000 conversations or 10,000,000.

That does not mean 10,000,000 conversations belong in the prompt.

Storage and attention are different problems.

ALM treats them that way.

---

Why lossless?

Consider this memory:

«Do not use X.»

That may be perfectly accurate.

But suppose the original decision was:

«Do not use X because library Y does not support Windows.»

Six months later, Y supports Windows.

The compressed memory was never false.

It simply lost the condition that made it true.

A system that retained only the conclusion may continue obeying an obsolete decision forever.

ALM preserves the chain:

current state
    ↓
decision
    ↓
revision history
    ↓
conditions
    ↓
alternatives
    ↓
rationale
    ↓
evidence
    ↓
original conversation

The old decision does not disappear.

The changed condition does not automatically create a new decision.

The system has enough evidence to recognize that reconsideration may now be appropriate.

---

Memory is not truth

ALM does not assume that something becomes true because:

- it is newer,
- an AI said it confidently,
- it appears in memory,
- it was retrieved by semantic similarity,
- it was written by an authoritative source,
- or another record contradicting it could not be found.

A memory can be:

- current,
- historical,
- disputed,
- conditional,
- rejected,
- superseded,
- proposed,
- inherited,
- locally overridden,
- or unresolved.

Contradictions do not have to disappear simply because the system wants one clean answer.

Sometimes the correct memory is:

«We do not currently know which of these claims is correct.»

---

The past is immutable. Its meaning is not.

ALM distinguishes the original record from the system's interpretation of that record.

An original conversation is evidence of what was said.

It is not automatically proof that what was said remains true.

Derived memory can evolve without rewriting its source.

SOURCE
  │
  ├── Revision 1
  │
  ├── Revision 2
  │
  └── Revision 3 ← current

Revision 3 does not erase Revision 1.

And Revision 1 can still lead back to the exact evidence that produced it.

This makes it possible to ask two very different questions:

«What applies now?»

and:

«What did the system believe applied then, using the information available at that time?»

ALM preserves both.

---

Forgetting is not the only way to stay within context

A common assumption in AI memory is:

history grows
      ↓
context grows
      ↓
compress history
      ↓
discard detail

ALM instead aims for:

history grows ───────────────────────────────►

working context
████████████████████
remains bounded

Older information can become colder without becoming nonexistent.

Summaries can exist without replacing their evidence.

Indexes can become smaller without destroying the material they index.

---

Search helps you find memory. It does not define memory.

Semantic search is useful.

ALM does not reject embeddings, vector databases, full-text search, graph search, or other discovery systems.

It rejects using approximate similarity as the final authority for questions such as:

«Which decision is currently in force?»

«Which revision superseded this one?»

«Who had authority to change this?»

«Which project owns this rule?»

«What evidence supported it?»

Once an identity is known, ALM favors deterministic traversal through stable references.

Search finds the filing cabinet.

Identity tells you which document inside it actually governs.

---

AI reasoning is not authorization

An LLM can propose a memory change.

That does not mean the LLM is allowed to perform it.

ALM separates reasoning from authority.

A model output can become a proposed event.

The memory service decides whether the actor has permission to commit that event.

This matters when persistent agents ingest:

- old conversations,
- external documents,
- web content,
- other agents' messages,
- retrieved memories,
- or potentially hostile instructions.

A sentence discovered in memory cannot grant itself permission to rewrite memory.

---

Memory for more than one agent

Persistent AI systems increasingly involve multiple agents, projects, models, tools, and humans.

ALM therefore treats memory ownership explicitly.

A project may inherit global knowledge without gaining authority to rewrite it.

A global system may inspect project state without silently changing project-owned memory.

Projects may create local variants.

Improvements may be proposed upward.

Global changes may be proposed downward.

Ownership follows scopes and authority, not whichever model happens to be running today.

This allows different agents to share institutional memory without sharing unrestricted write access.

---

Memory has time

ALM distinguishes:

Valid time
When something was actually applicable.

Recorded time
When the system learned or recorded it.

Those are not always the same.

A system may discover today that something changed three months ago.

ALM can preserve both:

«What do we now believe was true on that date?»

and

«What did the system believe was true on that date at the time?»

This allows historical reconstruction without rewriting history.

---

Consequential changes can require evidence review

For important changes, ALM can require the acting agent to descend through relevant history and evidence before committing a revision.

That review can produce an immutable receipt recording:

- what was inspected,
- which revisions were considered,
- which evidence was available,
- alternatives,
- constraints,
- consequences,
- unresolved gaps,
- and the resulting conclusion.

If the underlying memory changes before the new revision is committed, the review can become stale.

The agent must reconsider the changed evidence.

A review receipt does not prove that an AI understood what it read.

It proves what evidence was made available when the decision was made.

That distinction is deliberate.

---

What ALM is

ALM is a specification and conformance contract for durable AI memory.

It defines behavioral guarantees around:

- lossless source retention,
- bounded working context,
- immutable revisions,
- stable identity,
- evidence provenance,
- temporal reconstruction,
- explicit contradictions,
- negative memory,
- rejected and deferred alternatives,
- deterministic traversal,
- scope ownership,
- authority enforcement,
- atomic commits,
- optimistic concurrency,
- inheritance,
- proposals and overrides,
- consequential-change review,
- live observation,
- retrospective audit,
- replay,
- and portable export and restoration.

---

What ALM is not

ALM is not:

- a vector database,
- a RAG framework,
- a summarization strategy,
- a prompt template,
- a specific LLM,
- a specific database,
- a specific programming language,
- a specific agent framework,
- or a requirement to keep an entire archive in context.

You can implement ALM using PostgreSQL.

Or SQLite.

Or files.

Or a graph database.

You can use Python, Rust, Go, TypeScript, Java, or something that does not exist yet.

You can use embeddings for discovery.

You can use local models, cloud models, or both.

Those are implementation choices.

The guarantees are the architecture.

---

Build it your way

This repository deliberately contains a build specification, not one privileged implementation.

The goal is interoperability rather than technological lock-in.

An implementation should be able to say:

«We are ALM-conformant.»

and demonstrate what that means through portable contracts and conformance tests.

The repository includes:

- normative architecture,
- logical data contracts,
- numbered requirements,
- portable schemas,
- reference-format definitions,
- conformance fixtures,
- acceptance scenarios,
- implementation sequencing,
- and explicit implementation choices left open to builders.

Start here:

BUILD_SPEC.md
Normative architecture and behavioral requirements.

docs/IMPLEMENTATION_PLAN.md
Recommended implementation sequence.

docs/DATA_CONTRACTS.md
Logical records and transaction semantics.

docs/REFERENCE_FORMAT.md
Portable representation and schemas.

docs/REQUIREMENTS.md
Traceable ALM requirements.

conformance/
Portable conformance cases.

docs/OPEN_CHOICES.md
Technology decisions intentionally left to implementations.

---

A simple test for an AI memory system

Ask it:

«What is the current decision?»

Then:

«Why?»

Then:

«What did we believe before that?»

Then:

«Why did we change it?»

Then:

«What alternatives did we reject?»

Then:

«Under what conditions?»

Then:

«Who authorized the change?»

Then:

«Show me the exact evidence.»

Then:

«Show me the original conversation around that evidence.»

Then:

«Reconstruct what the system believed before the change occurred.»

If those questions eventually terminate in:

«“The summary says…”»

you do not have the past.

You have a story about the past.

---

The principle

AI systems will accumulate years of decisions, relationships, failures, corrections, exceptions, experiments, agreements, disagreements, and institutional knowledge.

We should not require them to repeatedly destroy that history merely because attention is finite.

Keep the evidence.

Keep the history.

Keep the contradictions.

Keep the reasons.

Keep context bounded.

And when the AI needs to know why it believes something:

let it look.

---

Aniukas Lossless Memory

The archive is not the context.