#!/usr/bin/env python3
"""
Script de Debug para Valor da Aposta
Investiga como o valor da aposta está sendo exibido na página
"""
import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

class BetValueDebugger:
    def __init__(self):
        self.driver = None
        
    def setup_driver(self):
        """Configura o driver Firefox"""
        try:
            options = Options()
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            
            self.driver = webdriver.Firefox(options=options)
            logger.info("🚀 Driver Firefox configurado com sucesso")
            return True
        except Exception as e:
            logger.error(f"❌ Erro ao configurar driver: {str(e)}")
            return False
    
    def login(self, username, password):
        """Faz login no sistema"""
        try:
            logger.info("🔐 Fazendo login...")
            self.driver.get("https://www.valsports.net/login")
            time.sleep(3)
            
            # Preencher usuário
            username_input = self.driver.find_element(By.NAME, "username")
            username_input.send_keys(username)
            
            # Preencher senha
            password_input = self.driver.find_element(By.NAME, "password")
            password_input.send_keys(password)
            
            # Clicar no botão de login
            login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            login_button.click()
            
            time.sleep(5)
            logger.info("✅ Login realizado com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro no login: {str(e)}")
            return False
    
    def navigate_to_bet(self, bet_code):
        """Navega para a página do bilhete"""
        try:
            logger.info(f"🌐 Navegando para bilhete: {bet_code}")
            url = f"https://www.valsports.net/prebet/{bet_code}"
            self.driver.get(url)
            time.sleep(5)
            
            # Aguardar carregamento da página
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".l-item"))
            )
            
            logger.info("✅ Página do bilhete carregada")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao navegar para bilhete: {str(e)}")
            return False
    
    def debug_bet_value(self):
        """Debug do valor da aposta"""
        try:
            logger.info("🔍 INICIANDO DEBUG DO VALOR DA APOSTA...")
            
            # 1. Verificar todos os inputs na página
            logger.info("📋 PROCURANDO TODOS OS INPUTS:")
            all_inputs = self.driver.find_elements(By.TAG_NAME, "input")
            logger.info(f"   Total de inputs encontrados: {len(all_inputs)}")
            
            for i, input_elem in enumerate(all_inputs):
                try:
                    input_type = input_elem.get_attribute("type")
                    input_placeholder = input_elem.get_attribute("placeholder")
                    input_value = input_elem.get_attribute("value")
                    input_id = input_elem.get_attribute("id")
                    input_class = input_elem.get_attribute("class")
                    input_name = input_elem.get_attribute("name")
                    
                    logger.info(f"     Input {i+1}:")
                    logger.info(f"       Tipo: {input_type}")
                    logger.info(f"       Placeholder: '{input_placeholder}'")
                    logger.info(f"       Valor: '{input_value}'")
                    logger.info(f"       ID: {input_id}")
                    logger.info(f"       Classe: {input_class}")
                    logger.info(f"       Nome: {input_name}")
                    logger.info(f"       ---")
                except Exception as e:
                    logger.error(f"     ❌ Erro ao analisar input {i+1}: {str(e)}")
            
            # 2. Procurar especificamente por campos de valor
            logger.info("💰 PROCURANDO CAMPOS DE VALOR:")
            
            # Procurar por inputs com placeholder "Valor"
            valor_inputs = self.driver.find_elements(By.XPATH, "//input[contains(@placeholder, 'Valor')]")
            logger.info(f"   Inputs com placeholder 'Valor': {len(valor_inputs)}")
            for i, input_elem in enumerate(valor_inputs):
                logger.info(f"     Valor Input {i+1}: '{input_elem.get_attribute('value')}'")
            
            # Procurar por inputs com placeholder "Valor da aposta"
            valor_aposta_inputs = self.driver.find_elements(By.XPATH, "//input[contains(@placeholder, 'aposta')]")
            logger.info(f"   Inputs com placeholder contendo 'aposta': {len(valor_aposta_inputs)}")
            for i, input_elem in enumerate(valor_aposta_inputs):
                logger.info(f"     Valor Aposta Input {i+1}: '{input_elem.get_attribute('value')}'")
            
            # Procurar por inputs com type="number"
            number_inputs = self.driver.find_elements(By.XPATH, "//input[@type='number']")
            logger.info(f"   Inputs tipo 'number': {len(number_inputs)}")
            for i, input_elem in enumerate(number_inputs):
                logger.info(f"     Number Input {i+1}: '{input_elem.get_attribute('value')}' (placeholder: '{input_elem.get_attribute('placeholder')}')")
            
            # 3. Procurar por elementos que podem conter o valor
            logger.info("🔍 PROCURANDO ELEMENTOS COM VALOR:")
            
            # Procurar por elementos que contêm "R$"
            rs_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'R$')]")
            logger.info(f"   Elementos contendo 'R$': {len(rs_elements)}")
            for i, elem in enumerate(rs_elements):
                text = elem.text.strip()
                if text and len(text) < 50:  # Só mostrar textos curtos
                    logger.info(f"     R$ Element {i+1}: '{text}'")
            
            # 4. Verificar se há algum elemento específico para valor da aposta
            logger.info("🎯 PROCURANDO ELEMENTOS ESPECÍFICOS DE VALOR:")
            
            # Procurar por elementos com classes específicas que podem conter valor
            value_classes = ["bet-value", "aposta-valor", "valor-aposta", "bet-amount", "amount"]
            for class_name in value_classes:
                elements = self.driver.find_elements(By.CSS_SELECTOR, f".{class_name}")
                if elements:
                    logger.info(f"   Elementos com classe '{class_name}': {len(elements)}")
                    for i, elem in enumerate(elements):
                        logger.info(f"     {class_name} {i+1}: '{elem.text.strip()}'")
            
            # 5. Verificar se o valor está sendo calculado dinamicamente
            logger.info("🧮 VERIFICANDO CÁLCULO DINÂMICO:")
            
            # Procurar por elementos que podem conter o valor calculado
            calculated_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Total') or contains(text(), 'Valor') or contains(text(), 'Aposta')]")
            logger.info(f"   Elementos contendo palavras-chave: {len(calculated_elements)}")
            for i, elem in enumerate(calculated_elements):
                text = elem.text.strip()
                if text and len(text) < 100:  # Só mostrar textos curtos
                    logger.info(f"     Calculated Element {i+1}: '{text}'")
            
        except Exception as e:
            logger.error(f"❌ Erro no debug: {str(e)}")
    
    def close(self):
        """Fecha o driver"""
        if self.driver:
            self.driver.quit()
            logger.info("🔒 Driver fechado")

def main():
    debugger = BetValueDebugger()
    
    try:
        # Configurar driver
        if not debugger.setup_driver():
            return
        
        # Fazer login
        if not debugger.login("cairovinicius", "279999"):
            return
        
        # Navegar para bilhete
        if not debugger.navigate_to_bet("5rywv3"):
            return
        
        # Debug do valor da aposta
        debugger.debug_bet_value()
        
    except Exception as e:
        logger.error(f"❌ Erro principal: {str(e)}")
    
    finally:
        debugger.close()

if __name__ == "__main__":
    main()

