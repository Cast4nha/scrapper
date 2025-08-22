#!/usr/bin/env python3
"""
Scraper Completo ValSports usando apenas Selenium
Captura TODOS os jogos aguardando JavaScript carregar
"""

import os
import time
import logging
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CompleteSeleniumScraper:
    def __init__(self):
        self.base_url = "https://www.valsports.net"
        self.is_logged_in = False
        
        # Configurar Firefox
        firefox_options = Options()
        firefox_options.add_argument("--headless")
        firefox_options.add_argument("--no-sandbox")
        firefox_options.add_argument("--disable-dev-shm-usage")
        firefox_options.add_argument("--disable-gpu")
        
        # Permitir JavaScript
        firefox_options.set_preference("javascript.enabled", True)
        
        self.driver = webdriver.Firefox(options=firefox_options)
        self.driver.set_window_size(1200, 800)
        self.driver.implicitly_wait(5)
        self.driver.set_page_load_timeout(30)
        
        logger.info("🚀 Scraper Selenium Completo inicializado")
    
    def login(self, username="cairovinicius", password="279999"):
        """Faz login no sistema"""
        try:
            logger.info(f"🔐 Fazendo login: {username}")
            
            self.driver.get(f"{self.base_url}/login")
            time.sleep(5)
            
            # Aguardar carregamento
            wait = WebDriverWait(self.driver, 15)
            
            # Preencher credenciais
            username_field = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".form-group:nth-child(1) > .form-control")))
            password_field = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".form-group:nth-child(2) > .form-control")))
            
            username_field.clear()
            username_field.send_keys(username)
            
            password_field.clear()
            password_field.send_keys(password)
            
            # Clicar no botão de login
            login_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")))
            login_button.click()
            
            time.sleep(8)
            
            # Verificar se login foi bem-sucedido
            current_url = self.driver.current_url
            
            if "login" not in current_url:
                self.is_logged_in = True
                logger.info("✅ Login realizado com sucesso")
                return True
            else:
                logger.error("❌ Login falhou")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro no login: {str(e)}")
            return False
    
    def capture_all_games(self, bet_code):
        """Captura TODOS os jogos do bilhete aguardando JavaScript"""
        try:
            if not self.is_logged_in:
                logger.error("❌ Usuário não está logado")
                return None
            
            logger.info(f"🎯 Capturando bilhete: {bet_code}")
            
            # Navegar para o bilhete
            bet_url = f"{self.base_url}/prebet/{bet_code}"
            self.driver.get(bet_url)
            
            # Aguardar página carregar
            time.sleep(10)
            
            # Aguardar JavaScript carregar completamente
            wait = WebDriverWait(self.driver, 30)
            
            try:
                # Aguardar elementos de bilhete aparecerem
                wait.until(lambda driver: len(driver.find_elements(By.TAG_NAME, "input")) >= 2)
                logger.info("✅ Página carregada com JavaScript")
            except TimeoutException:
                logger.warning("⚠️ Timeout aguardando JavaScript - continuando...")
            
            # Aguardar mais um pouco para garantir
            time.sleep(5)
            
            # Salvar debug
            current_url = self.driver.current_url
            logger.info(f"📍 URL atual: {current_url}")
            
            # Salvar screenshot e HTML para debug
            self.driver.save_screenshot(f"selenium_complete_{bet_code}.png")
            
            with open(f"selenium_complete_{bet_code}.html", "w", encoding="utf-8") as f:
                f.write(self.driver.page_source)
            
            # Capturar texto da página
            page_text = self.driver.find_element(By.TAG_NAME, "body").text
            
            with open(f"selenium_complete_text_{bet_code}.txt", "w", encoding="utf-8") as f:
                f.write(page_text)
            
            logger.info(f"📄 Tamanho do texto: {len(page_text)} caracteres")
            
            # Extrair dados do bilhete
            result = self._extract_bet_data(page_text, bet_code)
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Erro ao capturar bilhete: {str(e)}")
            return None
    
    def _extract_bet_data(self, page_text, bet_code):
        """Extrai dados do bilhete do texto da página"""
        try:
            logger.info("🔍 Extraindo dados do bilhete...")
            
            # Extrair informações gerais
            bet_data = {
                'bet_code': bet_code,
                'games': [],
                'total_odds': '0,00',
                'possible_prize': 'R$ 0,00',
                'bettor_name': '',
                'bet_value': '',
                'total_games': 0
            }
            
            # Extrair apostador e valor usando inputs
            try:
                inputs = self.driver.find_elements(By.TAG_NAME, "input")
                for input_elem in inputs:
                    placeholder = input_elem.get_attribute("placeholder")
                    value = input_elem.get_attribute("value")
                    
                    if placeholder and "apostador" in placeholder.lower() and value:
                        bet_data['bettor_name'] = value
                        logger.info(f"👤 Apostador: {value}")
                    
                    if placeholder and "valor" in placeholder.lower() and value:
                        bet_data['bet_value'] = value
                        logger.info(f"💵 Valor: {value}")
            except Exception as e:
                logger.warning(f"⚠️ Erro ao extrair inputs: {str(e)}")
            
            # Extrair total odds e possível prêmio do texto
            odds_match = re.search(r'Total odds\s*(\d+[,\d]*)', page_text, re.IGNORECASE)
            if odds_match:
                bet_data['total_odds'] = odds_match.group(1)
                logger.info(f"💰 Total odds: {odds_match.group(1)}")
            
            prize_match = re.search(r'Possível prêmio\s*(R\$\s*\d+[,\d]*)', page_text, re.IGNORECASE)
            if prize_match:
                bet_data['possible_prize'] = prize_match.group(1)
                logger.info(f"🏆 Possível prêmio: {prize_match.group(1)}")
            
            # Extrair jogos usando múltiplos padrões
            games = self._extract_games_from_text(page_text)
            
            if not games:
                # Tentar extrair usando XPaths (como backup)
                games = self._extract_games_from_elements()
            
            bet_data['games'] = games
            bet_data['total_games'] = len(games)
            
            logger.info(f"🎮 Total de jogos encontrados: {len(games)}")
            
            return bet_data
            
        except Exception as e:
            logger.error(f"❌ Erro ao extrair dados: {str(e)}")
            return None
    
    def _extract_games_from_text(self, page_text):
        """Extrai jogos usando regex no texto"""
        games = []
        
        # Padrões mais robustos para encontrar jogos
        patterns = [
            # Padrão completo: Liga: Campeonato Data/Hora Time1 x Time2 Vencedor: Time Odd
            r'([A-Za-zÀ-ÿ\s]+):\s*([A-Za-zÀ-ÿ\s]+)\s+(\d{2}/\d{2}\s+\d{2}:\d{2})\s+([A-Za-zÀ-ÿ\s]+?)\s+x\s+([A-Za-zÀ-ÿ\s]+?)\s+Vencedor:\s*([A-Za-zÀ-ÿ\s]+?)\s+(\d+\.\d+)',
            # Padrão sem liga
            r'(\d{2}/\d{2}\s+\d{2}:\d{2})\s+([A-Za-zÀ-ÿ\s]+?)\s+x\s+([A-Za-zÀ-ÿ\s]+?)\s+Vencedor:\s*([A-Za-zÀ-ÿ\s]+?)\s+(\d+\.\d+)',
            # Padrão apenas times e odd
            r'([A-Za-zÀ-ÿ\s]+?)\s+x\s+([A-Za-zÀ-ÿ\s]+?)\s+Vencedor:\s*([A-Za-zÀ-ÿ\s]+?)\s+(\d+\.\d+)',
            # Padrão para empate
            r'([A-Za-zÀ-ÿ\s]+?)\s+x\s+([A-Za-zÀ-ÿ\s]+?)\s+Empate\s+(\d+\.\d+)'
        ]
        
        for i, pattern in enumerate(patterns):
            matches = re.findall(pattern, page_text, re.MULTILINE | re.DOTALL)
            
            if matches:
                logger.info(f"✅ Padrão {i+1} encontrou {len(matches)} jogos")
                
                for match in matches:
                    if len(match) >= 4:
                        if len(match) == 7:  # Padrão completo
                            game = {
                                'league': f"{match[0].strip()}: {match[1].strip()}",
                                'datetime': match[2].strip(),
                                'teams': f"{match[3].strip()} x {match[4].strip()}",
                                'selection': f"Vencedor: {match[5].strip()}",
                                'odds': match[6].strip()
                            }
                        elif len(match) == 5:  # Sem liga
                            game = {
                                'league': "Liga não identificada",
                                'datetime': match[0].strip(),
                                'teams': f"{match[1].strip()} x {match[2].strip()}",
                                'selection': f"Vencedor: {match[3].strip()}",
                                'odds': match[4].strip()
                            }
                        elif len(match) == 4:  # Apenas times
                            game = {
                                'league': "Liga não identificada",
                                'datetime': "Data não identificada",
                                'teams': f"{match[0].strip()} x {match[1].strip()}",
                                'selection': f"Vencedor: {match[2].strip()}",
                                'odds': match[3].strip()
                            }
                        elif len(match) == 3:  # Empate
                            game = {
                                'league': "Liga não identificada",
                                'datetime': "Data não identificada",
                                'teams': f"{match[0].strip()} x {match[1].strip()}",
                                'selection': "Empate",
                                'odds': match[2].strip()
                            }
                        
                        # Limpar dados
                        game = self._clean_game_data(game)
                        if game:
                            games.append(game)
                
                if games:
                    break  # Se encontrou jogos, parar
        
        # Remover duplicatas
        unique_games = []
        seen = set()
        for game in games:
            game_key = f"{game['teams']}_{game['odds']}"
            if game_key not in seen:
                seen.add(game_key)
                unique_games.append(game)
        
        return unique_games
    
    def _extract_games_from_elements(self):
        """Método de backup usando XPaths"""
        games = []
        
        try:
            # Tentar XPaths conhecidos
            xpath_patterns = [
                "//main/div[3]/div/div/div/div/div[{i}]",
                "//div[3]/div/div/div/div/div[{i}]"
            ]
            
            for pattern in xpath_patterns:
                for i in range(1, 21):  # Até 20 jogos
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
                    except:
                        break
                
                if games:
                    break
        
        except Exception as e:
            logger.warning(f"⚠️ Erro no método backup: {str(e)}")
        
        return games
    
    def _parse_game_text(self, text):
        """Parse individual de texto de jogo"""
        try:
            # Usar mesmos padrões do método principal
            patterns = [
                r'([A-Za-zÀ-ÿ\s]+):\s*([A-Za-zÀ-ÿ\s]+)\s+(\d{2}/\d{2}\s+\d{2}:\d{2})\s+([A-Za-zÀ-ÿ\s]+?)\s+x\s+([A-Za-zÀ-ÿ\s]+?)\s+Vencedor:\s*([A-Za-zÀ-ÿ\s]+?)\s+(\d+\.\d+)',
                r'([A-Za-zÀ-ÿ\s]+?)\s+x\s+([A-Za-zÀ-ÿ\s]+?)\s+Vencedor:\s*([A-Za-zÀ-ÿ\s]+?)\s+(\d+\.\d+)'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, text, re.MULTILINE | re.DOTALL)
                if match:
                    if len(match.groups()) == 7:
                        return {
                            'league': f"{match.group(1).strip()}: {match.group(2).strip()}",
                            'datetime': match.group(3).strip(),
                            'teams': f"{match.group(4).strip()} x {match.group(5).strip()}",
                            'selection': f"Vencedor: {match.group(6).strip()}",
                            'odds': match.group(7).strip()
                        }
                    elif len(match.groups()) == 4:
                        return {
                            'league': "Liga não identificada",
                            'datetime': "Data não identificada",
                            'teams': f"{match.group(1).strip()} x {match.group(2).strip()}",
                            'selection': f"Vencedor: {match.group(3).strip()}",
                            'odds': match.group(4).strip()
                        }
            
            return None
            
        except Exception as e:
            logger.warning(f"⚠️ Erro ao parsear texto: {str(e)}")
            return None
    
    def _clean_game_data(self, game):
        """Limpa e valida dados do jogo"""
        try:
            # Limpar quebras de linha e espaços extras
            for key in game:
                if isinstance(game[key], str):
                    game[key] = re.sub(r'\s+', ' ', game[key]).strip()
            
            # Validar se tem dados mínimos
            if not game.get('teams') or not game.get('odds'):
                return None
            
            # Validar formato da odd
            if not re.match(r'\d+\.\d+', game['odds']):
                return None
            
            return game
            
        except Exception as e:
            logger.warning(f"⚠️ Erro ao limpar dados: {str(e)}")
            return None
    
    def close(self):
        """Fecha o driver"""
        try:
            self.driver.quit()
            logger.info("🔒 Driver fechado")
        except:
            pass

def test_complete_selenium():
    """Teste do scraper completo"""
    print("🧪 TESTE DO SCRAPER SELENIUM COMPLETO")
    print("=" * 50)
    
    scraper = CompleteSeleniumScraper()
    
    try:
        # Fazer login
        if scraper.login():
            print("✅ Login realizado com sucesso")
            
            # Testar bilhetes
            test_codes = ["ELM5IM", "TQE4X1"]
            
            for bet_code in test_codes:
                print(f"\n🎯 Testando bilhete: {bet_code}")
                
                result = scraper.capture_all_games(bet_code)
                
                if result:
                    print(f"📊 Sucesso! {result['total_games']} jogos encontrados")
                    print(f"💰 Total odds: {result['total_odds']}")
                    print(f"🏆 Possível prêmio: {result['possible_prize']}")
                    print(f"👤 Apostador: {result['bettor_name']}")
                    print(f"💵 Valor: {result['bet_value']}")
                    
                    print("\n🎮 Jogos encontrados:")
                    for i, game in enumerate(result['games'], 1):
                        print(f"   {i}. {game['teams']}")
                        print(f"      Liga: {game['league']}")
                        print(f"      Data: {game['datetime']}")
                        print(f"      Seleção: {game['selection']}")
                        print(f"      Odds: {game['odds']}")
                        print()
                else:
                    print("❌ Falha ao capturar dados")
                
                time.sleep(2)
        else:
            print("❌ Falha no login")
    
    finally:
        scraper.close()

if __name__ == "__main__":
    test_complete_selenium()
