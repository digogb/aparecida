"""
Testes do gate de anexo-documento (services/attachment_filter.py).
"""
from __future__ import annotations

import pytest

from app.services.attachment_filter import (
    has_document_attachment,
    is_document_attachment,
)


class TestIsDocumentAttachment:
    @pytest.mark.parametrize(
        "filename",
        [
            "edital.pdf",
            "LAUDO DE AVALIAÇÃO.PDF",
            "ata.docx",
            "minuta.doc",
            "texto.odt",
            "carta.rtf",
            "nota.txt",
            "planilha.xlsx",
            "custos.xls",
            "dados.csv",
            "tabela.ods",
        ],
    )
    def test_extensoes_de_documento(self, filename):
        assert is_document_attachment(filename, None) is True

    @pytest.mark.parametrize(
        "filename,mime",
        [
            ("assinatura.png", "image/png"),
            ("logo.jpg", "image/jpeg"),
            ("icon.gif", "image/gif"),
            # imagem sem extensão de doc, mesmo com MIME image → False
            ("d5583e27", "image/png"),
        ],
    )
    def test_imagens_nunca_contam(self, filename, mime):
        assert is_document_attachment(filename, mime) is False

    def test_casa_por_mime_quando_extensao_ausente(self):
        assert is_document_attachment("documento-sem-ext", "application/pdf") is True

    def test_mime_image_vence_extensao_de_doc(self):
        # Arquivo renomeado como .pdf mas servido como image/* não conta como documento.
        assert is_document_attachment("fake.pdf", "image/png") is False

    def test_desconhecido_false(self):
        assert is_document_attachment("arquivo.bin", "application/octet-stream") is False

    def test_mime_com_charset(self):
        assert is_document_attachment("x", "text/plain; charset=utf-8") is True


class TestHasDocumentAttachment:
    def test_vazio_false(self):
        assert has_document_attachment([]) is False

    def test_so_imagens_false(self):
        pares = [("assinatura.png", "image/png"), ("logo.gif", "image/gif")]
        assert has_document_attachment(pares) is False

    def test_um_documento_entre_imagens_true(self):
        pares = [
            ("logo.png", "image/png"),
            ("laudo.pdf", "application/pdf"),
        ]
        assert has_document_attachment(pares) is True

    def test_aceita_generator(self):
        pares = ((f, m) for f, m in [("ata.docx", None)])
        assert has_document_attachment(pares) is True
