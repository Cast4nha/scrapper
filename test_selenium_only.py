#!/usr/bin/env python3
"""
Teste usando apenas Selenium para acessar bilhete
"""

import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_selenium_only():
    """Testa acesso ao bilhete usando apenas Selenium"""
    print("🧪 TESTE APENAS COM SELENIUM")
    print("=" * 50)
    
    # Configurar Firefox
    firefox_options = Options()
    firefox_options.add_argument("--headless")
    firefox_options.add_argument("--no-sandbox")
    firefox_options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Firefox(options=firefox_options)
    driver.set_window_size(1200, 800)
    
    try:
        # Fazer login
        print("🔐 Fazendo login...")
        driver.get("https://www.valsports.net/login")
        time.sleep(5)
        
        # Preencher credenciais usando os seletores corretos
        username_field = driver.find_element(By.CSS_SELECTOR, ".form-group:nth-child(1) > .form-control")
        password_field = driver.find_element(By.CSS_SELECTOR, ".form-group:nth-child(2) > .form-control")
        
        username_field.send_keys("cairovinicius")
        password_field.send_keys("279999")
        
        # Clicar no botão de login
        login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        login_button.click()
        
        time.sleep(8)
        
        print(f"📍 URL após login: {driver.current_url}")
        
        # Verificar se o login foi bem-sucedido
        if "login" in driver.current_url.lower():
            print("❌ Login falhou - ainda na página de login")
            return
        
        print("✅ Login realizado com sucesso")
        
        # Tentar acessar o bilhete
        bet_code = "ELM5IM"  # Bilhete que sabemos que existe
        print(f"🎯 Acessando bilhete: {bet_code}")
        
        driver.get(f"https://www.valsports.net/prebet/{bet_code}")
        time.sleep(10)
        
        print(f"📍 URL do bilhete: {driver.current_url}")
        
        # Salvar screenshot
        driver.save_screenshot(f"selenium_bilhete_{bet_code}.png")
        print("📸 Screenshot salvo")
        
        # Salvar HTML
        with open(f"selenium_bilhete_{bet_code}.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print("📄 HTML salvo")
        
        # Analisar conteúdo
        page_text = driver.find_element(By.TAG_NAME, "body").text
        print(f"📏 Tamanho do texto: {len(page_text)} caracteres")
        
        # Procurar por padrões de jogos
        import re
        
        # Padrões para encontrar jogos
        patterns = [
            r'([A-Za-zÀ-ÿ\s]+):\s*([A-Za-zÀ-ÿ\s]+)\s+(\d{2}/\d{2}\s+\d{2}:\d{2})',
            r'([A-Za-zÀ-ÿ\s]+)\s+x\s+([A-Za-zÀ-ÿ\s]+)',
            r'Vencedor:\s*([A-Za-zÀ-ÿ\s]+)',
            r'Total odds\s*(\d+[,\d]*)',
            r'Possível prêmio\s*(R\$\s*\d+[,\d]*)'
        ]
        
        print("\n🔍 PADRÕES ENCONTRADOS:")
        print("-" * 30)
        
        for i, pattern in enumerate(patterns):
            matches = re.findall(pattern, page_text, re.MULTILINE)
            if matches:
                print(f"Padrão {i+1}: {len(matches)} matches")
                for match in matches[:3]:
                    print(f"   - {match}")
                if len(matches) > 3:
                    print(f"   ... e mais {len(matches) - 3}")
            else:
                print(f"Padrão {i+1}: Nenhum match")
        
        # Verificar se há elementos de bilhete
        ticket_elements = driver.find_elements(By.CSS_SELECTOR, "[class*='ticket'], [class*='bet'], [class*='game']")
        print(f"\n🎫 Elementos de bilhete encontrados: {len(ticket_elements)}")
        
        # Verificar se há inputs
        inputs = driver.find_elements(By.TAG_NAME, "input")
        print(f"📝 Inputs encontrados: {len(inputs)}")
        
        for i, input_elem in enumerate(inputs):
            placeholder = input_elem.get_attribute("placeholder")
            value = input_elem.get_attribute("value")
            if placeholder or value:
                print(f"   Input {i+1}: placeholder='{placeholder}', value='{value}'")
        
        print("\n✅ Teste concluído!")
        
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        driver.save_screenshot("selenium_error.png")
    
    finally:
        driver.quit()

if __name__ == "__main__":
    test_selenium_only()
