"""
T1 — Serviço de Prompts
Carrega, versiona e monta os system prompts para cada etapa do pipeline v4.1.
"""
from __future__ import annotations

import logging
from pathlib import Path

logger = logging.getLogger(__name__)

PROMPT_VERSION = "4.1"
PROMPTS_DIR = Path(__file__).parent.parent.parent / "prompts"


def load_prompt(stage: str) -> str:
    """
    Carrega o system prompt para a etapa.
    stage: "p1_classification" | "p2_parecer_generation" | "p3_parecer_revision"
    """
    path = PROMPTS_DIR / f"{stage}.txt"
    return path.read_text(encoding="utf-8")


def build_p2_prompt(include_fewshot: bool = True) -> str:
    """
    Monta o prompt do P2 com few-shot examples.
    O padrão é incluir os exemplos — garantem qualidade e consistência
    no formato XML de saída.
    """
    base = load_prompt("p2_parecer_generation")
    if include_fewshot:
        fewshot_path = PROMPTS_DIR / "examples_fewshot.md"
        if fewshot_path.exists():
            fewshot = fewshot_path.read_text(encoding="utf-8")
            return base + "\n\n---\n\n## EXEMPLOS DE REFERÊNCIA\n\n" + fewshot
    return base


def get_prompt_version() -> str:
    return PROMPT_VERSION
