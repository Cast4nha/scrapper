#!/usr/bin/env python3
"""
Script de Debug para Extração de Times
Investiga por que os times não estão sendo extraídos corretamente
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

class TeamExtractionDebugger:
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
    
    def debug_team_extraction(self):
        """Debug da extração de times"""
        try:
            logger.info("🔍 INICIANDO DEBUG DA EXTRAÇÃO DE TIMES...")
            
            # Encontrar todos os elementos .l-item
            game_elements = self.driver.find_elements(By.CSS_SELECTOR, ".l-item")
            logger.info(f"🔍 Encontrados {len(game_elements)} elementos .l-item")
            
            if not game_elements:
                logger.error("❌ Nenhum elemento .l-item encontrado!")
                return
            
            # Analisar o primeiro jogo em detalhes
            first_game = game_elements[0]
            logger.info("🎮 ANALISANDO PRIMEIRO JOGO EM DETALHES:")
            
            # 1. Verificar estrutura HTML
            logger.info("📋 ESTRUTURA HTML DO PRIMEIRO JOGO:")
            logger.info(f"   HTML: {first_game.get_attribute('outerHTML')[:500]}...")
            
            # 2. Verificar texto completo
            full_text = first_game.text
            logger.info(f"📝 TEXTO COMPLETO: {full_text}")
            
            # 3. Procurar por elementos específicos
            logger.info("🔍 PROCURANDO ELEMENTOS ESPECÍFICOS:")
            
            # Liga
            try:
                league_elements = first_game.find_elements(By.CSS_SELECTOR, ".l-item-emphasis")
                logger.info(f"   Liga (.l-item-emphasis): {len(league_elements)} elementos encontrados")
                for i, elem in enumerate(league_elements):
                    logger.info(f"     Liga {i+1}: '{elem.text.strip()}'")
            except Exception as e:
                logger.error(f"   ❌ Erro ao procurar liga: {str(e)}")
            
            # Times - procurar por .text-truncate
            try:
                team_elements = first_game.find_elements(By.CSS_SELECTOR, ".text-truncate")
                logger.info(f"   Times (.text-truncate): {len(team_elements)} elementos encontrados")
                for i, elem in enumerate(team_elements):
                    text = elem.text.strip()
                    logger.info(f"     Time {i+1}: '{text}' (classe: {elem.get_attribute('class')})")
            except Exception as e:
                logger.error(f"   ❌ Erro ao procurar times: {str(e)}")
            
            # Seleção
            try:
                selection_elements = first_game.find_elements(By.CSS_SELECTOR, ".text-theme")
                logger.info(f"   Seleção (.text-theme): {len(selection_elements)} elementos encontrados")
                for i, elem in enumerate(selection_elements):
                    text = elem.text.strip()
                    logger.info(f"     Seleção {i+1}: '{text}'")
            except Exception as e:
                logger.error(f"   ❌ Erro ao procurar seleção: {str(e)}")
            
            # Odds
            try:
                odds_elements = first_game.find_elements(By.CSS_SELECTOR, ".text-theme.text-right")
                logger.info(f"   Odds (.text-theme.text-right): {len(odds_elements)} elementos encontrados")
                for i, elem in enumerate(odds_elements):
                    text = elem.text.strip()
                    logger.info(f"     Odds {i+1}: '{text}'")
            except Exception as e:
                logger.error(f"   ❌ Erro ao procurar odds: {str(e)}")
            
            # Data/Hora
            try:
                clock_elements = first_game.find_elements(By.CSS_SELECTOR, "i.far.fa-clock")
                logger.info(f"   Data/Hora (i.far.fa-clock): {len(clock_elements)} elementos encontrados")
                for i, elem in enumerate(clock_elements):
                    parent = elem.find_element(By.XPATH, "./..")
                    text = parent.text.strip()
                    logger.info(f"     Data/Hora {i+1}: '{text}'")
            except Exception as e:
                logger.error(f"   ❌ Erro ao procurar data/hora: {str(e)}")
            
            # 4. Tentar extração manual
            logger.info("🎯 TENTANDO EXTRAÇÃO MANUAL:")
            
            # Procurar por todos os elementos que podem conter times
            all_elements = first_game.find_elements(By.CSS_SELECTOR, "*")
            potential_teams = []
            
            for elem in all_elements:
                try:
                    text = elem.text.strip()
                    if text and len(text) > 2 and not any(keyword in text.lower() for keyword in ['vencedor:', 'empate', 'odds', 'brasil:', 'colômbia:', 'copa', 'série', 'r$', 'total']):
                        # Verificar se parece ser um nome de time
                        if re.search(r'^[A-Za-zÀ-ÿ\s]+$', text) and len(text.split()) >= 1:
                            potential_teams.append({
                                'text': text,
                                'tag': elem.tag_name,
                                'class': elem.get_attribute('class'),
                                'xpath': self.driver.execute_script("""
                                    function getXPath(element) {
                                        if (element.id !== '') {
                                            return 'id("' + element.id + '")';
                                        }
                                        if (element === document.body) {
                                            return element.tagName;
                                        }
                                        var ix = 0;
                                        var siblings = element.parentNode.childNodes;
                                        for (var i = 0; i < siblings.length; i++) {
                                            var sibling = siblings[i];
                                            if (sibling === element) {
                                                return getXPath(element.parentNode) + '/' + element.tagName.toLowerCase() + '[' + (ix + 1) + ']';
                                            }
                                            if (sibling.nodeType === 1 && sibling.tagName === element.tagName) {
                                                ix++;
                                            }
                                        }
                                    }
                                    return getXPath(arguments[0]);
                                """, elem)
                            })
                except:
                    continue
            
            logger.info(f"   🎯 Possíveis times encontrados: {len(potential_teams)}")
            for i, team in enumerate(potential_teams):
                logger.info(f"     Time {i+1}: '{team['text']}' (tag: {team['tag']}, classe: {team['class']})")
            
        except Exception as e:
            logger.error(f"❌ Erro no debug: {str(e)}")
    
    def close(self):
        """Fecha o driver"""
        if self.driver:
            self.driver.quit()
            logger.info("🔒 Driver fechado")

def main():
    import re
    
    debugger = TeamExtractionDebugger()
    
    try:
        # Configurar driver
        if not debugger.setup_driver():
            return
        
        # Fazer login
        if not debugger.login("cairovinicius", "279999"):
            return
        
        # Navegar para bilhete
        if not debugger.navigate_to_bet("eowarg"):
            return
        
        # Debug da extração
        debugger.debug_team_extraction()
        
    except Exception as e:
        logger.error(f"❌ Erro principal: {str(e)}")
    
    finally:
        debugger.close()

if __name__ == "__main__":
    main()
