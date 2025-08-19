# 🚀 Guia de Integração n8n - ValSports Scraper API

## 📋 **Visão Geral**

Este guia explica como integrar o **ValSports Scraper API** com o **n8n** para automatizar a captura de dados de bilhetes de apostas.

## 🎯 **Abordagens Disponíveis**

### **1. Abordagem Otimizada (RECOMENDADA) ⭐**
- **Endpoint**: `/api/capture-bet`
- **Método**: `POST`
- **Funcionalidade**: Login + Captura em uma única operação
- **Vantagens**: Mais rápido, mais simples, menos pontos de falha

### **2. Abordagem Tradicional**
- **Endpoints**: `/api/login` + `/api/scrape-bet`
- **Método**: `POST` para ambos
- **Funcionalidade**: Login separado da captura
- **Vantagens**: Mais controle sobre cada etapa

## 🔧 **Configuração da API**

### **URL Base**
```
https://valsports.qobebrasil.com.br
```

### **Endpoints Disponíveis**
- `GET /health` - Verificação de saúde da API
- `GET /` - Informações da API
- `POST /api/capture-bet` - **Login + Captura (OTIMIZADO)**
- `POST /api/login` - Login separado
- `POST /api/scrape-bet` - Captura separada
- `POST /api/confirm-bet` - Confirmação de aposta

## 🚀 **Abordagem Otimizada (RECOMENDADA)**

### **1. Importar o Workflow**

1. Abra o n8n
2. Clique em **"Import from file"**
3. Selecione o arquivo `n8n_valsports_workflow.json`
4. Clique em **"Import"**

### **2. Configurar o Workflow**

O workflow otimizado contém apenas **3 nós**:

1. **"When executed by another workflow"** - Trigger
2. **"API Capture Bet"** - Requisição HTTP
3. **"Response"** - Resposta

### **3. Ativar o Workflow**

1. Clique no botão **"Active"** para ativar
2. Anote o **Webhook ID** gerado

### **4. Usar o Workflow**

#### **Chamada do Fluxo Principal:**
```javascript
// No seu fluxo principal do n8n
const result = await $http.post({
  url: 'https://seu-n8n.com/webhook/valsports-bet-capture-optimized',
  body: {
    bet_code: 'dmgkrn'  // Código do bilhete
  }
});
```

#### **Resposta de Sucesso:**
```json
{
  "status": "success",
  "bet_code": "dmgkrn",
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
  },
  "message": "Dados capturados com sucesso"
}
```

#### **Resposta de Erro:**
```json
{
  "status": "error",
  "message": "Falha no login - credenciais inválidas"
}
```

## 🔧 **Abordagem Tradicional (Legacy)**

### **1. Workflow de Login**

```javascript
// Requisição para login
const loginResponse = await $http.post({
  url: 'https://valsports.qobebrasil.com.br/api/login',
  body: {
    username: 'cairovinicius',
    password: '279999'
  }
});

if (loginResponse.status === 'success') {
  // Login bem-sucedido, prosseguir com captura
}
```

### **2. Workflow de Captura**

```javascript
// Requisição para capturar dados
const captureResponse = await $http.post({
  url: 'https://valsports.qobebrasil.com.br/api/scrape-bet',
  body: {
    bet_code: 'dmgkrn'
  }
});
```

## 📊 **Comparação de Performance**

| Métrica | Abordagem Otimizada | Abordagem Tradicional |
|---------|-------------------|---------------------|
| **Requisições** | 1 | 2 |
| **Tempo Estimado** | ~10-15s | ~20-30s |
| **Complexidade** | Baixa | Média |
| **Pontos de Falha** | 1 | 2 |
| **Manutenção** | Fácil | Moderada |

## 🧪 **Testando a Integração**

### **Script de Teste Python**
```bash
python test_capture_bet.py
```

### **Teste Manual com curl**
```bash
curl -X POST https://valsports.qobebrasil.com.br/api/capture-bet \
  -H "Content-Type: application/json" \
  -d '{"bet_code": "dmgkrn"}'
```

## 🔄 **Fluxo Completo no n8n**

### **1. Receber Mensagem WhatsApp**
```javascript
// Trigger: WhatsApp Message
if (message.text.includes('bilhete')) {
  // Extrair código do bilhete
  const betCode = extractBetCode(message.text);
  
  // Chamar workflow de captura
  const betData = await callCaptureWorkflow(betCode);
  
  // Enviar dados para o apostador
  await sendBetDataToUser(betData);
}
```

### **2. Processar Pagamento**
```javascript
// Após captura bem-sucedida
if (betData.status === 'success') {
  // Criar cobrança PIX
  const pixCharge = await createPixCharge(betData.data.bet_value);
  
  // Enviar chave PIX para o apostador
  await sendPixKeyToUser(pixCharge);
}
```

### **3. Confirmar Aposta**
```javascript
// Após confirmação do pagamento
const confirmation = await $http.post({
  url: 'https://valsports.qobebrasil.com.br/api/confirm-bet',
  body: {
    bet_code: betCode
  }
});

if (confirmation.status === 'success') {
  await sendConfirmationToUser();
}
```

## ⚠️ **Considerações Importantes**

### **Rate Limiting**
- A API pode ter limitações de requisições
- Implemente delays entre chamadas se necessário

### **Tratamento de Erros**
- Sempre verifique o status da resposta
- Implemente retry logic para falhas temporárias

### **Logs e Monitoramento**
- Monitore os logs da API para debugging
- Implemente alertas para falhas críticas

## 🆘 **Solução de Problemas**

### **Erro 401 - Falha no Login**
- Verifique as credenciais no ambiente
- Confirme se o site está acessível

### **Erro 404 - Bilhete não encontrado**
- Verifique se o código do bilhete está correto
- Confirme se o bilhete ainda é válido

### **Timeout**
- Aumente o timeout nas requisições
- Verifique a conectividade de rede

## 📞 **Suporte**

Para dúvidas ou problemas:
- Verifique os logs da API
- Teste com o script de teste fornecido
- Consulte a documentação da API

---

**🎯 Recomendação: Use a Abordagem Otimizada para melhor performance e simplicidade!**
