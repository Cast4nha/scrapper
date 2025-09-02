# 🚀 INSTRUÇÕES DE DEPLOY - ValSports Capture Service

## 📋 **Arquivos Criados para o Deploy:**

### 1. **Dockerfile** ✅
- Imagem base: Python 3.9-slim
- Firefox ESR + GeckoDriver para Selenium
- Otimizado para produção

### 2. **requirements.txt** ✅
- Todas as dependências Python necessárias
- Versões fixas para estabilidade

### 3. **.dockerignore** ✅
- Otimiza o build excluindo arquivos desnecessários
- Reduz o tamanho da imagem final

### 4. **easypanel.yml** ✅
- Configuração Docker Compose para EasyPanel
- Variáveis de ambiente configuráveis

## 🔧 **Configurações do EasyPanel:**

### **Variáveis de Ambiente:**
```bash
VALSORTS_USERNAME=cairovinicius
VALSORTS_PASSWORD=279999
PORT=5000
DEBUG=false
HEADLESS=true
```

### **Porta:**
- **Porta Interna:** 5000
- **Porta Externa:** 5000 (configurável)

### **Health Check:**
- Endpoint: `/health`
- Intervalo: 30s
- Timeout: 10s
- Retries: 3

## 🚀 **Passos para Deploy:**

### 1. **Fazer Commit dos Arquivos:**
```bash
git add .
git commit -m "🚀 PREPARANDO DEPLOY: Dockerfile e configurações para EasyPanel"
git push origin main
```

### 2. **No EasyPanel:**
- Verificar se o repositório foi atualizado
- O build deve funcionar agora com o Dockerfile
- Aguardar a conclusão do build

### 3. **Verificar Deploy:**
- Testar o endpoint de health: `https://seu-dominio.com/health`
- Testar captura de bilhete: `https://seu-dominio.com/capture/6nv51x`

## 📊 **Endpoints Disponíveis:**

### **Health Check:**
```
GET /health
```

### **Captura de Bilhete:**
```
POST /capture/{bet_code}
GET /capture/{bet_code}
POST /api/capture-bet
```

## ⚠️ **Observações Importantes:**

1. **Firefox Headless:** Configurado para execução sem interface gráfica
2. **Logs:** Salvos em volume Docker para persistência
3. **Restart Policy:** `unless-stopped` para alta disponibilidade
4. **Health Check:** Monitoramento automático do serviço

## 🎯 **Próximos Passos:**

1. ✅ Fazer commit e push dos arquivos
2. 🔄 Aguardar build no EasyPanel
3. 🧪 Testar endpoints em produção
4. 📈 Monitorar performance e logs

---

**Status:** 🚀 **PRONTO PARA DEPLOY!**
