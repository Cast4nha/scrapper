#!/usr/bin/env python3
"""
Teste específico para o bilhete fc9x4a
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scraper.valsports_scraper_final import ValSportsScraper
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_fc9x4a():
    """Testa o bilhete fc9x4a"""
    
    print("🧪 TESTE ESPECÍFICO - BILHETE FC9X4A")
    print("=" * 50)
    
    # Criar instância do scraper
    scraper = ValSportsScraper()
    
    try:
        # Fazer login
        print("🔐 Fazendo login...")
        if scraper.login("cairovinicius", "279999"):
            print("✅ Login realizado com sucesso")
            
            # Testar bilhete fc9x4a
            bet_code = "fc9x4a"
            print(f"🎯 Testando bilhete: {bet_code}")
            
            # Extrair dados
            bet_data = scraper.scrape_bet_ticket(bet_code)
            
            if bet_data:
                print("✅ Dados extraídos com sucesso!")
                print(f"📊 Total de jogos: {bet_data.get('total_games', 0)}")
                print(f"💰 Total odds: {bet_data.get('total_odds', 'N/A')}")
                print(f"🏆 Possível prêmio: {bet_data.get('possible_prize', 'N/A')}")
                print(f"👤 Apostador: {bet_data.get('bettor_name', 'N/A')}")
                print(f"💵 Valor: {bet_data.get('bet_value', 'N/A')}")
                
                games = bet_data.get('games', [])
                print(f"\n🎮 Jogos encontrados: {len(games)}")
                
                for i, game in enumerate(games, 1):
                    print(f"\n🎯 Jogo {i}:")
                    print(f"   Liga: {game.get('league', 'N/A')}")
                    print(f"   Times: {game.get('teams', 'N/A')}")
                    print(f"   Data/Hora: {game.get('datetime', 'N/A')}")
                    print(f"   Seleção: {game.get('selection', 'N/A')}")
                    print(f"   Odds: {game.get('odds', 'N/A')}")
            else:
                print("❌ Falha ao extrair dados")
        else:
            print("❌ Falha no login")
            
    except Exception as e:
        print(f"❌ Erro durante o teste: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Fechar driver
        if hasattr(scraper, 'driver') and scraper.driver:
            scraper.driver.quit()
            print("🔒 Driver fechado")

if __name__ == "__main__":
    test_fc9x4a()
