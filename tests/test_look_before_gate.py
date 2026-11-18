# SPDX-License-Identifier: Apache-2.0
"""Tests for hooks/look_before_gate.py. Standard library only: python -m unittest discover -s tests

Every test runs the gate as a real subprocess (the way an agent host runs it), with a clean
LOOK_BEFORE_* environment and a private project marker, so the result does not depend on the
machine the tests run on.
"""
import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

GATE = Path(__file__).resolve().parent.parent / "hooks" / "look_before_gate.py"
MARKER = ".lb-test-root"


def lines(n):
    return "".join("x = %d\n" % i for i in range(n))


def run_gate(payload, env_extra=None, raw=None):
    env = {k: v for k, v in os.environ.items() if not k.startswith("LOOK_BEFORE_")}
    env["LOOK_BEFORE_ROOT_MARKERS"] = MARKER
    env["LOOK_BEFORE_EXEMPT"] = "fixture-dir"
    env.update(env_extra or {})
    stdin = raw if raw is not None else json.dumps(payload).encode("utf-8")
    proc = subprocess.run(
        [sys.executable, "-I", "-S", str(GATE)], input=stdin, env=env, capture_output=True
    )
    return proc.returncode, proc.stderr.decode("utf-8", "replace")


class GateTestCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name).resolve() / "proj"
        (self.root / "src").mkdir(parents=True)
        (self.root / MARKER).write_text("", encoding="utf-8")

    def write_payload(self, rel="src/new_module.py", n=30, cwd=None, **kw):
        return {
            "tool_name": "Write",
            "cwd": str(cwd or self.root),
            "tool_input": {"file_path": str(self.root / rel), "content": lines(n)},
            **kw,
        }

    def add_note(self, rel=".prior-art/topic.md", age_hours=0.0):
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("# note\n", encoding="utf-8")
        stamp = time.time() - age_hours * 3600
        os.utime(path, (stamp, stamp))
        return path


class TestBlocks(GateTestCase):
    def test_blocks_new_code_file_without_note(self):
        code, err = run_gate(self.write_payload())
        self.assertEqual(code, 2)
        self.assertIn("Look before you code", err)
        self.assertIn(".prior-art", err)
        self.assertIn(self.root.as_posix(), err)

    def test_threshold_is_inclusive(self):
        self.assertEqual(run_gate(self.write_payload(n=30))[0], 2)
        self.assertEqual(run_gate(self.write_payload(n=29))[0], 0)

    def test_content_without_trailing_newline_counts_last_line(self):
        payload = self.write_payload(n=29)
        payload["tool_input"]["content"] = lines(29) + "last = 1"
        self.assertEqual(run_gate(payload)[0], 2)

    def test_relative_path_uses_cwd(self):
        payload = {
            "tool_name": "Write",
            "cwd": str(self.root),
            "tool_input": {"file_path": "src/rel.py", "content": lines(40)},
        }
        self.assertEqual(run_gate(payload)[0], 2)

    def test_stale_note_does_not_open_the_gate(self):
        self.add_note(age_hours=7)
        self.assertEqual(run_gate(self.write_payload())[0], 2)

    def test_non_markdown_file_in_notes_dir_does_not_count(self):
        path = self.add_note(rel=".prior-art/topic.txt")
        self.assertTrue(path.exists())
        self.assertEqual(run_gate(self.write_payload())[0], 2)

    def test_note_outside_project_root_does_not_count(self):
        outside = self.root.parent / ".prior-art"
        outside.mkdir()
        (outside / "topic.md").write_text("# n\n", encoding="utf-8")
        self.assertEqual(run_gate(self.write_payload())[0], 2)


class TestAllows(GateTestCase):
    def test_fresh_note_opens_the_gate(self):
        self.add_note()
        self.assertEqual(run_gate(self.write_payload())[0], 0)

    def test_fresh_note_in_subfolder_counts(self):
        self.add_note(rel=".prior-art/sub/deeper/topic.md")
        self.assertEqual(run_gate(self.write_payload())[0], 0)

    def test_note_just_inside_window(self):
        self.add_note(age_hours=5.9)
        self.assertEqual(run_gate(self.write_payload())[0], 0)

    def test_existing_file_is_never_blocked(self):
        target = self.root / "src" / "old.py"
        target.write_text("print('old')\n", encoding="utf-8")
        self.assertEqual(run_gate(self.write_payload(rel="src/old.py", n=200))[0], 0)

    def test_non_code_extension_is_allowed(self):
        self.assertEqual(run_gate(self.write_payload(rel="docs/guide.md", n=200))[0], 0)
        self.assertEqual(run_gate(self.write_payload(rel="data.json", n=200))[0], 0)
        self.assertEqual(run_gate(self.write_payload(rel="Makefile", n=200))[0], 0)

    def test_extension_match_is_case_insensitive(self):
        self.assertEqual(run_gate(self.write_payload(rel="src/Upper.PY"))[0], 2)

    def test_exempt_substring_is_allowed(self):
        self.assertEqual(run_gate(self.write_payload(rel="fixture-dir/gen.py", n=100))[0], 0)
        self.assertEqual(run_gate(self.write_payload(rel="FIXTURE-DIR/gen.py", n=100))[0], 0)

    def test_default_exempt_list(self):
        defaults = ("test", "fixture", ".claude", ".agents")
        if any(word in self.root.as_posix().lower() for word in defaults):
            self.skipTest("the temporary directory path itself matches a default exempt word")
        env = {"LOOK_BEFORE_EXEMPT": ""}  # empty value falls back to the built-in list
        for rel in ("tests/test_a.py", "src/fixtures/x.py", ".claude/hooks/h.py", ".agents/s/x.py"):
            self.assertEqual(run_gate(self.write_payload(rel=rel), env)[0], 0, rel)
        self.assertEqual(run_gate(self.write_payload(rel="src/real.py"), env)[0], 2)

    def test_removed_defaults_are_no_longer_exempt(self):
        # "scratchpad" and "_tmp" were removed from the defaults (they referred to one machine).
        env = {"LOOK_BEFORE_EXEMPT": ""}
        for rel in ("scratchpad/gen.py", "src/_tmp/gen.py", "src/my_tmp_dir/gen.py"):
            self.assertEqual(run_gate(self.write_payload(rel=rel), env)[0], 2, rel)

    def test_no_project_root_is_allowed(self):
        # No marker anywhere above this path, and cwd has none either.
        other = Path(self._tmp.name).resolve() / "loose"
        other.mkdir()
        payload = {
            "tool_name": "Write",
            "cwd": str(other),
            "tool_input": {"file_path": str(other / "a.py"), "content": lines(60)},
        }
        self.assertEqual(run_gate(payload)[0], 0)

    def test_disable_switch(self):
        self.assertEqual(run_gate(self.write_payload(), {"LOOK_BEFORE_DISABLE": "1"})[0], 0)


class TestConfiguration(GateTestCase):
    def test_min_lines_env(self):
        self.assertEqual(run_gate(self.write_payload(n=40), {"LOOK_BEFORE_MIN_LINES": "50"})[0], 0)
        self.assertEqual(run_gate(self.write_payload(n=50), {"LOOK_BEFORE_MIN_LINES": "50"})[0], 2)
        self.assertEqual(run_gate(self.write_payload(n=10), {"LOOK_BEFORE_MIN_LINES": "5"})[0], 2)

    def test_invalid_min_lines_falls_back_to_default(self):
        for bad in ("abc", "0", "-3", ""):
            env = {"LOOK_BEFORE_MIN_LINES": bad}
            self.assertEqual(run_gate(self.write_payload(n=30), env)[0], 2, bad)
            self.assertEqual(run_gate(self.write_payload(n=29), env)[0], 0, bad)

    def test_notes_dir_env(self):
        env = {"LOOK_BEFORE_NOTES_DIR": "research/notes"}
        self.add_note()  # default dir note must not count now
        code, err = run_gate(self.write_payload(), env)
        self.assertEqual(code, 2)
        self.assertIn("research/notes", err)
        self.add_note(rel="research/notes/topic.md")
        self.assertEqual(run_gate(self.write_payload(), env)[0], 0)

    def test_window_hours_env(self):
        self.add_note(age_hours=2)
        self.assertEqual(run_gate(self.write_payload(), {"LOOK_BEFORE_WINDOW_HOURS": "1"})[0], 2)
        self.assertEqual(run_gate(self.write_payload(), {"LOOK_BEFORE_WINDOW_HOURS": "3"})[0], 0)

    def test_invalid_window_falls_back_to_default(self):
        self.add_note(age_hours=5)
        self.assertEqual(run_gate(self.write_payload(), {"LOOK_BEFORE_WINDOW_HOURS": "x"})[0], 0)
        self.assertEqual(run_gate(self.write_payload(), {"LOOK_BEFORE_WINDOW_HOURS": "-1"})[0], 0)

    def test_extensions_env(self):
        env = {"LOOK_BEFORE_EXTENSIONS": ".rb, .lua"}
        self.assertEqual(run_gate(self.write_payload(rel="src/a.rb"), env)[0], 2)
        self.assertEqual(run_gate(self.write_payload(rel="src/a.py"), env)[0], 0)

    def test_exempt_env_replaces_defaults(self):
        env = {"LOOK_BEFORE_EXEMPT": "generated"}
        self.assertEqual(run_gate(self.write_payload(rel="src/generated/a.py"), env)[0], 0)
        self.assertEqual(run_gate(self.write_payload(rel="tests/test_a.py"), env)[0], 2)

    def test_root_markers_env(self):
        # Without the marker the project root is unknown, so the gate lets the call through.
        env = {"LOOK_BEFORE_ROOT_MARKERS": ".other-marker"}
        self.assertEqual(run_gate(self.write_payload(), env)[0], 0)
        (self.root / ".other-marker").write_text("", encoding="utf-8")
        self.assertEqual(run_gate(self.write_payload(), env)[0], 2)


class TestPathIsNotExpanded(GateTestCase):
    """The gate checks the path exactly as written; it must not expand "~" or variables."""

    def expand_env(self):
        # If the gate expanded these, the file would land in the exempt directory.
        home = str(self.root / "fixture-dir")
        return {"HOME": home, "USERPROFILE": home, "LB_HOME": home}

    def payload_for(self, file_path):
        return {
            "tool_name": "Write",
            "cwd": str(self.root),
            "tool_input": {"file_path": file_path, "content": lines(40)},
        }

    def test_tilde_is_not_expanded(self):
        self.assertEqual(run_gate(self.payload_for("~/new.py"), self.expand_env())[0], 2)

    def test_variables_are_not_expanded(self):
        env = self.expand_env()
        self.assertEqual(run_gate(self.payload_for("$LB_HOME/new.py"), env)[0], 2)
        self.assertEqual(run_gate(self.payload_for("%LB_HOME%/new.py"), env)[0], 2)


class TestApplyPatch(GateTestCase):
    def patch_payload(self, patch, key="command"):
        return {"tool_name": "apply_patch", "cwd": str(self.root), "tool_input": {key: patch}}

    @staticmethod
    def add_file(path, n):
        body = "".join("+x = %d\n" % i for i in range(n))
        return "*** Add File: %s\n%s" % (path, body)

    def test_blocks_added_file(self):
        patch = "*** Begin Patch\n" + self.add_file("src/new.py", 35) + "*** End Patch\n"
        self.assertEqual(run_gate(self.patch_payload(patch))[0], 2)

    def test_allows_short_added_file(self):
        patch = "*** Begin Patch\n" + self.add_file("src/new.py", 5) + "*** End Patch\n"
        self.assertEqual(run_gate(self.patch_payload(patch))[0], 0)

    def test_update_file_section_is_not_a_new_file(self):
        body = "".join("+y = %d\n" % i for i in range(80))
        patch = "*** Begin Patch\n*** Update File: src/old.py\n@@\n" + body + "*** End Patch\n"
        self.assertEqual(run_gate(self.patch_payload(patch))[0], 0)

    def test_second_file_in_one_patch_is_checked(self):
        patch = (
            "*** Begin Patch\n"
            + self.add_file("src/small.py", 3)
            + self.add_file("src/big.py", 45)
            + "*** End Patch\n"
        )
        self.assertEqual(run_gate(self.patch_payload(patch))[0], 2)

    def test_fresh_note_opens_the_gate_for_patches(self):
        self.add_note()
        patch = "*** Begin Patch\n" + self.add_file("src/new.py", 35) + "*** End Patch\n"
        self.assertEqual(run_gate(self.patch_payload(patch))[0], 0)

    def test_patch_and_input_keys_are_read(self):
        patch = "*** Begin Patch\n" + self.add_file("src/new.py", 35) + "*** End Patch\n"
        self.assertEqual(run_gate(self.patch_payload(patch, key="patch"))[0], 2)
        self.assertEqual(run_gate(self.patch_payload(patch, key="input"))[0], 2)


class TestFailOpen(GateTestCase):
    def test_garbage_stdin_is_allowed(self):
        for raw in (b"", b"not json", b"\xff\xfe\x00", b"[]", b"123", b"null", b'"text"'):
            self.assertEqual(run_gate(None, raw=raw)[0], 0, raw)

    def test_wrong_field_types_are_allowed(self):
        bad_payloads = [
            {},
            {"tool_input": None},
            {"tool_input": "text"},
            {"tool_name": "Write", "tool_input": {"file_path": 5, "content": 7}},
            {"tool_name": "Write", "tool_input": {"file_path": "a.py"}},
            {"tool_name": "apply_patch", "tool_input": {"command": ["list"]}},
            {"tool_name": "Write", "cwd": 12, "tool_input": {"file_path": "a.py", "content": "x\n" * 99}},
        ]
        for payload in bad_payloads:
            self.assertEqual(run_gate(payload)[0], 0, payload)

    def test_internal_error_is_allowed(self):
        # Load the module, make the blocking logic raise, and check that main() still returns 0.
        import importlib.util

        spec = importlib.util.spec_from_file_location("look_before_gate_under_test", GATE)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        def boom(_data, _cfg):
            raise RuntimeError("simulated failure")

        module.blocked_root = boom
        original_stdin = sys.stdin
        try:
            sys.stdin = type("S", (), {"buffer": __import__("io").BytesIO(b'{"tool_input": {}}')})()
            self.assertEqual(module.main(), 0)
        finally:
            sys.stdin = original_stdin

    def test_blocked_message_goes_to_stderr_not_stdout(self):
        env = {k: v for k, v in os.environ.items() if not k.startswith("LOOK_BEFORE_")}
        env["LOOK_BEFORE_ROOT_MARKERS"] = MARKER
        env["LOOK_BEFORE_EXEMPT"] = "fixture-dir"
        proc = subprocess.run(
            [sys.executable, "-I", "-S", str(GATE)],
            input=json.dumps(self.write_payload()).encode("utf-8"),
            env=env,
            capture_output=True,
        )
        self.assertEqual(proc.returncode, 2)
        self.assertEqual(proc.stdout, b"")
        self.assertTrue(proc.stderr.strip())


if __name__ == "__main__":
    unittest.main()
