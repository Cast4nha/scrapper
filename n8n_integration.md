# Integração com n8n - ValSports Scraper

## 📋 Visão Geral

Este documento descreve como integrar o ValSports Scraper com o n8n para automatizar o processo de cambista virtual via WhatsApp.

## 🔄 Fluxo de Automação

### 1. Recebimento de Mensagem WhatsApp
- **Trigger**: Webhook do WhatsApp
- **Condição**: Mensagem contém link de bilhete ValSports
- **Ação**: Extrair código do bilhete da URL

### 2. Captura de Dados do Bilhete
- **HTTP Request**: `POST /api/scrape-bet`
- **Payload**: `{"bet_code": "dmgkrn"}`
- **Resposta**: Dados completos do bilhete

### 3. Geração de PIX
- **HTTP Request**: Gateway de Pagamento
- **Payload**: Valor da aposta capturado
- **Resposta**: Chave PIX e QR Code

### 4. Envio de Dados para Apostador
- **WhatsApp**: Enviar dados + PIX
- **Conteúdo**: 
  - Detalhes da aposta
  - Valor a pagar
  - QR Code PIX

### 5. Monitoramento de Pagamento
- **Webhook**: Gateway de Pagamento
- **Condição**: Pagamento confirmado
- **Ação**: Confirmar aposta

### 6. Confirmação da Aposta
- **HTTP Request**: `POST /api/confirm-bet`
- **Payload**: `{"bet_code": "dmgkrn"}`
- **Resposta**: Confirmação de sucesso

### 7. Notificação Final
- **WhatsApp**: Enviar confirmação
- **Conteúdo**: "Aposta confirmada com sucesso!"

## 🔧 Configuração no n8n

### Variáveis de Ambiente
```bash
VALSORTS_API_URL=http://localhost:5000
VALSORTS_USERNAME=cairovinicius
VALSORTS_PASSWORD=279999
PIX_GATEWAY_URL=https://api.pix.com
PIX_API_KEY=your_pix_api_key
WHATSAPP_WEBHOOK_URL=https://your-n8n.com/webhook/whatsapp
```

### Workflow 1: Captura de Dados
```json
{
  "name": "ValSports - Captura de Dados",
  "nodes": [
    {
      "type": "webhook",
      "name": "WhatsApp Trigger",
      "webhookId": "whatsapp-message"
    },
    {
      "type": "httpRequest",
      "name": "Scrape Bet Data",
      "url": "{{$env.VALSORTS_API_URL}}/api/scrape-bet",
      "method": "POST",
      "body": {
        "bet_code": "{{$json.bet_code}}"
      }
    },
    {
      "type": "httpRequest",
      "name": "Generate PIX",
      "url": "{{$env.PIX_GATEWAY_URL}}/pix/create",
      "method": "POST",
      "body": {
        "amount": "{{$json.bet_value}}",
        "description": "Aposta ValSports - {{$json.bettor_name}}"
      }
    }
  ]
}
```

### Workflow 2: Confirmação de Aposta
```json
{
  "name": "ValSports - Confirmação",
  "nodes": [
    {
      "type": "webhook",
      "name": "PIX Payment Confirmed",
      "webhookId": "pix-confirmation"
    },
    {
      "type": "httpRequest",
      "name": "Confirm Bet",
      "url": "{{$env.VALSORTS_API_URL}}/api/confirm-bet",
      "method": "POST",
      "body": {
        "bet_code": "{{$json.bet_code}}"
      }
    },
    {
      "type": "httpRequest",
      "name": "Send WhatsApp Confirmation",
      "url": "{{$env.WHATSAPP_WEBHOOK_URL}}",
      "method": "POST",
      "body": {
        "message": "✅ Aposta confirmada com sucesso! Código: {{$json.bet_code}}"
      }
    }
  ]
}
```

## 📱 Exemplo de Mensagem WhatsApp

### Mensagem com Dados da Aposta
```
🎯 *DETALHES DA APOSTA*

📋 *Bilhete:* {{bet_code}}
👤 *Apostador:* {{bettor_name}}
🏆 *Liga:* {{league}}
⚽ *Jogo:* {{team1}} x {{team2}}
🎯 *Seleção:* {{selection}}
📅 *Data/Hora:* {{datetime}}
📊 *Odds:* {{odds}}
💰 *Valor:* {{bet_value}}
🏆 *Prêmio Possível:* {{possible_prize}}

💳 *PAGAMENTO PIX*
{{pix_qr_code}}

⚠️ *Aposta válida por 15 minutos*
```

### Mensagem de Confirmação
```
✅ *APOSTA CONFIRMADA!*

🎯 Código: {{bet_code}}
💰 Valor: {{bet_value}}
🏆 Prêmio: {{possible_prize}}

Sua aposta foi registrada com sucesso no sistema!
Boa sorte! 🍀
```

## 🔍 Monitoramento e Logs

### Endpoints de Status
- `GET /health` - Status da API
- `GET /api/status` - Status detalhado do scraper

### Logs Importantes
- Login bem-sucedido
- Captura de dados
- Confirmação de aposta
- Erros de scraping
- Timeouts de conexão

## 🚨 Tratamento de Erros

### Erros Comuns
1. **Login falhou** - Verificar credenciais
2. **Bilhete não encontrado** - Verificar código
3. **Timeout** - Aumentar timeouts
4. **Elemento não encontrado** - Verificar seletores

### Estratégias de Retry
- Máximo 3 tentativas
- Delay de 5 segundos entre tentativas
- Logs detalhados para debug

## 📊 Métricas de Produção

### KPIs Importantes
- Taxa de sucesso de captura
- Tempo médio de resposta
- Taxa de confirmação de apostas
- Uptime da API

### Alertas
- API indisponível
- Taxa de erro > 5%
- Tempo de resposta > 30s
- Falhas de login consecutivas
