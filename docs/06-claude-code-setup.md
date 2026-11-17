# Claude Code setup

The ten agents ship as Claude Code subagent files in `.claude/agents/`. Each file has YAML frontmatter (`name`, `description`, `tools`, `model`) and the agent's instructions as the body. The files are generated from `data/team.json`; edit the data, never the files.

## Quick start

```bash
git clone https://github.com/PolymathWizard/BHIL-Agent-Guardrail-Team.git
cd BHIL-Agent-Guardrail-Team
python3 tools/validate.py        # team invariants
python3 tools/selftest.py        # 20 tests
python3 tools/build.py --check   # derived files match the source
```

Then open the repository in Claude Code. The ten agents appear in the `/agents` list.

## Running the team

The Conductor is the orchestrator, so it runs as the main session and the nine specialists run as its subagents.

```bash
claude --agent conductor
```

Then give it a request in one of the three shapes it knows:

- "Clear this project: `<path or brief>`"
- "Review this pull request: `<diff or branch>`"
- "Run the drift watch"

You can also call one specialist directly for a narrow job, for example: "Use the code-reviewer subagent on the staged diff."

## Tool mapping

`data/team.json` holds two tool lists per agent: an abstract grant (`repo.read`, `agent.delegate`) that describes the design, and the Claude Code tool names that implement it.

| Agent | Claude Code tools | Model tier |
| --- | --- | --- |
| conductor | Agent | opus |
| intake | Read, Grep, Glob | sonnet |
| threat-modeler | Read, Grep, Glob, WebSearch, WebFetch | sonnet |
| policy-steward | Read, Grep, Glob, Edit, Write | sonnet |
| code-reviewer | Read, Grep, Glob | sonnet |
| supply-chain-auditor | Read, Grep, Glob, WebSearch, WebFetch | sonnet |
| privacy-guardian | Read, Grep, Glob | sonnet |
| red-team | Read, Grep, Glob, Bash | sonnet |
| verifier | Read, Grep, Glob | opus |
| sentinel | Read, Grep, Glob, Bash | sonnet |

The model column follows the BHIL CADRE pattern: a stronger model orchestrates and verifies; a faster one does the specialist work.

## Things to confirm against your installed version

Claude Code changes often. Three details in this setup should be checked against the current documentation before you rely on them.

1. **The delegation tool name.** The Conductor's allowlist names the subagent tool as `Agent`. Earlier versions called it `Task`. If the Conductor cannot delegate, check the name in your version and update `claude_tools` for the conductor in `data/team.json`, then rebuild.
2. **Tool allowlists are the enforced part.** A subagent can use only the tools in its `tools` line. That is the control this repository relies on. Everything else in the design is instruction or reference code.
3. **The hook contract.** `tools/hooks/path_guard.py` blocks `Edit` and `Write` outside the Policy Steward's write paths. It expects the hook event as JSON on stdin and blocks by exiting with code 2. Confirm the event shape and exit codes in the hooks documentation, then register it as a pre-tool-use hook for `Edit` and `Write`.

## Limits that Claude Code does not enforce for you

| Design rule | State in Claude Code |
| --- | --- |
| Red Team runs only in a no-egress sandbox | Not enforced by the agent file. Run the Red Team inside a container or VM with no network |
| Sentinel may run only the kill-switch script | Not enforced by the agent file. Restrict shell commands with your permission settings |
| Policy Steward writes only under `policies/`, `schemas/`, `templates/` | Enforced only if you register the path guard hook |
| Verifier shares no context with producers | Subagents start with their own context. Pass the Verifier findings and evidence pointers only, never another agent's transcript |
| Messages are signed and checked | Not enforced. `tools/envelope_check.py` is a reference for a harness to call |
| The kill switch stops agents | Not enforced. A harness must call `killswitch.may_run()` before each agent call |

Treat the first two rows as blocking for anything beyond a trial. An agent with unrestricted shell access is not a guardrail.

## Checking a grant

```bash
python3 tools/grant_check.py code-reviewer Read          # ALLOW
python3 tools/grant_check.py code-reviewer Bash          # DENY
python3 tools/grant_check.py verifier merge              # DENY, people-only
python3 tools/grant_check.py policy-steward Write --path policies/tools/roles.yaml
```

Exit code 0 means allow, 1 means deny. Unknown agents and unknown tools are denied.

## Changing the team

1. Edit `data/team.json`
2. `python3 tools/validate.py`
3. `python3 tools/build.py`
4. `python3 tools/selftest.py`
5. Commit the data and the regenerated files together

If the validator rejects your change, the change breaks one of the design rules. Read the violation before working around it.

## Other runtimes

The team definition is runtime-neutral. To target another framework, add a renderer to `tools/build.py` that reads the same `data/team.json` and writes that framework's agent format. Keep the Claude Code renderer as the reference.
