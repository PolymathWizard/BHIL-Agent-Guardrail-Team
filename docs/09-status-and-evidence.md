# Status and evidence

This page separates what is tested in this repository from what is design intent and what was taken on trust. Every claim carries one of the five BHIL tiers.

## Tested here

These claims are checked by `tools/selftest.py` and the CI gates on every commit. Tier: **VERIFIED** for the reference code in this repository, and only for that code.

| Claim | Checked by |
| --- | --- |
| No agent holds clear, merge or resume | `validate.py`, `selftest.py` |
| No agent that reads untrusted material holds a write tool | `validate.py`, `selftest.py` |
| The Conductor holds only delegation | `validate.py`, `selftest.py` |
| No edge connects two specialists | `validate.py`, `selftest.py` |
| Only a person can resume or trigger a global stop | `validate.py`, `selftest.py` |
| Bash is granted only with a sandbox or a declared scope | `validate.py`, `selftest.py` |
| Unknown agents and tools are denied | `selftest.py` |
| A write path with dot-dot segments cannot escape | `selftest.py` |
| A replayed, tampered, stale or laterally routed message is quarantined | `selftest.py` |
| An instruction embedded in a tainted result is quarantined | `selftest.py`, for the two patterns the reference detects |
| An edited kill-switch log is detected | `selftest.py` |
| Derived files match `data/team.json` | `build.py --check` |
| No em or en dash in tracked text | `dash_gate.py` |

## Design intent, not yet enforced

Tier: **INFERENCE**. These follow from the design but nothing in this repository makes them true in a running system.

| Claim | What would make it true |
| --- | --- |
| Messages between agents are signed and checked | A harness that calls the envelope check on every message, with per-agent asymmetric keys held outside the agents |
| Grants narrow at each delegation and expire | A policy service that mints and revokes grants |
| A halt revokes every grant in the run | The same policy service, plus tool gateways that honour it |
| The Red Team has no network access | A sandbox you provide |
| The Sentinel can run only the kill-switch script | Permission settings you configure |
| The Verifier never sees a producer's reasoning | A harness that passes it findings and evidence only |
| The Policy Steward cannot write outside its paths | Registering the path guard hook |

## Taken on trust

| Claim | Tier | Note |
| --- | --- | --- |
| OWASP keys, ATLAS technique IDs and CVE references in `data/threats.json` | UNCORROBORATED | From the BHIL playbook research run of 2026-11-17; not re-checked against primary sources here |
| The 95 percent block and 2 percent false-positive thresholds | STATED | Starting targets from the playbook, not measured on BHIL traffic |
| Kill-switch triggers (3 denials in 5 minutes; any cross-engagement access) | STATED | Starting values from the playbook |
| The 10-second approval flag and 5 percent review sample | STATED | Starting values from the playbook |
| Claude Code subagent frontmatter (`name`, `description`, `tools`, `model`) and `claude --agent` | CORROBORATED | Checked against the Claude Code subagent documentation on 2026-11-17 |
| The delegation tool is named `Agent` | UNCORROBORATED | Earlier versions used `Task`; confirm in your version |
| The hook event shape and exit-code contract used by `path_guard.py` | UNCORROBORATED | Confirm in the hooks documentation |

## Known limits of the reference code

- **The taint check is a tripwire.** It matches two phrasings: an override phrase and a note addressed to an agent. A determined injection will not use either. The protection is the structure, not the pattern.
- **The signature is a shared-key stand-in.** HMAC with a key the sender can read proves little against a compromised sender. Use asymmetric keys held by a policy service.
- **The kill switch is advisory.** It records state and refuses bad transitions. It cannot stop a process that never asks it.
- **Schema validation is partial.** The envelope check verifies required fields, intents and trust tiers by hand. It does not run a full JSON Schema validator, because the tools are stdlib-only.
- **No policy rules ship yet.** `policies/` is empty apart from its README.
- **No red-team corpus ships.** The Red Team's instructions assume one.
- **The figures are not generated from the data.** A change to the team can leave them stale.

## No measured performance

This repository contains no measured block rates, false-positive rates, latencies or cost figures. Any number in the documentation is a target, a limit or a placeholder, and is labelled as such.

## Version

0.1.0, draft. The team has not run a real engagement. Treat the specification as a starting point to test, not a certified control.
