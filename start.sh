#!/bin/bash

# Script de inicialização do ValSports Scraper
# Este script facilita o deploy e execução da aplicação

set -e

echo "🚀 Iniciando ValSports Scraper API..."

# Verificar se o Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado. Por favor, instale o Python 3.11+"
    exit 1
fi

# Verificar se o pip está instalado
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 não encontrado. Por favor, instale o pip"
    exit 1
fi

# Verificar se o arquivo requirements.txt existe
if [ ! -f "requirements.txt" ]; then
    echo "❌ Arquivo requirements.txt não encontrado"
    exit 1
fi

# Criar diretório de logs se não existir
mkdir -p logs

# Verificar se existe ambiente virtual
if [ ! -d "venv" ]; then
    echo "📦 Criando ambiente virtual..."
    python3 -m venv venv
fi

# Ativar ambiente virtual
echo "🔧 Ativando ambiente virtual..."
source venv/bin/activate

# Instalar/atualizar dependências
echo "📥 Instalando dependências..."
pip install --upgrade pip
pip install -r requirements.txt

# Verificar se o arquivo .env existe
if [ ! -f ".env" ]; then
    echo "⚠️  Arquivo .env não encontrado. Copiando exemplo..."
    if [ -f "config.env.example" ]; then
        cp config.env.example .env
        echo "📝 Arquivo .env criado. Por favor, configure as variáveis de ambiente."
    else
        echo "❌ Arquivo config.env.example não encontrado"
        exit 1
    fi
fi

# Carregar variáveis de ambiente
if [ -f ".env" ]; then
    echo "⚙️  Carregando variáveis de ambiente..."
    export $(cat .env | grep -v '^#' | xargs)
fi

# Verificar se a porta está disponível
PORT=${PORT:-5000}
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  Porta $PORT já está em uso. Tentando usar porta alternativa..."
    PORT=$((PORT + 1))
    echo "🔧 Usando porta $PORT"
fi

echo "✅ Configuração concluída!"
echo "🌐 API será iniciada na porta $PORT"
echo "📊 Health check: http://localhost:$PORT/health"
echo ""

# Iniciar a aplicação
echo "🚀 Iniciando aplicação..."
python app.py
