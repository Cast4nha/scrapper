#!/usr/bin/env python3
"""
Script para debugar toda a página do bilhete
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scraper.valsports_scraper import ValSportsScraper
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def debug_full_page():
    """Debugar toda a página do bilhete"""
    print("🔍 Debug Completo da Página do Bilhete - ValSports")
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
        
        # 4. Capturar toda a página
        print("\n4. Capturando toda a página...")
        try:
            # Salvar screenshot da página completa
            scraper.driver.save_screenshot("full_page_debug.png")
            print("📸 Screenshot da página completa salvo como full_page_debug.png")
            
            # Capturar HTML da página
            page_source = scraper.driver.page_source
            with open("page_source.html", "w", encoding="utf-8") as f:
                f.write(page_source)
            print("📄 HTML da página salvo como page_source.html")
            
            # Procurar por elementos que possam conter informações do apostador
            print("\n🔍 PROCURANDO ELEMENTOS COM INFORMAÇÕES DO APOSTADOR:")
            print("-" * 50)
            
            # Procurar por elementos que contenham "R$" (valores)
            reais_elements = scraper.driver.find_elements("xpath", "//*[contains(text(), 'R$')]")
            print(f"Elementos com 'R$': {len(reais_elements)}")
            for i, elem in enumerate(reais_elements[:5]):  # Mostrar apenas os primeiros 5
                print(f"  {i+1}. '{elem.text}'")
            
            # Procurar por elementos que possam ser nomes
            name_elements = scraper.driver.find_elements("xpath", "//*[not(contains(text(), 'R$')) and not(contains(text(), 'BILHETE')) and not(contains(text(), 'Mirassol')) and not(contains(text(), 'Cruzeiro')) and string-length(text()) > 3]")
            print(f"\nElementos que podem ser nomes: {len(name_elements)}")
            for i, elem in enumerate(name_elements[:10]):  # Mostrar apenas os primeiros 10
                text = elem.text.strip()
                if text and len(text) > 2:
                    print(f"  {i+1}. '{text}'")
            
            # Procurar por elementos com classes específicas
            print("\n🔍 ELEMENTOS COM CLASSES ESPECÍFICAS:")
            print("-" * 30)
            
            # Procurar por elementos com classes que possam conter informações do usuário
            user_classes = ["user", "name", "player", "bettor", "apostador", "cliente"]
            for class_name in user_classes:
                elements = scraper.driver.find_elements("css selector", f".{class_name}")
                if elements:
                    print(f"Classe '.{class_name}': {len(elements)} elementos")
                    for elem in elements:
                        print(f"  - '{elem.text}'")
            
            # Procurar por elementos com classes que possam conter valores
            value_classes = ["value", "amount", "valor", "aposta", "bet"]
            for class_name in value_classes:
                elements = scraper.driver.find_elements("css selector", f".{class_name}")
                if elements:
                    print(f"Classe '.{class_name}': {len(elements)} elementos")
                    for elem in elements:
                        print(f"  - '{elem.text}'")
            
            # Procurar por elementos com atributos específicos
            print("\n🔍 ELEMENTOS COM ATRIBUTOS ESPECÍFICOS:")
            print("-" * 35)
            
            # Procurar por elementos com data-* attributes
            data_elements = scraper.driver.find_elements("xpath", "//*[@data-*]")
            print(f"Elementos com data-*: {len(data_elements)}")
            for elem in data_elements[:5]:
                attrs = elem.get_attribute("outerHTML")
                print(f"  - {attrs[:100]}...")
            
        except Exception as e:
            print(f"❌ Erro ao capturar página: {str(e)}")
            return
        
    except Exception as e:
        print(f"❌ Erro geral: {str(e)}")
    finally:
        if scraper:
            print("\n5. Fechando scraper...")
            scraper.close()
            print("✓ Scraper fechado")

if __name__ == "__main__":
    debug_full_page()
