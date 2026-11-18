---
status: "accepted"
date: 2026-11-18
decision-makers: maintainer (Kemal)
consulted: Claude Code (proposed the defaults during the extraction)
---

# Generic defaults differ from the private origin in four places

## Context and Problem Statement

The gate began as a private script inside the author's own agent setup. Publishing it meant removing everything tied to that setup. Which defaults should change, and which behaviour must stay?

## Considered Options

* Keep every private default and only translate the text.
* Generalise the setup-specific defaults and document each change.

## Decision Outcome

Chosen option: "Generalise and document", with these changes from the private version:

| Private version | This project | Why |
|---|---|---|
| Notes directory named with a Turkish word (`.arama`) | `.prior-art`, configurable with `LOOK_BEFORE_NOTES_DIR` | A neutral English name; the old name works by setting the variable |
| Exempt substring `memory` (a notes folder of the author's agent setup) | removed from the defaults | It would exempt unrelated paths such as `src/memory_pool.py` for other users; the `.claude` entry already covers the agent folders |
| Project root marker `.git` or a `PROJECT.md` file (the author's own convention) | `.git` only, configurable with `LOOK_BEFORE_ROOT_MARKERS` | `PROJECT.md` is not a general convention |
| Message in Turkish, hard-coded constants | English message, constants configurable by environment variables | Audience and reuse |

Everything else is kept: threshold (30 lines, inclusive), window (6 hours), extension list, the remaining exempt substrings, fail-open behaviour, the `Write` and `apply_patch` parsing.

### Consequences

* Good, because nothing in the defaults refers to the author's machine or conventions.
* Bad, because a user of the private version who upgrades must set `LOOK_BEFORE_NOTES_DIR=.arama` to keep old notes working. The only such user is the author.

### Confirmation

Defaults are asserted in `tests/test_look_before_gate.py` (`TestBlocks`, `TestAllows.test_default_exempt_list`, `TestConfiguration`).

## More Information

Related: [0001](0001-fail-open.md), [0002](0002-note-file-as-proof.md).
