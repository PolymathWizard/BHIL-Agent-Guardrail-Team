# ADR-003: Claude Code subagents as the first runtime

- Status: accepted
- Date: 2026-11-17

## Context

The team specification is runtime-neutral. To be usable it needs at least one concrete form. BHIL's agent work follows the CADRE pattern: a stronger model orchestrates, faster models do specialist work, and each subagent's tools are isolated by the runtime.

## Decision

Ship the ten agents as Claude Code subagent files under `.claude/agents/`, generated from the canonical data. The Conductor runs as the main session (`claude --agent conductor`) and delegates to the nine specialists. The Conductor and the Verifier use the opus tier; the other eight use the sonnet tier.

Each agent's `tools` line is an allowlist. That allowlist is the one control the runtime enforces, and the design is arranged so that the most important rules (who can write, who can run commands, who can delegate) are expressible in it.

## Consequences

- The team can be tried today with no infrastructure beyond Claude Code.
- Rules that an allowlist cannot express are not enforced by the runtime: the sandbox for the Red Team, the command scope for the Sentinel, path limits for the Policy Steward, message signing, grant expiry and the kill switch. `docs/06-claude-code-setup.md` lists each one with what to configure.
- Tool names are specific to the runtime and its version. The canonical data keeps the abstract grant beside the tool names so another renderer can be added.

## Open questions

| Question | Settling criterion |
| --- | --- |
| Is the delegation tool named `Agent` or `Task` in the versions BHIL runs? | Settle on first run of `claude --agent conductor`; record the version and the name in the setup page |
| Should per-agent shell restrictions be shipped as a settings file in this repository? | Settle yes once the permission-rule syntax has been confirmed against the documentation and tested on one agent |
| Should a second renderer (for a graph-based agent framework) ship? | Settle yes when a BHIL project needs the team outside Claude Code |
