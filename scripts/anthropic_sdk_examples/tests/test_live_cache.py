"""Live test against the real API: the second call must read the cache.

Skipped when no ANTHROPIC_API_KEY is available. Costs two small API calls.
"""
import os
import sys
from pathlib import Path

import pytest
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import anthropic  # noqa: E402
import verify_spec  # noqa: E402

load_dotenv(Path(__file__).resolve().parents[1] / ".env")
pytestmark = pytest.mark.skipif(not os.environ.get("ANTHROPIC_API_KEY"), reason="ANTHROPIC_API_KEY not set")


def test_second_call_reads_cache(capsys):
    client = anthropic.Anthropic()
    spec = verify_spec.REPO / "specs/create-task"
    first = verify_spec.verify(client, spec, "claude-opus-5-5")
    second = verify_spec.verify(client, spec, "claude-opus-5-5")
    err = capsys.readouterr().err
    print(err, file=sys.stderr)  # keep the usage lines as evidence in the pytest output
    assert first["verdict"] in ("APPROVED", "CHANGES_REQUESTED")
    assert second["verdict"] in ("APPROVED", "CHANGES_REQUESTED")
    cache_reads = [int(line.split("cache_read=")[1].split()[0]) for line in err.splitlines() if "cache_read=" in line]
    assert cache_reads[-1] > 0, f"second call did not hit the cache: {err}"
