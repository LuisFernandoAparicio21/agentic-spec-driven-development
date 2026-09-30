"""Verify every spec under specs/ in parallel and write a markdown report.

Usage: python verify_batch.py [--out report.md] [--workers 4] [--model MODEL]
Exit code 1 if any spec is not APPROVED, so it can gate CI.
"""
import argparse
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import anthropic
from dotenv import load_dotenv

from verify_spec import REPO, verify


def run(client, spec, model):
    try:
        return verify(client, spec, model)
    except (anthropic.APIError, RuntimeError) as e:
        return {"spec": str(spec), "verdict": "ERROR", "issues": [], "error": str(e)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", type=Path)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--model", default="claude-opus-5-5")
    args = parser.parse_args()
    load_dotenv(Path(__file__).with_name(".env"))

    specs = sorted(p for p in (REPO / "specs").iterdir() if p.is_dir())
    if not specs:
        print("no specs found under specs/", file=sys.stderr)
        return 0
    client = anthropic.Anthropic()
    # First call alone writes the cache; parallel cold calls would all miss it.
    results = [run(client, specs[0], args.model)]
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        results += pool.map(lambda s: run(client, s, args.model), specs[1:])

    lines = ["# Spec verification report", "", "| Spec | Verdict | Issues |", "|---|---|---|"]
    lines += [f"| `{Path(r['spec']).name}` | {r['verdict']} | {len(r['issues'])} |" for r in results]
    for r in results:
        lines += ["", f"## {Path(r['spec']).name} — {r['verdict']}"]
        if "error" in r:
            lines.append(f"- error: {r['error']}")
        lines += [f"- **{i['severity']}** `{i['location']}` ({i['rule']}): {i['message']}" for i in r["issues"]]
    report = "\n".join(lines) + "\n"
    if args.out:
        args.out.write_text(report, encoding="utf-8")
    else:
        print(report)
    return 0 if all(r["verdict"] == "APPROVED" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
