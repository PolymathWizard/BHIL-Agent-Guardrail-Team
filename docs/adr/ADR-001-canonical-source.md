# ADR-001: One canonical team definition, everything else derived

- Status: accepted
- Date: 2026-11-17

## Context

The team is described in several places at once: ten agent files, a swarm manifest, a roster page, a grant matrix. If each is edited by hand they drift, and a drifted agent file is a security defect: the documentation says an agent cannot write while its tool list says it can.

## Decision

`data/team.json` is the single source of truth for the team. `data/threats.json` is the single source of truth for the threat register. `tools/build.py` generates every other description of the team from them:

- `.claude/agents/*.md`
- `swarms/guardrails/manifest.yaml`
- `docs/reference/roster.md`, `grant-matrix.md`, `threats.md`
- `data/derived.sha256`

Derived files carry a banner and are never hand-edited. The drift gate (`tools/build.py --check` plus a checksum check) fails CI when a derived file differs from what the source would produce.

## Consequences

- A change to the team is one edit, one rebuild and one commit.
- `tools/validate.py` can check design invariants on the data before anything is generated.
- Hand-written pages (`docs/01` to `docs/09`) repeat some facts from the data and can still go stale. The reference pages are the authority when they disagree.
- The figures are not derived. See the open question.

## Open questions

| Question | Settling criterion |
| --- | --- |
| Should the figures be generated from `data/team.json`? | Settle yes if the team definition changes more than twice before version 1.0 and a figure is found stale either time |
| Should the hand-written pages pull tables from the data at build time? | Settle yes the first time a hand-written table is found to contradict a reference page |
