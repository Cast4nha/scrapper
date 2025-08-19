#!/usr/bin/env python3
"""
Script para debugar o texto completo do bilhete
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scraper.valsports_scraper import ValSportsScraper
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def debug_ticket_text():
    """Debugar o texto completo do bilhete"""
    print("🔍 Debug do Texto do Bilhete - ValSports")
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
        
        # 3. Navegar até o bilhete
        print(f"\n3. Navegando até o bilhete: {bet_code}")
        try:
            # Clicar no menu de bilhetes
            scraper.driver.find_element("css selector", ".nav-item:nth-child(4) > .nav-link").click()
            print("✓ Clicou no menu de bilhetes")
            
            # Aguardar e digitar o código
            import time
            time.sleep(1)
            input_element = scraper.driver.find_element("css selector", ".v-dialog-input")
            input_element.clear()
            input_element.send_keys(bet_code)
            print("✓ Digitou o código do bilhete")
            
            # Clicar no botão de sucesso
            time.sleep(1)
            scraper.driver.find_element("css selector", ".success").click()
            print("✓ Clicou no botão de sucesso")
            
            # Clicar na área do bilhete
            time.sleep(2)
            scraper.driver.find_element("css selector", ".scroll-area-ticket > .p-2").click()
            print("✓ Clicou na área do bilhete")
            
            # Aguardar carregamento
            time.sleep(3)
            
        except Exception as e:
            print(f"❌ Erro ao navegar: {str(e)}")
            return
        
        # 4. Capturar e analisar o texto
        print("\n4. Capturando texto do bilhete...")
        try:
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
            wait = WebDriverWait(scraper.driver, 15)
            ticket_area = wait.until(EC.presence_of_element_located(("css selector", ".scroll-area-ticket > .p-2")))
            ticket_full_text = ticket_area.text
            
            print("\n📄 TEXTO COMPLETO DO BILHETE:")
            print("=" * 50)
            print(ticket_full_text)
            print("=" * 50)
            
            # Analisar linha por linha
            print("\n🔍 ANÁLISE LINHA POR LINHA:")
            print("-" * 30)
            lines = ticket_full_text.split('\n')
            for i, line in enumerate(lines):
                print(f"Linha {i+1}: '{line}'")
            
            # Salvar screenshot
            scraper.driver.save_screenshot("debug_ticket_text.png")
            print("\n📸 Screenshot salvo como debug_ticket_text.png")
            
        except Exception as e:
            print(f"❌ Erro ao capturar texto: {str(e)}")
            return
        
    except Exception as e:
        print(f"❌ Erro geral: {str(e)}")
    finally:
        if scraper:
            print("\n5. Fechando scraper...")
            scraper.close()
            print("✓ Scraper fechado")

if __name__ == "__main__":
    debug_ticket_text()
