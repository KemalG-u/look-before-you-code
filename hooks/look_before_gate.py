# SPDX-License-Identifier: Apache-2.0
"""look-before-you-code gate: a PreToolUse hook for AI coding agents.

Blocks (exit code 2) a tool call ONLY when all of these are true:
  * the call would create a NEW file (the path does not exist yet),
  * the file has a code extension,
  * the new content has at least MIN_LINES lines,
  * the path is not on the exempt list,
  * a project root is found, and
  * the project's notes directory has no Markdown note modified within the time window.

In every other case, and on every error, the gate exits 0 (fail-open): a broken gate must
never stop the user's work. This is a deliberate decision, see docs/decisions/0001-fail-open.md.

Supported input (JSON on stdin):
  Claude Code Write : tool_input.file_path + tool_input.content
  Codex apply_patch : tool_name "apply_patch", tool_input.command (patch text; "*** Add File: path"
                      sections, content lines start with "+"). tool_input.patch / input are read too.

Configuration (environment variables; every invalid value falls back to its default):
  LOOK_BEFORE_MIN_LINES     minimum line count of a new file that needs a note (default 30)
  LOOK_BEFORE_NOTES_DIR     notes directory, relative to the project root (default ".prior-art");
                            an absolute path is used as is
  LOOK_BEFORE_WINDOW_HOURS  how recent a note must be, in hours (default 6)
  LOOK_BEFORE_EXTENSIONS    comma-separated code extensions
                            (default ".py,.js,.ts,.tsx,.mjs,.go,.rs,.svelte,.ps1,.sh")
  LOOK_BEFORE_EXEMPT        comma-separated, case-insensitive substrings; a path containing any of
                            them is never blocked (default "test,fixture,.claude,.agents");
                            setting it REPLACES the default list
  LOOK_BEFORE_ROOT_MARKERS  comma-separated names that mark a project root (default ".git")
  LOOK_BEFORE_DISABLE       set to 1 to switch the gate off
"""
import json
import os
import re
import sys
import time

DEFAULT_EXTENSIONS = ".py,.js,.ts,.tsx,.mjs,.go,.rs,.svelte,.ps1,.sh"
DEFAULT_EXEMPT = "test,fixture,.claude,.agents"
DEFAULT_MARKERS = ".git"
DEFAULT_NOTES_DIR = ".prior-art"
DEFAULT_MIN_LINES = 30
DEFAULT_WINDOW_HOURS = 6.0

MESSAGE = (
    "Look before you code: this call would create a new code file of {min_lines}+ lines. "
    "Run the look-before-you-code skill (search for an existing solution first) and save "
    "a note to {notes}/<topic>.md, then retry. The note must have been written within the "
    "last {hours:g} hours."
)


def _env_int(name, default):
    try:
        value = int(os.environ.get(name, "").strip())
        return value if value >= 1 else default
    except ValueError:
        return default


def _env_float(name, default):
    try:
        value = float(os.environ.get(name, "").strip())
        return value if value > 0 else default
    except ValueError:
        return default


def _env_list(name, default, lower=True):
    raw = os.environ.get(name)
    if raw is None or not raw.strip():
        raw = default
    items = [x.strip() for x in raw.split(",") if x.strip()]
    return [x.lower() for x in items] if lower else items


def load_config():
    """Read the configuration from the environment. Never raises."""
    notes = os.environ.get("LOOK_BEFORE_NOTES_DIR", "").strip() or DEFAULT_NOTES_DIR
    return {
        "disabled": os.environ.get("LOOK_BEFORE_DISABLE", "").strip() == "1",
        "min_lines": _env_int("LOOK_BEFORE_MIN_LINES", DEFAULT_MIN_LINES),
        "window_sec": _env_float("LOOK_BEFORE_WINDOW_HOURS", DEFAULT_WINDOW_HOURS) * 3600,
        "notes_dir": notes,
        "extensions": set(_env_list("LOOK_BEFORE_EXTENSIONS", DEFAULT_EXTENSIONS)),
        "exempt": _env_list("LOOK_BEFORE_EXEMPT", DEFAULT_EXEMPT),
        "markers": _env_list("LOOK_BEFORE_ROOT_MARKERS", DEFAULT_MARKERS, lower=False),
    }


def count_lines(text):
    if not text:
        return 0
    return text.count("\n") + (0 if text.endswith("\n") else 1)


def absolute(path, cwd):
    # The path is used exactly as received: no "~" or "$VAR" expansion. The gate does not assume
    # the host expands them (the README "Limits" section says what follows if a host does);
    # a gate that expanded them could check a different file than the one written.
    if not os.path.isabs(path):
        path = os.path.join(cwd or os.getcwd(), path)
    return os.path.normpath(path)


def find_root(start, markers):
    d = start
    while d and not os.path.isdir(d):
        parent = os.path.dirname(d)
        if parent == d:
            return None
        d = parent
    while True:
        if any(os.path.exists(os.path.join(d, m)) for m in markers):
            return d
        parent = os.path.dirname(d)
        if parent == d:
            return None
        d = parent


def notes_path(root, notes_dir):
    return os.path.join(root, notes_dir)


def has_fresh_note(root, cfg):
    limit = time.time() - cfg["window_sec"]
    notes = notes_path(root, cfg["notes_dir"])
    if not os.path.isdir(notes):
        return False
    for dirpath, _dirs, files in os.walk(notes):
        for name in files:
            if name.lower().endswith(".md"):
                try:
                    if os.path.getmtime(os.path.join(dirpath, name)) >= limit:
                        return True
                except OSError:
                    pass
    return False


def candidates(data):
    """List of (path, content) for possible new files (existence is checked later)."""
    tool_input = data.get("tool_input")
    if not isinstance(tool_input, dict):
        return []
    result = []
    name = str(data.get("tool_name") or "").rsplit(".", 1)[-1].lower()
    path = tool_input.get("file_path") or tool_input.get("path")
    content = tool_input.get("content")
    if isinstance(path, str) and isinstance(content, str) and name in ("write", "write_file", ""):
        result.append((path, content))
        return result
    patch = tool_input.get("command") or tool_input.get("patch") or tool_input.get("input")
    if name == "apply_patch" or (isinstance(patch, str) and "*** Add File:" in patch):
        if isinstance(patch, str):
            cur_path, body = None, []
            for line in patch.splitlines():
                m = re.match(r"^\*\*\* Add File: (.+?)\s*$", line)
                if m:
                    if cur_path is not None:
                        result.append((cur_path, "\n".join(body) + "\n"))
                    cur_path, body = m.group(1), []
                elif line.startswith("*** "):
                    if cur_path is not None:
                        result.append((cur_path, "\n".join(body) + "\n"))
                    cur_path, body = None, []
                elif cur_path is not None:
                    body.append(line[1:] if line.startswith("+") else line)
            if cur_path is not None:
                result.append((cur_path, "\n".join(body) + ("\n" if body else "")))
    return result


def blocked_root(data, cfg):
    """Return the project root (forward slashes) if the call must be blocked, else None."""
    cwd = data.get("cwd") if isinstance(data.get("cwd"), str) else os.getcwd()
    for path, content in candidates(data):
        p = absolute(path, cwd)
        if os.path.exists(p):
            continue
        if os.path.splitext(p)[1].lower() not in cfg["extensions"]:
            continue
        if count_lines(content) < cfg["min_lines"]:
            continue
        lowered = p.replace("\\", "/").lower()
        if any(x in lowered for x in cfg["exempt"]):
            continue
        root = find_root(os.path.dirname(p), cfg["markers"]) or find_root(cwd, cfg["markers"])
        if not root:
            continue
        if has_fresh_note(root, cfg):
            continue
        return root.replace("\\", "/")
    return None


def main():
    try:
        cfg = load_config()
        if cfg["disabled"]:
            return 0
        data = json.loads(sys.stdin.buffer.read().decode("utf-8", "replace"))
        if not isinstance(data, dict):
            return 0
        root = blocked_root(data, cfg)
        if root:
            notes = notes_path(root, cfg["notes_dir"]).replace("\\", "/")
            text = MESSAGE.format(
                min_lines=cfg["min_lines"], notes=notes, hours=cfg["window_sec"] / 3600
            )
            sys.stderr.buffer.write((text + "\n").encode("utf-8"))
            sys.stderr.flush()
            return 2
    except Exception:
        return 0
    return 0


if __name__ == "__main__":
    try:
        code = main()
    except BaseException:
        code = 0
    sys.exit(code)
