#!/usr/bin/env python3
"""
Teste específico para o bilhete TQE4X1
"""

import time
import logging
from scraper.valsports_scraper_final import ValSportsScraper

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_tqe4x1():
    """Teste específico para o bilhete TQE4X1"""
    print("🧪 TESTE ESPECÍFICO - BILHETE TQE4X1")
    print("=" * 50)
    
    scraper = ValSportsScraper()
    
    try:
        # Fazer login
        if scraper.login("cairovinicius", "279999"):
            print("✅ Login realizado com sucesso")
            
            # Testar bilhete TQE4X1
            bet_code = "TQE4X1"
            print(f"\n🎯 Testando bilhete: {bet_code}")
            
            result = scraper.scrape_bet_ticket(bet_code)
            
            if result:
                print(f"📊 Sucesso! {result['total_games']} jogos encontrados")
                print(f"💰 Total odds: {result['total_odds']}")
                print(f"🏆 Possível prêmio: {result['possible_prize']}")
                print(f"👤 Apostador: {result['bettor_name']}")
                print(f"💵 Valor: {result['bet_value']}")
                
                print("\n🎮 Jogos encontrados:")
                for i, game in enumerate(result['games'], 1):
                    print(f"   {i}. {game['teams']}")
                    print(f"      Liga: {game['league']}")
                    print(f"      Data: {game['datetime']}")
                    print(f"      Seleção: {game['selection']}")
                    print(f"      Odds: {game['odds']}")
                    print()
                
                print(f"🎯 Total de jogos capturados: {len(result['games'])}")
                
            else:
                print("❌ Falha ao capturar dados")
        else:
            print("❌ Falha no login")
    
    finally:
        scraper.close()

if __name__ == "__main__":
    test_tqe4x1()
