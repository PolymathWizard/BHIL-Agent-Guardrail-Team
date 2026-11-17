#!/usr/bin/env python3
"""Three-level kill switch with a hash-chained log. Reference implementation.

  python3 tools/killswitch.py status
  python3 tools/killswitch.py pause <agent-id> --by sentinel --reason "..."
  python3 tools/killswitch.py halt --by sentinel --reason "..."
  python3 tools/killswitch.py stop --by human:barry --reason "..."
  python3 tools/killswitch.py resume --by human:barry --reason "..."

Who may do what comes from data/team.json. Agents can pause and halt; only a
person can run a global stop or resume. State lives in .guardrails/ (ignored by
git). A real deployment enforces this at the policy service and tool gateways;
this file shows the rules and gives a harness something to read before each call.

Stdlib only. Exit codes: 0 done, 1 refused, 2 usage error.
"""
import argparse
import hashlib
import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ACTIONS = {"pause": "pause_agent", "halt": "halt_swarm", "stop": "global_stop"}


def load_team():
    with open(os.path.join(ROOT, "data", "team.json"), encoding="utf-8") as fh:
        return json.load(fh)


def state_dir(base=None):
    path = base or os.environ.get("GUARDRAILS_STATE_DIR") or os.path.join(ROOT, ".guardrails")
    os.makedirs(path, exist_ok=True)
    return path


def read_state(base=None):
    path = os.path.join(state_dir(base), "state.json")
    if not os.path.exists(path):
        return {"paused_agents": [], "halted": False, "global_stop": False}
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def append_log(entry, base=None):
    path = os.path.join(state_dir(base), "log.jsonl")
    prev = "0" * 64
    if os.path.exists(path):
        with open(path, encoding="utf-8") as fh:
            lines = [ln for ln in fh.read().splitlines() if ln.strip()]
        if lines:
            prev = json.loads(lines[-1])["hash"]
    entry = dict(entry, prev=prev)
    entry["hash"] = hashlib.sha256(json.dumps(entry, sort_keys=True).encode("utf-8")).hexdigest()
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, sort_keys=True) + "\n")
    return entry


def verify_log(base=None):
    path = os.path.join(state_dir(base), "log.jsonl")
    if not os.path.exists(path):
        return True
    prev = "0" * 64
    with open(path, encoding="utf-8") as fh:
        for ln in fh.read().splitlines():
            if not ln.strip():
                continue
            entry = json.loads(ln)
            claimed = entry.pop("hash")
            if entry["prev"] != prev or hashlib.sha256(json.dumps(entry, sort_keys=True).encode("utf-8")).hexdigest() != claimed:
                return False
            prev = claimed
    return True


def actor_kind(by, team):
    if by.startswith("human:") and len(by) > 6:
        return "human"
    if by in [a["id"] for a in team["agents"]]:
        return by
    return None


def apply(action, by, reason, agent=None, base=None, team=None):
    """Apply one action. Returns (ok, message)."""
    team = team or load_team()
    kind = actor_kind(by, team)
    if kind is None:
        return False, f"unknown actor {by!r}; use an agent id or human:<name>"
    ks = team["kill_switch"]
    state = read_state(base)
    if action == "resume":
        allowed = ks["resume"]
    else:
        level = next(lv for lv in ks["levels"] if lv["id"] == ACTIONS[action])
        allowed = level["by"]
    if kind not in allowed:
        append_log({"ts": time.time(), "action": action, "by": by, "agent": agent, "reason": reason, "result": "refused"}, base)
        return False, f"REFUSED: {by} may not {action}; allowed: {', '.join(allowed)}"
    if action == "pause":
        if agent not in [a["id"] for a in team["agents"]]:
            return False, f"unknown agent {agent!r}"
        if agent not in state["paused_agents"]:
            state["paused_agents"].append(agent)
    elif action == "halt":
        state["halted"] = True
    elif action == "stop":
        state["halted"] = True
        state["global_stop"] = True
    elif action == "resume":
        state = {"paused_agents": [], "halted": False, "global_stop": False}
    with open(os.path.join(state_dir(base), "state.json"), "w", encoding="utf-8") as fh:
        json.dump(state, fh, indent=2)
    append_log({"ts": time.time(), "action": action, "by": by, "agent": agent, "reason": reason, "result": "applied"}, base)
    return True, f"APPLIED: {action}" + (f" {agent}" if agent else "") + f" by {by}"


def may_run(agent, base=None):
    """What a harness asks before every agent call. False means do not run it."""
    s = read_state(base)
    return not (s["global_stop"] or s["halted"] or agent in s["paused_agents"])


def main():
    ap = argparse.ArgumentParser(description="BHIL Guardrails Team kill switch")
    ap.add_argument("action", choices=["status", "pause", "halt", "stop", "resume"])
    ap.add_argument("agent", nargs="?")
    ap.add_argument("--by", default="")
    ap.add_argument("--reason", default="")
    args = ap.parse_args()
    if args.action == "status":
        print(json.dumps(read_state(), indent=2))
        print("log chain:", "intact" if verify_log() else "BROKEN")
        return 0
    if not args.by or not args.reason or (args.action == "pause" and not args.agent):
        print("usage error: --by and --reason are required; pause also needs an agent id")
        return 2
    ok, msg = apply(args.action, args.by, args.reason, args.agent)
    print(msg)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
