"""Offline tests: a fake client records every request, so no API key or network is needed."""
import json
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import verify_batch  # noqa: E402
import verify_spec  # noqa: E402

REPO = verify_spec.REPO
VERDICT = {"verdict": "APPROVED", "issues": []}


def fake_client(verdict=VERDICT, stop_reason="end_turn"):
    msg = SimpleNamespace(
        model="claude-opus-5-5", stop_reason=stop_reason, stop_details=None,
        content=[SimpleNamespace(type="thinking", text=None), SimpleNamespace(type="text", text=json.dumps(verdict))],
        usage=SimpleNamespace(cache_read_input_tokens=0, cache_creation_input_tokens=5000,
                              input_tokens=4000, output_tokens=300),
    )
    stream = MagicMock()
    stream.__enter__.return_value.get_final_message.return_value = msg
    client = MagicMock()
    client.beta.messages.stream.return_value = stream
    return client


def test_system_prompt_is_cached_and_byte_stable():
    client = fake_client()
    verify_spec.verify(client, REPO / "specs/create-task", "claude-opus-5-5")
    verify_spec.verify(client, REPO / "examples/illustrative-review-cycle/01-spec.md", "claude-opus-5-5")
    first, second = (c.kwargs for c in client.beta.messages.stream.call_args_list)
    assert first["system"] == second["system"]  # any byte change would invalidate the cache
    assert first["system"][-1]["cache_control"] == {"type": "ephemeral"}
    assert first["messages"] != second["messages"]  # only the user turn varies


def test_system_prompt_contains_rules_and_not_the_spec():
    client = fake_client()
    verify_spec.verify(client, REPO / "specs/create-task", "claude-opus-5-5")
    kwargs = client.beta.messages.stream.call_args.kwargs
    system = kwargs["system"][0]["text"]
    for path in verify_spec.RULE_FILES:
        assert f"path='{path}'" in system
    assert "<file path='requirements.md'>" not in system
    assert "<file path='requirements.md'>" in kwargs["messages"][0]["content"]


def test_request_uses_structured_output_schema():
    client = fake_client()
    verify_spec.verify(client, REPO / "specs/create-task", "claude-opus-5-5")
    fmt = client.beta.messages.stream.call_args.kwargs["output_config"]["format"]
    assert fmt["type"] == "json_schema" and fmt["schema"] is verify_spec.SCHEMA


def test_refusal_raises():
    with pytest.raises(RuntimeError, match="refused"):
        verify_spec.verify(fake_client(stop_reason="refusal"), REPO / "specs/create-task", "claude-opus-5-5")


def test_cli_prints_pure_json_on_stdout_and_usage_on_stderr(monkeypatch, capsys):
    monkeypatch.setattr(verify_spec.anthropic, "Anthropic", lambda: fake_client())
    monkeypatch.setattr(sys, "argv", ["verify_spec.py", str(REPO / "specs/create-task")])
    assert verify_spec.main() == 0
    out, err = capsys.readouterr()
    assert json.loads(out)["verdict"] == "APPROVED"
    assert "cache_read=" in err


def test_cli_api_error_exits_2(monkeypatch, capsys):
    client = fake_client()
    client.beta.messages.stream.side_effect = verify_spec.anthropic.APIConnectionError(request=MagicMock())
    monkeypatch.setattr(verify_spec.anthropic, "Anthropic", lambda: client)
    monkeypatch.setattr(sys, "argv", ["verify_spec.py", str(REPO / "specs/create-task")])
    assert verify_spec.main() == 2
    assert "error:" in capsys.readouterr().err


@pytest.mark.parametrize("verdict,code", [(VERDICT, 0), ({"verdict": "CHANGES_REQUESTED", "issues": []}, 1)])
def test_batch_warms_cache_first_and_gates_on_verdict(monkeypatch, tmp_path, verdict, code):
    specs = tmp_path / "specs"
    for name in ("a", "b", "c"):
        (specs / name).mkdir(parents=True)
        (specs / name / "requirements.md").write_text(f"# {name}", encoding="utf-8")
    calls = []

    def fake_verify(client, spec, model):
        calls.append(spec.name)
        return {"spec": str(spec), **verdict}

    monkeypatch.setattr(verify_batch, "REPO", tmp_path)
    monkeypatch.setattr(verify_batch, "verify", fake_verify)
    monkeypatch.setattr(verify_batch.anthropic, "Anthropic", MagicMock)
    out = tmp_path / "report.md"
    monkeypatch.setattr(sys, "argv", ["verify_batch.py", "--out", str(out)])
    assert verify_batch.main() == code
    assert calls[0] == "a" and sorted(calls) == ["a", "b", "c"]  # first one alone, before the pool
    assert "| `c` |" in out.read_text(encoding="utf-8")
