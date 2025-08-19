# 🚀 Guia de Integração n8n - ValSports Scraper

## 📋 **Visão Geral**

Este fluxo n8n funciona como uma **ferramenta (tool)** que pode ser chamada pelo seu fluxo principal de WhatsApp. Ele gerencia o login e captura de dados do bilhete no sistema ValSports.

## 🔧 **Instalação**

### **1. Importar o Fluxo**
1. Abra o n8n
2. Clique em **"Import from file"**
3. Selecione o arquivo `n8n_valsports_workflow.json`
4. Clique em **"Import"**

### **2. Ativar o Webhook**
1. Clique no nó **"Webhook Trigger"**
2. Clique em **"Listen for calls"**
3. Copie a URL do webhook (ex: `https://seu-n8n.com/webhook/valsports-scraper`)

## 📡 **Como Usar**

### **Endpoint do Webhook**
```
POST https://seu-n8n.com/webhook/valsports-scraper
```

### **Ações Disponíveis**

#### **1. Login no Sistema**
```json
{
  "action": "login",
  "username": "cairovinicius",
  "password": "279999"
}
```

**Resposta de Sucesso:**
```json
{
  "status": "success",
  "message": "Login realizado com sucesso",
  "session_id": "abc123..."
}
```

#### **2. Capturar Dados do Bilhete**
```json
{
  "action": "scrape_bet",
  "bet_code": "dmgkrn"
}
```

**Resposta de Sucesso:**
```json
{
  "status": "success",
  "data": {
    "league": "Premier League",
    "teams": "Manchester United vs Liverpool",
    "selection": "Manchester United",
    "datetime": "2025-08-20 15:00:00",
    "odds": "2.50",
    "total_odds": "5.25",
    "possible_prize": "R$ 525,00",
    "bettor_name": "João Silva",
    "bet_value": "R$ 100,00"
  }
}
```

#### **3. Confirmar Aposta**
```json
{
  "action": "confirm_bet",
  "bet_code": "dmgkrn"
}
```

**Resposta de Sucesso:**
```json
{
  "status": "success",
  "message": "Aposta confirmada com sucesso"
}
```

## 🔄 **Integração com Fluxo Principal**

### **Exemplo de Uso no Fluxo Principal:**

```javascript
// 1. Receber mensagem do WhatsApp
const message = $input.first().json.message;
const betCode = extractBetCode(message); // "dmgkrn"

// 2. Chamar ValSports Scraper
const scraperResponse = await $http.post({
  url: 'https://seu-n8n.com/webhook/valsports-scraper',
  body: {
    action: 'scrape_bet',
    bet_code: betCode
  }
});

// 3. Processar resposta
if (scraperResponse.data.status === 'success') {
  const betData = scraperResponse.data.data;
  
  // 4. Enviar dados para o apostador
  await sendWhatsAppMessage({
    to: userPhone,
    message: `📋 *Dados do Bilhete*\n\n` +
            `🏆 Liga: ${betData.league}\n` +
            `⚽ Jogo: ${betData.teams}\n` +
            `🎯 Seleção: ${betData.selection}\n` +
            `📅 Data: ${betData.datetime}\n` +
            `📊 Odds: ${betData.odds}\n` +
            `💰 Valor: ${betData.bet_value}\n` +
            `🏆 Prêmio: ${betData.possible_prize}\n\n` +
            `💳 *Chave PIX:* 123456789\n` +
            `📱 *Valor:* ${betData.bet_value}`
  });
}
```

## 🛠️ **Configuração no Fluxo Principal**

### **1. Adicionar Nó HTTP Request**
- **URL**: `https://seu-n8n.com/webhook/valsports-scraper`
- **Method**: `POST`
- **Headers**: `Content-Type: application/json`
- **Body**: JSON com `action` e parâmetros

### **2. Tratamento de Erros**
```javascript
if (scraperResponse.data.status === 'error') {
  await sendWhatsAppMessage({
    to: userPhone,
    message: `❌ Erro: ${scraperResponse.data.message}`
  });
  return;
}
```

## 📱 **Fluxo Completo do Cambista Virtual**

### **1. Receber Bilhete**
- Apostador envia link: `https://www.valsports.net/prebet/dmgkrn`
- Bot extrai código: `dmgkrn`

### **2. Capturar Dados**
- Chama ValSports Scraper
- Recebe dados completos do bilhete

### **3. Enviar Resumo**
- Envia dados para apostador
- Gera chave PIX
- Aguarda confirmação

### **4. Confirmar Aposta**
- Após pagamento confirmado
- Chama ValSports Scraper para confirmar
- Informa sucesso ao apostador

## 🔒 **Segurança**

### **Credenciais**
- Username e password configurados no fluxo
- Pode ser sobrescrito via parâmetros

### **Validações**
- Verificação de status de resposta
- Tratamento de erros de rede
- Timeout configurado

## 📊 **Monitoramento**

### **Logs Importantes**
- Sucesso/falha de login
- Captura de dados
- Confirmação de apostas
- Erros de API

### **Métricas**
- Tempo de resposta
- Taxa de sucesso
- Erros por tipo

## 🚀 **Próximos Passos**

1. **Testar o fluxo** com dados reais
2. **Configurar gateway PIX** no fluxo principal
3. **Implementar validações** adicionais
4. **Adicionar logs** detalhados
5. **Configurar alertas** de erro

---

**✅ Sistema pronto para produção!**
