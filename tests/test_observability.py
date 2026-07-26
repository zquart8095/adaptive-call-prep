from sales_prep.observability.tracing import is_tracing_enabled, traced_run_config, wrap_anthropic_if_enabled


def test_tracing_disabled_when_no_key(monkeypatch):
    monkeypatch.delenv("LANGSMITH_API_KEY", raising=False)
    monkeypatch.delenv("LANGSMITH_TRACING", raising=False)
    assert is_tracing_enabled() is False


def test_tracing_disabled_when_key_present_but_flag_not_true(monkeypatch):
    """The real LangSmith gotcha: the API key alone doesn't turn tracing on."""
    monkeypatch.setenv("LANGSMITH_API_KEY", "fake-key")
    monkeypatch.delenv("LANGSMITH_TRACING", raising=False)
    assert is_tracing_enabled() is False


def test_tracing_enabled_when_both_set(monkeypatch):
    monkeypatch.setenv("LANGSMITH_API_KEY", "fake-key")
    monkeypatch.setenv("LANGSMITH_TRACING", "true")
    assert is_tracing_enabled() is True


def test_wrap_anthropic_is_noop_when_disabled(monkeypatch):
    monkeypatch.delenv("LANGSMITH_API_KEY", raising=False)
    monkeypatch.delenv("LANGSMITH_TRACING", raising=False)
    sentinel = object()
    assert wrap_anthropic_if_enabled(sentinel) is sentinel


def test_traced_run_config_shape():
    config = traced_run_config(run_name="test-run", thread_id="thread-1", metadata={"a": 1})
    assert config["run_name"] == "test-run"
    assert config["configurable"]["thread_id"] == "thread-1"
    assert config["metadata"] == {"a": 1}
    assert "run_id" not in config  # only included when explicitly passed
