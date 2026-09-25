# What this memory system does

An AI assistant can lose track of early decisions in a long conversation. A short summary may preserve the conclusion while losing the conditions and reasons that made it sensible.

Aniukas Lossless Memory keeps the original conversations and builds a small, useful set of notes over them. Each note has a path back to its explanation and exact source.

## The desk and the archive

The assistant starts with a small desk: today's important rules, current project decisions, your relevant preferences, and unfinished work. Less relevant notes remain available elsewhere. The desk has a firm size limit so a growing archive does not automatically fill the assistant's conversation window.

Under each note is its history: what changed, why, when, and who authorized it. Under that history are the original words. Every step has a precise pointer, so the assistant does not need to guess which conversation a claim came from.

For ordinary work, it uses the note. When a decision needs explaining, it reads the history. When the history leaves uncertainty, it opens the original evidence. It can follow several related notes together and stop at different depths for each one.

Picture it as a fir tree: a narrow tip of current notes, wider layers of history below, and the complete original record at the base. The tip stays small no matter how large the tree grows.

## Changing your mind remains visible

Suppose you say, “Leave the reporting feature until after the first version.” Months later, you decide it is time to build it. The system keeps both decisions and why the timing changed. It does not turn the first statement into a permanent ban or erase the first version of the plan.

Rejected ideas also matter. If an approach failed for a particular reason, the next assistant should be able to discover that reason. If conditions have changed, it can reconsider with evidence.

## Projects can learn without rewriting each other

Each project owns its notebook. Shared rules live in a separate global notebook. Project agents can read shared rules, create justified local variations, and suggest improvements. The global rule manager can read project variations and make suggestions back. Each owner applies changes only to its own notebook; the human owner can authorize changes across them.

A shared rule carries a small pointer to a separate map of its project variations. An assistant can browse that map when useful without loading every variation into everyday memory.

## Decisions are captured while you talk

Decisions do not always sound formal. “Let's leave that until next month” can change a plan as much as “I have decided.” A live observer proposes memory changes from conversational context. Clear authorized decisions can be recorded automatically; uncertain ideas wait as candidates for clarification or review.

A retrospective audit reads the full relevant conversation later to find significance missed at the time. If both passes miss something, the captured original still exists. A human can inspect what has been recorded, correct it, and follow its evidence.

## What survives a new computer or a new AI

The notes, history, original sources, identities, and ownership rules belong to the memory system. Replacing an AI model should not reset them. A portable export and verified restore let an implementation move them to another supported system.

The hardware can change how quickly optional model-based search or extraction runs. It must not change the meaning of an exact evidence pointer or give an agent new authority.

This package tells developers what to build and includes examples they can check. It does not yet contain the complete working memory application. Its goal is recoverable, understandable memory—not a claim that an AI will always notice everything or that storage and computing power are unlimited.
