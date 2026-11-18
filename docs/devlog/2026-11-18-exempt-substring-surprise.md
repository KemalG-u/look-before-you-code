# The exempt list matched the temporary directory and silently allowed everything

Date: 2026-11-18 · Record: reconstructed on 2026-11-18 (written the same day from the test runs and the demo run; no separate contemporaneous note)

## Problem

Three symptoms appeared within minutes while the extraction was being tested on one machine:

1. A first run of the unit tests had `test_blocked_message_goes_to_stderr_not_stdout` fail with `0 != 2`: the gate allowed a call that should have been blocked.
2. `examples/demo.py` printed `(0, '')` for the "no note yet" case, where `(2, ...)` was expected.
3. `test_default_exempt_list` was skipped by its own guard because the temporary directory path matched a default exempt word.

## Diagnosis

The exempt list is a list of substrings matched against the whole absolute, lower-cased path (this behaviour was inherited from the private version and kept on purpose, see [decision 0003](../decisions/0003-generic-defaults.md)). On the author's machine the system temporary directory contains `_tmp`, which is one of the default exempt words, so every file created under it was exempt. The gate behaved as designed; the tests and the demo made a wrong assumption about where a temporary directory lives.

## Attempts that failed

The first test file did not set the exempt list for the stdout/stderr test, so only that test failed; the other tests already passed an explicit `LOOK_BEFORE_EXEMPT`. Setting it in that test fixed it.

## Resolution

- Tests and the demo pass an explicit `LOOK_BEFORE_EXEMPT` so they do not depend on the temporary directory name.
- `test_default_exempt_list` skips itself when the temporary path matches a default word. To check that it really passes, the suite was run once with `TMP`/`TEMP` pointing to a directory without such words: 35 tests ran, no skip, OK.
- The README "Limits" section now says the substring match is broad and tells users to check it first when a call is unexpectedly allowed.
- The matching rule itself was not changed. `Interpretation:` Matching whole path components would be stricter and less surprising; it was left out of 0.1.0 to keep the behaviour of the origin and is a candidate change.

## Update: fixed in 0.1.0

An independent review pointed out that the default list should not contain names from one machine. `scratchpad` and `_tmp` were removed from the default exempt list before the first release (see [decision 0003](../decisions/0003-generic-defaults.md)), so a temporary directory is no longer exempt by default. `test_default_exempt_list` now runs on every machine instead of skipping itself here; the full suite is 38 tests with no skip. The substring matching rule itself is unchanged.

## Evidence

- Commit: `9ac1c1f` (tests with explicit exempt list and the skip guard), `376f841` (demo with explicit exempt list)
- Test: `tests/test_look_before_gate.py::TestAllows::test_default_exempt_list`, `TestFailOpen::test_blocked_message_goes_to_stderr_not_stdout`
- Related decision: [0003-generic-defaults](../decisions/0003-generic-defaults.md)
