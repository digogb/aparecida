from __future__ import annotations

import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.parecer import ParecerModelo, ParecerRequest, ParecerStatus, ParecerTema
from app.services.parecer_ai_service import classify_email

logger = logging.getLogger(__name__)


class NotLegalConsultationError(ValueError):
    """Raised when P1 detects the email is not a legal consultation."""

# Mapeamento completo de área_principal (P1) → ParecerTema
# Taxonomia P1: licitacoes_contratos, agentes_publicos, terceiro_setor,
# responsabilidade_fiscal, tributos_municipais, repasses_financeiros,
# bens_servicos_publicos, controle_improbidade, previdenciario, urbanismo, outro
_LICITACAO_AREAS = {
    "licitacoes_contratos", "licitacoes", "licitações", "licitacao", "licitação",
}

_AREA_TO_TEMA: dict[str, ParecerTema] = {
    # Licitação
    **{area: ParecerTema.licitacao for area in _LICITACAO_AREAS},
    # Administrativo (todas as demais áreas da taxonomia P1)
    "agentes_publicos": ParecerTema.administrativo,
    "terceiro_setor": ParecerTema.administrativo,
    "responsabilidade_fiscal": ParecerTema.administrativo,
    "tributos_municipais": ParecerTema.administrativo,
    "repasses_financeiros": ParecerTema.administrativo,
    "bens_servicos_publicos": ParecerTema.administrativo,
    "controle_improbidade": ParecerTema.administrativo,
    "previdenciario": ParecerTema.administrativo,
    "urbanismo": ParecerTema.administrativo,
    "administrativo": ParecerTema.administrativo,
    "outro": ParecerTema.administrativo,
}

_AREA_TO_MODELO: dict[str, ParecerModelo] = {
    **{area: ParecerModelo.licitacao for area in _LICITACAO_AREAS},
}


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

    # Coleta textos dos anexos já extraídos
    attachment_texts = [
        a.extracted_text for a in pr.attachments if a.extracted_text
    ]
    email_body = pr.extracted_text

    data = await classify_email(email_body, attachment_texts)
    logger.info("P1 classificacao: %s", data)

    if data.get("is_consulta_juridica") is False:
        raise NotLegalConsultationError(
            f"Email não é uma consulta jurídica: {data.get('assunto_resumido') or (pr.subject or '')[:80]}"
        )

    area = (data.get("area_principal") or "administrativo").lower()
    pr.tema = _AREA_TO_TEMA.get(area, ParecerTema.administrativo)
    pr.modelo = _AREA_TO_MODELO.get(area, ParecerModelo.generico)
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
                    "area_principal": data.get("area_principal"),
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
