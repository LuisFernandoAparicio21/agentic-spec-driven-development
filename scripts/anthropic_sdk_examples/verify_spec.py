"""Verify one spec against the harness rules using the Anthropic SDK directly.

Usage: python verify_spec.py <spec file or specs/<id>/ dir> [--model MODEL]
Prints a JSON verdict on stdout (pipe to jq); cache usage goes to stderr.
"""
import argparse
import json
import sys
from pathlib import Path

import anthropic
from dotenv import load_dotenv

REPO = Path(__file__).resolve().parents[2]
# Order is fixed: any byte change here invalidates the cached prefix.
RULE_FILES = [".claude/agents/spec_author.md", "docs/07-spec-driven-development.md", "CHECKPOINTS.md"]

SCHEMA = {
    "type": "object",
    "properties": {
        "verdict": {"type": "string", "enum": ["APPROVED", "CHANGES_REQUESTED"]},
        "issues": {"type": "array", "items": {
            "type": "object",
            "properties": {
                "severity": {"type": "string", "enum": ["blocker", "major", "minor"]},
                "location": {"type": "string"},
                "rule": {"type": "string"},
                "message": {"type": "string"},
            },
            "required": ["severity", "location", "rule", "message"],
            "additionalProperties": False,
        }},
    },
    "required": ["verdict", "issues"],
    "additionalProperties": False,
}


def build_system() -> list[dict]:
    rules = "\n\n".join(f"<file path='{p}'>\n{(REPO / p).read_text(encoding='utf-8')}\n</file>" for p in RULE_FILES)
    text = ("You review specs for this spec-driven harness. Check the spec against the rules below "
            "(EARS notation, traceability, ambiguity, testability). Report only real issues, each "
            "pointing to a concrete location in the spec. APPROVED means no blocker or major issues.\n\n" + rules)
    return [{"type": "text", "text": text, "cache_control": {"type": "ephemeral"}}]


def read_spec(path: Path) -> str:
    files = sorted(path.glob("*.md")) if path.is_dir() else [path]
    return "\n\n".join(f"<file path='{f.name}'>\n{f.read_text(encoding='utf-8')}\n</file>" for f in files)


def verify(client: anthropic.Anthropic, spec: Path, model: str) -> dict:
    with client.beta.messages.stream(
        model=model,
        max_tokens=16000,
        system=build_system(),
        messages=[{"role": "user", "content": read_spec(spec)}],
        output_config={"effort": "medium", "format": {"type": "json_schema", "schema": SCHEMA}},
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
    ) as stream:
        msg = stream.get_final_message()
    u = msg.usage
    print(f"[{spec}] cache_read={u.cache_read_input_tokens} cache_write={u.cache_creation_input_tokens} "
          f"input={u.input_tokens} output={u.output_tokens}", file=sys.stderr)
    if msg.stop_reason == "refusal":
        raise RuntimeError(f"refused: {msg.stop_details}")
    result = json.loads(next(b.text for b in msg.content if b.type == "text"))
    return {"spec": str(spec), "model": msg.model, **result}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("spec", type=Path)
    parser.add_argument("--model", default="claude-opus-5-5")
    args = parser.parse_args()
    load_dotenv(Path(__file__).with_name(".env"))
    try:
        print(json.dumps(verify(anthropic.Anthropic(), args.spec, args.model), indent=2, ensure_ascii=False))
    except (anthropic.APIError, RuntimeError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
