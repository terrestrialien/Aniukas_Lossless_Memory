# Walkthrough: a fictional neighborhood lending library

This example is entirely invented. It shows how an assistant could remember decisions for a lending library with several branches. The [original conversation](memory/logs/original.txt) has 22 dated, labeled messages. People and agents explain *why* they make a choice, consider another option, or leave a question open. The [normalized messages](memory/logs/c001.jsonl) preserve each exact statement, timestamp, speaker, and byte position in the original file.

These are generated teaching files for the [portable reference profile](../docs/REFERENCE_FORMAT.md), not output from a running memory service. The stored addresses such as `mem://` and `win://` are pointers within the example.

## Follow one decision back to the conversation

The library wants to hold a repair workshop. The first [decision revision](memory/revision/LIB-DEC-0001.r1.json) records it as a future goal: members asked for it, but the room and instructor are not yet arranged. The user then changes its timing. The [current record](memory/record/LIB-DEC-0001.json) says **deferred**, and its [second revision](memory/revision/LIB-DEC-0001.r2.json) explains that the room schedule must be confirmed first.

| Depth | Where to look | What the assistant learns |
| --- | --- | --- |
| Current | [LIB-DEC-0001](memory/record/LIB-DEC-0001.json) and the [small branch working view](memory/primary/PROJECT-LIBRARY.md) | The workshop remains planned, with no announced date. |
| History | [r2](memory/revision/LIB-DEC-0001.r2.json) followed by [r1](memory/revision/LIB-DEC-0001.r1.json) | The change was a delay caused by the missing room booking, not a cancellation. |
| Evidence | [WIN-00005](memory/evidence-window/WIN-00005.json) | The second revision cites precisely message 5, with nearby context available on request. |
| Full source | [LOG-EXAMPLE](memory/log-manifest/LOG-EXAMPLE.json), [original.txt](memory/logs/original.txt), and [c001.jsonl](memory/logs/c001.jsonl) | The complete fictional conversation and exact retained bytes are available for reconstruction. |

Message 5 is dated `2026-09-23T11:05:00Z` and says:

> Defer the repair workshop until we confirm the room schedule. Keep it in the plan; I do not want the missing room booking mistaken for a decision to cancel.

The normalized message's `original_byte_start` and `original_byte_end` point to that exact text inside `original.txt`. The preceding time and speaker label remain in the original too. The revision's `created_at` is when the memory change was recorded, while the message timestamp is when the fictional speaker said it. A later request to schedule the workshop should inspect the room condition rather than treating the old deferral as a permanent refusal.

## One shared rule, one local variation

The shared [lending request rule](memory/record/SYS-RULE-0011.json) has four revisions. Its first version used email because two volunteers could manage one inbox. The second accepts phone requests to include people without email, while requiring one shared queue to prevent double promises. The third allows branches to choose their contact method but preserves that queue. The fourth adds a pickup checklist for substitute volunteers.

Riverside's [local phone-confirmation rule](memory/record/LIB-RULE-0005.json) pins the shared rule at **SYS-RULE-0011.r3**. It allows phone confirmations for members without email and still requires the shared queue. Because r3 already lets each branch choose its contact method, this local rule is recorded as a **specialization**: Riverside's particular choice within the shared rule, not an exception to it.

The shared rule's entry in the [global working view](memory/primary/GLOBAL.md) stays one line long. Next to its current meaning it shows only its status, a revision count with a pointer to its history, and a derivative count with the exact address of its [variation map](memory/derivation-map/MAP-SYS-RULE-0011.json). An assistant that already knows what its branch needs can ignore the map; one that wants precedent follows the pointer and reads only the compact entries it needs.

The owners act in separate steps:

| Commit | Scope | Why it exists |
| --- | --- | --- |
| [TXN-000006](memory/commit/TXN-000006.json) | Riverside branch | Creates the local rule and an [outbox request](memory/outbox-event/OUTBOX-REGISTER.json) to register it; [REVIEW-0006](memory/review-receipt/REVIEW-0006.json) records the parent revision, access need, alternative, and constraint reviewed. |
| [TXN-000007](memory/commit/TXN-000007.json) | Shared-rule owner | Adds Riverside to the separate [variation map](memory/derivation-map/MAP-SYS-RULE-0011.json). The branch owner did not write this map. |
| [TXN-000008](memory/commit/TXN-000008.json) | Riverside branch | Records the registration acknowledgement without editing the first local revision. |
| [TXN-000009](memory/commit/TXN-000009.json) | Shared-rule owner | Adds the shared pickup checklist. Riverside's local rule still points to r3; this later change does not rewrite the earlier variation. |

Riverside later proposes that other branches *may* offer phone confirmations. The [proposal](memory/proposal/SUG-PROMOTION.json) is sent in [TXN-000014](memory/commit/TXN-000014.json). The shared-rule owner creates [SYS-RULE-0020](memory/record/SYS-RULE-0020.json) in [TXN-000015](memory/commit/TXN-000015.json). Only Riverside's owner decides in [TXN-000016](memory/commit/TXN-000016.json) to mark its old local entry as a historical origin. Other branches remain free to make their own decision.

A later [combined Riverside variation](memory/record/LIB-RULE-0006.json) pins two shared rules. Its [registration request](memory/outbox-event/OUTBOX-COMBINATION.json) remains pending, so the shared map must not claim that variation is already registered.

## Keep uncertainty and rejected shortcuts visible

The workshop organizer says the meeting room seats 30. An assistant reports that a booking sheet lists 20; the sheet itself is not captured here. The two [capacity](memory/record/LIB-FACT-0003.json) [claims](memory/record/LIB-FACT-0004.json) and their [unresolved conflict](memory/conflict/CONF-0001.json) remain separate. The library should check the venue before promising 30 seats; the most recent source is not automatically the correct one.

The assistant suggests skipping Riverside's shared queue to save volunteer time. The [candidate](memory/candidate/CAND-REJECTED.json) starts as a tentative idea. The user rejects it because two volunteers could promise the same item. The [rejected record](memory/record/LIB-IDEA-0001.json) keeps that reason for future work instead of deleting the suggestion.

A different assistant suggestion, a large-print weekly schedule, is explicitly adopted in the next message. The [confirmed candidate](memory/candidate/CAND-CONFIRMED.json) cites both the [suggestion](memory/evidence-window/WIN-00018.json) and the [user's reasons](memory/evidence-window/WIN-00019.json). The first [schedule revision](memory/revision/SYS-RULE-0010.r1.json) directly cited only the suggestion as revision evidence, although its adoption field pointed to the user's message. A later [audit](memory/audit-run/AUDIT-0001.json) notices that incomplete source list. The shared-rule owner accepts a [repair proposal](memory/proposal/SUG-REPAIR.json) and appends [r2](memory/revision/SYS-RULE-0010.r2.json), citing the adoption directly. The original revision is retained unchanged.

The [imported flyer preference](memory/revision/LIB-PREF-0001.r1.json) illustrates another case: a conversation mentions an old style note, but the old note itself and its date are missing. The example records an explicit evidence gap instead of manufacturing a source or date.

## Try the files

The [fixture configuration](memory/config/CONFIG-EXAMPLE.json) declares UTF-8/LF generation, snapshot sequence 21, and example per-scope **byte** limits. It is a fixture artifact; actual model-token allocation, authentication, private storage, capture hooks, and production backup behavior are specified in the [adaptation guide](../docs/ADAPTATION.md) and [data contracts](../docs/DATA_CONTRACTS.md).

After installing the development requirements from the repository root, run `python tools/check_all.py`. That checks generated bytes, source positions and hashes, links, history, scope receipts, and deliberately broken examples in the regression suite. Builders can also run the [portable conformance cases](../conformance/README.md) against implementations in other languages. A future runtime must satisfy the [acceptance scenarios](../docs/ACCEPTANCE.md) separately.
