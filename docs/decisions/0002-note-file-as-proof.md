---
status: "accepted"
date: 2026-11-18
decision-makers: maintainer (Kemal)
consulted: Claude Code (drafted the options and wrote this record)
---

# A fresh Markdown note in the project is the proof that a search was done

## Context and Problem Statement

The gate must decide whether the agent "already looked". The gate runs as a separate short-lived process, so it cannot see the agent's reasoning or earlier tool calls. What observable evidence should it require?

## Decision Drivers

* The gate must be stateless and fast, with no database or server.
* The evidence should be useful to humans too: a reviewer can read what was searched and why the decision was made.
* The evidence should live with the project, so it survives across sessions and is visible in review.

## Considered Options

* A Markdown note in a notes directory of the project, modified within a time window.
* A marker file or a counter in the user's home directory (session state).
* Parsing the agent transcript for search tool calls.
* Asking the user for confirmation on every new file.

## Decision Outcome

Chosen option: "A Markdown note in the project's notes directory, modified within the last 6 hours", because it is observable with plain file system calls, readable by humans, and needs no host-specific transcript access.

### Consequences

* Good, because the note doubles as a record of the decision (searched, candidates, decision, date).
* Good, because the gate stays a stateless script.
* Bad, because a hollow note opens the gate. The gate checks existence and freshness, not quality. This is documented in the README "Limits".
* Bad, because the window is a guess: 6 hours is the value inherited from the private version, not a measured one. `Interpretation:` long enough for one work session, short enough that last week's note does not excuse today's new module. It is configurable with `LOOK_BEFORE_WINDOW_HOURS`.

### Confirmation

`TestBlocks.test_stale_note_does_not_open_the_gate`, `TestAllows.test_note_just_inside_window`, `TestConfiguration.test_window_hours_env`.

## Pros and Cons of the Options

### Note file in the project

* Good, because observable, durable and reviewable.
* Bad, because it can be faked cheaply.

### Marker file or counter in the home directory

* Good, because simple.
* Bad, because it carries no information for humans and is shared across unrelated projects.

### Parsing the agent transcript

* Good, because it could check that real searches ran.
* Bad, because transcript formats differ per host and change; it would couple the gate to host internals and break the fail-open simplicity.

### Asking the user each time

* Good, because a human is in the loop.
* Bad, because it turns a reminder into constant friction.

## More Information

See [0001](0001-fail-open.md). The hook payloads of the agent hosts carry the pending tool call, not the history, which is why transcript parsing was not pursued.
