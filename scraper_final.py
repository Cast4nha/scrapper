#!/usr/bin/env python3
"""
Scraper Final ValSports - Apenas Selenium
Usando XPaths e CSS selectors específicos fornecidos pelo usuário
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

class FinalValSportsScraper:
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
        
        logger.info("🚀 Scraper Final ValSports inicializado")
    
    def login(self, username="cairovinicius", password="279999"):
        """Faz login no sistema"""
        try:
            logger.info(f"🔐 Fazendo login: {username}")
            
            self.driver.get(f"{self.base_url}/login")
            time.sleep(5)
            
            # Aguardar carregamento
            wait = WebDriverWait(self.driver, 15)
            
            # Preencher credenciais usando seletores corretos
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
    
    def scrape_bet_ticket(self, bet_code):
        """Captura dados do bilhete usando XPaths e CSS selectors específicos"""
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
            
            # Aguardar JavaScript carregar
            wait = WebDriverWait(self.driver, 30)
            
            try:
                # Aguardar container principal do bilhete
                wait.until(EC.presence_of_element_located((By.XPATH, "//main/div[3]/div/div/div")))
                logger.info("✅ Container do bilhete carregado")
            except TimeoutException:
                logger.warning("⚠️ Timeout aguardando container - continuando...")
            
            # Aguardar mais um pouco para garantir
            time.sleep(5)
            
            # Salvar debug
            current_url = self.driver.current_url
            logger.info(f"📍 URL atual: {current_url}")
            
            # Salvar screenshot e HTML para debug
            self.driver.save_screenshot(f"final_scraper_{bet_code}.png")
            
            with open(f"final_scraper_{bet_code}.html", "w", encoding="utf-8") as f:
                f.write(self.driver.page_source)
            
            # Extrair dados usando XPaths e CSS selectors específicos
            bet_data = self._extract_bet_data_with_selectors(bet_code)
            
            return bet_data
            
        except Exception as e:
            logger.error(f"❌ Erro ao capturar bilhete: {str(e)}")
            return None
    
    def _extract_bet_data_with_selectors(self, bet_code):
        """Extrai dados usando XPaths e CSS selectors específicos"""
        try:
            logger.info("🔍 Extraindo dados com selectors específicos...")
            
            # Estrutura base dos dados
            bet_data = {
                'bet_code': bet_code,
                'total_games': 0,
                'total_odds': '',
                'possible_prize': '',
                'bettor_name': '',
                'bet_value': '',
                'games': []
            }
            
            # 1. Extrair quantidade de jogos
            try:
                games_count_element = self.driver.find_element(By.XPATH, "//div[3]/div/div/div/h5")
                games_text = games_count_element.text
                logger.info(f"📊 Texto do contador: {games_text}")
                
                # Extrair número do texto (ex: "5 jogos" -> 5)
                count_match = re.search(r'(\d+)', games_text)
                if count_match:
                    bet_data['total_games'] = int(count_match.group(1))
                    logger.info(f"🎮 Total de jogos: {bet_data['total_games']}")
            except Exception as e:
                logger.warning(f"⚠️ Erro ao extrair contador de jogos: {str(e)}")
            
            # 2. Extrair total das odds
            try:
                total_odds_element = self.driver.find_element(By.XPATH, "//main/div[3]/div/div[2]/div/div/div/div[2]")
                bet_data['total_odds'] = total_odds_element.text.strip()
                logger.info(f"💰 Total odds: {bet_data['total_odds']}")
            except Exception as e:
                logger.warning(f"⚠️ Erro ao extrair total odds: {str(e)}")
            
            # 3. Extrair possível retorno
            try:
                possible_prize_element = self.driver.find_element(By.XPATH, "//main/div[3]/div/div[2]/div/div[2]/div/div[2]")
                bet_data['possible_prize'] = possible_prize_element.text.strip()
                logger.info(f"🏆 Possível prêmio: {bet_data['possible_prize']}")
            except Exception as e:
                logger.warning(f"⚠️ Erro ao extrair possível prêmio: {str(e)}")
            
            # 4. Extrair nome do apostador
            try:
                bettor_inputs = self.driver.find_elements(By.XPATH, "//input[@type='text']")
                if len(bettor_inputs) >= 2:
                    bet_data['bettor_name'] = bettor_inputs[1].get_attribute("value")
                    logger.info(f"👤 Apostador: {bet_data['bettor_name']}")
            except Exception as e:
                logger.warning(f"⚠️ Erro ao extrair nome do apostador: {str(e)}")
            
            # 5. Extrair valor apostado
            try:
                bettor_inputs = self.driver.find_elements(By.XPATH, "//input[@type='text']")
                if len(bettor_inputs) >= 3:
                    bet_data['bet_value'] = bettor_inputs[2].get_attribute("value")
                    logger.info(f"💵 Valor: {bet_data['bet_value']}")
            except Exception as e:
                logger.warning(f"⚠️ Erro ao extrair valor: {str(e)}")
            
            # 6. Extrair jogos usando iteração dinâmica
            games = self._extract_games_dynamically()
            bet_data['games'] = games
            
            # Atualizar contador se não foi encontrado
            if bet_data['total_games'] == 0:
                bet_data['total_games'] = len(games)
            
            logger.info(f"🎮 Total de jogos extraídos: {len(games)}")
            
            return bet_data
            
        except Exception as e:
            logger.error(f"❌ Erro ao extrair dados: {str(e)}")
            return None
    
    def _extract_games_dynamically(self):
        """Extrai jogos usando iteração dinâmica com .find_elements"""
        games = []
        
        try:
            logger.info("🎯 Extraindo jogos dinamicamente...")
            
            # Encontrar todos os elementos .l-item (jogos)
            game_elements = self.driver.find_elements(By.CSS_SELECTOR, ".l-item")
            
            logger.info(f"🔍 Encontrados {len(game_elements)} elementos .l-item")
            
            for i, game_element in enumerate(game_elements, 1):
                try:
                    logger.info(f"🎮 Processando jogo {i}...")
                    
                    game_data = {
                        'game_number': i,
                        'league': '',
                        'home_team': '',
                        'away_team': '',
                        'selection': '',
                        'odds': '',
                        'datetime': ''
                    }
                    
                    # Extrair nome da liga
                    try:
                        league_element = game_element.find_element(By.CSS_SELECTOR, ".l-item-emphasis")
                        game_data['league'] = league_element.text.strip()
                        logger.info(f"   Liga: {game_data['league']}")
                    except Exception as e:
                        logger.warning(f"   ⚠️ Erro ao extrair liga: {str(e)}")
                    
                    # Extrair times usando colunas
                    try:
                        # Time da casa (coluna 4)
                        home_team_element = game_element.find_element(By.CSS_SELECTOR, ".col:nth-child(4)")
                        game_data['home_team'] = home_team_element.text.strip()
                        logger.info(f"   Time casa: {game_data['home_team']}")
                    except Exception as e:
                        logger.warning(f"   ⚠️ Erro ao extrair time casa: {str(e)}")
                    
                    try:
                        # Time fora (coluna 7)
                        away_team_element = game_element.find_element(By.CSS_SELECTOR, ".col:nth-child(7)")
                        game_data['away_team'] = away_team_element.text.strip()
                        logger.info(f"   Time fora: {game_data['away_team']}")
                    except Exception as e:
                        logger.warning(f"   ⚠️ Erro ao extrair time fora: {str(e)}")
                    
                    try:
                        # Seleção/aposta (coluna 10)
                        selection_element = game_element.find_element(By.CSS_SELECTOR, ".col:nth-child(10)")
                        game_data['selection'] = selection_element.text.strip()
                        logger.info(f"   Seleção: {game_data['selection']}")
                    except Exception as e:
                        logger.warning(f"   ⚠️ Erro ao extrair seleção: {str(e)}")
                    
                    try:
                        # Odds (coluna 11)
                        odds_element = game_element.find_element(By.CSS_SELECTOR, ".col-auto:nth-child(11)")
                        game_data['odds'] = odds_element.text.strip()
                        logger.info(f"   Odds: {game_data['odds']}")
                    except Exception as e:
                        logger.warning(f"   ⚠️ Erro ao extrair odds: {str(e)}")
                    
                    # Tentar extrair data/hora do texto completo do elemento
                    try:
                        full_text = game_element.text
                        datetime_match = re.search(r'(\d{2}/\d{2}\s+\d{2}:\d{2})', full_text)
                        if datetime_match:
                            game_data['datetime'] = datetime_match.group(1)
                            logger.info(f"   Data/Hora: {game_data['datetime']}")
                    except Exception as e:
                        logger.warning(f"   ⚠️ Erro ao extrair data/hora: {str(e)}")
                    
                    # Validar se tem dados mínimos
                    if game_data['home_team'] and game_data['away_team'] and game_data['odds']:
                        # Formatar dados
                        game_data['teams'] = f"{game_data['home_team']} x {game_data['away_team']}"
                        games.append(game_data)
                        logger.info(f"   ✅ Jogo {i} adicionado")
                    else:
                        logger.warning(f"   ⚠️ Jogo {i} sem dados suficientes - ignorando")
                
                except Exception as e:
                    logger.error(f"   ❌ Erro ao processar jogo {i}: {str(e)}")
                    continue
            
            logger.info(f"🎮 Total de jogos válidos extraídos: {len(games)}")
            
        except Exception as e:
            logger.error(f"❌ Erro na extração dinâmica: {str(e)}")
        
        return games
    
    def confirm_bet(self, bet_code):
        """Confirma a aposta no sistema"""
        try:
            if not self.is_logged_in:
                logger.error("❌ Usuário não está logado")
                return False
            
            logger.info(f"✅ Confirmando aposta: {bet_code}")
            
            # Navegar para o bilhete
            bet_url = f"{self.base_url}/prebet/{bet_code}"
            self.driver.get(bet_url)
            time.sleep(5)
            
            # Aguardar carregamento
            wait = WebDriverWait(self.driver, 15)
            
            # Clicar no botão de confirmação
            confirm_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".btn-group > .text-style")))
            confirm_button.click()
            time.sleep(2)
            
            # Clicar em "Sim" para confirmar
            yes_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(),'Sim')]")))
            yes_button.click()
            time.sleep(3)
            
            logger.info("✅ Aposta confirmada com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao confirmar aposta: {str(e)}")
            return False
    
    def close(self):
        """Fecha o driver"""
        try:
            self.driver.quit()
            logger.info("🔒 Driver fechado")
        except:
            pass

def test_final_scraper():
    """Teste do scraper final"""
    print("🧪 TESTE DO SCRAPER FINAL")
    print("=" * 50)
    
    scraper = FinalValSportsScraper()
    
    try:
        # Fazer login
        if scraper.login():
            print("✅ Login realizado com sucesso")
            
            # Testar bilhetes
            test_codes = ["ELM5IM", "TQE4X1"]
            
            for bet_code in test_codes:
                print(f"\n🎯 Testando bilhete: {bet_code}")
                
                result = scraper.scrape_bet_ticket(bet_code)
                
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
    test_final_scraper()
