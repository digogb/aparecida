"""Defesa contra prompt injection nos anexos.

O texto extraído de cada anexo é conteúdo NÃO-CONFIÁVEL: pode conter instruções
tentando redirecionar o pipeline ("desconsidere as regras", cabeçalhos falsos
"## DADOS DA CONSULTA", etc.). Este módulo isola esse conteúdo numa fronteira
estrutural inforjável — cada anexo vai envolto na tag `<documento_anexo>`, e
qualquer tentativa do próprio conteúdo de "fechar" a tag e escapar é neutralizada.

A garantia é ESTRUTURAL (o conteúdo não consegue forjar o delimitador); a
instrução ao modelo de tratar o que está dentro da tag como dado, não comando,
vive nos system prompts (REGRA de FRONTEIRA DE CONFIANÇA em p2_*.txt / p1_*.txt).
"""
from __future__ import annotations

import re

# Nome da tag que delimita conteúdo de anexo (não-confiável) no user_message.
DOC_TAG = "documento_anexo"

# Casa qualquer tag de abertura/fechamento `<documento_anexo ...>` ou
# `</documento_anexo>` forjada dentro do conteúdo — inclusive com atributos,
# espaços internos e variações de caixa. Usada para impedir que o conteúdo do
# anexo feche o próprio bloco e injete texto "fora" da fronteira de confiança.
_FORGED_TAG_RE = re.compile(rf"<\s*/?\s*{DOC_TAG}\b[^>]*>", re.IGNORECASE)

# Caracteres que quebrariam o atributo `fonte="..."` (ou a própria tag).
_NAME_STRIP_RE = re.compile(r'["<>\r\n]')


def neutralize_delimiters(text: str) -> str:
    """Remove tags `<documento_anexo>` forjadas de dentro do conteúdo de um anexo.

    Sem isso, um anexo poderia conter `</documento_anexo>` seguido de texto e
    "escapar" da fronteira de confiança, passando-se por instrução do sistema.
    """
    if not text:
        return text
    return _FORGED_TAG_RE.sub("[marcação removida]", text)


def sanitize_name(name: str) -> str:
    """Limpa o filename para uso seguro no atributo `fonte` da tag."""
    if not name:
        return ""
    return _NAME_STRIP_RE.sub("", name).strip()


def wrap_document(name: str, text: str) -> str:
    """Envolve o texto de um anexo na tag de fronteira de confiança.

    O conteúdo é neutralizado (tags forjadas removidas) antes de ser envolto,
    e o filename vai sanitizado no atributo `fonte`. Quando não há nome, a tag
    sai sem atributo.
    """
    safe_name = sanitize_name(name)
    open_tag = f'<{DOC_TAG} fonte="{safe_name}">' if safe_name else f"<{DOC_TAG}>"
    return f"{open_tag}\n{neutralize_delimiters(text)}\n</{DOC_TAG}>"


def wrap_documents(documents: list[tuple[str, str]]) -> str:
    """Envolve uma lista de (nome, texto) de anexos, um bloco por anexo."""
    return "\n\n".join(wrap_document(name, text) for name, text in documents)
