# SPDX-License-Identifier: Apache-2.0
"""Run the gate against a throw-away project: blocked, then allowed after a note is written."""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

GATE = Path(__file__).resolve().parent.parent / "hooks" / "look_before_gate.py"


def call_gate(project, content):
    payload = {"tool_name": "Write", "cwd": str(project),
               "tool_input": {"file_path": str(project / "client.py"), "content": content}}
    run = subprocess.run([sys.executable, "-I", "-S", str(GATE)], input=json.dumps(payload).encode(),
                         capture_output=True,
                         env={**os.environ, "LOOK_BEFORE_EXEMPT": "none"})  # temp dirs may match defaults
    return run.returncode, run.stderr.decode().strip()


with tempfile.TemporaryDirectory() as tmp:
    project = Path(tmp) / "demo-project"
    (project / ".git").mkdir(parents=True)
    code = "x = 1\n" * 40
    print("no note yet  ->", call_gate(project, code))
    (project / ".prior-art").mkdir()
    (project / ".prior-art" / "http-client.md").write_text("# searched, decided to write\n")
    print("note written ->", call_gate(project, code))
