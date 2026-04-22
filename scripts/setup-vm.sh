#!/bin/bash
# setup-vm.sh — Configuração inicial da VM OCI (Ubuntu 22.04 ARM)
# Execute UMA VEZ após criar a VM:
#   ssh ubuntu@<IP_DA_VM> "bash -s" < scripts/setup-vm.sh
#
# Substitua REPO_URL pelo endereço real do repositório antes de rodar.

set -e

REPO_URL="https://github.com/digogb/aparecida.git"
APP_DIR="/home/ubuntu/ione"

echo "======================================"
echo " Setup da VM OCI — Sistema Ione"
echo "======================================"

# --- Atualiza o sistema ---
echo "==> Atualizando pacotes..."
sudo apt-get update -q
sudo apt-get upgrade -y -q

# --- Instala Docker ---
echo "==> Instalando Docker..."
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker "$USER"

# --- Instala Git ---
sudo apt-get install -y git

# --- Clona o repositório ---
echo "==> Clonando repositório em ${APP_DIR}..."
git clone "$REPO_URL" "$APP_DIR"

# --- Cria diretórios de dados ---
mkdir -p "$APP_DIR/uploads"
mkdir -p "$APP_DIR/backend/credentials"
mkdir -p "$APP_DIR/nginx/ssl"

# --- Cria o .env a partir do exemplo ---
cp "$APP_DIR/.env.production.example" "$APP_DIR/.env"

echo ""
echo "======================================"
echo " Setup concluído!"
echo "======================================"
echo ""
echo "Próximos passos:"
echo "  1. Edite o arquivo .env:"
echo "     nano ${APP_DIR}/.env"
echo ""
echo "  2. Coloque o service account do Gmail em:"
echo "     ${APP_DIR}/backend/credentials/gmail_service_account.json"
echo ""
echo "  3. IMPORTANTE: faça logout e login novamente para"
echo "     o grupo 'docker' ter efeito, depois rode:"
echo "     cd ${APP_DIR}"
echo "     docker compose -f docker-compose.prod.yml up -d --build"
echo ""
echo "  4. Para SSL (após apontar o domínio para este IP):"
echo "     docker compose -f docker-compose.prod.yml run --rm certbot \\"
echo "       certonly --webroot -w /var/www/certbot \\"
echo "       -d seudominio.com.br --email seuemail@email.com --agree-tos"
echo ""
echo "  5. Depois de obter o certificado, ative o bloco HTTPS"
echo "     em nginx/nginx.conf e reinicie o nginx:"
echo "     docker compose -f docker-compose.prod.yml restart nginx"
