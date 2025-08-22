#!/usr/bin/env python3
"""
Scraper Robusto para ValSports.net
Captura TODOS os jogos de qualquer bilhete, independente do tamanho
"""

import os
import time
import logging
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RobustValSportsScraper:
    def __init__(self):
        self.base_url = "https://www.valsports.net"
        self.is_logged_in = False
        
        # Configurar Firefox com otimizações
        firefox_options = Options()
        firefox_options.add_argument("--headless")
        firefox_options.add_argument("--no-sandbox")
        firefox_options.add_argument("--disable-dev-shm-usage")
        firefox_options.add_argument("--disable-gpu")
        firefox_options.add_argument("--disable-extensions")
        firefox_options.add_argument("--disable-plugins")
        firefox_options.add_argument("--disable-images")
        firefox_options.add_argument("--disable-javascript")
        firefox_options.add_argument("--disable-css")
        firefox_options.add_argument("--disable-web-security")
        firefox_options.add_argument("--disable-features=VizDisplayCompositor")
        
        self.driver = webdriver.Firefox(options=firefox_options)
        self.driver.set_window_size(1200, 800)
        self.driver.implicitly_wait(3)
        self.driver.set_page_load_timeout(10)
        
        logger.info("🚀 Scraper Robusto inicializado")
    
    def login(self, username, password):
        """Login no sistema"""
        try:
            logger.info(f"🔐 Fazendo login com usuário: {username}")
            
            self.driver.get(f"{self.base_url}/login")
            time.sleep(2)
            
            # Preencher credenciais
            username_field = self.driver.find_element(By.CSS_SELECTOR, "input[name='username']")
            password_field = self.driver.find_element(By.CSS_SELECTOR, "input[name='password']")
            
            username_field.send_keys(username)
            password_field.send_keys(password)
            
            # Clicar no botão de login
            login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            login_button.click()
            
            time.sleep(3)
            
            # Verificar se o login foi bem-sucedido
            if "dashboard" in self.driver.current_url or "logout" in self.driver.page_source.lower():
                self.is_logged_in = True
                logger.info("✅ Login realizado com sucesso")
                return True
            else:
                logger.error("❌ Login falhou")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro no login: {str(e)}")
            return False
    
    def get_all_games_robust(self, bet_code):
        """Método robusto para capturar TODOS os jogos"""
        try:
            logger.info(f"🎯 CAPTURANDO TODOS OS JOGOS DO BILHETE: {bet_code}")
            
            # Navegar para o bilhete
            bet_url = f"{self.base_url}/prebet/{bet_code}"
            logger.info(f"🌐 Navegando para: {bet_url}")
            
            self.driver.get(bet_url)
            time.sleep(3)
            
            # Aguardar carregamento
            wait = WebDriverWait(self.driver, 10)
            
            # Método 1: Tentar capturar pelo container principal
            games = self._method1_container_based()
            if games:
                logger.info(f"✅ Método 1 funcionou: {len(games)} jogos encontrados")
                return games
            
            # Método 2: Tentar capturar por XPaths dinâmicos
            games = self._method2_dynamic_xpath()
            if games:
                logger.info(f"✅ Método 2 funcionou: {len(games)} jogos encontrados")
                return games
            
            # Método 3: Tentar capturar por texto completo
            games = self._method3_text_analysis()
            if games:
                logger.info(f"✅ Método 3 funcionou: {len(games)} jogos encontrados")
                return games
            
            logger.error("❌ Nenhum método funcionou")
            return []
            
        except Exception as e:
            logger.error(f"❌ Erro ao capturar jogos: {str(e)}")
            return []
    
    def _method1_container_based(self):
        """Método 1: Baseado em containers"""
        try:
            logger.info("🔍 Método 1: Procurando por containers de jogos...")
            
            # Procurar por diferentes tipos de containers
            selectors = [
                ".l-item",
                ".game-item",
                ".bet-item",
                "[class*='game']",
                "[class*='bet']",
                "[class*='item']"
            ]
            
            for selector in selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements and len(elements) > 0:
                        logger.info(f"🎯 Encontrados {len(elements)} elementos com selector: {selector}")
                        return self._extract_games_from_elements(elements)
                except:
                    continue
            
            return []
            
        except Exception as e:
            logger.error(f"❌ Erro no método 1: {str(e)}")
            return []
    
    def _method2_dynamic_xpath(self):
        """Método 2: XPaths dinâmicos"""
        try:
            logger.info("🔍 Método 2: Usando XPaths dinâmicos...")
            
            games = []
            max_attempts = 50  # Aumentar para bilhetes muito grandes
            
            # Tentar diferentes padrões de XPath
            xpath_patterns = [
                "//main/div[3]/div/div/div/div/div[{i}]",
                "//div[3]/div/div/div/div/div[{i}]",
                "//div[@class='l-item'][{i}]",
                "//div[contains(@class, 'game')][{i}]",
                "//div[contains(@class, 'bet')][{i}]"
            ]
            
            for pattern in xpath_patterns:
                logger.info(f"🔍 Testando padrão: {pattern}")
                
                for i in range(1, max_attempts + 1):
                    try:
                        xpath = pattern.format(i=i)
                        element = WebDriverWait(self.driver, 1).until(
                            EC.presence_of_element_located((By.XPATH, xpath))
                        )
                        
                        game_text = element.text.strip()
                        if game_text and len(game_text) > 10:
                            game_data = self._parse_game_text(game_text)
                            if game_data:
                                games.append(game_data)
                                logger.info(f"🎮 Jogo {len(games)}: {game_data.get('teams', 'N/A')}")
                        
                    except TimeoutException:
                        # Se não encontrou o elemento, tentar próximo padrão
                        break
                    except Exception as e:
                        continue
                
                if games:
                    break
            
            return games
            
        except Exception as e:
            logger.error(f"❌ Erro no método 2: {str(e)}")
            return []
    
    def _method3_text_analysis(self):
        """Método 3: Análise de texto completo"""
        try:
            logger.info("🔍 Método 3: Análise de texto completo...")
            
            # Capturar todo o texto da página
            page_text = self.driver.find_element(By.TAG_NAME, "body").text
            
            # Salvar para debug
            with open(f"debug_page_text_{int(time.time())}.txt", 'w', encoding='utf-8') as f:
                f.write(page_text)
            
            # Procurar por padrões de jogos no texto
            games = []
            
            # Padrão para encontrar blocos de jogos
            game_patterns = [
                r'([A-Za-zÀ-ÿ\s]+):\s*([A-Za-zÀ-ÿ\s]+)\s+(\d{2}/\d{2}\s+\d{2}:\d{2})\s+([A-Za-zÀ-ÿ\s]+)\s+x\s+([A-Za-zÀ-ÿ\s]+)\s+Vencedor:\s+([A-Za-zÀ-ÿ\s]+)\s+(\d+\.\d+)',
                r'([A-Za-zÀ-ÿ\s]+)\s+(\d{2}/\d{2}\s+\d{2}:\d{2})\s+([A-Za-zÀ-ÿ\s]+)\s+x\s+([A-Za-zÀ-ÿ\s]+)\s+Vencedor:\s+([A-Za-zÀ-ÿ\s]+)\s+(\d+\.\d+)',
                r'([A-Za-zÀ-ÿ\s]+)\s+x\s+([A-Za-zÀ-ÿ\s]+)\s+Vencedor:\s+([A-Za-zÀ-ÿ\s]+)\s+(\d+\.\d+)'
            ]
            
            for pattern in game_patterns:
                matches = re.findall(pattern, page_text, re.MULTILINE)
                for match in matches:
                    if len(match) >= 4:
                        game_data = {
                            'league': match[0] if len(match) > 4 else 'Liga não identificada',
                            'datetime': match[1] if len(match) > 4 else 'Data não identificada',
                            'teams': f"{match[-4]} x {match[-3]}" if len(match) > 4 else f"{match[0]} x {match[1]}",
                            'selection': f"Vencedor: {match[-2]}" if len(match) > 4 else f"Vencedor: {match[2]}",
                            'odds': match[-1]
                        }
                        games.append(game_data)
            
            # Remover duplicatas
            unique_games = []
            seen = set()
            for game in games:
                game_key = f"{game['teams']}_{game['odds']}"
                if game_key not in seen:
                    seen.add(game_key)
                    unique_games.append(game)
            
            return unique_games
            
        except Exception as e:
            logger.error(f"❌ Erro no método 3: {str(e)}")
            return []
    
    def _extract_games_from_elements(self, elements):
        """Extrai dados de jogos de uma lista de elementos"""
        games = []
        
        for i, element in enumerate(elements):
            try:
                game_text = element.text.strip()
                if game_text and len(game_text) > 10:
                    game_data = self._parse_game_text(game_text)
                    if game_data:
                        games.append(game_data)
                        logger.info(f"🎮 Jogo {len(games)}: {game_data.get('teams', 'N/A')}")
            except Exception as e:
                logger.warning(f"⚠️ Erro ao processar elemento {i}: {str(e)}")
                continue
        
        return games
    
    def _parse_game_text(self, text):
        """Parse do texto de um jogo"""
        try:
            # Padrões para extrair dados
            league_match = re.search(r'([A-Za-zÀ-ÿ\s]+):\s*([A-Za-zÀ-ÿ\s]+)', text)
            datetime_match = re.search(r'(\d{2}/\d{2}\s+\d{2}:\d{2})', text)
            teams_match = re.search(r'([A-Za-zÀ-ÿ\s]+)\s+x\s+([A-Za-zÀ-ÿ\s]+)', text)
            selection_match = re.search(r'Vencedor:\s*([A-Za-zÀ-ÿ\s]+)', text)
            odds_match = re.search(r'\b(\d+\.\d+)\b', text)
            
            if not teams_match:
                return None
            
            game_data = {
                'league': f"{league_match.group(1).strip()}: {league_match.group(2).strip()}" if league_match else "Liga não encontrada",
                'datetime': datetime_match.group(1) if datetime_match else "Data/Hora não encontrada",
                'teams': f"{teams_match.group(1).strip()} x {teams_match.group(2).strip()}",
                'selection': f"Vencedor: {selection_match.group(1).strip()}" if selection_match else "Aposta não encontrada",
                'odds': odds_match.group(1) if odds_match else "Odd não encontrada"
            }
            
            return game_data
            
        except Exception as e:
            logger.warning(f"⚠️ Erro ao fazer parse do texto: {str(e)}")
            return None
    
    def close(self):
        """Fecha o driver"""
        try:
            self.driver.quit()
            logger.info("🔒 Driver fechado")
        except:
            pass

def test_robust_scraper():
    """Teste do scraper robusto"""
    print("🧪 TESTE DO SCRAPER ROBUSTO")
    print("=" * 50)
    
    scraper = RobustValSportsScraper()
    
    try:
        # Testar com diferentes bilhetes
        test_codes = ["ELM5IM", "TQE4X1", "5pfin1"]
        
        for bet_code in test_codes:
            print(f"\n🎯 Testando bilhete: {bet_code}")
            
            games = scraper.get_all_games_robust(bet_code)
            
            print(f"📊 Resultado: {len(games)} jogos encontrados")
            
            for i, game in enumerate(games, 1):
                print(f"   🎮 Jogo {i}:")
                print(f"      🏆 Liga: {game.get('league')}")
                print(f"      ⚽ Times: {game.get('teams')}")
                print(f"      🎯 Seleção: {game.get('selection')}")
                print(f"      📅 Data/Hora: {game.get('datetime')}")
                print(f"      📈 Odds: {game.get('odds')}")
                print()
            
            time.sleep(2)
    
    finally:
        scraper.close()

if __name__ == "__main__":
    test_robust_scraper()
