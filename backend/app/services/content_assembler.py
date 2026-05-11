"""
Content assembler: combines email body + attachment texts into a single clean string.
"""
from __future__ import annotations

import re
from typing import List

_BLANK_LINES_RE = re.compile(r"\n{3,}")

# Separador entre seções do texto montado (corpo + anexos).
SECTION_SEPARATOR = "\n\n---\n\n"

# Common email header lines to strip
_HEADER_PATTERNS: list[re.Pattern] = [
    re.compile(r"^De:.*$", re.MULTILINE | re.IGNORECASE),
    re.compile(r"^Para:.*$", re.MULTILINE | re.IGNORECASE),
    re.compile(r"^Assunto:.*$", re.MULTILINE | re.IGNORECASE),
    re.compile(r"^Data:.*$", re.MULTILINE | re.IGNORECASE),
    re.compile(r"^From:.*$", re.MULTILINE | re.IGNORECASE),
    re.compile(r"^To:.*$", re.MULTILINE | re.IGNORECASE),
    re.compile(r"^Subject:.*$", re.MULTILINE | re.IGNORECASE),
    re.compile(r"^Date:.*$", re.MULTILINE | re.IGNORECASE),
    re.compile(r"^Sent:.*$", re.MULTILINE | re.IGNORECASE),
    re.compile(r"^CC:.*$", re.MULTILINE | re.IGNORECASE),
]

# Footer / quoted-message patterns (remove everything from match onwards)
_FOOTER_PATTERNS: list[re.Pattern] = [
    re.compile(
        r"---+\s*mensagem original.*$",
        re.MULTILINE | re.IGNORECASE | re.DOTALL,
    ),
    re.compile(
        r"---+\s*original message.*$",
        re.MULTILINE | re.IGNORECASE | re.DOTALL,
    ),
    re.compile(
        r"em \d{1,2}/\d{1,2}/\d{2,4}.*escreveu:.*$",
        re.MULTILINE | re.IGNORECASE | re.DOTALL,
    ),
]


def _clean(text: str) -> str:
    for pattern in _HEADER_PATTERNS:
        text = pattern.sub("", text)
    for pattern in _FOOTER_PATTERNS:
        text = pattern.sub("", text)
    text = _BLANK_LINES_RE.sub("\n\n", text)
    return text.strip()


def assemble(corpo_email: str, attachments_texts: List[str]) -> str:
    """Combine email body and attachment texts into a single clean string.

    Sections are separated by a horizontal rule.  Empty sections are skipped.
    """
    sections: list[str] = []

    if corpo_email and corpo_email.strip():
        cleaned = _clean(corpo_email)
        if cleaned:
            sections.append(cleaned)

    for att_text in attachments_texts:
        if att_text and att_text.strip():
            cleaned = _clean(att_text)
            if cleaned:
                sections.append(cleaned)

    return SECTION_SEPARATOR.join(sections)


def extract_body_section(assembled: str | None) -> str:
    """Devolve apenas a primeira seção do texto montado (header + corpo do email).

    O texto persistido em `pr.extracted_text` é o resultado de `assemble()`:
    a primeira seção é o corpo do email; as demais são anexos. Para alimentar
    classify_email / generate_parecer, queremos só essa primeira seção — os
    anexos vêm separados via `pr.attachments` para evitar duplicação no prompt.
    """
    if not assembled:
        return ""
    return assembled.split(SECTION_SEPARATOR, 1)[0]
