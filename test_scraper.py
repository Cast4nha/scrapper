#!/usr/bin/env python3
"""
Script de teste para o ValSports Scraper
"""

import os
import sys
import json
from dotenv import load_dotenv

# Adicionar o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scraper.valsports_scraper import ValSportsScraper

def test_scraper():
    """Testa o funcionamento básico do scraper"""
    
    print("=== Teste do ValSports Scraper ===")
    
    # Carregar variáveis de ambiente
    load_dotenv()
    
    # Credenciais de teste (baseadas no Selenium IDE)
    username = "cairovinicius"
    password = "279999"
    
    # URL de teste (baseada no exemplo fornecido)
    test_url = "https://www.valsports.net/prebet/dmgkrn"
    
    scraper = None
    
    try:
        print("\n1. Inicializando scraper...")
        scraper = ValSportsScraper()
        print("✓ Scraper inicializado com sucesso")
        
        print("\n2. Fazendo login...")
        login_success = scraper.login(username, password)
        
        if login_success:
            print("✓ Login realizado com sucesso")
            
            print("\n3. Capturando dados do bilhete...")
            bet_data = scraper.scrape_bet_ticket(test_url)
            
            if bet_data:
                print("✓ Dados capturados com sucesso:")
                print(json.dumps(bet_data, indent=2, ensure_ascii=False))
                
                print("\n4. Testando confirmação de aposta...")
                # Teste com valor baixo
                confirmation_success = scraper.confirm_bet(test_url, 1.00)
                
                if confirmation_success:
                    print("✓ Confirmação de aposta funcionando")
                else:
                    print("⚠ Confirmação de aposta falhou (pode ser normal em ambiente de teste)")
            else:
                print("✗ Falha ao capturar dados do bilhete")
        else:
            print("✗ Falha no login")
            
    except Exception as e:
        print(f"✗ Erro durante o teste: {str(e)}")
        
    finally:
        if scraper:
            print("\n5. Fechando scraper...")
            scraper.close()
            print("✓ Scraper fechado")

if __name__ == "__main__":
    test_scraper()
