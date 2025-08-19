# ValSports Web Scraper API

Sistema de web scraping para o site [valsports.net](https://www.valsports.net) que fornece uma API REST para capturar dados de bilhetes de apostas e automatizar o processo de cambista virtual.

## 🎯 Objetivo

Este sistema foi desenvolvido para integrar com automações n8n, funcionando como um cambista virtual via WhatsApp. O fluxo completo inclui:

1. **Apostador** envia link do pré-bilhete para o cambista virtual
2. **Sistema** captura automaticamente os dados da aposta
3. **Cambista** envia dados capturados para o apostador
4. **Sistema** gera chave PIX através de gateway de pagamento
5. **Após confirmação do pagamento**, sistema confirma a aposta
6. **Sistema** notifica sucesso para o apostador

## 🏗️ Arquitetura

- **Backend**: Python + Flask
- **Web Scraping**: Selenium WebDriver
- **Containerização**: Docker
- **Deploy**: EasyPanel (cPanel)

## 📋 Pré-requisitos

- Python 3.11+
- Google Chrome
- Docker (opcional, para containerização)
- Conta ativa no ValSports

## 🚀 Instalação

### Opção 1: Instalação Local

```bash
# Clone o repositório
git clone <seu-repositorio>
cd scrapper

# Crie um ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Instale as dependências
pip install -r requirements.txt

# Configure as variáveis de ambiente
cp config.env.example .env
# Edite o arquivo .env com suas configurações
```

### Opção 2: Docker

```bash
# Clone o repositório
git clone <seu-repositorio>
cd scrapper

# Execute com Docker Compose
docker-compose up -d

# Ou construa manualmente
docker build -t valsports-scraper .
docker run -p 5000:5000 valsports-scraper
```

## ⚙️ Configuração

### Variáveis de Ambiente

Crie um arquivo `.env` baseado no `config.env.example`:

```env
# Configurações da API
PORT=5000
DEBUG=False

# Configurações do Selenium
HEADLESS=False

# Configurações de Log
LOG_LEVEL=INFO

# Configurações de Segurança (opcional)
API_KEY=your_api_key_here
```

## 🧪 Testando o Sistema

### Teste Manual

```bash
# Execute o script de teste
python test_scraper.py

# Ou execute o debug para analisar a estrutura da página
python debug_page.py
```

### Teste da API

```bash
# Verificar saúde da API
curl http://localhost:5000/health

# Testar captura de bilhete
curl -X POST http://localhost:5000/api/scrape-bet \
  -H "Content-Type: application/json" \
  -d '{"bet_url": "https://www.valsports.net/prebet/dmgkrn"}'
```

## 📡 Endpoints da API

### 1. Health Check
```
GET /health
```
Verifica se a API está funcionando.

**Resposta:**
```json
{
  "status": "healthy",
  "service": "valsports-scraper-api",
  "version": "1.0.0"
}
```

### 2. Login
```
POST /api/login
```
Faz login no sistema ValSports.

**Body:**
```json
{
  "username": "seu_usuario",
  "password": "sua_senha"
}
```

**Resposta:**
```json
{
  "success": true,
  "message": "Login realizado com sucesso"
}
```

### 3. Capturar Bilhete
```
POST /api/scrape-bet
```
Captura dados de um bilhete específico.

**Body:**
```json
{
  "bet_code": "dmgkrn"
}
```

**Resposta:**
```json
{
  "success": true,
  "data": {
    "ticket_id": "BILHETE 1",
    "league": "Brasil: Série A",
    "team1": "Mirassol",
    "team2": "Cruzeiro",
    "selection": "Vencedor: Mirassol",
    "datetime": "18/08 20:00",
    "odds": "2.91",
    "total_odds": "2.91",
    "possible_prize": "R$ 5,82",
    "bettor_name": "Felipe",
    "bet_value": "R$ 2",
    "bet_code": "dmgkrn"
  }
}
```

### 4. Confirmar Aposta
```
POST /api/confirm-bet
```
Confirma uma aposta no sistema.

**Body:**
```json
{
  "bet_code": "dmgkrn"
}
```

**Resposta:**
```json
{
  "success": true,
  "message": "Aposta confirmada com sucesso",
  "bet_code": "dmgkrn",
  "status": "confirmed"
}
```

## 🔧 Integração com n8n

### Exemplo de Workflow

1. **Trigger**: Mensagem recebida no WhatsApp
2. **Extract URL**: Extrair URL do bilhete da mensagem
3. **HTTP Request**: Chamar `/api/scrape-bet` com a URL
4. **Format Message**: Formatar dados para envio
5. **Send WhatsApp**: Enviar dados para o apostador
6. **Wait for Payment**: Aguardar confirmação de pagamento
7. **HTTP Request**: Chamar `/api/confirm-bet` para confirmar
8. **Send WhatsApp**: Notificar sucesso

### Configuração no n8n

```javascript
// Exemplo de configuração do HTTP Request node
{
  "method": "POST",
  "url": "http://localhost:5000/api/scrape-bet",
  "headers": {
    "Content-Type": "application/json"
  },
  "body": {
    "bet_url": "{{$json.bet_url}}"
  }
}
```

## 🚀 Deploy em Produção

### 1. Preparação para Produção

#### Variáveis de Ambiente
```bash
# Configurações do Servidor
PORT=5000
DEBUG=false
LOG_LEVEL=INFO

# Configurações do Selenium
HEADLESS=true
BROWSER_TIMEOUT=30
PAGE_LOAD_TIMEOUT=20

# Configurações do ValSports
VALSORTS_USERNAME=cairovinicius
VALSORTS_PASSWORD=279999

# Configurações de Segurança
API_KEY=your_secret_api_key
MAX_REQUESTS_PER_MINUTE=60

# Configurações de Retry
MAX_RETRIES=3
RETRY_DELAY=5

# Configurações de Cache
CACHE_ENABLED=true
CACHE_TTL=300
```

#### Construção da Imagem
```bash
# Construa a imagem Docker
docker build -t valsports-scraper .

# Faça push para seu registry (se necessário)
docker tag valsports-scraper seu-registry/valsports-scraper:latest
docker push seu-registry/valsports-scraper:latest
```

### 2. Deploy no EasyPanel

1. **Criar Projeto**: Novo projeto no EasyPanel
2. **Upload Código**: Fazer upload dos arquivos
3. **Configurar Docker**: Usar o Dockerfile fornecido
4. **Variáveis de Ambiente**: Configurar todas as variáveis acima
5. **Build e Deploy**: Executar build e configurar domínio

### 3. Configuração do n8n

#### Workflow Principal
1. **Trigger WhatsApp**: Receber mensagens com links de bilhete
2. **Extração de Código**: Extrair `bet_code` da URL
3. **Captura de Dados**: Chamar `/api/scrape-bet`
4. **Geração PIX**: Integrar com gateway de pagamento
5. **Envio de Dados**: Enviar detalhes + PIX para apostador
6. **Monitoramento**: Aguardar confirmação de pagamento
7. **Confirmação**: Chamar `/api/confirm-bet`
8. **Notificação Final**: Enviar confirmação de sucesso

#### Configuração de Webhooks
```bash
# Webhook para captura de dados
POST https://your-api.com/api/scrape-bet
Content-Type: application/json
{"bet_code": "dmgkrn"}

# Webhook para confirmação
POST https://your-api.com/api/confirm-bet
Content-Type: application/json
{"bet_code": "dmgkrn"}
```

### 4. Monitoramento e Logs

#### Health Checks
- `GET /health` - Status da API
- `GET /api/status` - Status detalhado do scraper

#### Logs Importantes
- Login bem-sucedido
- Captura de dados
- Confirmação de apostas
- Erros de scraping
- Timeouts de conexão

#### Métricas de Produção
- Taxa de sucesso de captura
- Tempo médio de resposta
- Taxa de confirmação de apostas
- Uptime da API

### 5. Segurança

#### Configurações Recomendadas
- API Key obrigatória para endpoints sensíveis
- Rate limiting configurado
- Logs de auditoria
- Timeouts adequados
- Usuário não-root no container

#### Backup e Recuperação
- Backup regular dos logs
- Configuração de restart automático
- Monitoramento de recursos
- Alertas de falha

1. Acesse o painel do EasyPanel
2. Crie um novo projeto
3. Configure as variáveis de ambiente
4. Defina a porta 5000
5. Configure o health check
6. Deploy da aplicação

### 3. Configurações Recomendadas

- **Memory**: 1GB mínimo
- **CPU**: 1 vCPU mínimo
- **Storage**: 10GB mínimo
- **Port**: 5000
- **Health Check**: `/health`

## 🔍 Monitoramento

### Logs

Os logs são exibidos no console e podem ser configurados para arquivo:

```python
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/scraper.log'),
        logging.StreamHandler()
    ]
)
```

### Métricas

- **Health Check**: `/health`
- **Status do Scraper**: Verificar logs
- **Performance**: Monitorar tempo de resposta das requisições

## 🛠️ Troubleshooting

### Problemas Comuns

1. **Driver do Chrome não encontrado**
   - Solução: Verificar se o Chrome está instalado
   - Docker: A imagem já inclui o Chrome

2. **Login falha**
   - Verificar credenciais
   - Verificar se a conta não está bloqueada
   - Verificar se o site não mudou a estrutura

3. **Elementos não encontrados**
   - O site pode ter mudado a estrutura
   - Ajustar seletores XPath no código
   - Verificar se está logado

4. **Timeout nas requisições**
   - Aumentar timeouts no código
   - Verificar conexão com internet
   - Verificar se o site está respondendo

### Debug

Para ativar o modo debug:

```bash
export DEBUG=True
python app.py
```

## 📝 Estrutura do Projeto

```
scrapper/
├── app.py                 # Aplicação Flask principal
├── requirements.txt       # Dependências Python
├── Dockerfile            # Configuração Docker
├── docker-compose.yml    # Docker Compose
├── test_scraper.py       # Script de teste
├── config.env.example    # Exemplo de configuração
├── README.md             # Este arquivo
└── scraper/
    ├── __init__.py
    └── valsports_scraper.py  # Classe principal do scraper
```

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📄 Licença

Este projeto é privado e de uso interno.

## 📞 Suporte

Para suporte técnico, entre em contato com a equipe de desenvolvimento.

---

**Nota**: Este sistema é destinado para uso interno e deve respeitar os termos de uso do site ValSports.
