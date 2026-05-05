from unittest.mock import MagicMock, patch

import pytest

from app.config import settings


def _make_mock_response(content: str, model: str):
    mock_response = MagicMock()
    mock_response.choices[0].message.content = content
    return mock_response


@pytest.fixture(autouse=True)
def reset_client():
    """Re-import module to reset any cached state."""
    import importlib
    import app.services.llm_client as llm_module
    importlib.reload(llm_module)
    yield


def test_llm_client_uses_primary_model():
    with patch("app.services.llm_client.client") as mock_client:
        mock_client.chat.completions.create.return_value = _make_mock_response("ok", settings.primary_llm_model)
        from app.services.llm_client import chat_completion
        answer, model_used = chat_completion([{"role": "user", "content": "hello"}])
        call_kwargs = mock_client.chat.completions.create.call_args
        assert call_kwargs.kwargs["model"] == settings.primary_llm_model
        assert model_used == settings.primary_llm_model


def test_llm_client_fallback_on_429():
    call_count = {"n": 0}

    def side_effect(**kwargs):
        call_count["n"] += 1
        if kwargs["model"] == settings.primary_llm_model:
            raise Exception("Error code: 429 - rate limit exceeded")
        return _make_mock_response("fallback answer", settings.fallback_llm_model)

    with patch("app.services.llm_client.client") as mock_client:
        mock_client.chat.completions.create.side_effect = side_effect
        from app.services.llm_client import chat_completion
        answer, model_used = chat_completion([{"role": "user", "content": "hello"}])
        assert model_used == settings.fallback_llm_model
        assert answer == "fallback answer"
        assert call_count["n"] == 2  # tried primary then fallback


def test_llm_client_raises_on_503():
    def side_effect(**kwargs):
        raise Exception("Error code: 503 - service unavailable")

    with patch("app.services.llm_client.client") as mock_client:
        mock_client.chat.completions.create.side_effect = side_effect
        from app.services.llm_client import chat_completion
        with pytest.raises(Exception, match="503"):
            chat_completion([{"role": "user", "content": "hello"}])


def test_response_includes_model_used():
    with patch("app.services.llm_client.client") as mock_client:
        mock_client.chat.completions.create.return_value = _make_mock_response("answer", settings.primary_llm_model)
        from app.services.llm_client import chat_completion
        answer, model_used = chat_completion([{"role": "user", "content": "q"}])
        assert isinstance(model_used, str)
        assert len(model_used) > 0


def test_llm_client_both_models_fail_raises():
    def side_effect(**kwargs):
        if kwargs["model"] == settings.primary_llm_model:
            raise Exception("Error code: 429")
        raise Exception("Error code: 503")

    with patch("app.services.llm_client.client") as mock_client:
        mock_client.chat.completions.create.side_effect = side_effect
        from app.services.llm_client import chat_completion
        with pytest.raises(Exception):
            chat_completion([{"role": "user", "content": "hello"}])
