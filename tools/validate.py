#!/usr/bin/env python3
"""Check the team's structural invariants against data/team.json and data/threats.json.

These are the rules the design depends on. A change to the canonical data that
breaks one of them fails the quality gate. Stdlib only.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WRITE_TOOLS = {"Edit", "Write", "NotebookEdit"}
SIDE_EFFECT_TOOLS = WRITE_TOOLS | {"Bash", "WebSearch", "WebFetch", "Read", "Grep", "Glob"}
TIERS = {"VERIFIED", "CORROBORATED", "STATED", "UNCORROBORATED", "INFERENCE"}


def check(team, threats):
    """Return a list of violation strings; empty means every invariant holds."""
    v = []
    agents = team["agents"]
    ids = [a["id"] for a in agents]
    if len(set(ids)) != len(ids):
        v.append("agent ids are not unique")
    if sorted(a["num"] for a in agents) != list(range(1, len(agents) + 1)):
        v.append("agent numbers are not 1..N without gaps")
    orch = [a for a in agents if a["role"] == "orchestrator"]
    if len(orch) != 1:
        v.append("there must be exactly one orchestrator")
    for a in agents:
        caps, tools = set(a["capabilities"]), set(a["claude_tools"])
        unknown = caps - set(team["capabilities"])
        if unknown:
            v.append(f"{a['id']}: unknown capabilities {sorted(unknown)}")
        held = caps & set(team["human_only"])
        if held:
            v.append(f"{a['id']}: holds people-only capabilities {sorted(held)}")
        if not a.get("hard_limit") or not a.get("prompt"):
            v.append(f"{a['id']}: missing hard_limit or prompt")
        if a["role"] == "orchestrator":
            if caps != {"delegate"}:
                v.append(f"{a['id']}: the orchestrator may hold only the delegate capability")
            if tools & SIDE_EFFECT_TOOLS:
                v.append(f"{a['id']}: the orchestrator holds non-delegation tools {sorted(tools & SIDE_EFFECT_TOOLS)}")
        else:
            if "delegate" in caps or "Agent" in tools or "Task" in tools:
                v.append(f"{a['id']}: specialists cannot delegate")
        if a["reads_untrusted"]:
            if tools & WRITE_TOOLS:
                v.append(f"{a['id']}: reads untrusted material but holds write tools")
            if not caps <= {"read", "propose", "run_sandbox"}:
                v.append(f"{a['id']}: reads untrusted material but holds acting capabilities")
        if "Bash" in tools:
            sandboxed = bool(a.get("sandbox")) and "run_sandbox" in caps
            scoped = "pause_halt" in caps and a.get("bash_scope")
            if not (sandboxed or scoped):
                v.append(f"{a['id']}: holds Bash without a sandbox or a declared bash_scope")
        if tools & WRITE_TOOLS and not a.get("write_paths"):
            v.append(f"{a['id']}: holds write tools without write_paths")
    ver = next((a for a in agents if a["id"] == "verifier"), None)
    if not ver or not ver["context_isolation"] or set(ver["capabilities"]) != {"read"}:
        v.append("verifier must be context-isolated and read-only")
    for e in team["edges"]:
        if e["from"] not in ("conductor", "*") and e["to"] not in ("conductor", "human"):
            v.append(f"edge {e['from']} -> {e['to']}: specialists may message only the conductor or a human")
    lim, dfl = team["limits"], team["defaults"]
    if lim["max_delegation_depth"] != 1:
        v.append("max_delegation_depth must be 1")
    if dfl != {"tool_effect": "deny", "fail_mode": "closed"}:
        v.append("defaults must be deny and fail closed")
    ks = team["kill_switch"]
    if ks["resume"] != ["human"]:
        v.append("only a human may resume")
    for lv in ks["levels"]:
        if "human" not in lv["by"]:
            v.append(f"kill switch level {lv['id']}: a human must be able to trigger it")
        if lv["id"] == "global_stop" and lv["by"] != ["human"]:
            v.append("global_stop must be human only")
    human_roles = {"engagement_lead", "repo_owner", "security_owner"}
    for d in team["decisions"]:
        if d["owner"] not in human_roles:
            v.append(f"decision {d['id']}: owner must be a human role")
        if d["prepared_by"] not in ids:
            v.append(f"decision {d['id']}: prepared_by is not an agent")
    rolled = [x for s in team["rollout"] for x in s["adds"]]
    if sorted(rolled) != sorted(ids):
        v.append("rollout stages must add every agent exactly once")
    if threats["mapping_tier"] not in TIERS:
        v.append("threats.mapping_tier is not a valid evidence tier")
    for t in threats["threats"]:
        if not t["pillars"] or not set(t["pillars"]) <= set(threats["pillars"]):
            v.append(f"{t['id']}: pillars missing or unknown")
        if not set(t["owners"]) <= set(ids):
            v.append(f"{t['id']}: owner is not an agent")
    return v


def main():
    with open(os.path.join(ROOT, "data", "team.json"), encoding="utf-8") as fh:
        team = json.load(fh)
    with open(os.path.join(ROOT, "data", "threats.json"), encoding="utf-8") as fh:
        threats = json.load(fh)
    violations = check(team, threats)
    for line in violations:
        print("VIOLATION:", line)
    if violations:
        print(f"VALIDATE: FAIL ({len(violations)} violations)")
        return 1
    print(f"VALIDATE: PASS ({len(team['agents'])} agents, {len(threats['threats'])} threats, all invariants hold)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
