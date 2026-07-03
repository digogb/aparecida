"""Cor de realce das anotações inline, por autor (paleta fixa — decisão do cliente 03/07/2026).

Amarelo = Dr. Ione, azul-claro = Matheus (pedido explícito). Verde/roxo para
Flávio/Valéria. Qualquer outro usuário recebe uma cor determinística da paleta de
fallback (estável por autor). As cores são tons pastel para não competir com o texto.
"""

# Chaveado por e-mail (minúsculo). Inclui os e-mails reais de prod e os seeds antigos.
_BY_EMAIL: dict[str, str] = {
    "dr.ione@uol.com.br": "#FDE68A",          # amarelo — Dr. Ione (prod)
    "francisco@ione.adv.br": "#FDE68A",       # amarelo — Dr. Ione (HML)
    "matheuspl20@hotmail.com": "#BFDBFE",     # azul-claro — Matheus (prod)
    "matheus@ione.adv.br": "#BFDBFE",         # azul-claro — Matheus (HML)
    "flavio@ione.adv.br": "#BBF7D0",          # verde — Flávio
    "flaviolona@uol.com.br": "#BBF7D0",
    "valeria@ione.adv.br": "#DDD6FE",         # roxo — Valéria
    "valeria.alencar.adv@gmail.com": "#DDD6FE",
}

_FALLBACK_PALETTE: list[str] = [
    "#FBCFE8",  # rosa
    "#FED7AA",  # laranja
    "#A7F3D0",  # verde-água
    "#C7D2FE",  # índigo
    "#FEF08A",  # amarelo-claro
    "#E9D5FF",  # lilás
]


def color_for(email: str | None, user_id: object) -> str:
    """Cor de realce para o autor. E-mail conhecido → cor fixa; senão determinística."""
    if email:
        fixed = _BY_EMAIL.get(email.strip().lower())
        if fixed:
            return fixed
    key = str(user_id or email or "")
    h = 0
    for ch in key:
        h = (h * 31 + ord(ch)) & 0xFFFFFFFF
    return _FALLBACK_PALETTE[h % len(_FALLBACK_PALETTE)]
