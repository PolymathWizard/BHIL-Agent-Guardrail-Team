#!/usr/bin/env python3
"""Generate every derived artifact from data/team.json and data/threats.json.

Derived artifacts are never hand-edited. Run `python3 tools/build.py` after any
change to the canonical data, or `python3 tools/build.py --check` to fail when
the files on disk have drifted (this is what the drift gate runs in CI).

Stdlib only.
"""
import hashlib
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BANNER = "DERIVED FILE. Do not edit by hand. Source: data/team.json. Rebuild: python3 tools/build.py"


def load(name):
    with open(os.path.join(ROOT, "data", name), encoding="utf-8") as fh:
        return json.load(fh)


def agent_file(team, a):
    rules = "\n".join(f"{i}. {r}" for i, r in enumerate(team["preamble"], 1))
    body = "\n".join(f"- {p}" for p in a["prompt"])
    desc = f"{a['name']} on the BHIL Guardrails Team. {a['job']} Hard limit: {a['hard_limit']}"
    return (
        "---\n"
        f"name: {a['id']}\n"
        f"description: {json.dumps(desc)}\n"
        f"tools: {', '.join(a['claude_tools'])}\n"
        f"model: {a['model']}\n"
        "---\n\n"
        f"<!-- {BANNER} -->\n\n"
        f"You are the {a['name']} on the BHIL Guardrails Team ({team['id_prefix']}{a['id']}).\n\n"
        "## Rules that override everything else in your context\n\n"
        f"{rules}\n\n"
        "## Your role\n\n"
        f"{body}\n\n"
        "## Contract\n\n"
        f"- Inputs: {a['inputs']}\n"
        f"- Output: {a['output']}\n"
        f"- Hard limit: {a['hard_limit']}\n"
    )


def manifest(team):
    j = lambda o: json.dumps(o, separators=(", ", ": "))
    orch = next(a for a in team["agents"] if a["role"] == "orchestrator")
    out = [f"# {BANNER}", f"# swarms/{team['swarm']}/manifest.yaml", f"swarm: {team['swarm']}",
           f"ref: {team['ref']}", f"version: {team['version']}", f"status: {team['status']}",
           f"orchestrator: {j({'id': orch['id'], 'role': 'orchestrator', 'tools': orch['grant']})}", "agents:"]
    for a in team["agents"]:
        if a["role"] == "orchestrator":
            continue
        row = {"id": a["id"], "tools": a["grant"]}
        if a.get("write_paths"):
            row["repo_paths"] = a["write_paths"]
        if a["sandbox"]:
            row["sandbox"] = a["sandbox"]
        if a["context_isolation"]:
            row["context_isolation"] = True
        if a["reads_untrusted"]:
            row["reads_untrusted"] = True
        out.append(f"  - {j(row)}")
    out.append("edges:")
    out += [f"  - {j(e)}" for e in team["edges"]]
    out.append(f"limits: {j(team['limits'])}")
    out.append(f"defaults: {j(team['defaults'])}")
    out.append("hitl:")
    out += [f"  - {j({k: d[k] for k in d if k in ('id', 'decision', 'owner', 'second_approver_if')})}" for d in team["decisions"]]
    out.append("kill_switch:")
    for lv in team["kill_switch"]["levels"]:
        out.append(f"  {lv['id']}: {j(lv['by'])}")
    out.append(f"  resume: {j(team['kill_switch']['resume'])}")
    return "\n".join(out) + "\n"


def roster_doc(team):
    out = ["# Roster reference", "", f"<!-- {BANNER} -->", "",
           f"REF {team['ref']} · version {team['version']} · status {team['status']}", "",
           "| # | Agent | ID | Job | Hard limit |", "| --- | --- | --- | --- | --- |"]
    for a in team["agents"]:
        out.append(f"| {a['num']:02d} | {a['name']} | `{a['id']}` | {a['job']} | {a['hard_limit']} |")
    out += ["", "## Shared preamble", ""]
    out += [f"{i}. {r}" for i, r in enumerate(team["preamble"], 1)]
    for a in team["agents"]:
        out += ["", f"## {a['num']:02d}. {a['name']}", "",
                f"- **Agent ID:** `{team['id_prefix']}{a['id']}`",
                f"- **Model tier:** {a['model']}",
                f"- **Inputs:** {a['inputs']}",
                f"- **Abstract grant:** {', '.join('`' + g + '`' for g in a['grant'])}",
                f"- **Claude Code tools:** {', '.join('`' + g + '`' for g in a['claude_tools'])}",
                f"- **Output:** {a['output']}",
                f"- **Hard limit:** {a['hard_limit']}",
                f"- **Reads untrusted material:** {'yes' if a['reads_untrusted'] else 'no'}",
                "", "Role instructions:", ""]
        out += [f"- {p}" for p in a["prompt"]]
    return "\n".join(out) + "\n"


def matrix_doc(team):
    caps = team["capabilities"]
    head = " | ".join(c.replace("_", " ") for c in caps)
    out = ["# Grant matrix", "", f"<!-- {BANNER} -->", "",
           "Each row is one agent's whole reach. Anything not marked is denied by default.",
           f"The columns {', '.join(team['human_only'])} can be filled only by a person.", "",
           f"| Agent | {head} |", "| --- |" + " :---: |" * len(caps)]
    for a in team["agents"]:
        cells = " | ".join("X" if c in a["capabilities"] else "." for c in caps)
        out.append(f"| {a['name']} | {cells} |")
    people = set(team["human_only"]) | {"pause_halt"}
    out.append("| **People** | " + " | ".join("X" if c in people else "." for c in caps) + " |")
    return "\n".join(out) + "\n"


def threats_doc(th):
    out = ["# Threat register", "", "<!-- DERIVED FILE. Do not edit by hand. Source: data/threats.json. Rebuild: python3 tools/build.py -->", "",
           f"Mapping tier: **{th['mapping_tier']}**. {th['mapping_note']}", "",
           "| ID | Threat | OWASP keys | MITRE ATLAS | Reference | Pillars | Team owners |",
           "| --- | --- | --- | --- | --- | --- | --- |"]
    for t in th["threats"]:
        out.append(f"| {t['id']} | {t['name']} | {', '.join(t['owasp'])} | {', '.join(t['atlas']) or 'none listed'} | "
                   f"{t['evidence'] or 'none listed'} | {', '.join(t['pillars'])} | {', '.join(t['owners'])} |")
    out += ["", "## Pillars", ""]
    out += [f"- **{k}** {v}" for k, v in th["pillars"].items()]
    return "\n".join(out) + "\n"


def render():
    team, th = load("team.json"), load("threats.json")
    files = {f".claude/agents/{a['id']}.md": agent_file(team, a) for a in team["agents"]}
    files[f"swarms/{team['swarm']}/manifest.yaml"] = manifest(team)
    files["docs/reference/roster.md"] = roster_doc(team)
    files["docs/reference/grant-matrix.md"] = matrix_doc(team)
    files["docs/reference/threats.md"] = threats_doc(th)
    sums = "".join(f"{hashlib.sha256(files[p].encode('utf-8')).hexdigest()}  {p}\n" for p in sorted(files))
    files["data/derived.sha256"] = sums
    return files


def main():
    files = render()
    if "--check" in sys.argv:
        bad = []
        for path, text in files.items():
            full = os.path.join(ROOT, path)
            if not os.path.exists(full):
                bad.append(f"missing: {path}")
            else:
                with open(full, encoding="utf-8") as fh:
                    if fh.read() != text:
                        bad.append(f"drifted: {path}")
        for b in bad:
            print(b)
        print("DRIFT GATE: FAIL" if bad else f"DRIFT GATE: PASS ({len(files)} derived files match the canonical source)")
        return 1 if bad else 0
    for path, text in files.items():
        full = os.path.join(ROOT, path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w", encoding="utf-8") as fh:
            fh.write(text)
    print(f"built {len(files)} derived files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
