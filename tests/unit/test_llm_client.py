"""Tests for LLMClient initialization and provider configuration."""

from agent.llm_client import LLMClient, PROVIDERS


def test_llm_client_loads():
    client = LLMClient()
    assert len(client._available) >= 1, "At least one provider must be configured"


def test_active_provider_is_set():
    client = LLMClient()
    assert client.active_provider in [p["name"] for p in PROVIDERS]


def test_all_configured_providers_have_clients():
    client = LLMClient()
    for p in client._available:
        assert p["name"] in client._clients


def test_provider_priority_order():
    client = LLMClient()
    available_names = [p["name"] for p in client._available]
    provider_names = [p["name"] for p in PROVIDERS]
    # Available providers should appear in the same order as PROVIDERS
    ordered = [n for n in provider_names if n in available_names]
    assert ordered == available_names


def test_no_keys_raises():
    import os
    from unittest.mock import patch
    with patch.dict(os.environ, {"GROQ_API_KEY": "", "CEREBRAS_API_KEY": ""}, clear=False):
        try:
            client = LLMClient()
            # If no keys resolved, should raise
            if not client._clients:
                assert False, "Should have raised RuntimeError"
        except RuntimeError as e:
            assert "No LLM providers" in str(e)
