# Threat register

<!-- DERIVED FILE. Do not edit by hand. Source: data/threats.json. Rebuild: python3 tools/build.py -->

Mapping tier: **UNCORROBORATED**. Framework keys and CVE references were taken from the BHIL playbook research run of 2026-11-17 and have not been re-checked against primary sources in this repository. Re-verify before citing them in client material.

| ID | Threat | OWASP keys | MITRE ATLAS | Reference | Pillars | Team owners |
| --- | --- | --- | --- | --- | --- | --- |
| BHIL-T01 | Direct injection or jailbreak | LLM01, ASI01 | AML.T0051.000, AML.T0054 | none listed | P1, P3 | code-reviewer, red-team |
| BHIL-T02 | Indirect injection through web pages, documents, email or tool output | LLM01, ASI01 | AML.T0051.001, AML.T0053 | CVE-2025-32711 | P3, P1, P6 | code-reviewer, red-team |
| BHIL-T03 | Agent-to-agent injection or spoofing | ASI07, ASI01 | AML.T0051.001 | OWASP multi-agent threat modelling guide | P3, P6, P8 | threat-modeler, red-team, sentinel |
| BHIL-T04 | Memory or shared-context poisoning | ASI06, LLM09 | AML.T0080.000, AML.T0080.001, AML.T0070 | none listed | P3, P4, P8 | threat-modeler, red-team |
| BHIL-T05 | Tool poisoning or tool-definition swap after approval | ASI04, LLM04 | AML.T0110, AML.T0104 | CVE-2025-54136 | P6, P3 | supply-chain-auditor, sentinel |
| BHIL-T06 | Malicious or vulnerable MCP server or client | ASI04, ASI05 | AML.T0010 | CVE-2025-6514, CVE-2025-49596 | P6 | supply-chain-auditor |
| BHIL-T07 | Excessive agency or confused deputy in delegation | LLM03, ASI03, ASI02 | AML.T0053 | none listed | P6, P7 | threat-modeler, policy-steward |
| BHIL-T08 | Unexpected code execution | ASI05, LLM10 | AML.T0053 | CVE-2025-53773 | P6, P4 | code-reviewer |
| BHIL-T09 | Sensitive or client-confidential disclosure | LLM02, LLM08 | AML.T0086, AML.T0056 | none listed | P2, P4 | privacy-guardian |
| BHIL-T10 | Ungrounded intelligence | LLM07 | none listed | none listed | P4 | verifier |
| BHIL-T11 | Cascading swarm failure | ASI08, LLM06 | none listed | none listed | P8, P7, P6 | sentinel |
| BHIL-T12 | Human-agent trust exploitation | ASI09 | none listed | none listed | P7 | verifier, sentinel |
| BHIL-T13 | Rogue or drifting agent | ASI10 | AML.T0081, AML.T0103 | none listed | P8, P6 | sentinel |
| BHIL-T14 | Off-scope engagement | LLM03, LLM07 | none listed | none listed | P5 | intake |
| BHIL-T15 | Denial of wallet | LLM06 | none listed | none listed | P8, P6 | conductor, sentinel |
| BHIL-T16 | AI service API used as a covert command channel | ASI10 | AML.T0096 | none listed | P8 | sentinel |

## Pillars

- **P1** Input filters
- **P2** PII redaction
- **P3** Prompt injection defense
- **P4** Output validation
- **P5** Topic limits
- **P6** Tool permissions
- **P7** Human approval
- **P8** Monitoring
