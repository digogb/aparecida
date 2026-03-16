# Templates

Diretorio reservado para templates de documentos do escritorio.

## Uso futuro

- Templates DOCX customizados (cabecalhos, rodapes, estilos)
- Templates HTML para geracao de PDF
- Templates de email para diferentes tipos de comunicacao

## Atual

Os templates de cabecalho, rodape e assinaturas estao definidos diretamente em:

- `backend/app/services/export_service.py` — constantes `ESCRITORIO_*` e CSS `_PDF_CSS`
- `backend/app/services/email_sender.py` — funcao `_build_email_body()`

Quando houver necessidade de customizacao por usuario ou municipio,
os templates devem ser migrados para arquivos neste diretorio.
