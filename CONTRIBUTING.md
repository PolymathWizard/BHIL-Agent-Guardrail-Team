# Contributing

## The one rule

Edit `data/team.json` or `data/threats.json`. Never edit a derived file. Then:

```bash
python3 tools/validate.py
python3 tools/build.py
python3 tools/selftest.py
python3 tools/dash_gate.py
```

Commit the data and the regenerated files together.

## House rules

- **Stdlib-only Python** in `tools/`. No pip dependencies. The figure generator under `docs/assets/figures/src/` is the single exception and no gate depends on it.
- **No em dashes or en dashes** anywhere in tracked text. The dash gate checks raw bytes.
- **Evidence tiers** on factual claims about anything outside this repository: VERIFIED, CORROBORATED, STATED, UNCORROBORATED, INFERENCE.
- **Nothing is reported as clean.** Absence of findings is INCONCLUSIVE.
- **Regression tests name their bugs.** Every test in `tools/selftest.py` has a docstring that begins "Prevents the bug where".
- **Open questions are written down.** If a design question is unresolved, add it to an ADR with a settling criterion.
- **Conventional commits** scoped to the framework: `feat(guardrail):`, `fix(guardrail):`, `docs(guardrail):`.

## Changes that will be refused

- Granting any agent clear, merge or resume
- Giving a write tool to an agent that reads untrusted material
- Adding an edge between two specialists
- Letting an agent resume a run or trigger a global stop
- Any tool, test or document that scans, probes or attacks a system BHIL does not own

The validator rejects the first four. The fifth is a scope rule: the Red Team works inside a sandbox on BHIL's own configurations.

## Proposing a new agent

Open an issue first with: the job, why an existing agent cannot do it, its inputs and whether they are untrusted, the narrowest grant that works, and its hard limit. An eleventh agent changes the rollout, the grant matrix and at least four figures.

## Proposing a new threat

Add a record to `data/threats.json` with framework keys, pillars, owners and links to the sources you checked. New records enter as UNCORROBORATED until the Verifier step in the upkeep workflow is done.

## Documentation

`mkdocs build --strict` must pass. Content pages aim for the BHIL depth standard of 100 to 300 lines; the pages in version 0.1.0 are shorter than that and expanding them is welcome.
