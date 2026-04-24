"""
Testes unitários para deadline_calculator.
Nenhum banco real — DB mockado via AsyncMock.
"""
from __future__ import annotations

from datetime import date
from unittest.mock import AsyncMock, MagicMock

import pytest
from freezegun import freeze_time

from app.services.deadline_calculator import calculate_due_date, update_all_deadlines


def _mock_db(holidays: list[date] | None = None):
    """Monta AsyncMock de DB com lista de feriados."""
    scalars = MagicMock()
    scalars.all.return_value = holidays or []
    execute_result = MagicMock()
    execute_result.scalars.return_value = scalars

    db = AsyncMock()
    db.execute = AsyncMock(return_value=execute_result)
    db.commit = AsyncMock()
    return db


class TestCalculateDueDate:
    async def test_pula_fim_de_semana(self):
        """Sexta + 1 dia útil = segunda."""
        db = _mock_db()
        result = await calculate_due_date(date(2026, 4, 24), 1, db)  # sexta
        assert result == date(2026, 4, 27)  # segunda

    async def test_pula_feriado(self):
        """Segunda + 1 dia útil pula feriado de segunda → terça."""
        segunda = date(2026, 4, 27)
        db = _mock_db(holidays=[segunda])
        result = await calculate_due_date(date(2026, 4, 24), 1, db)  # sexta
        assert result == date(2026, 4, 28)  # terça

    async def test_cinco_dias_uteis(self):
        """Segunda + 5 dias úteis = próxima segunda."""
        db = _mock_db()
        result = await calculate_due_date(date(2026, 4, 27), 5, db)
        assert result == date(2026, 5, 4)

    async def test_sem_feriados(self):
        """Terça + 3 dias úteis = sexta."""
        db = _mock_db()
        result = await calculate_due_date(date(2026, 4, 28), 3, db)
        assert result == date(2026, 5, 1)

    async def test_feriado_na_semana_seguinte(self):
        """Feriado no meio do período conta corretamente."""
        feriado = date(2026, 4, 30)  # quinta
        db = _mock_db(holidays=[feriado])
        # Terça 28/04 + 3 dias úteis: qua(1), qui=feriado(skip), sex(2), seg(3) = 04/05
        result = await calculate_due_date(date(2026, 4, 28), 3, db)
        assert result == date(2026, 5, 4)
