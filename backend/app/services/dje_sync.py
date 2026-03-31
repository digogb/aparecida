"""
DJE Sync service — normalizes, deduplicates, and classifies DJE movements.

Supports two ingestion modes:
  - Webhook: call ingest_movement() directly from the /dje/webhook endpoint.
  - Polling: schedule poll_dje() via APScheduler (every 15 min) once a real
    DJE API URL is configured in settings.
"""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.movement import Movement, MovementType, Process

logger = logging.getLogger(__name__)

_FORMATO_SYSTEM_PROMPT = """Você é um formatador de textos do Diário de Justiça Eletrônico.
Regras estritas:
- NÃO altere nenhuma palavra, número ou pontuação
- NÃO use markdown (sem **, *, #, >, - para listas, etc.)
- Apenas adicione quebras de linha e indentação com espaços
- Separe blocos lógicos (cabeçalho, partes, ementa, decisão, dispositivo)
- Use linha em branco entre seções
- Mantenha citações de artigos e leis em parágrafos próprios
- Retorne apenas texto puro com quebras de linha"""


async def _formatar_publicacao(texto: str) -> str:
    """Formata o texto bruto de uma publicação do DJE usando Claude."""
    if not texto or not texto.strip():
        return texto
    try:
        from anthropic import AsyncAnthropic
        from app.config import settings

        async with AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY) as client:
            resp = await client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4096,
                system=_FORMATO_SYSTEM_PROMPT,
                messages=[{"role": "user", "content": texto}],
            )
        return resp.content[0].text
    except Exception as e:
        logger.warning("Falha ao formatar publicação via Claude: %s — usando texto original", e)
        return texto

# Raw DJE type string → MovementType adapter
_TYPE_MAP: dict[str, MovementType] = {
    "intimacao":    MovementType.intimacao,
    "intimação":    MovementType.intimacao,
    "sentenca":     MovementType.sentenca,
    "sentença":     MovementType.sentenca,
    "despacho":     MovementType.despacho,
    "acordao":      MovementType.acordao,
    "acórdão":      MovementType.acordao,
    "publicacao":   MovementType.publicacao,
    "publicação":   MovementType.publicacao,
    "distribuicao": MovementType.distribuicao,
    "distribuição": MovementType.distribuicao,
    # tipo_documento values from DJEN API
    "intimação da sentença":          MovementType.sentenca,
    "intimação de acórdão":           MovementType.acordao,
    "intimação de pauta":             MovementType.intimacao,
    "despacho / decisão":             MovementType.despacho,
    "decisão":                        MovementType.despacho,
    "ato ordinatório":                MovementType.despacho,
    "ementa / acordão":               MovementType.acordao,
    "certidão":                       MovementType.publicacao,
    "ata de distribuição":            MovementType.distribuicao,
    "ata de julgamento":              MovementType.publicacao,
    "pauta de julgamentos":           MovementType.publicacao,
}

# Business rules per movement type
MOVEMENT_RULES: dict[MovementType, dict] = {
    MovementType.intimacao:    {"notify": True,  "email_alert": True,  "priority": "high"},
    MovementType.sentenca:     {"notify": True,  "email_alert": False, "priority": "medium"},
    MovementType.despacho:     {"notify": True,  "email_alert": False, "priority": "low"},
    MovementType.acordao:      {"notify": True,  "email_alert": False, "priority": "medium"},
    MovementType.publicacao:   {"notify": True,  "email_alert": False, "priority": "medium"},
    MovementType.distribuicao: {"notify": True,  "email_alert": False, "priority": "low"},
    MovementType.outros:       {"notify": False, "email_alert": False, "priority": "low"},
}


def _normalize_type(raw_type: str) -> MovementType:
    """Adapter: map raw DJE string to MovementType enum."""
    return _TYPE_MAP.get(raw_type.lower().strip(), MovementType.outros)


def _parse_dje_date(raw: str | None) -> datetime | None:
    """Parse DJE date string (DD/MM/YYYY or YYYY-MM-DD) to datetime."""
    if not raw:
        return None
    raw = raw.strip()
    parts = raw.split("/")
    if len(parts) == 3:
        try:
            return datetime(int(parts[2]), int(parts[1]), int(parts[0]))
        except (ValueError, IndexError):
            return None
    try:
        return datetime.fromisoformat(raw.split("T")[0])
    except ValueError:
        return None


async def _get_or_create_process(
    db: AsyncSession,
    number: str,
    court: str | None = None,
) -> Process:
    result = await db.execute(select(Process).where(Process.number == number))
    process = result.scalar_one_or_none()
    if process is None:
        process = Process(number=number, court=court)
        db.add(process)
        await db.flush()
    return process


async def ingest_movement(
    db: AsyncSession,
    dje_id: str,
    process_number: str,
    raw_type: str,
    content: str | None = None,
    published_at: datetime | None = None,
    court: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> Movement | None:
    """
    Normalize and insert one DJE movement.

    Returns the Movement on success, None if it is a duplicate
    (deduplication via ON CONFLICT DO NOTHING on dje_id).
    """
    movement_type = _normalize_type(raw_type)
    process = await _get_or_create_process(db, process_number, court)

    formatted_content = await _formatar_publicacao(content) if content else content

    # Deduplication: ON CONFLICT DO NOTHING ensures idempotency
    stmt = (
        pg_insert(Movement)
        .values(
            process_id=process.id,
            dje_id=dje_id,
            type=movement_type,
            content=formatted_content,
            published_at=published_at,
            is_read=False,
            metadata_=metadata,
        )
        .on_conflict_do_nothing(index_elements=["dje_id"])
        .returning(Movement.id)
    )
    result = await db.execute(stmt)
    row = result.fetchone()

    if row is None:
        logger.debug("Movement %s already exists — skipped", dje_id)
        return None

    await db.commit()

    movement_result = await db.execute(select(Movement).where(Movement.id == row[0]))
    movement = movement_result.scalar_one()

    # Apply business rules
    rules = MOVEMENT_RULES.get(movement_type, {})
    if rules.get("notify"):
        from app.services.notification import notify_movement
        await notify_movement(db, movement)

    from app.services.event_dispatcher import dispatch_movement_event
    await dispatch_movement_event(movement, db)

    logger.info(
        "Ingested movement dje_id=%s type=%s process=%s",
        dje_id,
        movement_type.value,
        process_number,
    )
    return movement


async def poll_dje(db: AsyncSession) -> int:
    """
    Polling adapter — called by APScheduler every 15 minutes.

    Uses DJESearchClient to query comunicaapi.pje.jus.br with settings:
      DJE_NOME_ADVOGADO, DJE_NUMERO_OAB, DJE_SIGLA_TRIBUNAL

    Returns number of new movements ingested.
    """
    import asyncio
    from app.config import settings

    nome_advogado = settings.DJE_NOME_ADVOGADO.strip()
    numero_oab = settings.DJE_NUMERO_OAB.strip()
    sigla_tribunal = settings.DJE_SIGLA_TRIBUNAL.strip() or None

    if not nome_advogado and not numero_oab:
        logger.debug("DJE_NOME_ADVOGADO/DJE_NUMERO_OAB not configured, skipping poll")
        return 0

    try:
        from dje_search import DJESearchClient, DJESearchParams

        params = DJESearchParams(
            nome_advogado=nome_advogado or None,
            numero_oab=numero_oab or None,
            sigla_tribunal=sigla_tribunal,
        )

        # DJESearchClient is synchronous — run in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        client = DJESearchClient()
        comunicacoes = await loop.run_in_executor(None, client.buscar, params)

        count = 0
        for com in comunicacoes:
            movement = await ingest_movement(
                db=db,
                dje_id=com.id,
                process_number=com.numero_processo,
                raw_type=com.tipo_documento or com.tipo_comunicacao or "publicacao",
                content=com.texto,
                published_at=_parse_dje_date(com.data_disponibilizacao),
                court=com.tribunal or com.orgao or None,
                metadata={
                    "link": com.link,
                    "tribunal": com.tribunal,
                    "orgao": com.orgao,
                    "polos": com.polos.to_dict(),
                    "destinatarios": com.destinatarios,
                    "advogados": [a.to_dict() for a in com.advogados],
                    "data_disponibilizacao": com.data_disponibilizacao,
                    "termo_buscado": com.termo_buscado,
                    "tipo_documento": com.tipo_documento,
                    "nome_classe": com.nome_classe,
                    "meio_completo": com.meio_completo,
                },
            )
            if movement is not None:
                count += 1

        logger.info("DJE poll completed: %d new movements", count)
        return count
    except ImportError:
        logger.warning("dje-search-client not installed, skipping poll")
        return 0
    except Exception as e:
        logger.warning("DJE poll failed: %s", e)
        return 0
