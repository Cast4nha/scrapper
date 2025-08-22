#!/usr/bin/env python3
"""
Debug da estrutura completa do bilhete 22ove2
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

def debug_22ove2_structure():
    """Debug da estrutura completa do bilhete 22ove2"""
    
    print("🔍 DEBUG DA ESTRUTURA COMPLETA - BILHETE 22OVE2")
    print("=" * 60)
    
    # Criar instância do scraper
    scraper = ValSportsScraper()
    
    try:
        # Fazer login
        print("🔐 Fazendo login...")
        if scraper.login("cairovinicius", "279999"):
            print("✅ Login realizado com sucesso")
            
            # Testar bilhete 22ove2
            bet_code = "22ove2"
            print(f"🎯 Testando bilhete: {bet_code}")
            
            # Navegar para o bilhete
            bet_url = f"{scraper.base_url}/prebet/{bet_code}"
            scraper.driver.get(bet_url)
            
            # Aguardar carregamento
            import time
            time.sleep(5)
            
            print("\n🔍 ANALISANDO TODOS OS ELEMENTOS .l-item.d-block...")
            print("=" * 60)
            
            # Encontrar todos os elementos .l-item.d-block
            all_items = scraper.driver.find_elements(By.CSS_SELECTOR, ".l-item.d-block")
            print(f"📊 Total de elementos .l-item.d-block encontrados: {len(all_items)}")
            
            # Analisar cada elemento
            for i, item in enumerate(all_items):
                try:
                    full_text = item.text
                    print(f"\n📝 Elemento {i+1}:")
                    print(f"   Texto completo: {full_text[:200]}...")
                    
                    # Verificar se tem dados de jogo
                    has_odds = bool(re.search(r'\b\d+\.\d+\b', full_text))
                    has_selection = any(keyword in full_text for keyword in ['Vencedor:', 'Empate'])
                    has_teams = ' x ' in full_text
                    
                    print(f"   Tem odds: {has_odds}")
                    print(f"   Tem seleção: {has_selection}")
                    print(f"   Tem times: {has_teams}")
                    
                    if has_odds and has_selection and has_teams:
                        print(f"   ✅ É um jogo válido")
                    else:
                        print(f"   ❌ Não é um jogo válido")
                        
                except Exception as e:
                    print(f"   ❌ Erro ao analisar elemento {i+1}: {str(e)}")
            
            print("\n🎯 ELEMENTOS APÓS O ÍNDICE 10 (jogos válidos):")
            print("=" * 60)
            
            # Analisar apenas os elementos após o índice 10
            valid_items = all_items[10:]
            print(f"📊 Elementos válidos (após índice 10): {len(valid_items)}")
            
            for i, item in enumerate(valid_items):
                try:
                    full_text = item.text
                    print(f"\n🎮 Jogo {i+1}:")
                    print(f"   Texto: {full_text}")
                    
                    # Extrair dados básicos
                    lines = full_text.split('\n')
                    if lines:
                        print(f"   Primeira linha: {lines[0]}")
                    
                    # Verificar se tem múltiplas seleções
                    if full_text.count('Vencedor:') > 1 or full_text.count('Empate') > 1:
                        print(f"   ⚠️ MÚLTIPLAS SELEÇÕES DETECTADAS!")
                    
                except Exception as e:
                    print(f"   ❌ Erro ao analisar jogo {i+1}: {str(e)}")
            
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
    debug_22ove2_structure()
