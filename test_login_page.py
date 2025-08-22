#!/usr/bin/env python3
"""
Teste da Página de Login do ValSports
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

def test_login_page():
    """Testa e analisa a página de login"""
    print("🔍 ANALISANDO PÁGINA DE LOGIN")
    print("=" * 50)
    
    # Configurar Firefox
    firefox_options = Options()
    firefox_options.add_argument("--headless")
    firefox_options.add_argument("--no-sandbox")
    firefox_options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Firefox(options=firefox_options)
    driver.set_window_size(1200, 800)
    
    try:
        # Navegar para página de login
        print("🌐 Navegando para página de login...")
        driver.get("https://www.valsports.net/login")
        time.sleep(5)
        
        # Salvar screenshot
        driver.save_screenshot("login_page.png")
        print("📸 Screenshot salvo: login_page.png")
        
        # Salvar HTML
        with open("login_page.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print("📄 HTML salvo: login_page.html")
        
        # Analisar elementos da página
        print("\n🔍 ANALISANDO ELEMENTOS:")
        print("-" * 30)
        
        # Procurar por inputs
        inputs = driver.find_elements(By.TAG_NAME, "input")
        print(f"📝 Inputs encontrados: {len(inputs)}")
        
        for i, input_elem in enumerate(inputs):
            input_type = input_elem.get_attribute("type")
            input_name = input_elem.get_attribute("name")
            input_id = input_elem.get_attribute("id")
            input_placeholder = input_elem.get_attribute("placeholder")
            input_class = input_elem.get_attribute("class")
            
            print(f"   Input {i+1}:")
            print(f"      Tipo: {input_type}")
            print(f"      Nome: {input_name}")
            print(f"      ID: {input_id}")
            print(f"      Placeholder: {input_placeholder}")
            print(f"      Classe: {input_class}")
            print()
        
        # Procurar por botões
        buttons = driver.find_elements(By.TAG_NAME, "button")
        print(f"🔘 Botões encontrados: {len(buttons)}")
        
        for i, button in enumerate(buttons):
            button_text = button.text
            button_type = button.get_attribute("type")
            button_class = button.get_attribute("class")
            
            print(f"   Botão {i+1}:")
            print(f"      Texto: '{button_text}'")
            print(f"      Tipo: {button_type}")
            print(f"      Classe: {button_class}")
            print()
        
        # Procurar por formulários
        forms = driver.find_elements(By.TAG_NAME, "form")
        print(f"📋 Formulários encontrados: {len(forms)}")
        
        for i, form in enumerate(forms):
            form_action = form.get_attribute("action")
            form_method = form.get_attribute("method")
            form_class = form.get_attribute("class")
            
            print(f"   Formulário {i+1}:")
            print(f"      Action: {form_action}")
            print(f"      Method: {form_method}")
            print(f"      Classe: {form_class}")
            print()
        
        # Verificar se há redirecionamento
        current_url = driver.current_url
        print(f"📍 URL atual: {current_url}")
        
        if "login" not in current_url.lower():
            print("⚠️  Página foi redirecionada!")
        
        # Verificar título da página
        page_title = driver.title
        print(f"📰 Título da página: {page_title}")
        
        # Verificar se há mensagens de erro
        error_elements = driver.find_elements(By.CSS_SELECTOR, "[class*='error'], [class*='alert'], [class*='message']")
        if error_elements:
            print(f"❌ Elementos de erro encontrados: {len(error_elements)}")
            for elem in error_elements:
                print(f"   - {elem.text}")
        
        print("\n✅ Análise concluída!")
        
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
    
    finally:
        driver.quit()

if __name__ == "__main__":
    test_login_page()
