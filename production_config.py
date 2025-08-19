#!/usr/bin/env python3
"""
Configurações para produção
"""

import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

class ProductionConfig:
    """Configurações para ambiente de produção"""
    
    # Configurações do servidor
    HOST = '0.0.0.0'
    PORT = int(os.getenv('PORT', 5000))
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # Configurações do Selenium
    HEADLESS = os.getenv('HEADLESS', 'True').lower() == 'true'
    BROWSER_TIMEOUT = int(os.getenv('BROWSER_TIMEOUT', 30))
    PAGE_LOAD_TIMEOUT = int(os.getenv('PAGE_LOAD_TIMEOUT', 20))
    
    # Configurações de logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', '/var/log/valsports-scraper.log')
    
    # Configurações de segurança
    API_KEY = os.getenv('API_KEY')
    MAX_REQUESTS_PER_MINUTE = int(os.getenv('MAX_REQUESTS_PER_MINUTE', 60))
    
    # Configurações do ValSports
    VALSORTS_USERNAME = os.getenv('VALSORTS_USERNAME')
    VALSORTS_PASSWORD = os.getenv('VALSORTS_PASSWORD')
    
    # Configurações de retry
    MAX_RETRIES = int(os.getenv('MAX_RETRIES', 3))
    RETRY_DELAY = int(os.getenv('RETRY_DELAY', 5))
    
    # Configurações de cache
    CACHE_ENABLED = os.getenv('CACHE_ENABLED', 'True').lower() == 'true'
    CACHE_TTL = int(os.getenv('CACHE_TTL', 300))  # 5 minutos
    
    @classmethod
    def validate(cls):
        """Validar configurações obrigatórias"""
        required_vars = [
            'VALSORTS_USERNAME',
            'VALSORTS_PASSWORD'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not getattr(cls, var):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(f"Variáveis de ambiente obrigatórias não definidas: {', '.join(missing_vars)}")
        
        return True
    
    @classmethod
    def get_browser_options(cls):
        """Obter opções do navegador para produção"""
        return {
            'headless': cls.HEADLESS,
            'timeout': cls.BROWSER_TIMEOUT,
            'page_load_timeout': cls.PAGE_LOAD_TIMEOUT
        }
