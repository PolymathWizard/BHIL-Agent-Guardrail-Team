# policies/

Policy-as-code lands here. This directory, `schemas/` and `templates/` are the only paths the Policy Steward may write to.

Version 0.1.0 ships no policy rules. The team definition in `data/team.json` and the manifest in `swarms/guardrails/manifest.yaml` are the only enforceable artifacts so far. The first policy packs planned are:

| Pack | Purpose | Pillar |
| --- | --- | --- |
| `input_filters/regex_pack.yaml` | Cheap tripwires for override phrases, role-tag spoofing and parameterised image links | P1 |
| `tools/roles.yaml` | Role to tool mapping with side-effect classes | P6 |
| `hitl/triggers.yaml` | Conditions that force a human approval state | P7 |
| `budgets/limits.yaml` | Per-agent and per-run spend, token and time limits | P8 |

Every rule added here carries a rule ID, a BHIL-T threat ID and a reference to a red-team corpus case. A pull request that adds a rule without all three should be sent back.
