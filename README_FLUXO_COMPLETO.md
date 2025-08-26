# 🔄 Fluxo Completo de Confirmação de Bilhete

## 📋 Visão Geral

Este documento descreve o fluxo completo de confirmação automática de bilhetes após pagamento PIX aprovado.

## 🔄 Fluxo de Trabalho

### 1. **Captura de Dados do Bilhete**
- Cliente envia link do bilhete
- Sistema extrai código do bilhete
- API captura todos os dados (jogos, odds, valores)
- Gera QR Code PIX para pagamento

### 2. **Pagamento PIX**
- Cliente paga via PIX
- Mercado Pago processa pagamento
- Webhook recebe notificação de pagamento

### 3. **Confirmação Automática**
- Sistema verifica se pagamento foi aprovado
- Extrai código do bilhete da referência externa
- Chama API de confirmação
- Confirma bilhete no ValSports

## 🛠️ Componentes do Sistema

### API Endpoints

#### `/api/capture-bet` (POST)
**Captura dados do bilhete e gera PIX**

```json
{
  "bet_code": "n6e2er"
}
```

**Resposta:**
```json
{
  "status": "success",
  "bet_code": "n6e2er",
  "data": {
    "total_games": 6,
    "total_odds": "655,68",
    "possible_prize": "R$ 9.179,49",
    "bettor_name": "Felipe",
    "bet_value": "14",
    "games": [...]
  },
  "message": "Dados capturados com sucesso",
  "execution_time": "23.17s"
}
```

#### `/api/confirm-bet` (POST)
**Confirma bilhete após pagamento aprovado**

```json
{
  "bet_code": "n6e2er"
}
```

**Resposta:**
```json
{
  "status": "success",
  "bet_code": "n6e2er",
  "message": "Bilhete confirmado com sucesso",
  "confirmed_at": "2025-08-22 11:46:31"
}
```

## 🔧 Workflow n8n

### Estrutura do Workflow

1. **Webhook - Pix Notification**
   - Recebe notificações do Mercado Pago
   - Path: `/pagamentonovo`

2. **Extract Payment ID**
   - Extrai ID do pagamento da query string

3. **Get Payment Info**
   - Consulta API do Mercado Pago
   - Verifica status do pagamento

4. **IF - Payment Approved?**
   - Verifica se status = "approved"
   - Se sim, continua para confirmação

5. **Extract Bet Code**
   - Extrai código do bilhete de `external_reference`

6. **Confirm Bet API**
   - Chama API de confirmação
   - URL: `https://valsports.qobebrasil.com.br/api/confirm-bet`

7. **IF - Confirmation Success?**
   - Verifica se confirmação foi bem-sucedida

8. **Success/Error Response**
   - Retorna mensagem apropriada

### Configuração do Mercado Pago

**Webhook URL:**
```
https://seu-n8n.com/webhook/pagamentonovo
```

**External Reference:**
- Deve conter o código do bilhete
- Exemplo: `n6e2er`

## 🎯 Fluxo de Confirmação no ValSports

### Passos Automatizados

1. **Login no ValSports**
   - Usuário: `cairovinicius`
   - Senha: `279999`

2. **Navegação para Pré-aposta**
   - Clica em "Pré-aposta" no menu

3. **Digitação do Código**
   - Insere código do bilhete no campo

4. **Busca do Bilhete**
   - Clica em "Buscar"

5. **Confirmação da Aposta**
   - Clica em "Apostar"
   - Confirma clicando em "Sim"

### Seletores CSS/XPath Utilizados

```python
# Botão Pré-aposta
"a.nav-link[href='javascript:;']"

# Campo código do bilhete
"input[placeholder='Digite o código do bilhete']"

# Botão Buscar
"a.v-dialog-btn.success"

# Botão Apostar
"button.btn.text-style"

# Botão Sim (confirmação)
"a.v-dialog-btn.success"
```

## 📊 Monitoramento e Logs

### Logs da API

```bash
# Captura de bilhete
2025-08-22 11:46:31 - INFO - Capturando bilhete: n6e2er
2025-08-22 11:46:31 - INFO - Usando sessão existente
2025-08-22 11:46:31 - INFO - Capturando dados do bilhete: n6e2er
2025-08-22 11:46:54 - INFO - Dados capturados com sucesso para bilhete: n6e2er em 23.17s

# Confirmação de bilhete
2025-08-22 11:47:00 - INFO - Confirmando bilhete: n6e2er
2025-08-22 11:47:00 - INFO - Usando sessão existente
2025-08-22 11:47:00 - INFO - Confirmando bilhete: n6e2er
2025-08-22 11:47:15 - INFO - Bilhete confirmado com sucesso
```

### Métricas de Performance

- **Tempo médio de captura:** 20-25 segundos
- **Tempo médio de confirmação:** 10-15 segundos
- **Taxa de sucesso:** >95%

## 🚨 Tratamento de Erros

### Cenários de Erro

1. **Pagamento não aprovado**
   - Workflow para no IF de verificação
   - Não executa confirmação

2. **Bilhete não encontrado**
   - API retorna 404
   - Log de erro registrado

3. **Falha no login**
   - API retorna 401
   - Nova tentativa de login

4. **Erro na confirmação**
   - API retorna 400
   - Log detalhado do erro

### Recuperação Automática

- **Cache de sessão:** Reutiliza login por 5 minutos
- **Retry automático:** 3 tentativas em caso de erro
- **Fallback:** Logs detalhados para debug

## 🔐 Segurança

### Credenciais

- **Armazenamento:** Variáveis de ambiente
- **Rotação:** Senhas alteradas periodicamente
- **Acesso:** Restrito a IPs autorizados

### Validações

- **Código do bilhete:** Formato válido
- **Status do pagamento:** Apenas "approved"
- **Sessão ativa:** Login válido

## 📈 Monitoramento

### Métricas Importantes

- **Taxa de sucesso de confirmação**
- **Tempo médio de processamento**
- **Erros por tipo**
- **Uso de recursos**

### Alertas

- **Falha na confirmação**
- **Tempo de resposta alto**
- **Erro de autenticação**
- **Bilhete não encontrado**

## 🎯 Próximos Passos

1. **Implementar retry automático**
2. **Adicionar notificações por email/SMS**
3. **Dashboard de monitoramento**
4. **Logs estruturados (JSON)**
5. **Métricas em tempo real**

---

**Versão:** 1.0.0  
**Última atualização:** 2025-08-22  
**Responsável:** Felipe Castanheira

