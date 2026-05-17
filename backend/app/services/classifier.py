from __future__ import annotations

import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.parecer import ParecerModelo, ParecerRequest, ParecerStatus, ParecerTema
from app.services.content_assembler import extract_body_section
from app.services.parecer_ai_service import classify_email

logger = logging.getLogger(__name__)


class NotLegalConsultationError(ValueError):
    """Raised when P1 detects the email is not a legal consultation."""

# Mapeamento de vertente (P1 v5.0) → ParecerTema / ParecerModelo legacy.
# A taxonomia v5.0 do P1 devolve `vertente` ∈ {licitacao_14133, administrativo,
# tributario_financeiro, terceiro_setor}. Os enums ParecerTema/ParecerModelo do banco são
# binários (licitacao vs administrativo / licitacao vs generico) — preservados por
# compatibilidade com versões antigas e com queries existentes.
_VERTENTE_TO_TEMA: dict[str, ParecerTema] = {
    "licitacao_14133": ParecerTema.licitacao,
    "administrativo": ParecerTema.administrativo,
    "tributario_financeiro": ParecerTema.administrativo,
    "terceiro_setor": ParecerTema.administrativo,
}

_VERTENTE_TO_MODELO: dict[str, ParecerModelo] = {
    "licitacao_14133": ParecerModelo.licitacao,
    "administrativo": ParecerModelo.generico,
    "tributario_financeiro": ParecerModelo.generico,
    "terceiro_setor": ParecerModelo.generico,
}

# Fallback v4.1: quando o P1 (por qualquer razão) devolver o schema antigo com
# `area_principal` em vez de `vertente`, mapeamos pelas chaves históricas.
_LEGACY_AREA_TO_VERTENTE: dict[str, str] = {
    "licitacoes_contratos": "licitacao_14133",
    "terceiro_setor": "terceiro_setor",
    "responsabilidade_fiscal": "tributario_financeiro",
    "tributos_municipais": "tributario_financeiro",
    "repasses_financeiros": "tributario_financeiro",
    "agentes_publicos": "administrativo",
    "controle_improbidade": "administrativo",
    "previdenciario": "administrativo",
    "urbanismo": "administrativo",
    "bens_servicos_publicos": "administrativo",
    "outro": "administrativo",
}


def _resolve_vertente_from_data(data: dict) -> str:
    """Resolve a vertente a partir do payload do P1, com fallback para schema legacy."""
    v = data.get("vertente")
    if isinstance(v, str) and v in _VERTENTE_TO_TEMA:
        return v

    legacy_area = (data.get("area_principal") or "").strip().lower()
    return _LEGACY_AREA_TO_VERTENTE.get(legacy_area, "administrativo")


async def classify(parecer_request_id: str, db: AsyncSession) -> tuple[ParecerRequest, dict]:
    result = await db.execute(
        select(ParecerRequest)
        .where(ParecerRequest.id == parecer_request_id)
        .options(selectinload(ParecerRequest.attachments))
    )
    pr = result.scalar_one_or_none()
    if pr is None:
        raise ValueError(f"ParecerRequest {parecer_request_id} nao encontrado")

    if not pr.extracted_text:
        raise ValueError("ParecerRequest sem texto extraido para classificar")

    # Coleta (filename, texto) dos anexos já extraídos — P1 usa o filename
    # para distinguir a consulta dos documentos de referência.
    attachments = [
        (a.filename or "anexo_sem_nome", a.extracted_text)
        for a in pr.attachments
        if a.extracted_text
    ]
    # extract_body_section evita duplicar os anexos no user_message: pr.extracted_text
    # já contém o corpo + todos os anexos concatenados; queremos só a primeira seção.
    email_body = extract_body_section(pr.extracted_text)

    data = await classify_email(email_body, attachments, subject=pr.subject or "")
    logger.warning("P1 classificacao: %s", data)

    if data.get("is_consulta_juridica") is False:
        # A mensagem é exposta ao usuário no card do parecer. O P1 retorna em
        # `motivo_nao_juridica` a razão objetiva pela qual classificou o email
        # como não-jurídico. Fallback para o assunto se a IA não preencher.
        motivo = (
            data.get("motivo_nao_juridica")
            or data.get("assunto_resumido")
            or (pr.subject or "Email sem assunto")[:80]
        )
        raise NotLegalConsultationError(motivo)

    vertente = _resolve_vertente_from_data(data)
    pr.tema = _VERTENTE_TO_TEMA.get(vertente, ParecerTema.administrativo)
    pr.modelo = _VERTENTE_TO_MODELO.get(vertente, ParecerModelo.generico)
    pr.classificacao = data

    old_status = pr.status
    pr.status = ParecerStatus.classificado

    from app.models.parecer import ParecerStatusHistory
    import json

    db.add(
        ParecerStatusHistory(
            request_id=pr.id,
            from_status=old_status,
            to_status=ParecerStatus.classificado,
            notes=json.dumps(
                {
                    "vertente": vertente,
                    "subtipo": data.get("subtipo"),
                    "modo": data.get("modo"),
                    "municipio": data.get("municipio"),
                    "confianca": data.get("confianca_classificacao"),
                },
                ensure_ascii=False,
            ),
        )
    )

    await db.commit()
    await db.refresh(pr)

    return pr, data
