#!/usr/bin/env python3
"""
Script de Debug para Estrutura Completa da Página
Investiga por que apenas 3 jogos estão sendo capturados
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

class FullStructureDebugger:
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
    
    def debug_full_structure(self):
        """Debug da estrutura completa da página"""
        try:
            logger.info("🔍 INICIANDO DEBUG DA ESTRUTURA COMPLETA...")
            
            # 1. Verificar todos os elementos .l-item
            logger.info("📋 ANÁLISE DOS ELEMENTOS .l-item:")
            l_item_elements = self.driver.find_elements(By.CSS_SELECTOR, ".l-item")
            logger.info(f"   Total de elementos .l-item: {len(l_item_elements)}")
            
            for i, elem in enumerate(l_item_elements):
                try:
                    text = elem.text.strip()
                    classes = elem.get_attribute('class')
                    logger.info(f"     .l-item {i+1}:")
                    logger.info(f"       Classes: {classes}")
                    logger.info(f"       Texto: {text[:200]}...")
                    logger.info(f"       ---")
                except Exception as e:
                    logger.error(f"     ❌ Erro ao analisar .l-item {i+1}: {str(e)}")
            
            # 2. Verificar se há outros seletores que podem conter jogos
            logger.info("🔍 PROCURANDO OUTROS SELETORES DE JOGOS:")
            
            # Procurar por elementos que podem conter jogos
            possible_selectors = [
                ".game-item", ".bet-item", ".match-item", ".selection-item",
                ".palpite-item", ".jogo-item", ".aposta-item", ".item"
            ]
            
            for selector in possible_selectors:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    logger.info(f"   Seletor '{selector}': {len(elements)} elementos")
                    for i, elem in enumerate(elements[:3]):  # Só mostrar os primeiros 3
                        text = elem.text.strip()
                        if text and len(text) > 10:
                            logger.info(f"     {selector} {i+1}: {text[:100]}...")
            
            # 3. Verificar se há paginação ou carregamento dinâmico
            logger.info("📄 VERIFICANDO PAGINAÇÃO/CARREGAMENTO:")
            
            # Procurar por botões de paginação
            pagination_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Próxima') or contains(text(), 'Anterior') or contains(text(), 'Carregar') or contains(text(), 'Mais')]")
            if pagination_elements:
                logger.info(f"   Elementos de paginação encontrados: {len(pagination_elements)}")
                for elem in pagination_elements:
                    logger.info(f"     Paginação: {elem.text.strip()}")
            
            # 4. Verificar se há elementos colapsados/expandidos
            logger.info("🔽 VERIFICANDO ELEMENTOS COLAPSADOS:")
            
            # Procurar por elementos que podem estar escondidos
            hidden_elements = self.driver.find_elements(By.CSS_SELECTOR, "[style*='display: none'], [style*='visibility: hidden'], .hidden, .collapsed")
            if hidden_elements:
                logger.info(f"   Elementos escondidos encontrados: {len(hidden_elements)}")
                for i, elem in enumerate(hidden_elements[:5]):  # Só mostrar os primeiros 5
                    logger.info(f"     Escondido {i+1}: {elem.tag_name} - {elem.get_attribute('class')}")
            
            # 5. Verificar se há iframes ou elementos aninhados
            logger.info("🖼️ VERIFICANDO IFRAMES E ELEMENTOS ANINHADOS:")
            
            iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
            if iframes:
                logger.info(f"   Iframes encontrados: {len(iframes)}")
                for i, iframe in enumerate(iframes):
                    logger.info(f"     Iframe {i+1}: {iframe.get_attribute('src')}")
            
            # 6. Verificar se há elementos com scroll ou overflow
            logger.info("📜 VERIFICANDO ELEMENTOS COM SCROLL:")
            
            scroll_elements = self.driver.find_elements(By.CSS_SELECTOR, "[style*='overflow'], [style*='scroll']")
            if scroll_elements:
                logger.info(f"   Elementos com scroll encontrados: {len(scroll_elements)}")
                for i, elem in enumerate(scroll_elements[:3]):
                    logger.info(f"     Scroll {i+1}: {elem.tag_name} - {elem.get_attribute('style')}")
            
            # 7. Verificar se há elementos que precisam ser clicados para expandir
            logger.info("🖱️ VERIFICANDO ELEMENTOS EXPANSÍVEIS:")
            
            expandable_elements = self.driver.find_elements(By.CSS_SELECTOR, "[onclick*='expand'], [onclick*='show'], [onclick*='toggle'], .expandable, .collapsible")
            if expandable_elements:
                logger.info(f"   Elementos expansíveis encontrados: {len(expandable_elements)}")
                for i, elem in enumerate(expandable_elements[:3]):
                    logger.info(f"     Expansível {i+1}: {elem.tag_name} - {elem.get_attribute('onclick')}")
            
        except Exception as e:
            logger.error(f"❌ Erro no debug: {str(e)}")
    
    def close(self):
        """Fecha o driver"""
        if self.driver:
            self.driver.quit()
            logger.info("🔒 Driver fechado")

def main():
    debugger = FullStructureDebugger()
    
    try:
        # Configurar driver
        if not debugger.setup_driver():
            return
        
        # Fazer login
        if not debugger.login("cairovinicius", "279999"):
            return
        
        # Navegar para bilhete
        if not debugger.navigate_to_bet("3psw5x"):
            return
        
        # Debug da estrutura completa
        debugger.debug_full_structure()
        
    except Exception as e:
        logger.error(f"❌ Erro principal: {str(e)}")
    
    finally:
        debugger.close()

if __name__ == "__main__":
    main()

