#!/usr/bin/env python3
"""
Script de validação do setup do ValSports Scraper
Verifica se todas as dependências e configurações estão corretas
"""

import os
import sys
import importlib
import subprocess
import requests
import json
from pathlib import Path

def check_python_version():
    """Verifica se a versão do Python é compatível"""
    print("🐍 Verificando versão do Python...")
    
    version = sys.version_info
    if version.major == 3 and version.minor >= 11:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - Versão 3.11+ requerida")
        return False

def check_dependencies():
    """Verifica se todas as dependências estão instaladas"""
    print("\n📦 Verificando dependências...")
    
    required_packages = [
        'selenium',
        'flask',
        'flask_cors',
        'requests',
        'beautifulsoup4',
        'python_dotenv',
        'gunicorn',
        'lxml'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            importlib.import_module(package.replace('-', '_'))
            print(f"✅ {package} - OK")
        except ImportError:
            print(f"❌ {package} - Não encontrado")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  Pacotes faltando: {', '.join(missing_packages)}")
        print("Execute: pip install -r requirements.txt")
        return False
    
    return True

def check_files():
    """Verifica se todos os arquivos necessários existem"""
    print("\n📁 Verificando arquivos do projeto...")
    
    required_files = [
        'app.py',
        'requirements.txt',
        'Dockerfile',
        'docker-compose.yml',
        'README.md',
        'scraper/__init__.py',
        'scraper/valsports_scraper.py'
    ]
    
    missing_files = []
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path} - OK")
        else:
            print(f"❌ {file_path} - Não encontrado")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n⚠️  Arquivos faltando: {', '.join(missing_files)}")
        return False
    
    return True

def check_environment():
    """Verifica configurações de ambiente"""
    print("\n⚙️  Verificando configurações de ambiente...")
    
    # Verificar se arquivo .env existe
    if os.path.exists('.env'):
        print("✅ Arquivo .env - OK")
    else:
        print("⚠️  Arquivo .env não encontrado (copie config.env.example)")
    
    # Verificar variáveis de ambiente
    env_vars = ['PORT', 'DEBUG', 'HEADLESS', 'LOG_LEVEL']
    for var in env_vars:
        value = os.environ.get(var)
        if value:
            print(f"✅ {var}={value} - OK")
        else:
            print(f"⚠️  {var} - Não definida (usando padrão)")
    
    return True

def check_chrome():
    """Verifica se o Chrome está disponível"""
    print("\n🌐 Verificando Google Chrome...")
    
    try:
        # Tentar executar chrome --version
        result = subprocess.run(['google-chrome', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ Chrome encontrado: {result.stdout.strip()}")
            return True
        else:
            print("❌ Chrome não encontrado")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("❌ Chrome não encontrado ou não acessível")
        return False

def test_api_endpoints():
    """Testa os endpoints da API"""
    print("\n🔌 Testando endpoints da API...")
    
    base_url = "http://localhost:5000"
    
    try:
        # Testar health check
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            print("✅ Health check - OK")
            data = response.json()
            print(f"   Status: {data.get('status')}")
            print(f"   Versão: {data.get('version')}")
        else:
            print(f"❌ Health check - Erro {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ API não está rodando (execute: python app.py)")
        return False
    except Exception as e:
        print(f"❌ Erro ao testar API: {str(e)}")
        return False
    
    return True

def check_docker():
    """Verifica se o Docker está disponível"""
    print("\n🐳 Verificando Docker...")
    
    try:
        result = subprocess.run(['docker', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ Docker encontrado: {result.stdout.strip()}")
            return True
        else:
            print("❌ Docker não encontrado")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("❌ Docker não encontrado ou não acessível")
        return False

def main():
    """Função principal de validação"""
    print("🔍 Validação do Setup - ValSports Scraper")
    print("=" * 50)
    
    checks = [
        check_python_version(),
        check_dependencies(),
        check_files(),
        check_environment(),
        check_chrome(),
        check_docker()
    ]
    
    print("\n" + "=" * 50)
    
    if all(checks):
        print("🎉 Todas as verificações passaram!")
        print("\n📋 Próximos passos:")
        print("1. Configure o arquivo .env com suas credenciais")
        print("2. Execute: python test_scraper.py")
        print("3. Execute: python app.py")
        print("4. Teste a API em: http://localhost:5000/health")
        
        # Perguntar se quer testar a API
        try:
            response = input("\n🤔 Quer testar a API agora? (s/n): ").lower()
            if response in ['s', 'sim', 'y', 'yes']:
                test_api_endpoints()
        except KeyboardInterrupt:
            print("\n👋 Validação interrompida")
            
    else:
        print("❌ Algumas verificações falharam")
        print("\n🔧 Corrija os problemas acima e execute novamente")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
