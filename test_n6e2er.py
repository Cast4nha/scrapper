#!/usr/bin/env python3
"""
Teste específico para o bilhete n6e2er
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scraper.valsports_scraper_final import ValSportsScraper
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_n6e2er():
    """Testa o bilhete n6e2er"""
    
    print("🧪 TESTE ESPECÍFICO - BILHETE N6E2ER")
    print("=" * 50)
    
    # Criar instância do scraper
    scraper = ValSportsScraper()
    
    try:
        # Fazer login
        print("🔐 Fazendo login...")
        if scraper.login("cairovinicius", "279999"):
            print("✅ Login realizado com sucesso")
            
            # Testar bilhete n6e2er
            bet_code = "n6e2er"
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
                    
                    # Mostrar todas as apostas do jogo
                    selections = game.get('selections', [])
                    odds_list = game.get('odds_list', [])
                    
                    if selections and odds_list:
                        for j, (selection, odds) in enumerate(zip(selections, odds_list), 1):
                            print(f"   Aposta {j}: {selection} - Odds: {odds}")
                    else:
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
    test_n6e2er()
