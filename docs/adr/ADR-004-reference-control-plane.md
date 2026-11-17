# ADR-004: Ship reference code for the rules, not a control plane

- Status: accepted
- Date: 2026-11-17

## Context

The full design calls for a policy service that mints and revokes grants, asymmetric signing of every message, tool gateways and per-agent telemetry. Building that is a project of its own. Shipping nothing would leave the rules as prose that nobody can run or test.

## Decision

Ship small, stdlib-only reference implementations of the rules:

- `tools/envelope_check.py` runs the six message checks, signing with HMAC and a shared key per agent
- `tools/killswitch.py` applies the three stop levels and the resume rule, with a hash-chained log
- `tools/grant_check.py` answers allow or deny for any agent and tool
- `tools/hooks/path_guard.py` blocks writes outside an agent's paths

Each one is tested by `tools/selftest.py`, and every regression test names the bug it prevents. Each one states in its docstring what it does not do.

## Consequences

- The rules are executable and regression-tested. A change that weakens one fails CI.
- Nobody should mistake the reference code for enforcement. `docs/09-status-and-evidence.md` lists the gap claim by claim.
- The tools have no dependencies, so they run anywhere Python 3 runs, at the cost of hand-rolled schema checks.

## Open questions

| Question | Settling criterion |
| --- | --- |
| When does BHIL build or adopt a real policy service? | Before the first High-tier client engagement is cleared by this team |
| Should the envelope check move to asymmetric signatures inside this repository? | Settle no while the tools stay stdlib-only; revisit if the stdlib-only rule is relaxed for a `controlplane/` package |
| Should the taint check call an external detector? | Settle after the first red-team corpus run: yes if the two built-in patterns catch under half of the agent-to-agent cases |
