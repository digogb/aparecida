"""
Tests for Camada 6 — habilitação do server tool web_search.

Cobre:
- _extract_text_and_tool_calls: concatena texto, conta server_tool_use,
  pareia com web_search_tool_result.
- _call_api: passa `tools=[web_search_20250305]` quando web_search_max_uses > 0
  e WEB_SEARCH_ENABLED=True.

Run: pytest backend/tests/test_web_search_tool.py -v
"""
from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.parecer_ai_service import _extract_text_and_tool_calls


def _block(btype: str, **kwargs) -> SimpleNamespace:
    return SimpleNamespace(type=btype, **kwargs)


class TestExtractTextAndToolCalls:

    def test_apenas_texto_sem_tools(self):
        resp = SimpleNamespace(content=[_block("text", text="resposta final")])
        text, calls = _extract_text_and_tool_calls(resp)
        assert text == "resposta final"
        assert calls == []

    def test_multiplos_blocos_de_texto_concatenados(self):
        resp = SimpleNamespace(content=[
            _block("text", text="parte 1 "),
            _block("text", text="parte 2"),
        ])
        text, _ = _extract_text_and_tool_calls(resp)
        assert text == "parte 1 parte 2"

    def test_um_web_search_pareado_com_result(self):
        resp = SimpleNamespace(content=[
            _block("server_tool_use", id="t1", name="web_search",
                   input={"query": "art. 53 Lei 14.133"}),
            _block("web_search_tool_result", tool_use_id="t1",
                   content=[{"url": "x"}, {"url": "y"}]),
            _block("text", text="resposta com busca"),
        ])
        text, calls = _extract_text_and_tool_calls(resp)
        assert text == "resposta com busca"
        assert len(calls) == 1
        assert calls[0]["tool_name"] == "web_search"
        assert calls[0]["query"] == "art. 53 Lei 14.133"
        assert "2 result" in calls[0]["result_summary"]

    def test_multiplos_web_search_mantem_ordem(self):
        resp = SimpleNamespace(content=[
            _block("server_tool_use", id="t1", name="web_search",
                   input={"query": "primeira"}),
            _block("web_search_tool_result", tool_use_id="t1", content=[{"u": "1"}]),
            _block("server_tool_use", id="t2", name="web_search",
                   input={"query": "segunda"}),
            _block("web_search_tool_result", tool_use_id="t2", content=[]),
            _block("text", text="final"),
        ])
        _, calls = _extract_text_and_tool_calls(resp)
        assert [c["query"] for c in calls] == ["primeira", "segunda"]

    def test_tool_use_sem_result_block(self):
        """Quando uma busca falha sem result_block, ainda registra."""
        resp = SimpleNamespace(content=[
            _block("server_tool_use", id="t1", name="web_search",
                   input={"query": "falha"}),
            _block("text", text="resposta apesar da falha"),
        ])
        _, calls = _extract_text_and_tool_calls(resp)
        assert len(calls) == 1
        assert calls[0]["query"] == "falha"
        assert calls[0]["result_summary"] == "no_result_block"


@pytest.mark.asyncio
class TestCallApiWebSearch:

    @patch("app.services.parecer_ai_service.AsyncAnthropic")
    @patch("app.services.parecer_ai_service._log_api_call")
    async def test_web_search_max_uses_zero_nao_passa_tools(
        self, _mock_log, mock_client_cls,
    ):
        """Comportamento histórico: sem tools=, recebe único bloco text."""
        from app.services.parecer_ai_service import _call_api

        mock_client = MagicMock()
        mock_client_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client_cls.return_value.__aexit__ = AsyncMock(return_value=False)

        fake_response = MagicMock()
        fake_response.usage.input_tokens = 100
        fake_response.usage.output_tokens = 50
        fake_response.content = [MagicMock(text="resposta")]
        mock_client.messages.create = AsyncMock(return_value=fake_response)

        await _call_api(
            model="claude-sonnet-4-6",
            system="sys",
            user_message="msg",
            max_tokens=8000,
            stage="P2-test",
            web_search_max_uses=0,
        )

        call_kwargs = mock_client.messages.create.call_args.kwargs
        assert "tools" not in call_kwargs

    @patch("app.services.parecer_ai_service.AsyncAnthropic")
    @patch("app.services.parecer_ai_service._log_api_call")
    async def test_web_search_max_uses_passa_tools(
        self, _mock_log, mock_client_cls,
    ):
        from app.services.parecer_ai_service import _call_api

        mock_client = MagicMock()
        mock_client_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client_cls.return_value.__aexit__ = AsyncMock(return_value=False)

        # Resposta com texto + 1 server_tool_use
        fake_response = MagicMock()
        fake_response.usage.input_tokens = 200
        fake_response.usage.output_tokens = 80
        fake_response.content = [
            SimpleNamespace(type="server_tool_use", id="t1", name="web_search",
                            input={"query": "art. 75"}),
            SimpleNamespace(type="web_search_tool_result", tool_use_id="t1",
                            content=[{"url": "ok"}]),
            SimpleNamespace(type="text", text="OK"),
        ]
        mock_client.messages.create = AsyncMock(return_value=fake_response)

        result = await _call_api(
            model="claude-sonnet-4-6",
            system="sys",
            user_message="msg",
            max_tokens=8000,
            stage="P2-test",
            web_search_max_uses=8,
        )

        call_kwargs = mock_client.messages.create.call_args.kwargs
        assert call_kwargs.get("tools") == [
            {
                "type": "web_search_20250305",
                "name": "web_search",
                "max_uses": 8,
            }
        ]
        assert result == "OK"
