#!/usr/bin/env python3
"""
Debug da extração de times do bilhete n6e2er
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

def debug_n6e2er_times():
    """Debug da extração de times do bilhete n6e2er"""
    
    print("🔍 DEBUG DA EXTRAÇÃO DE TIMES - BILHETE N6E2ER")
    print("=" * 60)
    
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
            
            # Navegar para o bilhete
            bet_url = f"{scraper.base_url}/prebet/{bet_code}"
            scraper.driver.get(bet_url)
            
            # Aguardar carregamento
            import time
            time.sleep(5)
            
            print("\n🔍 ANALISANDO ELEMENTOS COM JOGOS...")
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
                    print(f"   Texto completo:")
                    lines = full_text.split('\n')
                    for j, line in enumerate(lines):
                        print(f"   Linha {j}: '{line}'")
                    
                    # Verificar se é um novo jogo
                    league_keywords = ['Alemanha:', 'Brasil:', 'França:', 'Internacional:', 'EUA:', 'Inglaterra:', 'Bundesliga', 'Série B', 'Ligue 1', 'FIBA', 'WNBA', 'Premier League']
                    has_league = any(keyword in full_text for keyword in league_keywords)
                    has_teams = ' x ' in full_text
                    
                    if has_league and has_teams:
                        game_counter += 1
                        current_game = f"Jogo {game_counter}"
                        print(f"   🎮 {current_game} (NOVO JOGO)")
                        
                        # Tentar extrair times
                        print(f"   🔍 Tentando extrair times...")
                        for j, line in enumerate(lines):
                            line = line.strip()
                            print(f"      Analisando linha {j}: '{line}'")
                            
                            if (' x ' in line and 
                                not any(keyword in line.lower() for keyword in ['vencedor:', 'empate', 'odds', 'data', 'hora', 'live']) and
                                not re.search(r'^\d+\.\d+$', line) and
                                not re.search(r'^\d{2}/\d{2}', line) and
                                len(line) > 3):
                                
                                teams = line.split(' x ')
                                if len(teams) == 2:
                                    home_team = teams[0].strip()
                                    away_team = teams[1].strip()
                                    
                                    if home_team and away_team and len(home_team) > 1 and len(away_team) > 1:
                                        print(f"      ✅ TIMES ENCONTRADOS: {home_team} x {away_team}")
                                        break
                                    else:
                                        print(f"      ❌ Times inválidos: '{home_team}' x '{away_team}'")
                                else:
                                    print(f"      ❌ Não conseguiu dividir times: {line}")
                            else:
                                print(f"      ⏭️ Linha não é times: {line}")
                    else:
                        print(f"   🎯 Aposta adicional do {current_game}")
                        
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
    debug_n6e2er_times()
