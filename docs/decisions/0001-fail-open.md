---
status: "accepted"
date: 2026-11-18
decision-makers: maintainer (Kemal)
consulted: Claude Code (drafted the options and wrote this record; the decision itself was the maintainer's)
---

# The gate fails open: any error lets the tool call through

## Context and Problem Statement

The gate runs before every `Write` / `apply_patch` call of an AI coding agent. It reads JSON from stdin, walks parent directories and scans a notes folder. Things can go wrong: unexpected payload shapes after an agent update, permissions, odd paths, a wrongly set environment variable. What should the gate do when it cannot decide?

## Decision Drivers

* The gate is a reminder to search first, not a security control; the cost of a wrongly blocked call is a stalled agent and an annoyed user.
* Agent hosts change hook payloads over time; a gate that blocks on a payload it does not understand would break work after an unrelated update.
* The author's original private version already stated, in a code comment, that fail-open was chosen deliberately so that it would not stop the maintainer's work.

## Considered Options

* Fail-open: exit code 0 on every error and on every input the gate does not understand.
* Fail-closed: exit code 2 whenever the gate cannot decide.
* Configurable (`LOOK_BEFORE_STRICT=1` for fail-closed).

## Decision Outcome

Chosen option: "Fail-open", because a speed bump that can brick the agent will be uninstalled, and then it protects nothing.

### Consequences

* Good, because a broken or outdated gate never blocks work.
* Bad, because a wrongly wired gate does nothing, silently. The README tells users to run `examples/demo.py` and one real blocked write after installing.
* Bad, because input the gate does not parse (for example a new patch format) is let through.

### Confirmation

`tests/test_look_before_gate.py`, class `TestFailOpen`: garbage stdin, wrong field types, and an exception inside the blocking logic all end in exit code 0. Invalid environment values fall back to defaults (`TestConfiguration`).

## Pros and Cons of the Options

### Fail-open

* Good, because it cannot stall the user's work.
* Bad, because failures are invisible.

### Fail-closed

* Good, because misconfiguration is noticed at once.
* Bad, because every host update or odd input can block all new code files; the gate is not a security boundary, so this cost buys little.

### Configurable strict mode

* Good, because teams that want enforcement could have it.
* Bad, because it adds a setting and a failure mode that nobody asked for yet. Not chosen for 0.1.0; it can be added later without breaking anyone.

## More Information

Hook documentation for both hosts says exit code 2 blocks the call ([Claude Code](https://code.claude.com/docs/en/hooks), [Codex](https://learn.chatgpt.com/docs/hooks)); exit code 0 with no output lets it proceed. Related: [0002](0002-note-file-as-proof.md). The options were proposed by an AI tool; the choice follows the maintainer's original comment in the private version.
