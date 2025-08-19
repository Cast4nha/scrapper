#!/usr/bin/env python3
"""
Script de teste que executa o fluxo completo baseado no Selenium IDE
"""

import os
import sys
import json
import time
from dotenv import load_dotenv

# Adicionar o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scraper.valsports_scraper import ValSportsScraper

def test_complete_flow():
    """Testa o fluxo completo de login e captura de dados"""
    
    print("🔍 Teste do Fluxo Completo - ValSports")
    print("=" * 50)
    
    # Carregar variáveis de ambiente
    load_dotenv()
    
    # Credenciais e código do bilhete
    username = "cairovinicius"
    password = "279999"
    bet_code = "dmgkrn"
    
    scraper = None
    
    try:
        print("\n1. Inicializando scraper...")
        scraper = ValSportsScraper()
        print("✓ Scraper inicializado")
        
        print("\n2. Executando login...")
        login_success = scraper.login(username, password)
        
        if login_success:
            print("✅ Login realizado com sucesso")
            
            print(f"\n3. Capturando dados do bilhete: {bet_code}")
            bet_data = scraper.scrape_bet_ticket(bet_code)
            
            if bet_data:
                print("✅ Dados capturados com sucesso!")
                print("\n📊 Dados do Bilhete:")
                print(json.dumps(bet_data, indent=2, ensure_ascii=False))
                
                # Salvar screenshot
                scraper.driver.save_screenshot("complete_flow_success.png")
                print("\n📸 Screenshot salvo como complete_flow_success.png")
                
                return True
            else:
                print("❌ Falha ao capturar dados do bilhete")
                return False
        else:
            print("❌ Falha no login")
            return False
            
    except Exception as e:
        print(f"❌ Erro durante teste: {str(e)}")
        return False
        
    finally:
        if scraper:
            print("\n4. Fechando scraper...")
            scraper.close()
            print("✓ Scraper fechado")

if __name__ == "__main__":
    success = test_complete_flow()
    if success:
        print("\n🎉 Fluxo completo executado com sucesso!")
        print("   O sistema está funcionando corretamente")
    else:
        print("\n❌ Fluxo completo falhou")
        print("   Verifique os logs para identificar o problema")
