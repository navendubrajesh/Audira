"""Tests for Hugging Face token helpers."""

from audira_core.huggingface import apply_hf_token_env, resolve_hf_token, verify_hf_token


def test_resolve_hf_token_prefers_explicit(monkeypatch) -> None:
    monkeypatch.setenv("HF_TOKEN", "from-env")
    assert resolve_hf_token("from-arg") == "from-arg"


def test_resolve_hf_token_reads_env(monkeypatch) -> None:
    monkeypatch.delenv("HF_TOKEN", raising=False)
    monkeypatch.setenv("HUGGINGFACE_HUB_TOKEN", "hub-token")
    assert resolve_hf_token() == "hub-token"


def test_apply_hf_token_env_sets_aliases(monkeypatch) -> None:
    monkeypatch.delenv("HF_TOKEN", raising=False)
    monkeypatch.delenv("HUGGINGFACE_HUB_TOKEN", raising=False)
    apply_hf_token_env("secret-token")
    assert resolve_hf_token() == "secret-token"


def test_verify_hf_token_success(monkeypatch) -> None:
    class FakeResponse:
        status_code = 200

        def json(self):
            return {"name": "demo-user", "type": "user"}

    def fake_get(url, headers=None, timeout=None):
        assert headers["Authorization"] == "Bearer good-token"
        return FakeResponse()

    monkeypatch.setattr("httpx.get", fake_get)
    result = verify_hf_token("good-token")
    assert result["ok"] is True
    assert result["name"] == "demo-user"


def test_verify_hf_token_failure(monkeypatch) -> None:
    class FakeResponse:
        status_code = 401

        def json(self):
            return {}

    monkeypatch.setattr("httpx.get", lambda *args, **kwargs: FakeResponse())
    result = verify_hf_token("bad-token")
    assert result["ok"] is False
