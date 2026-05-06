#!/usr/bin/env python
# encoding: utf-8
import argparse, os, re, sys
from datetime import date
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
PLANS = ROOT / "docs" / "plans"
TODAY = date.today()

ALLOW = ["AGENTS.md","CLAUDE.md","Version.md","README.md","LICENSE",
    "docs/",".githooks/",".claude/",".opencode/","openspec/","bin/","logs/",
    "opencode.json","pyproject.toml",".gitignore",".pre-commit-config.yaml"]
BLOCK = ["zip_rar_tool/","tests/","scripts/"]

def _rel(p):
    r = str(ROOT).replace("\\","/")
    return p[len(r)+1:] if p.startswith(r) else p

def allow(f):
    n = f.replace("\\","/"); r = _rel(n)
    if n.endswith(".md") or r.endswith(".md"): return True
    for x in ALLOW:
        if n==x or n.startswith(x): return True
        if r and (r==x or r.startswith(x)): return True
    return False

def block(f):
    n = f.replace("\\","/")
    for x in BLOCK:
        if n.startswith(x): return True
    return False

def today_plan():
    if not PLANS.exists(): return False
    p = re.compile(r"^"+TODAY.strftime("%Y-%m-%d")+r"-.*\.md$")
    return any(f.is_file() and p.match(f.name) for f in PLANS.iterdir())

def any_plan():
    return PLANS.exists() and any(f.is_file() and f.suffix==".md" for f in PLANS.iterdir())

def check_file(fp):
    if allow(fp): return 0
    if not block(fp): return 0
    if today_plan(): return 0
    if any_plan(): return 1
    print("[Guard] BLOCKED: no plan for",TODAY)
    print("  => run /opsx:propose <name>")
    return 2

def check_commit():
    if today_plan(): return 0
    if any_plan(): return 1
    print("[Guard] BLOCKED: create plan before commit")
    print("  => run /opsx:propose <name>")
    return 2

def check_logs():
    import subprocess
    r = subprocess.run(["git","diff","--cached","--diff-filter=D","--name-only"],capture_output=True,text=True,cwd=ROOT)
    deleted = [f for f in r.stdout.strip().split("\n") if f and ("logs/runs/" in f or "docs/test-logs/" in f)]
    if deleted:
        print("[Guard] BLOCKED: Deleting log files is forbidden!")
        for f in deleted: print("  - "+f)
        print("  => Restore logs before commit (git checkout -- "+f+")")
        return 2
    return 0

def main():
    import argparse
    a = argparse.ArgumentParser()
    a.add_argument("--file"); a.add_argument("--commit",action="store_true")
    a.add_argument("--check-logs",action="store_true")
    o = a.parse_args()
    if o.file: sys.exit(check_file(o.file))
    elif o.commit: sys.exit(check_commit())
    elif o.check_logs: sys.exit(check_logs())
    else: sys.exit(0)

if __name__=="__main__": main()