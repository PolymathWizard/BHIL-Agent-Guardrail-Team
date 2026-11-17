# Security

## Scope

This repository defines an agent team and ships reference code for its rules. It is defensive. It contains no exploit code and nothing that scans or probes third-party systems.

## Reporting a problem

If you find a way to make the reference code allow something the rules forbid (for example, a message that passes the envelope check when it should be quarantined, or a path that escapes the write guard), please report it privately through GitHub's "Report a vulnerability" button on this repository rather than opening a public issue.

Useful reports include: the input, the expected decision, the actual decision, and the commit hash.

## What to expect

A fix lands as a regression test first: a test in `tools/selftest.py` whose docstring names the bug, then the change that makes it pass.

## Known limits

The reference code is not a control plane. Its limits are listed in `docs/09-status-and-evidence.md`. Reports that restate those limits are welcome as pull requests against that page.

## Using the agents safely

- Run the Red Team only inside a container or VM with no network access
- Restrict the Sentinel's shell access to the kill-switch script
- Register the path guard hook before enabling the Policy Steward
- Do not point the team at client material until the entry criteria in `docs/07-rollout.md` are met
