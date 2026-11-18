---
status: "accepted"
date: 2026-11-18
decision-makers: maintainer (Kemal)
consulted: Claude Code (proposed the defaults during the extraction)
---

# Generic defaults differ from the private origin in six places

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
| Exempt substrings `scratchpad` and `_tmp` (names of temporary folders on the author's machine) | removed from the defaults (changed before 0.1.0, after an independent review) | They exist only on one machine, and `_tmp` silently exempted every file under such a temporary directory (see the [devlog](../devlog/2026-11-18-exempt-substring-surprise.md)). Anyone who wants them sets `LOOK_BEFORE_EXEMPT`. The remaining defaults, `test,fixture,.claude,.agents`, are general: `.claude` and `.agents` are the configuration folders of Claude Code and Codex |
| `~` and `$VAR` in the path were expanded before the check | no expansion (changed before 0.1.0, after an independent review) | The gate must check the path the `Write` tool will really use; expanding could make it look at another file |
| Project root marker `.git` or a `PROJECT.md` file (the author's own convention) | `.git` only, configurable with `LOOK_BEFORE_ROOT_MARKERS` | `PROJECT.md` is not a general convention |
| Message in Turkish, hard-coded constants | English message, constants configurable by environment variables | Audience and reuse |

Everything else is kept: threshold (30 lines, inclusive), window (6 hours), extension list, the other exempt substrings (`test`, `fixture`, `.claude`, `.agents`), fail-open behaviour, the `Write` and `apply_patch` parsing.

### Consequences

* Good, because nothing in the defaults refers to the author's machine or conventions.
* Bad, because a user of the private version who upgrades must set `LOOK_BEFORE_NOTES_DIR=.arama` to keep old notes working. The only such user is the author.

### Confirmation

Defaults are asserted in `tests/test_look_before_gate.py` (`TestBlocks`, `TestAllows.test_default_exempt_list`, `TestAllows.test_removed_defaults_are_no_longer_exempt`, `TestPathIsNotExpanded`, `TestConfiguration`).

## More Information

Related: [0001](0001-fail-open.md), [0002](0002-note-file-as-proof.md).
