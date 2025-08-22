#!/usr/bin/env python3
"""
Teste Simples do Scraper Híbrido
"""

import os
import sys
from scraper_hybrid import HybridValSportsScraper
from config_hybrid import validate_config

def main():
    print("🧪 TESTE SIMPLES DO SCRAPER HÍBRIDO")
    print("=" * 50)
    
    # Validar configurações
    if not validate_config():
        sys.exit(1)
    
    # Criar scraper
    scraper = HybridValSportsScraper()
    
    try:
        # Fazer login
        print("🔐 Fazendo login...")
        if scraper.login_with_selenium(
            os.getenv('VALSPORTS_USERNAME'),
            os.getenv('VALSPORTS_PASSWORD')
        ):
            print("✅ Login realizado com sucesso")
            
            # Testar um bilhete
            bet_code = input("🎯 Digite o código do bilhete para testar: ").strip()
            
            if bet_code:
                print(f"📊 Capturando bilhete: {bet_code}")
                result = scraper.scrape_with_scrapingdog(bet_code)
                
                if result:
                    print(f"✅ Sucesso! {result['total_games']} jogos encontrados")
                    print(f"💰 Total odds: {result['total_odds']}")
                    print(f"🏆 Possível prêmio: {result['possible_prize']}")
                    print(f"👤 Apostador: {result['bettor_name']}")
                    print(f"💵 Valor: {result['bet_value']}")
                    
                    print("\n🎮 Jogos:")
                    for i, game in enumerate(result['games'], 1):
                        print(f"   {i}. {game['teams']} - {game['selection']} ({game['odds']})")
                else:
                    print("❌ Falha ao capturar dados")
            else:
                print("❌ Código do bilhete não informado")
        else:
            print("❌ Falha no login")
    
    finally:
        scraper.close()

if __name__ == "__main__":
    main()
