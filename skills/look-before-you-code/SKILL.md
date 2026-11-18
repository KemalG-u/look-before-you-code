---
name: look-before-you-code
description: "Use BEFORE writing a new integration, authentication/OAuth flow, SDK wrapper, protocol implementation, parser, queue/orchestrator, UI component, or any new module longer than about 30 lines: search for an existing, maintained solution first, then write a short note. Do not use for small fixes in an existing file, tests, or documentation."
---

# Look before you code

Goal: do not write from scratch what a maintained solution already provides. Before creating a new code file of roughly 30+ lines, search, compare, decide, and leave a short note. If the companion gate hook is installed, it blocks the new file until a fresh note exists (see the repository README).

## 1. State the need

One sentence: what is needed, which language or runtime, which constraints.

## 2. Search in parallel

In the same turn, independently:

- The official SDK and documentation for the service or protocol.
- Package registries (PyPI, npm, crates.io, pkg.go.dev, and so on).
- GitHub: `gh search repos "<topic>" --sort updated` and `gh search code "<signature>"`.
- Skill and MCP directories, if your agent uses them.
- Local first: the project's own code (`rg "<name>"`) and the dependencies it already has. Do not rewrite what is already there.

## 3. Shortlist

For 2-3 candidates record: latest release date, maintenance (last commit, open issues), license, security (known advisories, permission scope). Code or skills from outside that would enter your toolchain deserve a proper review before you adopt them.

## 4. Decide

Use / adapt / write. One line of reasoning.

## Output

Write `<project root>/.prior-art/<topic>.md` with: what was searched for, the candidates (source and date), the decision, and today's date. The project root is the first parent directory that contains `.git`. Writing the note opens the gate. (The notes directory, the freshness window and the line threshold are configurable; see the README.)

## Cautions

- Do not bloat dependencies: do not add a heavy package for one small function.
- Do not invent package names. Verify a name against the registry (`npm view`, `pip index versions`, `gh repo view`) before writing it down or installing it.
- Pin versions (lock file or an exact version).
- A search result is not permission: installing, paying or publishing needs its own approval.
