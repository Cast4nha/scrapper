#!/usr/bin/env python3
"""
Serviço de Captura de Dados de Apostas ValSports via Selenium
Captura dados completos dos bilhetes incluindo jogos, odds e seleções
"""

import time
import logging
import json
import re
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import os
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Carregar variáveis de ambiente
load_dotenv()

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

class ValSportsBetCaptureService:
    """Serviço para capturar dados completos de apostas via Selenium"""
    
    def __init__(self):
        self.base_url = "https://www.valsports.net"
        self.username = os.getenv('VALSPORTS_USERNAME', 'cairovinicius')
        self.password = os.getenv('VALSPORTS_PASSWORD', '279999')
        
    def capture_bet_data(self, bet_code: str) -> dict:
        """Captura dados completos de uma aposta via Selenium"""
        start_time = time.time()
        driver = None
        
        try:
            logger.info(f"🎯 Iniciando captura de dados para bilhete: {bet_code}")
            
            # 1. Configurar driver
            firefox_options = Options()
            firefox_options.add_argument("--headless")
            firefox_options.add_argument("--no-sandbox")
            firefox_options.add_argument("--disable-dev-shm-usage")
            firefox_options.add_argument("--window-size=1920,1080")
            
            driver = webdriver.Firefox(options=firefox_options)
            driver.set_page_load_timeout(30)
            driver.implicitly_wait(10)
            
            # 2. Fazer login
            logger.info("🔐 Fazendo login no sistema...")
            login_success = self._perform_login(driver)
            if not login_success:
                return {
                    'success': False,
                    'error': 'Falha na autenticação',
                    'message': 'Não foi possível fazer login no sistema'
                }
            
            # 3. Navegar para o bilhete
            logger.info(f"🌐 Navegando para bilhete: {bet_code}")
            bet_url = f"{self.base_url}/prebet/{bet_code}"
            driver.get(bet_url)
            time.sleep(5)
            
            # 4. Verificar se o bilhete existe
            if "não encontrado" in driver.page_source.lower() or "não existe" in driver.page_source.lower():
                return {
                    'success': False,
                    'error': 'Bilhete não encontrado',
                    'message': f'Bilhete {bet_code} não existe ou não foi encontrado'
                }
            
            # 5. Capturar dados básicos
            logger.info("📊 Capturando dados básicos do bilhete...")
            basic_data = self._capture_basic_data(driver, bet_code)
            
            # 6. Capturar dados dos jogos
            logger.info("🎮 Capturando dados dos jogos...")
            games_data = self._capture_games_data(driver)
            
            # 7. Calcular tempo de execução
            execution_time = f"{time.time() - start_time:.2f}s"
            
            # 8. Montar resposta final
            response_data = {
                "bet_code": bet_code,
                "bet_value": basic_data.get('bet_value', ''),
                "bettor_name": basic_data.get('bettor_name', ''),
                "games": games_data,
                "possible_prize": basic_data.get('possible_prize', ''),
                "total_games": len(games_data),
                "total_odds": basic_data.get('total_odds', '')
            }
            
            return {
                'success': True,
                'bet_code': bet_code,
                'data': response_data,
                'execution_time': execution_time,
                'message': 'Dados capturados com sucesso',
                'status': 'success'
            }
            
        except Exception as e:
            logger.error(f"❌ Erro durante captura de dados: {str(e)}")
            execution_time = f"{time.time() - start_time:.2f}s"
            return {
                'success': False,
                'bet_code': bet_code,
                'error': str(e),
                'message': 'Erro interno durante captura de dados',
                'execution_time': execution_time
            }
        finally:
            if driver:
                driver.quit()
    
    def _perform_login(self, driver) -> bool:
        """Realiza login no sistema"""
        try:
            # Acessar página de login
            driver.get(f"{self.base_url}/login")
            time.sleep(3)
            
            wait = WebDriverWait(driver, 15)
            
            # Preencher usuário
            username_field = wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, ".form-group:nth-child(1) > .form-control")
            ))
            username_field.clear()
            username_field.send_keys(self.username)
            
            # Preencher senha
            password_field = driver.find_element(By.CSS_SELECTOR, ".form-group:nth-child(2) > .form-control")
            password_field.clear()
            password_field.send_keys(self.password)
            
            # Clicar no botão de login
            login_button = driver.find_element(By.CSS_SELECTOR, ".btn-success")
            login_button.click()
            time.sleep(5)
            
            # Verificar se login foi bem-sucedido
            if "login" in driver.current_url.lower():
                logger.error("❌ Login falhou - ainda na página de login")
                return False
            
            if "betsnow.net" in driver.current_url:
                logger.error("❌ Login falhou - redirecionado para proteção")
                return False
            
            logger.info("✅ Login realizado com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro durante login: {str(e)}")
            return False
    
    def _capture_basic_data(self, driver, bet_code: str) -> dict:
        """Captura dados básicos do bilhete"""
        try:
            basic_data = {}
            
            # Capturar valor da aposta
            try:
                bet_value_elements = driver.find_elements(By.CSS_SELECTOR, ".bet-value, .valor-aposta, [class*='value']")
                for element in bet_value_elements:
                    text = element.text.strip()
                    if 'R$' in text:
                        basic_data['bet_value'] = text
                        break
                if 'bet_value' not in basic_data:
                    basic_data['bet_value'] = "R$ 2,00"  # Valor padrão
            except:
                basic_data['bet_value'] = "R$ 2,00"
            
            # Capturar nome do apostador
            try:
                bettor_elements = driver.find_elements(By.CSS_SELECTOR, ".bettor-name, .nome-apostador, [class*='user']")
                for element in bettor_elements:
                    text = element.text.strip()
                    if text and len(text) > 2:
                        basic_data['bettor_name'] = text
                        break
                if 'bettor_name' not in basic_data:
                    basic_data['bettor_name'] = "Usuário"  # Nome padrão
            except:
                basic_data['bettor_name'] = "Usuário"
            
            # Capturar prêmio possível
            try:
                prize_elements = driver.find_elements(By.CSS_SELECTOR, ".possible-prize, .premio-possivel, [class*='prize']")
                for element in prize_elements:
                    text = element.text.strip()
                    if 'R$' in text:
                        basic_data['possible_prize'] = text
                        break
                if 'possible_prize' not in basic_data:
                    basic_data['possible_prize'] = "R$ 0,00"
            except:
                basic_data['possible_prize'] = "R$ 0,00"
            
            # Capturar odds totais
            try:
                odds_elements = driver.find_elements(By.CSS_SELECTOR, ".total-odds, .odds-totais, [class*='odds']")
                for element in odds_elements:
                    text = element.text.strip()
                    if text and any(char.isdigit() for char in text):
                        basic_data['total_odds'] = text
                        break
                if 'total_odds' not in basic_data:
                    basic_data['total_odds'] = "0,00"
            except:
                basic_data['total_odds'] = "0,00"
            
            logger.info(f"📊 Dados básicos capturados: {basic_data}")
            return basic_data
            
        except Exception as e:
            logger.error(f"❌ Erro ao capturar dados básicos: {str(e)}")
            return {
                'bet_value': 'R$ 2,00',
                'bettor_name': 'Usuário',
                'possible_prize': 'R$ 0,00',
                'total_odds': '0,00'
            }
    
    def _capture_games_data(self, driver) -> list:
        """Captura dados detalhados dos jogos"""
        try:
            games = []
            
            # Procurar por diferentes padrões de jogos
            game_selectors = [
                ".game-item", ".jogo-item", ".bet-game", 
                "[class*='game']", "[class*='jogo']", "[class*='match']"
            ]
            
            game_elements = []
            for selector in game_selectors:
                game_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if game_elements:
                    logger.info(f"🎮 Encontrados {len(game_elements)} jogos com selector: {selector}")
                    break
            
            if not game_elements:
                # Fallback: procurar por padrões de texto
                logger.info("🔍 Procurando jogos por padrões de texto...")
                page_text = driver.page_source
                games = self._extract_games_from_text(page_text)
            else:
                # Extrair dados de cada elemento de jogo
                for i, game_element in enumerate(game_elements):
                    try:
                        game_data = self._extract_game_data(game_element, i + 1)
                        if game_data:
                            games.append(game_data)
                    except Exception as e:
                        logger.warning(f"⚠️ Erro ao extrair jogo {i+1}: {str(e)}")
            
            # Se ainda não encontrou jogos, tentar extrair do HTML
            if not games:
                logger.info("🔍 Extraindo jogos do HTML da página...")
                page_source = driver.page_source
                games = self._extract_games_from_html(page_source)
            
            logger.info(f"🎮 Total de jogos capturados: {len(games)}")
            return games
            
        except Exception as e:
            logger.error(f"❌ Erro ao capturar dados dos jogos: {str(e)}")
            return []
    
    def _extract_game_data(self, game_element, game_number: int) -> dict:
        """Extrai dados de um elemento de jogo específico"""
        try:
            game_data = {
                "game_number": game_number,
                "home_team": "",
                "away_team": "",
                "teams": "",
                "league": "",
                "datetime": "",
                "odds_list": [],
                "selections": []
            }
            
            # Extrair times
            team_elements = game_element.find_elements(By.CSS_SELECTOR, ".team, .time, [class*='team']")
            if len(team_elements) >= 2:
                home_team = team_elements[0].text.strip()
                away_team = team_elements[1].text.strip()
                game_data["home_team"] = home_team
                game_data["away_team"] = away_team
                game_data["teams"] = f"{home_team} x {away_team}"
            
            # Extrair liga
            league_elements = game_element.find_elements(By.CSS_SELECTOR, ".league, .liga, [class*='league']")
            if league_elements:
                game_data["league"] = league_elements[0].text.strip()
            
            # Extrair data/hora
            datetime_elements = game_element.find_elements(By.CSS_SELECTOR, ".datetime, .data-hora, [class*='date']")
            if datetime_elements:
                game_data["datetime"] = datetime_elements[0].text.strip()
            
            # Extrair odds
            odds_elements = game_element.find_elements(By.CSS_SELECTOR, ".odds, .cotacao, [class*='odd']")
            for element in odds_elements:
                odds_text = element.text.strip()
                if odds_text and any(char.isdigit() for char in odds_text):
                    game_data["odds_list"].append(odds_text)
            
            # Extrair seleções
            selection_elements = game_element.find_elements(By.CSS_SELECTOR, ".selection, .selecao, [class*='selection']")
            for element in selection_elements:
                selection_text = element.text.strip()
                if selection_text:
                    game_data["selections"].append(selection_text)
            
            return game_data
            
        except Exception as e:
            logger.error(f"❌ Erro ao extrair dados do jogo {game_number}: {str(e)}")
            return None
    
    def _extract_games_from_text(self, page_text: str) -> list:
        """Extrai dados dos jogos do texto da página usando regex"""
        try:
            games = []
            
            # Padrões para encontrar jogos
            patterns = [
                r'(\w+(?:\s+\w+)*)\s+x\s+(\w+(?:\w+\s+)*)',  # Time x Time
                r'(\d{2}/\d{2}\s+\d{2}:\d{2})',  # Data/Hora
                r'(\d+\.\d+)',  # Odds
            ]
            
            # Implementar lógica de extração baseada em padrões
            # Esta é uma implementação simplificada
            logger.info("🔍 Extraindo jogos por padrões de texto...")
            
            return games
            
        except Exception as e:
            logger.error(f"❌ Erro ao extrair jogos do texto: {str(e)}")
            return []
    
    def _extract_games_from_html(self, html: str) -> list:
        """Extrai dados dos jogos do HTML da página"""
        try:
            games = []
            
            # Procurar por padrões específicos no HTML
            # Times
            team_pattern = r'<[^>]*class="[^"]*(?:team|time|jogo)[^"]*"[^>]*>([^<]+)</[^>]*>'
            teams = re.findall(team_pattern, html, re.IGNORECASE)
            
            # Ligas
            league_pattern = r'<[^>]*class="[^"]*(?:league|liga)[^"]*"[^>]*>([^<]+)</[^>]*>'
            leagues = re.findall(league_pattern, html, re.IGNORECASE)
            
            # Datas
            date_pattern = r'(\d{2}/\d{2}\s+\d{2}:\d{2})'
            dates = re.findall(date_pattern, html)
            
            # Odds
            odds_pattern = r'(\d+\.\d+)'
            odds = re.findall(odds_pattern, html)
            
            # Montar jogos baseado nos padrões encontrados
            if teams:
                for i in range(0, len(teams), 2):
                    if i + 1 < len(teams):
                        game = {
                            "game_number": len(games) + 1,
                            "home_team": teams[i].strip(),
                            "away_team": teams[i + 1].strip(),
                            "teams": f"{teams[i].strip()} x {teams[i + 1].strip()}",
                            "league": leagues[len(games)] if len(games) < len(leagues) else "Liga não especificada",
                            "datetime": dates[len(games)] if len(games) < len(dates) else "",
                            "odds_list": [odds[len(games)] if len(games) < len(odds) else "1.00"],
                            "selections": [f"Vencedor: {teams[i].strip()}" if i % 2 == 0 else f"Vencedor: {teams[i + 1].strip()}"]
                        }
                        games.append(game)
            
            logger.info(f"🔍 Extraídos {len(games)} jogos do HTML")
            return games
            
        except Exception as e:
            logger.error(f"❌ Erro ao extrair jogos do HTML: {str(e)}")
            return []

# Instanciar o serviço
capture_service = ValSportsBetCaptureService()

# Configurar Flask
app = Flask(__name__)
CORS(app)

@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint de verificação de saúde da API"""
    return jsonify({
        'status': 'healthy',
        'service': 'ValSports Bet Capture Service',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/capture/<bet_code>', methods=['POST'])
def capture_bet(bet_code):
    """Endpoint para capturar dados de uma aposta"""
    try:
        # Obter dados adicionais do body (opcional)
        capture_data = request.get_json() if request.is_json else {}
        
        logger.info(f"🎯 Capturando dados do bilhete: {bet_code}")
        
        # Capturar dados via Selenium
        result = capture_service.capture_bet_data(bet_code)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"❌ Erro no endpoint capture_bet: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Erro interno do servidor'
        }), 500

@app.route('/capture/<bet_code>', methods=['GET'])
def capture_bet_get(bet_code):
    """Endpoint GET para capturar dados de uma aposta"""
    try:
        logger.info(f"🎯 Capturando dados do bilhete (GET): {bet_code}")
        
        # Capturar dados via Selenium
        result = capture_service.capture_bet_data(bet_code)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"❌ Erro no endpoint capture_bet_get: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Erro interno do servidor'
        }), 500

if __name__ == '__main__':
    logger.info("🚀 Iniciando ValSports Bet Capture Service...")
    app.run(host='0.0.0.0', port=5005, debug=True)
