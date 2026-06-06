FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    tesseract-ocr \
    tesseract-ocr-por \
    libreoffice-writer-nogui \
    fontconfig \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Fontes proprietárias do escritório (Consolas + Garamond) — necessárias
# para que `soffice` renderize o PDF com o mesmo layout do .docx aberto no
# Word. Sem essas fontes, o LibreOffice substitui silenciosamente por
# DejaVu/Liberation e quebra o alinhamento manual do bloco de assinaturas.
COPY fonts/*.TTF /usr/share/fonts/truetype/microsoft/
RUN fc-cache -f

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Run as non-root user (UID 1001 casa com ubuntu no host, permitindo writes no bind mount ./uploads)
RUN groupadd --gid 1001 appuser && \
    useradd --uid 1001 --gid 1001 --no-create-home appuser && \
    chown -R appuser:appuser /app
USER appuser
