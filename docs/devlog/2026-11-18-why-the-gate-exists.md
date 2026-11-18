# Why a gate: advice alone did not stop agents from writing from scratch

Date: 2026-11-18 · Record: reconstructed on 2026-11-18 (from the maintainer's own statement of the origin and from the extraction work; no earlier written note exists in this repository)

## Problem

On the night of 2026-11-17 (the private files carry the creation time 23:44 +0300) the maintainer (Kemal) set a standing rule in the maintainer's own agent setup and had the gate and skill written for it; they were generalised for publication on 2026-11-18. The rule: "look first" before writing a new module. The maintainer's reason, in the maintainer's words as relayed for this write-up: the maintainer's coding agents were writing things from scratch even though ready-made tools already existed. `unverified`: this origin is the maintainer's account. There is no commit, ticket or log in this repository that shows the incidents, and no count of them was kept.

## Diagnosis

`Interpretation:` A rule that exists only as advice (a skill description or an instruction file) is optional for the agent: it can skip it when it feels sure. What was missing was something outside the model's own judgement that makes the search visible before the file is written. A PreToolUse hook sees the pending `Write` call before it happens, so it can ask for evidence. The evidence has to be observable from a separate process, which led to the note-file design ([decision 0002](../decisions/0002-note-file-as-proof.md)).

## Attempts that failed

No failed attempts are recorded for the origin. The private version was already a skill plus a gate; this repository does not contain the earlier history.

## Resolution

Two parts that work together: a skill that describes how to search and what to write down (`skills/look-before-you-code/SKILL.md`), and a gate that blocks new code files of 30+ lines until a fresh note exists (`hooks/look_before_gate.py`). The gate fails open ([decision 0001](../decisions/0001-fail-open.md)) so a defect in it can never stop work.

One observation from the extraction itself, `unverified` because it left no artifact in the repository: while the new gate file was being written, the author's private gate (still active in that session) blocked the very first write of the public gate's source, because it was a new code file above the threshold and no search note existed yet. A short note was written, then the write went through.

## Evidence

- Commit: `702767e` (the gate), `65e2862` (the skill)
- Test: `tests/test_look_before_gate.py::TestBlocks::test_blocks_new_code_file_without_note`, `TestAllows::test_fresh_note_opens_the_gate`
- Related decision: [0001-fail-open](../decisions/0001-fail-open.md), [0002-note-file-as-proof](../decisions/0002-note-file-as-proof.md)
