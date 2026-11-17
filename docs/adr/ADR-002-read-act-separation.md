# ADR-002: Agents that read untrusted material hold no tools that act

- Status: accepted
- Date: 2026-11-17

## Context

Prompt injection cannot be filtered to zero. A detector reduces the rate; it does not remove the risk. An agent that reads a web page, a diff or a client document may be steered by text inside it.

## Decision

Separate reading from acting. An agent marked `reads_untrusted` may hold only read tools, propose-style outputs and, for the Red Team, code execution inside a no-egress sandbox. It may not hold `Edit`, `Write`, delegation, or any capability that changes state outside its own output.

The Conductor, which holds delegation, never receives raw content. It receives validated fields of a result.

The Policy Steward, which holds write tools, takes its input from validated records (control gaps from the Threat Modeler), not from raw project material, and writes only under three paths.

`tools/validate.py` enforces the rule on the data.

## Consequences

- A successful injection against a reader can produce a wrong or missing finding. It cannot merge, send, spend or write.
- The Verifier re-checks findings from evidence, which limits the damage of a wrong finding. A missing finding is harder to catch; that is why specialists overlap on the highest-risk threats.
- The design costs a hop: nothing a reader discovers becomes an action without passing through the Conductor and, for decisions, a person.

## Open questions

| Question | Settling criterion |
| --- | --- |
| The Sentinel reads telemetry, which can contain attacker-influenced strings, and holds Bash for the kill-switch script. Is that a breach of this rule? | Settle by moving the Sentinel to emit a breaker request that a deterministic runner applies, if a red-team case shows telemetry content steering a pause or halt, or by version 1.0, whichever is first |
| The Policy Steward reads existing policy files that a prior pull request may have poisoned. Is CODEOWNERS review enough? | Settle after the first three policy pull requests: if any contains text aimed at the agent, add the path guard and a second reviewer as hard requirements |
| The Red Team reads untrusted material and executes code. Is a no-egress sandbox sufficient containment? | Settle with a documented sandbox escape drill before stage 4 leaves detect mode |
