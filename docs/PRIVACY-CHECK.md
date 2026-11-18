# Privacy and secret check

What was checked before this repository was made public: which tool, which version, which commit, and how many results. Raw scanner output is **not** published. No secret value appears in this file or anywhere in the repository. Counts are copied from tool output.

Check date: 2026-11-18 · Checked tree/commit: `a1da445` (history and working tree, after the review fixes; the same scans were first run at `93e69c5` with the same result of 0 findings; the update of this file was committed afterwards and its own text was checked after that, see section 6) · Record: contemporaneous (written right after the runs)

## 1. Publication method

| Item | Value |
|---|---|
| History option | Fresh repository with its real development history (20 commits at the checked commit); no squash, no rewrite. The original private files and their earlier history are not published |
| Source repository modified? | No. The private source files were read only; their SHA-256 prefixes and modification times (2026-11-17 23:44) were recorded before and are unchanged: skill `92d9003382a9c4a0`, gate script `f39f8796bacabf65` |
| Commit identity (name, e-mail domain) in published history | Maintainer's public name; e-mail domain `users.noreply.github.com` only (GitHub noreply address, checked with `gh api user`) |
| Files excluded from export | 0. Nothing was exported: all files were written new in this repository. The owner's exclusion list was applied (no listed path was opened or copied) |

## 2. Secret scanning (full history and working tree)

| Tool | Version | Scope (commit) | Commits scanned | Findings | Real / uncertain | Placeholder / test data |
|---|---|---|---|---|---|---|
| Betterleaks (git mode, `--redact=100`, validation off) | 1.10.1 | history @ `a1da445` | 20 | 0 | 0 / 0 | 0 |
| Betterleaks (dir mode, `--redact=100`, validation off) | 1.10.1 | working tree @ `a1da445` | not applicable (tree) | 0 | 0 / 0 | 0 |
| TruffleHog (`--no-verification --no-update`, git mode) | 3.99.9 | history @ `a1da445` | 20 (86 chunks, 115,889 bytes) | 0 (0 verified, 0 unverified) | 0 / 0 | 0 |
| TruffleHog (`--no-verification --no-update`, filesystem mode) | 3.99.9 | working tree @ `a1da445` | not applicable (tree) | 0 (0 verified, 0 unverified) | 0 / 0 | 0 |

Positive control: a scratch repository in a temporary folder outside this repository, with one commit containing a randomly generated GitHub-token-shaped string. Betterleaks reported 1 finding (rule `github-pat`); TruffleHog reported 1 finding (detector `Github`, unverified). Both scanners therefore work on this machine with these flags. The control value was generated at run time and never printed or stored in this repository.
Findings handling: no findings, so nothing to classify, revoke or clean.
GitHub secret scanning, push protection and private vulnerability reporting on the public repository: enabled on 2026-11-18, when the repository was made public; read back from the GitHub API on that date (`secret_scanning` enabled, `secret_scanning_push_protection` enabled, private vulnerability reporting `enabled: true`); [SECURITY.md](../SECURITY.md) says the same. Dependabot alerts: enabled (API status 204). Dependabot security updates, secret-scanning validity checks and non-provider patterns: disabled, not part of the claim.

## 3. Personal data, local paths and agent-specific leaks

Tool: `kontrol.py` 2.0 with extra terms (the terms themselves are not listed here; the first run used 6 terms, the rerun after the review fixes used 6 other private-setup terms because the first list was not at hand, so the term check is repeated but not identical).

| Check | Count before cleanup | Count after cleanup |
|---|---|---|
| Local absolute paths (Windows and Unix user-profile paths) | 2 over the history of edits: a made-up example path in the README "Limits" section (false positive, rewritten in `7051a3f`) and a made-up user-name example in the same section added by the review fixes (false positive, rewritten in `a1da445`) | 0 |
| E-mail addresses (excluding harmless domains) | 0 | 0 |
| Personal terms | 0 | 0 |
| `*.jsonl` (raw agent or conversation logs) | 0 | 0 |
| Secret-like file names | 0 | 0 |
| Agent files with local content (`CLAUDE.md`, `AGENTS.md`, memory notes) | 0 reviewed (none exist) | 0 |
| Commit author/committer e-mail domains | `users.noreply.github.com` | `users.noreply.github.com` |
| Exclusion list of the owner applied | yes (list of 2026-11-18) | yes |

Remaining intentional occurrences: the maintainer's name and brand in the copyright line (`NOTICE`), in the AI-use statement and in the decision records; the maintainer's GitHub user name in URLs and in the noreply commit address. The name of a private notes folder (`.arama`) and of a marker file appear in decision 0003 to document what was changed; they are not paths on any machine.

## 4. Legal and naming checks

| Check | Result | Evidence / date |
|---|---|---|
| Name and trademark conflict search (search engine, GitHub, package registries) | No exact conflict: GitHub repository search for the name returned no repository named `look-before-you-code`; npm registry: not found (404); PyPI `look-before-you-code` and `look_before_you_code`: not found (404). Similar names and ideas exist and are not the same project: `look-before-you-leap` (a Claude Code skill set in `miospotdevteam/claude-control`), `before` / Before You Code (`AbudiHadi/coderv`), `preflight-agent-skill` (`R-Dilipkumar`). No trademark database was searched; `Interpretation:` low risk for a descriptive phrase, not a legal opinion | 2026-11-18; queries: GitHub `look-before-you-code in:name`, `npm view look-before-you-code`, PyPI JSON API, one web search for the phrase |
| Dependency license inventory (dependency graph / SBOM export) compatible with Apache-2.0 | None needed: the code imports only the Python standard library (`importlib`, `io`, `json`, `os`, `re`, `sys`, `time`, `pathlib`, `subprocess`, `tempfile`, `unittest`), checked by grepping the import lines. CI uses two GitHub actions pinned by SHA (`actions/checkout`, `actions/setup-python`), which are not bundled. After publication the GitHub dependency graph SBOM export (`dependency-graph/sbom`, SPDX 2.3) was read on 2026-11-18: 3 packages, namely the repository itself and the two pinned actions above, no Python package dependency; this matches the grep result | 2026-11-18 |
| Employer IP: no employer or client code or data in this project | Confirmed by the maintainer on 2026-11-18: personal project, not owned by an employer. (This is the maintainer's statement; the AI tool cannot attest it.) | 2026-11-18 |
| Encryption code (export note) | none: the project contains no cryptographic code (it reads files, parses JSON and compares time stamps) | 2026-11-18 |

## 5. Independent second reading

| Item | Value |
|---|---|
| Date | 2026-11-18 |
| Reader | Fresh-context reviewer agent (Claude Opus); an AI tool, so this is an additional adversarial read, not a human sign-off |
| Tree read | `d590fe9` (before the fixes) |
| Result | Minor fixes required; fixed in commits `75bdbce`, `d43b4a9`, `1c89264`, `383e9f1`, `0ad3dc4` |

Findings, summarised (the review text itself is not published):

1. `SECURITY.md` said secret scanning and push protection are enabled, while the repository is not on GitHub yet. Fixed at that time: it said they, and private vulnerability reporting, would be enabled when the repository is published (`75bdbce`); after publication they were enabled and the text was updated to the checked state (section 2).
2. The README and the AI-use statement said the private original had been "in daily use". The files were written on the night of 2026-11-17 and generalised on 2026-11-18. Fixed: the origin is stated with those dates (`d43b4a9`).
3. The default exempt list contained two entries that exist only on the author's machine (`scratchpad`, `_tmp`), and one test skipped itself because of it. Fixed: both removed, tests no longer skip (`1c89264`, `383e9f1`).
4. The gate expanded `~` and variables in the path, which could make it check another file than the one written; and the README did not name the two-step bypass (write a short file, then overwrite it). Fixed: expansion removed with tests; both are in the Limits section (`1c89264`, `383e9f1`).
5. Small items: a stray ignore entry for a private folder, an unspecified Codex skill location, an incomplete module list in section 4, the wording of the `Assisted-by` rule, the CHANGELOG showing type prefixes and docs commits (`383e9f1`, `0ad3dc4`).

Items that need the maintainer (not the AI tool): all maintainer confirmations recorded on 2026-11-18, in `docs/AI-USE.md` and in section 4.

## 6. Limits

`Interpretation:` Scanners can miss secrets and can flag placeholders. A clean result lowers risk; it does not prove absence. The scanners ran locally; no operating-system level network isolation was set up, but both were started with their verification and update features switched off. The positive control used one token shape; it shows the scanners work, not that every secret type is found. This file itself was written after the history scans; a Betterleaks dir-mode scan and a TruffleHog filesystem scan of the working tree run after it was written found 0 findings.
