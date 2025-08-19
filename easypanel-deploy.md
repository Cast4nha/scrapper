# Deploy no EasyPanel - Upload de Arquivos

## 📦 **Passo a Passo para Deploy**

### 1. **Preparação dos Arquivos**
✅ **Arquivo ZIP criado**: `valsports-scraper.zip` (35.7 KB)
✅ **Contém todos os arquivos necessários**

### 2. **No EasyPanel**

#### **A) Criar Novo Projeto**
1. Acesse o EasyPanel
2. Clique em **"Novo Projeto"**
3. Selecione **"Upload de Arquivos"**
4. Nome do projeto: `valsports`

#### **B) Upload do Arquivo**
1. Clique em **"Escolher Arquivo"**
2. Selecione: `valsports-scraper.zip`
3. Aguarde o upload completar

#### **C) Configuração do Docker**
1. **Tipo**: `Dockerfile`
2. **Porta**: `5000`
3. **Build Command**: (deixar padrão)
4. **Start Command**: (deixar padrão)

### 3. **Variáveis de Ambiente**

Configure as seguintes variáveis:

```bash
# Configurações do ValSports
VALSORTS_USERNAME=cairovinicius
VALSORTS_PASSWORD=279999

# Configurações do Servidor
PORT=5000
DEBUG=false
LOG_LEVEL=INFO

# Configurações do Selenium
HEADLESS=true
BROWSER_TIMEOUT=30
PAGE_LOAD_TIMEOUT=20
```

### 4. **Configuração de Domínio**

- **Domínio**: `valsports.qobebrasil.com.br`
- **SSL**: Ativar (se disponível)
- **Proxy**: Configurar para porta 5000

### 5. **Deploy**

1. Clique em **"Deploy"**
2. Aguarde o build completar
3. Verifique os logs de build

### 6. **Teste da Aplicação**

Após o deploy bem-sucedido:

```bash
# Teste de saúde
curl https://valsports.qobebrasil.com.br/health

# Teste de captura de dados
curl -X POST https://valsports.qobebrasil.com.br/api/scrape-bet \
  -H "Content-Type: application/json" \
  -d '{"bet_code": "dmgkrn"}'
```

## 🔧 **Troubleshooting**

### **Se o build falhar:**
1. Verifique os logs de build
2. Confirme que o Dockerfile está correto
3. Verifique se todas as dependências estão no requirements.txt

### **Se a aplicação não responder:**
1. Verifique os logs da aplicação
2. Confirme as variáveis de ambiente
3. Teste localmente primeiro

### **Se der erro 502:**
1. Verifique se a porta está correta
2. Confirme se o domínio está configurado
3. Verifique os logs de proxy/reverse proxy

## 📋 **Arquivos Incluídos no ZIP**

- ✅ `Dockerfile` - Configuração do container
- ✅ `requirements.txt` - Dependências Python
- ✅ `app.py` - Aplicação Flask
- ✅ `scraper/` - Módulo de scraping
- ✅ `README.md` - Documentação
- ✅ `n8n_integration.md` - Integração n8n
- ✅ Scripts de teste e debug

## 🚀 **Vantagens desta Abordagem**

1. **Controle total** sobre o código
2. **Debug mais fácil** - logs locais
3. **Atualizações simples** - novo ZIP
4. **Sem dependência** de registros externos
5. **Build personalizado** para o ambiente
