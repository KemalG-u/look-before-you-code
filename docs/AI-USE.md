# AI use in look-before-you-code

This is the maintainer's own statement of how AI tools were used to build this project, what the human did, and what was verified. Raw agent transcripts (`*.jsonl`) are **not** published: they can contain private paths, personal data and secrets. This record is a curated summary; its claims point to commits, tests and files you can inspect.

Maintainer: Kemal (KarıncaAI) · Record: reconstructed on 2026-11-18 (drafted by the AI tool that did the extraction; the maintainer has to confirm it, see the open items below) · Last reviewed at commit: KEMAL-VERIFY (to be filled when the maintainer reviews)

## Summary

All code, tests and documents in this repository were written by AI coding agents (Claude Code) working from instructions of the maintainer. The tool is itself the subject: a gate that makes AI coding agents look before they write. The original gate and skill were private tools of the maintainer's own agent setup; this repository is a generalised extraction of them. Review by the maintainer: KEMAL-VERIFY (state what was read line by line and what was skimmed).

## Tools and models

| Tool / model (version) | Role | Which parts of the project |
|---|---|---|
| Claude Code, sub-agent on Claude Sonnet 5.5 | Did the extraction: generalised the gate, wrote the tests, the skill text, the examples and all documents; ran tests and scanners | Everything in this repository |
| Claude Code, main session (model: KEMAL-VERIFY) | Gave the sub-agent its task, constraints and acceptance criteria on behalf of the maintainer | Task definition only; it did not write files here |
| Claude Code (session and model: KEMAL-VERIFY) | Wrote the original private gate script and skill text that this repository started from. The author of the original is stated by the maintainer, not established here | Origin of `hooks/look_before_gate.py` and `skills/look-before-you-code/SKILL.md` |
| git-cliff 2.14.2, Betterleaks 1.10.1, TruffleHog 3.99.9 | Changelog generation and secret scanning (tools, not AI) | `CHANGELOG.md`, [PRIVACY-CHECK.md](PRIVACY-CHECK.md) |

## What the human did

- Decided: the goal (publish a generalised version), the rule that created the need (agents must search before writing new modules, set on 2026-11-18), that the gate fails open (the original code comment states this was a deliberate choice), the copyright holder line and the license. See [decisions/](decisions/).
- Reviewed: KEMAL-VERIFY (what the maintainer actually read before publishing).
- Ran and checked: KEMAL-VERIFY (whether the maintainer ran the tests and installed the hook himself). The tests were run by the AI tool; see below.
- Accepted or rejected: KEMAL-VERIFY (examples of AI output the maintainer rejected or changed, with devlog links, or "none").

## What the AI did

- Read the original private gate and skill and listed what was specific to the maintainer's setup (language, a notes folder name, a project marker file, an exemption entry, a name in a comment).
- Rewrote the gate with configuration by environment variables and English messages, keeping the original blocking logic ([decision 0003](decisions/0003-generic-defaults.md)).
- Wrote the unit tests, the skill text in English, the examples, the README and the other documents, and the draft of this file.
- Checked the hook syntax of Claude Code and Codex against their online documentation on 2026-11-18.
- Ran the tests, the standard-files checker, the secret scanner and the metrics script.

## What was verified, and how

| Claim | Verification | Evidence |
|---|---|---|
| The unit tests pass | Run by the AI tool with `python -B -m unittest discover -s tests` on Windows, Python 3.12; CI to run on Linux after publication | [METRICS.md](METRICS.md); CI run: not yet (repository not published) |
| No secrets or personal data in the tree and history | Betterleaks (with a positive control), TruffleHog, and a script for local paths and e-mail addresses | [PRIVACY-CHECK.md](PRIVACY-CHECK.md) |
| Blocking, allowing, fail-open and configuration behave as documented | Unit tests run the gate as a subprocess | `tests/test_look_before_gate.py` |
| README demo works | `python examples/demo.py` run by the AI tool | [PROCESS.md](PROCESS.md) "Verification" |

## What was not verified

- The gate has **not** been run inside a live Codex session, and the Codex hook file was not loaded by Codex. Only the documented syntax and synthetic `apply_patch` payloads in unit tests back it.
- The Claude Code hook example was written from the documentation; the extracting agent did not install the public copy as a hook and trigger a real blocked write with it. (The maintainer's private original is in daily use; that is not evidence for this copy.)
- Behaviour on macOS and on Python versions other than 3.12 was not tested.
- Whether the thresholds (30 lines, 6 hours) are good values was not measured; they are inherited.
- The AI-written code was reviewed by the AI tool that wrote it and by no second AI reviewer so far. An independent second reading is planned before release and will be recorded in [PRIVACY-CHECK.md](PRIVACY-CHECK.md) section 5.

## Authorship in commits

AI involvement is marked with an `Assisted-by: Claude Code` trailer in commits ([convention from the LLVM policy](https://llvm.org/docs/AIToolPolicy.html)). The model is not named in the trailer; it is named in the table above. `Signed-off-by` appears only for the human maintainer; AI tools never sign off ([Linux kernel guidance](https://docs.kernel.org/process/coding-assistants.html)). The history in this repository is the real development history of the extraction (several commits), not a squash; the earlier private history of the original is not published.

## Copyright note

Copyright rests on human creative contribution. The maintainer contributed: the idea and the rule behind it, the decision to publish, the design requirement that the gate fail open, the choice of license and copyright line, and selection and approval of the result (KEMAL-VERIFY: confirm and add anything that was hand-written). `Interpretation:` Purely machine-generated passages may not be protected; this project does not claim otherwise.

## Limits of this record

`Interpretation:` The share of AI-written code is not measured; by the statement above it is all of it. Readers cannot verify the tool and model list independently because the raw transcripts are not published. This document is not a quality guarantee; the tests and the code are the evidence.
