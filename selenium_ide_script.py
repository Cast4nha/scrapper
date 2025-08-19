#!/usr/bin/env python3
"""
Script baseado no Selenium IDE que funcionou
"""

import os
import sys
import time
from dotenv import load_dotenv

# Adicionar o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scraper.valsports_scraper import ValSportsScraper

def selenium_ide_script():
    """Executa o script baseado no Selenium IDE"""
    
    print("🔍 Script Selenium IDE - ValSports")
    print("=" * 40)
    
    # Carregar variáveis de ambiente
    load_dotenv()
    
    scraper = None
    
    try:
        print("\n1. Inicializando scraper...")
        scraper = ValSportsScraper()
        print("✓ Scraper inicializado")
        
        # Credenciais baseadas no Selenium IDE
        username = "cairovinicius"
        password = "279999"
        
        print("\n2. Executando script do Selenium IDE...")
        
        # 1. open on https://www.valsports.net/login
        print("   - Acessando página de login...")
        scraper.driver.get("https://www.valsports.net/login")
        time.sleep(2)
        
        # 2. setWindowSize on 1680x964
        print("   - Configurando tamanho da janela...")
        scraper.driver.set_window_size(1680, 964)
        time.sleep(1)
        
        # 3. click on css=.form-group:nth-child(1) > .form-control
        print("   - Clicando no campo usuário...")
        username_field = scraper.driver.find_element("css selector", ".form-group:nth-child(1) > .form-control")
        username_field.click()
        time.sleep(1)
        
        # 4. type on css=.form-group:nth-child(1) > .form-control with value cairovinicius
        print("   - Digitando usuário...")
        username_field.clear()
        username_field.send_keys(username)
        time.sleep(1)
        
        # 5. type on css=.form-group:nth-child(2) > .form-control with value 279999
        print("   - Digitando senha...")
        password_field = scraper.driver.find_element("css selector", ".form-group:nth-child(2) > .form-control")
        password_field.clear()
        password_field.send_keys(password)
        time.sleep(1)
        
        # 6. click on css=.btn-success
        print("   - Clicando no botão de login...")
        login_button = scraper.driver.find_element("css selector", ".btn-success")
        login_button.click()
        time.sleep(3)
        
        print(f"✓ URL após login: {scraper.driver.current_url}")
        print(f"✓ Título da página: {scraper.driver.title}")
        
        # Verificar se o login foi bem-sucedido
        if "betsnow.net" in scraper.driver.current_url:
            print("❌ Redirecionado para betsnow.net - proteção ativada")
            return False
        
        if "login" in scraper.driver.current_url.lower():
            print("❌ Ainda na página de login - credenciais inválidas")
            return False
        
        print("✅ Login aparentemente bem-sucedido!")
        
        # 7. Acessar o bilhete
        print("\n3. Acessando bilhete...")
        bet_url = "https://www.valsports.net/prebet/dmgkrn"
        scraper.driver.get(bet_url)
        time.sleep(3)
        
        print(f"✓ URL do bilhete: {scraper.driver.current_url}")
        print(f"✓ Título da página: {scraper.driver.title}")
        
        # Verificar se conseguiu acessar o bilhete
        if "prebet" in scraper.driver.current_url or "dmgkrn" in scraper.driver.current_url:
            print("✅ Acesso ao bilhete bem-sucedido!")
            
            # Salvar screenshot
            scraper.driver.save_screenshot("login_success.png")
            print("📸 Screenshot salvo como login_success.png")
            
            return True
        else:
            print("❌ Não conseguiu acessar o bilhete")
            return False
            
    except Exception as e:
        print(f"❌ Erro durante execução: {str(e)}")
        return False
        
    finally:
        if scraper:
            print("\n4. Fechando scraper...")
            scraper.close()
            print("✓ Scraper fechado")

if __name__ == "__main__":
    success = selenium_ide_script()
    if success:
        print("\n🎉 Script Selenium IDE executado com sucesso!")
        print("   O login e acesso ao bilhete funcionaram")
    else:
        print("\n❌ Script Selenium IDE falhou")
        print("   O site pode ter mudado ou a proteção está mais forte")
