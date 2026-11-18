# look-before-you-code

A skill plus a PreToolUse gate hook that makes AI coding agents (Claude Code, Codex) search for an existing solution before they write a new module from scratch.

[![CI](https://github.com/KemalG-u/look-before-you-code/actions/workflows/ci.yml/badge.svg)](https://github.com/KemalG-u/look-before-you-code/actions/workflows/ci.yml)
**Status:** alpha · **License:** Apache-2.0

<!-- Test and coverage badges come from CI only. Never type a test count by hand. -->

## What it does

Coding agents often write a 200-line client, parser or queue from nothing while a maintained library already does the job. This project adds a small speed bump:

- The **skill** (`skills/look-before-you-code/SKILL.md`) tells the agent how to search (official SDK, package registries, GitHub, the project's own code), shortlist 2-3 candidates, decide use / adapt / write, and record that in a short note.
- The **gate** (`hooks/look_before_gate.py`) is a PreToolUse hook. It blocks a tool call that would create a **new code file of 30 or more lines** unless the project has a Markdown note in `.prior-art/` written within the last 6 hours. The message tells the agent to run the skill and write the note, then retry.
- The gate is **fail-open**: any error, odd input or missing project root lets the call through. It never stops your work because it is broken (see [decision 0001](docs/decisions/0001-fail-open.md)).

What it does not do: it does not judge the quality of the search, it does not look at edits to existing files, and it can be bypassed (see [Limits](#limits)). It is a reminder with teeth, not a security boundary.

## Install and run

Requirements: Python 3 (tested on 3.12). Dependencies: none (standard library only). The commands below use `python3`; on Windows use `python`.

Try the gate on a throw-away project:

```
python3 examples/demo.py
```

Expected output (path shortened to `<tmp>`):

```
no note yet  -> (2, 'Look before you code: this call would create a new code file of 30+ lines. Run the look-before-you-code skill (search for an existing solution first) and save a note to <tmp>/demo-project/.prior-art/<topic>.md, then retry. The note must have been written within the last 6 hours.')
note written -> (0, '')
```

### Claude Code

1. Copy `hooks/look_before_gate.py` to `.claude/hooks/` in your project (or to `~/.claude/hooks/` for all projects).
2. Merge [`examples/claude-code-settings.json`](examples/claude-code-settings.json) into `.claude/settings.json` (adjust the script path if you used `~/.claude/hooks/`).
3. Copy `skills/look-before-you-code/` to `.claude/skills/`.

The gate reads `tool_input.file_path` and `tool_input.content` of the `Write` tool, as documented in the [Claude Code hooks reference](https://code.claude.com/docs/en/hooks). Exit code 2 blocks the call and shows the stderr message to the agent.

### Codex

1. Copy `hooks/look_before_gate.py` to `.codex/hooks/` in your project.
2. Merge [`examples/codex-hooks.json`](examples/codex-hooks.json) into `.codex/hooks.json` (or `~/.codex/hooks.json`), then review and trust the hook with `/hooks` in the Codex CLI; non-managed hooks do not run before that.
3. Put the skill where your Codex version reads skills.

The hook syntax above follows the [Codex hooks documentation](https://learn.chatgpt.com/docs/hooks) (checked 2026-11-18). The gate parses `*** Add File:` sections of the `apply_patch` payload; this is covered by unit tests with synthetic payloads. It has **not** been run inside a live Codex session by the author (see [AI-USE](docs/AI-USE.md)).

## Configuration

Environment variables, read on every call. An invalid value falls back to its default.

| Variable | Default | Meaning |
|---|---|---|
| `LOOK_BEFORE_MIN_LINES` | `30` | Smallest new file (in lines) that needs a note |
| `LOOK_BEFORE_NOTES_DIR` | `.prior-art` | Notes directory, relative to the project root (an absolute path is used as is) |
| `LOOK_BEFORE_WINDOW_HOURS` | `6` | How recent a note must be |
| `LOOK_BEFORE_EXTENSIONS` | `.py,.js,.ts,.tsx,.mjs,.go,.rs,.svelte,.ps1,.sh` | Code extensions that are checked |
| `LOOK_BEFORE_EXEMPT` | `test,fixture,scratchpad,_tmp,.claude,.agents` | Case-insensitive substrings; a path containing one is never blocked. Setting it **replaces** the list |
| `LOOK_BEFORE_ROOT_MARKERS` | `.git` | File or directory names that mark a project root |
| `LOOK_BEFORE_DISABLE` | unset | `1` switches the gate off |

Set them in the environment that launches the agent, or inline in the hook command on POSIX shells:

```
LOOK_BEFORE_MIN_LINES=50 LOOK_BEFORE_NOTES_DIR=docs/research python3 -I -S .claude/hooks/look_before_gate.py
```

Decide whether `.prior-art/` is committed or ignored in your project; the gate only reads modification times.

## Limits

- **Substring exemptions are broad.** The exempt list matches anywhere in the absolute path, so a parent directory named `latest-work` matches `test`, and a temporary directory called `..._tmp...` matches `_tmp`. When a call is unexpectedly allowed, check this first (the story is in [devlog](docs/devlog/2026-11-18-exempt-substring-surprise.md)). Narrow the list with `LOOK_BEFORE_EXEMPT`.
- **Honor system.** Any fresh `.md` file in the notes directory opens the gate, whatever it contains. An agent can write a hollow note. The skill asks for sources and dates; the gate cannot check them.
- **Only `Write` and `apply_patch`.** Shell redirection or other editing tools are not seen. Add matchers for them yourself if you need to.
- **Only new files.** Overwriting or growing an existing file is never blocked.
- **Fail-open means silent failure.** If the hook is wired wrongly it does nothing and says nothing. Run `python3 examples/demo.py` and a real blocked write after installing.
- Windows paths and `apply_patch` payloads are handled, but only the unit tests and a Windows run of the author exercised them.

## Tests

```
python3 -B -m unittest discover -s tests -v
```

Current numbers (tests run, passed, failed) are generated by script into [docs/METRICS.md](docs/METRICS.md); they are not typed by hand.

## How it was built

This is a generalised extraction of a gate and a skill the author had been using privately in his own agent setup. The origin is a personal rule set on 2026-11-18: agents kept writing things from scratch when ready-made tools existed. The extraction removed everything specific to that setup, made the threshold, notes directory and exemptions configurable, added tests for the gate, and wrote the English documentation. It was written with Claude Code under the author's direction; what the human did and what the agent did, and what was not verified, are stated in [docs/AI-USE.md](docs/AI-USE.md).

- Stages and timeline: [docs/PROCESS.md](docs/PROCESS.md)
- Problems and fixes, dated and with evidence: [docs/devlog/](docs/devlog/)
- Design decisions (MADR): [docs/decisions/](docs/decisions/)
- How AI tools were used and what was verified: [docs/AI-USE.md](docs/AI-USE.md)
- Pre-release privacy and secret checks: [docs/PRIVACY-CHECK.md](docs/PRIVACY-CHECK.md)

## Contributing and security

See [CONTRIBUTING.md](CONTRIBUTING.md), [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) and [SECURITY.md](SECURITY.md). Release notes: [CHANGELOG.md](CHANGELOG.md).

## License

Apache-2.0. See [LICENSE](LICENSE) and [NOTICE](NOTICE).
