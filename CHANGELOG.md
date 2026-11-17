# Changelog

## 0.1.0 (2026-11-17) DRAFT

First release. REF GUARDRAIL-001.

- Canonical team definition for ten agents in `data/team.json`
- Sixteen-threat register in `data/threats.json` (framework keys UNCORROBORATED)
- Ten generated Claude Code subagent files and a generated swarm manifest
- JSON Schemas for the message envelope, a finding and the clearance packet
- Templates for the scope manifest, clearance packet, pull request review and incident record
- Stdlib-only tools: build, validate, dash gate, grant check, envelope check, kill switch, path guard hook, self-test (20 tests)
- CI: quality gate, drift gate, GitHub Pages publish
- MkDocs site with nine guide pages, three generated reference pages and four ADRs
- Ten support figures (SG01 to SG10) as PNG and SVG

Not in this release: policy rules, a red-team corpus, a policy service, asymmetric message signing.
