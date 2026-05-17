from unittest.mock import patch

import pytest

from app.config import settings


def test_llm_client_uses_primary_model():
    with patch("app.services.llm_client.client") as mock_client:
        mock_client.invoke.return_value = "ok"
        from app.services.llm_client import chat_completion

        answer, model_used = chat_completion([{"role": "user", "content": "hello"}])

        mock_client.invoke.assert_called_once_with(
            [{"role": "user", "content": "hello"}],
            model=settings.primary_llm_model,
        )
        assert answer == "ok"
        assert model_used == settings.primary_llm_model


def test_llm_client_fallback_on_429():
    call_count = {"n": 0}

    def side_effect(messages, model):
        call_count["n"] += 1
        if model == settings.primary_llm_model:
            raise Exception("Error code: 429 - rate limit exceeded")
        return "fallback answer"

    with patch("app.services.llm_client.client") as mock_client:
        mock_client.invoke.side_effect = side_effect
        from app.services.llm_client import chat_completion

        answer, model_used = chat_completion([{"role": "user", "content": "hello"}])

        assert model_used == settings.fallback_llm_model
        assert answer == "fallback answer"
        assert call_count["n"] == 2


def test_llm_client_raises_on_503():
    with patch("app.services.llm_client.client") as mock_client:
        mock_client.invoke.side_effect = Exception("Error code: 503 - service unavailable")
        from app.services.llm_client import chat_completion

        with pytest.raises(Exception, match="503"):
            chat_completion([{"role": "user", "content": "hello"}])


def test_response_includes_model_used():
    with patch("app.services.llm_client.client") as mock_client:
        mock_client.invoke.return_value = "answer"
        from app.services.llm_client import chat_completion

        answer, model_used = chat_completion([{"role": "user", "content": "q"}])

        assert answer == "answer"
        assert isinstance(model_used, str)
        assert len(model_used) > 0


def test_llm_client_both_models_fail_raises():
    def side_effect(messages, model):
        if model == settings.primary_llm_model:
            raise Exception("Error code: 429")
        raise Exception("Error code: 503")

    with patch("app.services.llm_client.client") as mock_client:
        mock_client.invoke.side_effect = side_effect
        from app.services.llm_client import chat_completion

        with pytest.raises(Exception):
            chat_completion([{"role": "user", "content": "hello"}])
