# Security Policy

## Supported versions

| Version | Supported |
|---|---|
| 0.1.x | yes |
| older | no |

## Reporting a vulnerability

Please do **not** open a public issue for a security problem.

Report it privately with GitHub's private vulnerability reporting: open the repository's **Security** tab and choose **Report a vulnerability** (https://github.com/KemalG-u/look-before-you-code/security/advisories/new). The repository does not exist on GitHub yet; private vulnerability reporting will be enabled when the repository is published, and until then this link does not work.

Include: affected version, a description, steps to reproduce, and the impact you see. Never include real secrets or personal data in a report; describe where they appear instead.

## What to expect

This is a one-person project maintained on a best-effort basis. The maintainer aims to send an initial response within **14 days** of a report (the threshold the OpenSSF Best Practices "passing" criteria use). A fix date is not promised; the maintainer will tell you what is planned.

## Scope

In scope: the gate hook (`hooks/look_before_gate.py`), for example a way to make it execute unintended code, write files, or crash the host agent. Out of scope: the gate being bypassable by design (it only sees `Write` and `apply_patch` calls, trusts any fresh note, and fails open; see the README "Limits" section), and problems in Claude Code, Codex or other agent hosts themselves.

## Repository hygiene

The publication of this repository was checked for committed secrets and personal data; the checks and their result counts are in [docs/PRIVACY-CHECK.md](docs/PRIVACY-CHECK.md). Secret scanning and push protection will be enabled when the repository is published. If you find a secret or personal data that was missed, report it through the private channel above.
