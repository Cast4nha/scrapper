# 🚀 Guia de Deploy no EasyPanel - ValSports Scraper

## 📋 Configuração via GitHub

### **1. Configurações Básicas**
- **Tipo**: `GitHub Repository`
- **Repository**: Seu repositório GitHub
- **Branch**: `main`
- **Root Directory**: `/` (raiz do projeto)

### **2. Build Settings**
```bash
# Build Command (deixe vazio para usar Dockerfile padrão)
# O EasyPanel detectará automaticamente o Dockerfile

# Start Command (opcional - o Dockerfile já define)
gunicorn --bind 0.0.0.0:5000 --workers 1 --timeout 300 app:app
```

### **3. Environment Variables**
```bash
VALSORTS_USERNAME=cairovinicius
VALSORTS_PASSWORD=279999
PORT=5000
DEBUG=false
HEADLESS=true
LOG_LEVEL=INFO
```

### **4. Port Configuration**
- **Container Port**: `5000`
- **Host Port**: `5000` (ou deixar automático)

### **5. Domínios Configurados**
- ✅ `https://valsports.qobebrasil.com.br/`
- ✅ `https://www.valsports.qobebrasil.com.br/`

## 🔧 Troubleshooting

### **Problema: Serviço para logo após iniciar**
**Solução**: Verificar se o Dockerfile está correto e se todas as dependências estão instaladas.

### **Problema: Erro 504 Gateway Timeout**
**Solução**: 
1. Verificar se o container está rodando
2. Verificar logs do container
3. Verificar configuração de portas

### **Problema: ModuleNotFoundError**
**Solução**: Garantir que o `requirements.txt` está sendo instalado corretamente.

## 📝 Logs de Debug

### **Verificar logs do container:**
```bash
# No EasyPanel, vá em "Logs" para ver os logs em tempo real
```

### **Teste local da imagem:**
```bash
docker run --rm -p 5000:5000 \
  -e VALSORTS_USERNAME=cairovinicius \
  -e VALSORTS_PASSWORD=279999 \
  -e PORT=5000 \
  -e DEBUG=false \
  -e HEADLESS=true \
  c4st4nha/valsports-scraper:latest
```

## 🎯 Testes Pós-Deploy

### **1. Teste de Saúde**
```bash
curl https://valsports.qobebrasil.com.br/health
```

### **2. Teste de Captura de Dados**
```bash
curl -X POST https://valsports.qobebrasil.com.br/api/scrape-bet \
  -H "Content-Type: application/json" \
  -d '{"bet_code": "dmgkrn"}'
```

### **3. Teste de Confirmação**
```bash
curl -X POST https://valsports.qobebrasil.com.br/api/confirm-bet \
  -H "Content-Type: application/json" \
  -d '{"bet_code": "dmgkrn"}'
```

## ✅ Checklist de Deploy

- [ ] Repositório GitHub atualizado
- [ ] Dockerfile correto no repositório
- [ ] requirements.txt atualizado
- [ ] Environment variables configuradas
- [ ] Portas configuradas corretamente
- [ ] Domínios configurados
- [ ] Deploy executado com sucesso
- [ ] Testes de API funcionando

## 🆘 Suporte

Se houver problemas:
1. Verificar logs no EasyPanel
2. Testar imagem localmente
3. Verificar configurações de rede/porta
4. Verificar se todas as dependências estão instaladas
