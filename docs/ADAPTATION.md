# Adapting Aniukas Lossless Memory

An ALM implementation is a memory component connected to an existing assistant or agent system. The normative behavior stays the same across hardware; capture adapters, storage engines, model providers, transport, and resource budgets can vary.

## Choose a declared capability profile

| Profile | Required behavior | Capability limitations |
|---|---|---|
| Capture/manual | Durable source capture/import, manual sourced decisions, scoped writes, histories, exact retrieval, portable restore | Automatic extraction may be unavailable; preserve and report its backlog. This is a partial implementation. |
| Portable automatic | Core behavior plus live observer/compiler, candidate review, audit, bounded working-set injection | One supported machine and a configured capable local or explicitly enabled remote model are sufficient. |
| Accelerated local | All portable automatic behavior plus the optional embeddings, reranking or accelerators the deployment claims | Faster or richer discovery; exact pointers and ownership do not change. |
| Service-backed | All portable automatic behavior plus multiple authenticated clients, transactional service storage and a scalable source store | Higher throughput and deployment complexity; same reference export and memory semantics. |

No particular GPU, cloud account, container runtime, vector database, operating system, or agent vendor is mandated. Finite disk/RAM and model capacity still constrain a deployment. Report what works on a named supported environment rather than promising identical performance on every machine.

The [acceptance matrix](ACCEPTANCE.md) identifies which scenarios each setup type must pass. Report required functionality not yet implemented as `not implemented`; use `not applicable` only for a documented optional feature or a scenario specific to a backend the implementation does not use.

## Make the three integration points concrete

| Integration point | Host supplies | Memory service returns or does |
|---|---|---|
| Task startup and substantial requests | Authenticated actor, assigned scope/task, current request, usable model-context budget | A bounded working set with applicable rules, task state, conflict/candidate status, provenance, and explicit overflow if needed |
| Every conversation turn/event | Stable event identity, order, available original content/bytes, trusted speaker metadata, timestamps if known | Durable capture acknowledgement before extraction; observer queue/checkpoint and capture-gap reporting |
| Proposed memory transition | Candidate or manual change, exact evidence, actual caller authorization, expected revisions, review receipt where required | Authorized atomic commit, a reviewable candidate, a cross-scope proposal, or a typed error |

An adapter must document where those hooks actually exist in its host. A prompt instruction to save memory does not prove capture. A watcher must handle file rotation, partial writes, restarts, duplicate delivery, and source edits. A proxy must distinguish a new event from replayed conversation history and preserve the source the host actually supplied.

The service must not treat a string such as `role: user` inside an imported conversation as authentication for today's writer. Archived instructions remain evidence. The current authenticated human or scope owner authorizes imports and resulting changes.

## Setup sequence for implementers

1. Follow [the implementation plan](IMPLEMENTATION_PLAN.md), starting with the versioned [reference format](REFERENCE_FORMAT.md) and explicit ownership policy.
2. Put private operational data outside the public source checkout. Configure paths at the instance boundary; exports use relative paths and stable IDs.
3. Assign the human owner, optional global governor, project owners, and any specifically delegated task owners. Workers gain no broader rights from model capability or administrative seniority.
4. Implement durable capture and exact source reads before enabling automatic extraction. Import/export must preserve original bytes and declare unavailable messages, attachments, or metadata.
5. Implement source-backed manual decisions, complete immutable revisions, permissions, atomic changes, replay, and restore. Run the corresponding acceptance scenarios before adding model-driven writes.
6. Connect an extraction model through a replaceable adapter. Validate source ranges, adoption evidence, authority, and expected revisions. Preserve ambiguous candidates for review.
7. Connect working-set injection and the procedural retrieval tools to the host. Reserve space for host instructions, current input, and response generation before allocating the combined memory budget.
8. Add the retrospective auditor and a live decision/candidate inspection interface. Both use ordinary ownership checks.
9. Measure extraction quality, capture backlog, direct lookup, deeper reconstruction, and context size. Enable optional search enrichment only when useful.

These steps describe software to implement. The included generator creates a synthetic contract fixture; running it does not install an ALM service.

## Storage choices and portability

The reference interchange format is the common boundary. A deployment may use a transactional database internally or a specified crash-safe file store. It must export the same meaning, original evidence, identities, ownership policy, and complete history. Human-readable exported JSON is not a demand that every live database update be a separate uncoordinated file write.

A local transactional database plus an immutable source directory is a practical starting profile. Validate the actual durability, journaling, source-finalization, and backup behavior. A server backend can use the same logical contracts. An index is rebuildable only when every authoritative object needed for reconstruction exists elsewhere.

For a files-first backend, publish the exact commit visibility, write ordering, flush, crash recovery, and replay protocol. A Git commit after several ordinary file writes does not make those preceding writes atomically visible to running readers.

Copying a memory directory while a writer is active is not a defined backup. Use a consistent export/snapshot, then verify hashes, references, revision state, pending jobs, and ownership policy at restore. Do not blindly reuse machine-local credentials on the destination. Multi-machine simultaneous synchronization is a separate extension, not implied by portable export.

## Models, slow hardware, and failure

Models for extraction, audit, embedding, and reranking are independently replaceable. Capabilities include context size, tokenizer, structured-output support, expected latency, and network policy. Prompts and policies must remain editable and versioned.

If a local adapter is unavailable, preserve source capture and report the durable backlog. Do not silently send private memory to a remote provider. External calls require an explicitly configured provider and data policy.

Use bounded worker queues and backpressure. Lack of disk space or a capture gap must be visible; deleting old conversations or dropping turns to appear fast violates the core guarantee. Deep investigations may page/resume across many calls instead of overflowing one model prompt.

## Replacing an agent or changing the implementation

Memory belongs to the scope. Reassign its owner with an explicit new grant generation, revoke stale write credentials, and preserve all records, candidates, proposals, sources, and history. Changing the model does not reset ownership or make its new output authoritative.

For migration, export a consistent manifest and original bytes; validate on the destination; preserve the prior backup until exact evidence, historical queries, pending work, and permissions pass. Unknown source times remain unknown. Colliding IDs or unsupported format versions require an explicit migration decision, not silent renaming or dropped data.

Record the supported OS/runtime, storage backend, model adapters, measured limits, and test results for each released implementation. Use [ACCEPTANCE.md](ACCEPTANCE.md) to report `pass`, `fail`, `not implemented`, or genuinely optional `not applicable` capabilities.
