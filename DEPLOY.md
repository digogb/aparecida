# Guia de Deploy — Sistema Ione

Checklist completo do zero até o sistema rodando na VM OCI com CI/CD automático.

---

## Etapa 1 — Repositório GitHub

- [ ] Crie um repositório privado no GitHub
- [ ] Faça o primeiro push do código:
  ```bash
  cd /home/rodgb/personal/aparecida/ione
  git init
  git add .
  git commit -m "feat: entrega 1 — módulo de pareceres"
  git remote add origin https://github.com/SEU_USER/SEU_REPO.git
  git push -u origin master
  ```

---

## Etapa 2 — Criar a VM na OCI

1. Acesse [cloud.oracle.com](https://cloud.oracle.com) → **Compute → Instances → Create Instance**
2. Configure:
   - **Nome:** `ione-prod`
   - **Image:** Ubuntu 22.04 (Minimal)
   - **Shape:** Ampere A1 Flex → **4 OCPUs, 24 GB RAM**
   - **Boot volume:** 200 GB
   - **SSH keys:** faça upload da sua chave pública (`~/.ssh/id_rsa.pub`)  
     Se não tiver, gere no WSL: `ssh-keygen -t rsa -b 4096`
3. Anote o **IP público** da VM após a criação

---

## Etapa 3 — Abrir as portas no firewall da OCI

> **Atenção:** a OCI tem duas camadas de firewall. Você precisa liberar nas duas.

### 3.1 Security List (painel OCI)

1. No painel da VM → **Subnet** → **Security List**
2. Em **Ingress Rules**, adicione:

   | Protocolo | Porta | Origem       |
   |-----------|-------|--------------|
   | TCP       | 22    | 0.0.0.0/0    |
   | TCP       | 80    | 0.0.0.0/0    |
   | TCP       | 443   | 0.0.0.0/0    |

### 3.2 Firewall interno da VM (iptables)

Conecte na VM e rode:

```bash
ssh ubuntu@<IP_DA_VM>

sudo iptables -I INPUT -p tcp --dport 80 -j ACCEPT
sudo iptables -I INPUT -p tcp --dport 443 -j ACCEPT
sudo netfilter-persistent save
```

> Se `netfilter-persistent` não estiver instalado:  
> `sudo apt-get install -y iptables-persistent`

---

## Etapa 4 — Configurar o GitHub Actions

No repositório GitHub → **Settings → Secrets and variables → Actions → New repository secret**:

| Nome do secret | Valor |
|---|---|
| `OCI_HOST` | IP público da VM |
| `OCI_USER` | `ubuntu` |
| `OCI_SSH_KEY` | Conteúdo completo do arquivo `~/.ssh/id_rsa` (chave **privada**) |

> A chave privada inclui as linhas `-----BEGIN RSA PRIVATE KEY-----` e `-----END RSA PRIVATE KEY-----`.  
> No WSL: `cat ~/.ssh/id_rsa` para ver o conteúdo.

---

## Etapa 5 — Setup inicial da VM

### 5.1 Edite o script com a URL do seu repositório

No WSL, abra `scripts/setup-vm.sh` e troque a linha:
```bash
REPO_URL="https://github.com/SEU_USER/SEU_REPO.git"
```

### 5.2 Execute o script na VM

```bash
# No WSL:
ssh ubuntu@<IP_DA_VM> "bash -s" < scripts/setup-vm.sh
```

Isso instala Docker, clona o repositório em `/opt/ione` e cria a estrutura de pastas.

### 5.3 Faça logout e login novamente na VM

Necessário para o grupo `docker` ter efeito:

```bash
exit
ssh ubuntu@<IP_DA_VM>
```

---

## Etapa 6 — Configurar variáveis de ambiente na VM

```bash
ssh ubuntu@<IP_DA_VM>
nano /opt/ione/.env
```

Preencha todos os campos (use `.env.production.example` como referência):

```env
DB_PASSWORD=        # senha forte, ex: openssl rand -hex 20
JWT_SECRET=         # python -c "import secrets; print(secrets.token_hex(32))"
ANTHROPIC_API_KEY=  # sk-ant-...
GMAIL_SENDER_EMAIL= # email@gmail.com
GMAIL_CLIENT_ID=
GMAIL_CLIENT_SECRET=
GMAIL_REFRESH_TOKEN=
```

---

## Etapa 7 — Primeiro deploy manual

```bash
ssh ubuntu@<IP_DA_VM>
cd /opt/ione
docker compose -f docker-compose.prod.yml up -d --build
```

O build leva alguns minutos na primeira vez (compilar frontend, instalar dependências Python, etc.).

Verifique se subiu:

```bash
docker compose -f docker-compose.prod.yml ps
```

Todos os containers devem estar `Up`. Teste acessando `http://<IP_DA_VM>` no navegador.

---

## Etapa 8 — Configurar domínio e SSL

> Faça isso após o sistema estar rodando via HTTP.

### 8.1 DNS

No seu registrador de domínio, crie um registro A:
```
seudominio.com.br  →  <IP_DA_VM>
```

Aguarde a propagação (pode levar até 24h, geralmente menos de 1h).

### 8.2 Obter certificado SSL

```bash
ssh ubuntu@<IP_DA_VM>
cd /opt/ione

docker compose -f docker-compose.prod.yml run --rm certbot \
  certonly --webroot -w /var/www/certbot \
  -d seudominio.com.br \
  --email seuemail@email.com \
  --agree-tos --no-eff-email
```

### 8.3 Ativar HTTPS no Nginx

Edite `nginx/nginx.conf` na VM:

```bash
nano /opt/ione/nginx/nginx.conf
```

1. No bloco HTTP (porta 80), descomente o redirect:
   ```nginx
   location / {
       return 301 https://$host$request_uri;
   }
   ```

2. Descomente o bloco `server { listen 443 ssl; ... }` inteiro, substituindo `seudominio.com.br` pelo domínio real.

3. Reinicie o Nginx:
   ```bash
   docker compose -f docker-compose.prod.yml restart nginx
   ```

Teste acessando `https://seudominio.com.br`.

---

## Etapa 9 — Configurar integração Gmail / GCP

> Necessário para receber pedidos de parecer automaticamente por e-mail.

1. Acesse [console.cloud.google.com](https://console.cloud.google.com)
2. Crie um projeto (ou use um existente)
3. Ative as APIs: **Gmail API** e **Cloud Pub/Sub API**
4. Crie uma **Service Account** com papel `Pub/Sub Subscriber`
5. Baixe o JSON de credenciais e envie para a VM:
   ```bash
   scp gmail_service_account.json ubuntu@<IP_DA_VM>:/opt/ione/backend/credentials/
   ```
6. Configure o OAuth do Gmail (Client ID, Client Secret, Refresh Token) e preencha no `.env`
7. Reinicie o backend:
   ```bash
   ssh ubuntu@<IP_DA_VM>
   cd /opt/ione
   docker compose -f docker-compose.prod.yml restart backend
   ```

---

## Etapa 10 — Verificar pipeline automática

Após tudo configurado, cada `git push main` irá:

1. Rodar testes do backend (pytest) e verificar build do frontend
2. Se passar: fazer SSH na VM, `git pull` e `docker compose up -d --build`

Acompanhe em: **GitHub → Actions** (aba do repositório)

---

## Comandos úteis na VM

```bash
# Ver logs em tempo real
docker compose -f docker-compose.prod.yml logs -f backend

# Reiniciar um serviço específico
docker compose -f docker-compose.prod.yml restart backend

# Ver status
docker compose -f docker-compose.prod.yml ps

# Rodar migrations manualmente
docker compose -f docker-compose.prod.yml exec backend alembic upgrade head

# Acessar o banco
docker compose -f docker-compose.prod.yml exec db psql -U ione
```

---

## Resumo da ordem de execução

```
1. GitHub (repositório + push)
2. OCI (criar VM)
3. OCI (abrir portas — Security List + iptables)
4. GitHub (configurar secrets)
5. VM (rodar setup-vm.sh)
6. VM (preencher .env)
7. VM (primeiro deploy manual)
8. DNS + SSL (após sistema funcionando)
9. Gmail/GCP (integração de e-mail)
10. Pronto — deploys automáticos a cada push
```
