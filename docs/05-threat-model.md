# Threat model

## Where the threats come from

The team is built against sixteen threats, BHIL-T01 to BHIL-T16. The register is in `data/threats.json` and rendered in the [threat register reference](reference/threats.md). Each threat is keyed to the OWASP lists for LLM and agentic applications and to MITRE ATLAS technique IDs, names at least one of eight guardrail pillars, and names the agents on this team that own it.

!!! warning "Evidence tier for the framework keys"
    The OWASP keys, ATLAS technique IDs and CVE references in the register are **UNCORROBORATED** in this repository. They were taken from the BHIL playbook research run of 2026-11-17 and have not been re-checked here against the primary sources. Re-verify any key before citing it in client material. The first drift watch should do this for the whole register.

## The eight pillars

| Pillar | What it does | Agents that test or maintain it |
| --- | --- | --- |
| P1 Input filters | Screens what enters an agent on every inbound edge | Code Reviewer, Red Team |
| P2 PII redaction | Detects and masks personal and client-confidential data before handoffs and memory writes | Privacy Guardian |
| P3 Prompt injection defense | Isolates untrusted content and validates messages between agents | Code Reviewer, Red Team, Threat Modeler |
| P4 Output validation | Checks structure, grounding and policy before output moves on | Verifier |
| P5 Topic limits | Keeps work inside the engagement scope | Intake |
| P6 Tool permissions | Default-deny grants, narrowing delegation, pinned tool definitions | Supply Chain Auditor, Policy Steward |
| P7 Human approval | Routes the five decisions to people | Verifier, Sentinel |
| P8 Monitoring | Per-agent telemetry, circuit breakers, the kill switch | Sentinel |

## Threats that exist only in a team

Four of the sixteen do not exist for a single agent in a single chat. They are the reason this team is shaped the way it is.

| Threat | What goes wrong | The structural answer here |
| --- | --- | --- |
| BHIL-T03 Agent-to-agent injection | One agent's output carries an instruction that the next agent follows | No specialist-to-specialist edges; six checks on every message; the Conductor sees validated fields only |
| BHIL-T07 Confused deputy in delegation | A sub-agent acts with its parent's authority | Depth of one; grants narrow at each hop; specialists cannot delegate |
| BHIL-T11 Cascading failure | One agent's error fans out through the swarm | Fan-out and budget limits; the Sentinel halts the run |
| BHIL-T13 Rogue or drifting agent | An agent behaves outside its role over time | Per-agent identity in telemetry; pause on repeated denials; only a person resumes |

## Trust tiers for material

Every piece of material an agent reads carries a tier in its provenance.

| Tier | Source | How it is treated |
| --- | --- | --- |
| T0 | BHIL internal | Trusted for facts; still never trusted for instructions |
| T1 | Client provided | Trusted for facts about the client; scoped to the engagement |
| T2 | Licensed data | Trusted within the licence |
| T3 | Open web | Needs corroboration before it is cited as fact |
| T4 | Unknown | Same as T3, and flagged |

No tier makes instructions inside the material safe to follow.

## The collection ethics rule

BHIL agents collect only lawfully accessible information. Surveillance of individuals, non-public access, pretexting and the use of credentials against third parties are denied in every engagement. `templates/scope.yaml` carries the three denied topics that every scope manifest must include, and the Privacy Guardian checks collection methods on every clearance.

## What the monthly drift watch tracks

The Threat Modeler's watch list. Each item is something whose current state should be looked up, never recalled.

- The OWASP lists for LLM applications and for agentic applications
- MITRE ATLAS data releases
- NIST AI risk management publications and drafts
- The guardrail tools BHIL uses as detectors, including their ownership and deprecation notices
- The Model Context Protocol and agent-to-agent protocol specifications
- New CVEs affecting MCP servers, clients and agent frameworks in use

## How a new threat enters

1. The Threat Modeler proposes a record for `data/threats.json` with keys, pillars, owners and source links
2. The Red Team adds corpus cases for it
3. The Verifier checks the mapping
4. The security owner merges
5. `python3 tools/build.py` regenerates the reference page

Until step 3 is done, the new record carries the tier UNCORROBORATED.
