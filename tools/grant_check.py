#!/usr/bin/env python3
"""Answer one question: may this agent do this thing? Default deny.

  python3 tools/grant_check.py code-reviewer read        -> ALLOW
  python3 tools/grant_check.py code-reviewer merge       -> DENY
  python3 tools/grant_check.py red-team Bash             -> ALLOW (sandbox: no-egress)
  python3 tools/grant_check.py policy-steward Write --path policies/tools/roles.yaml

The second argument may be a capability (read, propose, open_pr, run_sandbox,
delegate, pause_halt, clear, merge, resume), an abstract grant (repo.read) or a
Claude Code tool name (Read, Bash). Unknown agents and unknown things are denied.

Stdlib only. Exit 0 allow, 1 deny, 2 usage error.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_team():
    with open(os.path.join(ROOT, "data", "team.json"), encoding="utf-8") as fh:
        return json.load(fh)


def decide(team, agent_id, thing, path=None):
    """Return (allowed, reason)."""
    agent = next((a for a in team["agents"] if a["id"] == agent_id), None)
    if agent is None:
        return False, f"unknown agent {agent_id!r}: denied by default"
    if thing in team["human_only"]:
        return False, f"{thing} is a people-only decision"
    held = set(agent["capabilities"]) | set(agent["grant"]) | set(agent["claude_tools"])
    if thing not in held:
        return False, f"{thing} is not in {agent_id}'s grant: denied by default"
    if thing in ("Edit", "Write") or path:
        allowed = agent.get("write_paths", [])
        norm = os.path.normpath(path or "").replace(os.sep, "/")
        if not path or norm.startswith("..") or os.path.isabs(norm) or not any(norm.startswith(p) for p in allowed):
            return False, f"path {path!r} is outside {agent_id}'s write paths {allowed}"
    note = ""
    if thing == "Bash":
        note = f" (sandbox: {agent['sandbox']})" if agent.get("sandbox") else f" (scope: {agent.get('bash_scope')})"
    return True, f"{thing} is in {agent_id}'s grant{note}"


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    path = None
    if "--path" in sys.argv:
        idx = sys.argv.index("--path")
        if idx + 1 >= len(sys.argv):
            print("usage error: --path needs a value")
            return 2
        path = sys.argv[idx + 1]
        args = [a for a in args if a != path]
    if len(args) != 2:
        print(__doc__)
        return 2
    ok, reason = decide(load_team(), args[0], args[1], path)
    print(("ALLOW: " if ok else "DENY: ") + reason)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
