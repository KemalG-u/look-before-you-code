# AI use in look-before-you-code

This is the maintainer's own statement of how AI tools were used to build this project, what the human did, and what was verified. Raw agent transcripts (`*.jsonl`) are **not** published: they can contain private paths, personal data and secrets. This record is a curated summary; its claims point to commits, tests and files you can inspect.

Maintainer: Kemal (KarıncaAI) · Record: reconstructed on 2026-11-18 (drafted by the AI tool that did the extraction; confirmed by the maintainer on 2026-11-18) · Last reviewed at commit: reviewed up to 738b51e; this record confirmed on 2026-11-18

## Summary

All code, tests and documents in this repository were written by AI coding agents (Claude Code) working from instructions of the maintainer. The tool is itself the subject: a gate that makes AI coding agents look before they write. The original gate and skill were private tools of the maintainer's own agent setup; this repository is a generalised extraction of them. The maintainer did not review the code line by line (see "What the human did").

## Tools and models

| Tool / model (version) | Role | Which parts of the project |
|---|---|---|
| Claude Code, sub-agent on Claude Sonnet 5.5 (implementation); independent read by a fresh-context Claude Opus 5.5 agent | Did the extraction: generalised the gate, wrote the tests, the skill text, the examples and all documents; ran tests and scanners | Everything in this repository |
| Claude Code, main session (Claude Opus 5.5) | Gave the sub-agent its task, constraints and acceptance criteria on behalf of the maintainer | Task definition only; it did not write files here |
| Claude Code, session of 2026-11-17 (main session Claude Opus 5.5; sub-agent that wrote the files Claude Sonnet 5.5) | Wrote the original private gate script and skill text that this repository started from, with the maintainer's approval. Model names come from the main session's log of that night, not from files kept here | Origin of `hooks/look_before_gate.py` and `skills/look-before-you-code/SKILL.md` |
| git-cliff 2.14.2, Betterleaks 1.10.1, TruffleHog 3.99.9 | Changelog generation and secret scanning (tools, not AI) | `CHANGELOG.md`, [PRIVACY-CHECK.md](PRIVACY-CHECK.md) |

## What the human did

- Decided: the goal (publish a generalised version), the rule that created the need (agents must search before writing new modules, set on the night of 2026-11-17, when the original gate and skill were written for the maintainer's own setup; generalised for publication on 2026-11-18), that the gate fails open (the original code comment states this was a deliberate choice), the copyright holder line and the license. See [decisions/](decisions/).
- Reviewed: the maintainer did not review the code line by line. He set the rule and requirements, made the design and publishing decisions, and read the agents' reports and the independent review before approving.
- Ran and checked: the maintainer did not run the tests himself; the tests, the scans and the independent read were done by AI agents (see below). The original private gate has run live in the maintainer's own setup since the night it was written.
- Accepted or rejected: none by the maintainer directly (he rejected no line himself). The independent reviewer agent found overstated origin claims, a too-early "enabled" sentence in `SECURITY.md` and author-specific defaults; these were corrected before release (see [PRIVACY-CHECK.md](PRIVACY-CHECK.md) section 5 and commits `75bdbce`, `d43b4a9`, `1c89264`).

## What the AI did

- Read the original private gate and skill and listed what was specific to the maintainer's setup (language, a notes folder name, a project marker file, exemption entries, a name in a comment).
- Rewrote the gate with configuration by environment variables and English messages, keeping the original blocking logic ([decision 0003](decisions/0003-generic-defaults.md)).
- Wrote the unit tests, the skill text in English, the examples, the README and the other documents, and the draft of this file.
- Checked the hook syntax of Claude Code and Codex against their online documentation on 2026-11-18.
- Ran the tests, the standard-files checker, the secret scanner and the metrics script.

## What was verified, and how

| Claim | Verification | Evidence |
|---|---|---|
| The unit tests pass | Run by the AI tool with `python -B -m unittest discover -s tests` on Windows, Python 3.12; CI runs on Linux (Python 3.12) on every push | [METRICS.md](METRICS.md); CI run for commit `8742201` (workflow `CI`, job `test`): success, [run 44311432087](https://github.com/KemalG-u/look-before-you-code/actions/runs/44311432087), 2026-11-18 |
| No secrets or personal data in the tree and history | Betterleaks (with a positive control), TruffleHog, and a script for local paths and e-mail addresses | [PRIVACY-CHECK.md](PRIVACY-CHECK.md) |
| Blocking, allowing, fail-open and configuration behave as documented | Unit tests run the gate as a subprocess | `tests/test_look_before_gate.py` |
| README demo works | `python examples/demo.py` run by the AI tool | [PROCESS.md](PROCESS.md) "Verification" |

## What was not verified

- The gate has **not** been run inside a live Codex session, and the Codex hook file was not loaded by Codex. Only the documented syntax and synthetic `apply_patch` payloads in unit tests back it.
- The Claude Code hook example was written from the documentation; the extracting agent did not install the public copy as a hook and trigger a real blocked write with it. (The private original was written only on the night of 2026-11-17, one day before this extraction, so it has no long record of use; whatever use it has seen is not evidence for this copy.)
- Behaviour on macOS and on Python versions other than 3.12 was not tested.
- Whether the thresholds (30 lines, 6 hours) are good values was not measured; they are inherited.
- The AI-written code was reviewed by the AI tool that wrote it and then by one independent fresh-context AI reviewer (recorded in [PRIVACY-CHECK.md](PRIVACY-CHECK.md) section 5). No human read it line by line.

## Authorship in commits

AI involvement is marked with an `Assisted-by: Claude Code` trailer in commits ([convention from the LLVM policy](https://llvm.org/docs/AIToolPolicy.html)). The model is not named in the trailer; it is named in the table above. `Signed-off-by` appears only for the human maintainer; AI tools never sign off ([Linux kernel guidance](https://docs.kernel.org/process/coding-assistants.html)). The history in this repository is the real development history of the extraction (several commits), not a squash; the earlier private history of the original is not published.

## Copyright note

Copyright rests on human creative contribution. The maintainer contributed: the idea and the rule behind it, the decision to publish, the design requirement that the gate fail open, the choice of license and copyright line, and selection and approval of the result. Confirmed by the maintainer on 2026-11-18: his contribution is the idea and rule, the requirements, and the design and publishing decisions; the code and the text were produced by AI, and nothing here is claimed as human-written. `Interpretation:` Purely machine-generated passages may not be protected; this project does not claim otherwise.

## Limits of this record

`Interpretation:` The share of AI-written code is not measured; by the statement above it is all of it. Readers cannot verify the tool and model list independently because the raw transcripts are not published. This document is not a quality guarantee; the tests and the code are the evidence.
