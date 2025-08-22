#!/usr/bin/env python3
"""
Configuração para o Scraper Híbrido ValSports
"""

import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configurações do ScrapingDog
SCRAPINGDOG_API_KEY = os.getenv('SCRAPINGDOG_API_KEY')

# Configurações do ValSports
VALSPORTS_USERNAME = os.getenv('VALSPORTS_USERNAME', 'cairovinicius')
VALSPORTS_PASSWORD = os.getenv('VALSPORTS_PASSWORD', '279999')

# Configurações do sistema
BASE_URL = "https://www.valsports.net"
TIMEOUT = 60
WAIT_TIME = 5000  # 5 segundos para renderização JS

# Headers para requisições
DEFAULT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}

def validate_config():
    """Valida se todas as configurações necessárias estão presentes"""
    missing_configs = []
    
    if not SCRAPINGDOG_API_KEY:
        missing_configs.append("SCRAPINGDOG_API_KEY")
    
    if not VALSPORTS_USERNAME:
        missing_configs.append("VALSPORTS_USERNAME")
    
    if not VALSPORTS_PASSWORD:
        missing_configs.append("VALSPORTS_PASSWORD")
    
    if missing_configs:
        print("❌ Configurações ausentes:")
        for config in missing_configs:
            print(f"   - {config}")
        print("\n📝 Configure no arquivo .env:")
        print("SCRAPINGDOG_API_KEY=sua_chave_aqui")
        print("VALSPORTS_USERNAME=seu_usuario")
        print("VALSPORTS_PASSWORD=sua_senha")
        return False
    
    return True

def get_scrapingdog_params(bet_url):
    """Retorna parâmetros para requisição do ScrapingDog"""
    return {
        'api_key': SCRAPINGDOG_API_KEY,
        'url': bet_url,
        'render': 'true',      # Renderização JavaScript
        'wait': str(WAIT_TIME), # Aguardar carregamento
        'country': 'br',       # Proxy do Brasil
        'premium': 'true'      # Usar proxy premium
    }
