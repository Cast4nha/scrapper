#!/usr/bin/env python3
"""
Script para testar a confirmação de aposta
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scraper.valsports_scraper import ValSportsScraper
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_confirm_bet():
    """Testar confirmação de aposta"""
    print("🔍 Teste de Confirmação de Aposta - ValSports")
    print("=" * 50)
    
    # Credenciais
    username = "cairovinicius"
    password = "279999"
    bet_code = "dmgkrn"
    
    scraper = None
    try:
        # 1. Inicializar scraper
        print("1. Inicializando scraper...")
        scraper = ValSportsScraper()
        print("✓ Scraper inicializado")
        
        # 2. Fazer login
        print("\n2. Executando login...")
        if scraper.login(username, password):
            print("✅ Login realizado com sucesso")
        else:
            print("❌ Falha no login")
            return
        
        # 3. Capturar dados do bilhete primeiro
        print(f"\n3. Capturando dados do bilhete: {bet_code}")
        bet_data = scraper.scrape_bet_ticket(bet_code)
        if bet_data:
            print("✅ Dados capturados com sucesso!")
            print(f"📊 Valor da aposta: {bet_data.get('bet_value', 'N/A')}")
            print(f"📊 Nome do apostador: {bet_data.get('bettor_name', 'N/A')}")
        else:
            print("❌ Falha ao capturar dados")
            return
        
        # 4. Confirmar aposta
        print(f"\n4. Confirmando aposta: {bet_code}")
        if scraper.confirm_bet(bet_code):
            print("✅ Aposta confirmada com sucesso!")
            print("📸 Screenshot salvo como bet_confirmed.png")
        else:
            print("❌ Falha ao confirmar aposta")
            print("📸 Screenshots de erro salvos para debug")
            return
        
        print("\n🎉 Teste de confirmação concluído com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro geral: {str(e)}")
    finally:
        if scraper:
            print("\n5. Fechando scraper...")
            scraper.close()
            print("✓ Scraper fechado")

if __name__ == "__main__":
    test_confirm_bet()
