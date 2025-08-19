# Deploy no EasyPanel - ValSports Scraper

## 📋 Pré-requisitos

- Conta ativa no EasyPanel
- Acesso ao painel de controle
- Docker habilitado no projeto

## 🚀 Passo a Passo

### 1. Preparação do Código

```bash
# Clone o repositório no seu servidor local
git clone <seu-repositorio>
cd scrapper

# Teste localmente (opcional)
./start.sh
```

### 2. Configuração no EasyPanel

#### 2.1 Criar Novo Projeto

1. Acesse o painel do EasyPanel
2. Clique em "New Project"
3. Selecione "Docker" como tipo de projeto
4. Escolha "Git Repository" como fonte

#### 2.2 Configurar Repositório

- **Repository URL**: URL do seu repositório Git
- **Branch**: `main` ou `master`
- **Dockerfile Path**: `Dockerfile`

#### 2.3 Configurar Variáveis de Ambiente

Adicione as seguintes variáveis:

```env
PORT=5000
DEBUG=False
HEADLESS=True
LOG_LEVEL=INFO
```

#### 2.4 Configurar Portas

- **Port**: `5000`
- **Protocol**: `HTTP`

#### 2.5 Configurar Health Check

- **Path**: `/health`
- **Interval**: `30s`
- **Timeout**: `10s`
- **Retries**: `3`
- **Start Period**: `40s`

### 3. Configurações Avançadas

#### 3.1 Recursos Recomendados

- **Memory**: 1GB mínimo (2GB recomendado)
- **CPU**: 1 vCPU mínimo
- **Storage**: 10GB mínimo

#### 3.2 Configurações de Rede

- **Domain**: Configure um domínio personalizado (opcional)
- **SSL**: Habilite SSL automático
- **Proxy**: Configure proxy reverso se necessário

### 4. Deploy

#### 4.1 Primeiro Deploy

1. Clique em "Deploy"
2. Aguarde a construção da imagem Docker
3. Verifique os logs para identificar possíveis erros
4. Teste o endpoint de health check

#### 4.2 Verificação

```bash
# Teste o health check
curl https://seu-dominio.com/health

# Resposta esperada:
{
  "status": "healthy",
  "service": "valsports-scraper-api",
  "version": "1.0.0"
}
```

### 5. Configuração de Logs

#### 5.1 Acessar Logs

1. No painel do EasyPanel, vá para o projeto
2. Clique em "Logs"
3. Monitore os logs em tempo real

#### 5.2 Logs Importantes

- **Startup**: Verificar se o Chrome foi instalado corretamente
- **Login**: Verificar se o login está funcionando
- **Scraping**: Verificar se os dados estão sendo capturados

### 6. Monitoramento

#### 6.1 Métricas Básicas

- **CPU Usage**: Deve ficar abaixo de 80%
- **Memory Usage**: Deve ficar abaixo de 1.5GB
- **Response Time**: Deve ser menor que 30s

#### 6.2 Alertas

Configure alertas para:
- CPU > 80%
- Memory > 1.5GB
- Health check falhando
- Response time > 30s

### 7. Troubleshooting

#### 7.1 Problemas Comuns

**Erro: Chrome não encontrado**
```bash
# Verificar se o Chrome foi instalado
docker exec -it <container-id> google-chrome --version
```

**Erro: Driver não encontrado**
```bash
# Verificar se o chromedriver está funcionando
docker exec -it <container-id> chromedriver --version
```

**Erro: Timeout no scraping**
- Aumentar timeout no código
- Verificar conexão com internet
- Verificar se o site está respondendo

#### 7.2 Logs de Debug

Para ativar logs detalhados:

```env
DEBUG=True
LOG_LEVEL=DEBUG
```

### 8. Backup e Recuperação

#### 8.1 Backup

1. Configure backup automático do código
2. Mantenha backup das variáveis de ambiente
3. Documente configurações específicas

#### 8.2 Recuperação

1. Restaure o código do backup
2. Reconfigure variáveis de ambiente
3. Refaça o deploy

### 9. Segurança

#### 9.1 Configurações Recomendadas

- Use HTTPS sempre
- Configure firewall adequado
- Mantenha dependências atualizadas
- Use variáveis de ambiente para credenciais

#### 9.2 Monitoramento de Segurança

- Monitore logs de acesso
- Configure alertas para tentativas de acesso não autorizado
- Mantenha backup de segurança

### 10. Manutenção

#### 10.1 Atualizações

1. Faça backup antes de atualizar
2. Teste em ambiente de desenvolvimento
3. Atualize em horário de baixo tráfego
4. Monitore após a atualização

#### 10.2 Limpeza

- Limpe logs antigos regularmente
- Remova imagens Docker não utilizadas
- Mantenha espaço em disco adequado

## 📞 Suporte

Para problemas específicos do EasyPanel:
- Consulte a documentação oficial
- Entre em contato com o suporte técnico
- Verifique fóruns da comunidade

---

**Nota**: Este guia assume que você tem conhecimento básico do EasyPanel. Para dúvidas específicas, consulte a documentação oficial da plataforma.
