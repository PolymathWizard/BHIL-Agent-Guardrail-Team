#!/usr/bin/env python3
"""Pre-tool-use hook: block Edit and Write calls outside an agent's write paths.

Reads the hook event as JSON on stdin and expects `tool_name` and
`tool_input.file_path`. The agent id comes from the GUARDRAILS_AGENT
environment variable (default: policy-steward). Exit 0 lets the call through;
exit 2 blocks it and prints the reason on stderr.

The event shape and the exit-code contract follow the Claude Code hooks
interface as BHIL understands it. Confirm both against the hooks documentation
for your installed version before relying on this in production.

Stdlib only.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from grant_check import ROOT, decide, load_team  # noqa: E402


def main():
    try:
        event = json.load(sys.stdin)
    except ValueError:
        print("path_guard: unreadable hook event; blocking", file=sys.stderr)
        return 2
    tool = event.get("tool_name", "")
    if tool not in ("Edit", "Write"):
        return 0
    target = (event.get("tool_input") or {}).get("file_path", "")
    rel = os.path.relpath(os.path.abspath(target), ROOT) if target else ""
    agent = os.environ.get("GUARDRAILS_AGENT", "policy-steward")
    ok, reason = decide(load_team(), agent, tool, rel)
    if ok:
        return 0
    print(f"path_guard: {reason}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
