#!/usr/bin/env python3
"""
Teste focado apenas na extração de dados do bilhete TQE4X1
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scraper.valsports_scraper_final import ValSportsScraper
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_extraction_only():
    """Testa apenas a extração de dados sem login"""
    
    print("🧪 TESTE DE EXTRAÇÃO - BILHETE TQE4X1")
    print("=" * 50)
    
    # Criar instância do scraper
    scraper = ValSportsScraper()
    
    try:
        # Simular que já está logado
        scraper.is_logged_in = True
        
        # Testar bilhete TQE4X1
        bet_code = "TQE4X1"
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
    test_extraction_only()
