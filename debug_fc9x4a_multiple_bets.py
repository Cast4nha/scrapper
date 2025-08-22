#!/usr/bin/env python3
"""
Debug das apostas múltiplas do bilhete fc9x4a
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scraper.valsports_scraper_final import ValSportsScraper
import logging
from selenium.webdriver.common.by import By
import re

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def debug_fc9x4a_multiple_bets():
    """Debug das apostas múltiplas do bilhete fc9x4a"""
    
    print("🔍 DEBUG DAS APOSTAS MÚLTIPLAS - BILHETE FC9X4A")
    print("=" * 60)
    
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
            
            # Navegar para o bilhete
            bet_url = f"{scraper.base_url}/prebet/{bet_code}"
            scraper.driver.get(bet_url)
            
            # Aguardar carregamento
            import time
            time.sleep(5)
            
            print("\n🔍 ANALISANDO ELEMENTOS COM APOSTAS...")
            print("=" * 60)
            
            # Encontrar todos os elementos .l-item.d-block
            all_items = scraper.driver.find_elements(By.CSS_SELECTOR, ".l-item.d-block")
            print(f"📊 Total de elementos .l-item.d-block encontrados: {len(all_items)}")
            
            # Analisar apenas os elementos após o índice 10
            valid_items = all_items[10:]
            print(f"📊 Elementos válidos (após índice 10): {len(valid_items)}")
            
            current_game = None
            game_counter = 0
            
            for i, item in enumerate(valid_items):
                try:
                    full_text = item.text
                    
                    # Verificar se tem dados essenciais
                    has_selection = any(keyword in full_text for keyword in ['Vencedor:', 'Empate', 'Ambas equipes marcam', 'Mais de', 'Menos de', 'Gols', 'Corner', 'Cartão', 'Jogador'])
                    has_odds = bool(re.search(r'\b\d+\.\d+\b', full_text))
                    
                    if not has_selection or not has_odds:
                        continue
                    
                    print(f"\n📝 Elemento {i+1}:")
                    print(f"   Texto completo: {full_text}")
                    
                    # Verificar se é um novo jogo
                    league_keywords = ['América do Sul:', 'CONCACAF:', 'Costa Rica:', 'Venezuela:', 'Inglaterra:', 'Brasil:', 'Espanha:', 'Itália:', 'Alemanha:', 'Argentina:', 'Uruguai:', 'Colômbia:', 'Chile:', 'Peru:', 'Equador:', 'Bolívia:', 'Paraguai:', 'UEFA:', 'Copa Libertadores', 'Copa Sul Americana', 'Champions League', 'Europa League', 'Premier League', 'La Liga', 'Serie A', 'Bundesliga', 'Brasileirão', 'Copa do Brasil', 'Copa do Nordeste', 'Primeira Liga', 'Série A', 'Série B', 'Série C', 'Série D']
                    has_league = any(keyword in full_text for keyword in league_keywords)
                    has_teams = ' x ' in full_text
                    
                    if has_league and has_teams:
                        game_counter += 1
                        current_game = f"Jogo {game_counter}"
                        print(f"   🎮 {current_game} (NOVO JOGO)")
                    else:
                        print(f"   🎯 Aposta adicional do {current_game}")
                    
                    # Extrair seleção e odds
                    lines = full_text.split('\n')
                    selection = ""
                    odds = ""
                    
                    for line in lines:
                        line = line.strip()
                        if any(keyword in line for keyword in ['Vencedor:', 'Empate', 'Ambas equipes marcam', 'Mais de', 'Menos de', 'Gols', 'Corner', 'Cartão', 'Jogador']):
                            selection = line
                        elif re.search(r'^\d+\.\d+$', line):
                            odds = line
                    
                    if selection and odds:
                        print(f"   ✅ Seleção: {selection}")
                        print(f"   ✅ Odds: {odds}")
                    else:
                        print(f"   ❌ Não conseguiu extrair seleção/odds")
                        
                except Exception as e:
                    print(f"   ❌ Erro ao analisar elemento {i+1}: {str(e)}")
            
        else:
            print("❌ Falha no login")
            
    except Exception as e:
        print(f"❌ Erro durante o debug: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Fechar driver
        if hasattr(scraper, 'driver') and scraper.driver:
            scraper.driver.quit()
            print("🔒 Driver fechado")

if __name__ == "__main__":
    debug_fc9x4a_multiple_bets()
