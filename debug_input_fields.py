#!/usr/bin/env python3
"""
Debug dos campos de input na página
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scraper.valsports_scraper_final import ValSportsScraper
import logging
from selenium.webdriver.common.by import By

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def debug_input_fields():
    """Debug dos campos de input"""
    
    print("🔍 DEBUG DOS CAMPOS DE INPUT")
    print("=" * 50)
    
    # Criar instância do scraper
    scraper = ValSportsScraper()
    
    try:
        # Fazer login
        print("🔐 Fazendo login...")
        if scraper.login("cairovinicius", "279999"):
            print("✅ Login realizado com sucesso")
            
            # Testar bilhete 67izkv
            bet_code = "67izkv"
            print(f"🎯 Testando bilhete: {bet_code}")
            
            # Navegar para o bilhete
            bet_url = f"{scraper.base_url}/prebet/{bet_code}"
            scraper.driver.get(bet_url)
            
            # Aguardar carregamento
            import time
            time.sleep(5)
            
            print("\n🔍 PROCURANDO CAMPOS DE INPUT...")
            print("=" * 50)
            
            # 1. Procurar todos os inputs
            all_inputs = scraper.driver.find_elements(By.CSS_SELECTOR, "input")
            print(f"📊 Total de inputs encontrados: {len(all_inputs)}")
            
            for i, input_elem in enumerate(all_inputs):
                input_type = input_elem.get_attribute("type")
                input_class = input_elem.get_attribute("class")
                input_value = input_elem.get_attribute("value")
                input_placeholder = input_elem.get_attribute("placeholder")
                input_id = input_elem.get_attribute("id")
                input_name = input_elem.get_attribute("name")
                
                print(f"\n📝 Input {i+1}:")
                print(f"   Type: {input_type}")
                print(f"   Class: {input_class}")
                print(f"   Value: {input_value}")
                print(f"   Placeholder: {input_placeholder}")
                print(f"   ID: {input_id}")
                print(f"   Name: {input_name}")
            
            # 2. Procurar inputs específicos
            print("\n🎯 PROCURANDO INPUTS ESPECÍFICOS...")
            print("=" * 50)
            
            # Inputs com classe form-control
            form_inputs = scraper.driver.find_elements(By.CSS_SELECTOR, "input.form-control")
            print(f"📊 Inputs com classe 'form-control': {len(form_inputs)}")
            
            for i, input_elem in enumerate(form_inputs):
                input_type = input_elem.get_attribute("type")
                input_class = input_elem.get_attribute("class")
                input_value = input_elem.get_attribute("value")
                input_placeholder = input_elem.get_attribute("placeholder")
                
                print(f"\n📝 Form Input {i+1}:")
                print(f"   Type: {input_type}")
                print(f"   Class: {input_class}")
                print(f"   Value: {input_value}")
                print(f"   Placeholder: {input_placeholder}")
            
            # 3. Procurar por placeholders específicos
            print("\n🔍 PROCURANDO POR PLACEHOLDERS...")
            print("=" * 50)
            
            # Procurar por "Apostador" ou "Valor"
            apostador_inputs = scraper.driver.find_elements(By.XPATH, "//input[contains(@placeholder, 'Apostador') or contains(@placeholder, 'apostador')]")
            valor_inputs = scraper.driver.find_elements(By.XPATH, "//input[contains(@placeholder, 'Valor') or contains(@placeholder, 'valor')]")
            
            print(f"📊 Inputs com placeholder 'Apostador': {len(apostador_inputs)}")
            print(f"📊 Inputs com placeholder 'Valor': {len(valor_inputs)}")
            
            for i, input_elem in enumerate(apostador_inputs):
                print(f"\n👤 Apostador Input {i+1}:")
                print(f"   Value: {input_elem.get_attribute('value')}")
                print(f"   Placeholder: {input_elem.get_attribute('placeholder')}")
            
            for i, input_elem in enumerate(valor_inputs):
                print(f"\n💵 Valor Input {i+1}:")
                print(f"   Value: {input_elem.get_attribute('value')}")
                print(f"   Placeholder: {input_elem.get_attribute('placeholder')}")
            
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
    debug_input_fields()
