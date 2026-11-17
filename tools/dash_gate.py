#!/usr/bin/env python3
"""Fail if any tracked text file contains an em dash or an en dash.

BHIL house rule: no em or en dashes anywhere in derived prose. The check runs
on raw bytes, not parsed values, so a dash inside a JSON string or a YAML
scalar is still caught. Binary assets and vendored figure sources are skipped.

Stdlib only. Exit 0 clean, 1 when a dash is found.
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BAD = {b"\xe2\x80\x94": "em dash", b"\xe2\x80\x93": "en dash"}
SKIP_DIRS = {".git", "site", "__pycache__", ".guardrails", "node_modules"}
SKIP_EXT = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".pdf", ".docx", ".woff2", ".zip", ".ico"}


def scan(root=ROOT):
    hits = []
    for base, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for name in files:
            if os.path.splitext(name)[1].lower() in SKIP_EXT:
                continue
            path = os.path.join(base, name)
            with open(path, "rb") as fh:
                for n, line in enumerate(fh.read().split(b"\n"), 1):
                    for seq, label in BAD.items():
                        if seq in line:
                            hits.append((os.path.relpath(path, root), n, label))
    return hits


def main():
    hits = scan()
    for path, n, label in hits:
        print(f"{path}:{n}: {label}")
    print("DASH GATE: FAIL" if hits else "DASH GATE: PASS")
    return 1 if hits else 0


if __name__ == "__main__":
    sys.exit(main())
