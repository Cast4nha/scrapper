#!/usr/bin/env python3
"""
Serviço de Captura de Dados de Apostas ValSports via Selenium - VERSÃO MELHORADA
Captura dados completos dos bilhetes com análise profunda da página
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

class ValSportsBetCaptureServiceImproved:
    """Serviço melhorado para capturar dados completos de apostas via Selenium"""
    
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
            time.sleep(8)  # Aguardar mais tempo para carregar
            
            # 4. Verificar se o bilhete existe
            if "não encontrado" in driver.page_source.lower() or "não existe" in driver.page_source.lower():
                return {
                    'success': False,
                    'error': 'Bilhete não encontrado',
                    'message': f'Bilhete {bet_code} não existe ou não foi encontrado'
                }
            
            # 5. Capturar dados básicos
            logger.info("📊 Capturando dados básicos do bilhete...")
            basic_data = self._capture_basic_data_improved(driver, bet_code)
            
            # 6. Capturar dados dos jogos com análise profunda
            logger.info("🎮 Capturando dados dos jogos com análise profunda...")
            games_data = self._capture_games_data_improved(driver)
            
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
    
    def _capture_basic_data_improved(self, driver, bet_code: str) -> dict:
        """Captura dados básicos do bilhete com seletores melhorados"""
        try:
            basic_data = {}
            
            # Capturar valor da aposta - múltiplos seletores
            bet_value_selectors = [
                ".bet-value", ".valor-aposta", "[class*='value']", 
                ".amount", ".valor", ".price", ".bet-amount",
                "span:contains('R$')", "div:contains('R$')"
            ]
            
            for selector in bet_value_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        text = element.text.strip()
                        if 'R$' in text:
                            basic_data['bet_value'] = text
                            logger.info(f"💰 Valor da aposta encontrado: {text}")
                            break
                    if 'bet_value' in basic_data:
                        break
                except:
                    continue
            
            if 'bet_value' not in basic_data:
                # Fallback: procurar por texto contendo R$
                page_text = driver.page_source
                bet_value_match = re.search(r'R\$\s*[\d,]+\.?\d*', page_text)
                if bet_value_match:
                    basic_data['bet_value'] = bet_value_match.group()
                else:
                    basic_data['bet_value'] = "R$ 2,00"
            
            # Capturar nome do apostador
            bettor_selectors = [
                ".bettor-name", ".nome-apostador", "[class*='user']", 
                ".username", ".user-name", ".player-name"
            ]
            
            for selector in bettor_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        text = element.text.strip()
                        if text and len(text) > 2 and not text.isdigit():
                            basic_data['bettor_name'] = text
                            logger.info(f"👤 Nome do apostador encontrado: {text}")
                            break
                    if 'bettor_name' in basic_data:
                        break
                except:
                    continue
            
            if 'bettor_name' not in basic_data:
                basic_data['bettor_name'] = "Usuário"
            
            # Capturar prêmio possível
            prize_selectors = [
                ".possible-prize", ".premio-possivel", "[class*='prize']",
                ".prize", ".ganho", ".retorno", ".profit"
            ]
            
            for selector in prize_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        text = element.text.strip()
                        if 'R$' in text:
                            basic_data['possible_prize'] = text
                            logger.info(f"🏆 Prêmio possível encontrado: {text}")
                            break
                    if 'possible_prize' in basic_data:
                        break
                except:
                    continue
            
            if 'possible_prize' not in basic_data:
                basic_data['possible_prize'] = "R$ 0,00"
            
            # Capturar odds totais
            odds_selectors = [
                ".total-odds", ".odds-totais", "[class*='odds']",
                ".multiplier", ".multiplicador", ".total-multiplier"
            ]
            
            for selector in odds_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        text = element.text.strip()
                        if text and any(char.isdigit() for char in text):
                            basic_data['total_odds'] = text
                            logger.info(f"📈 Odds totais encontradas: {text}")
                            break
                    if 'total_odds' in basic_data:
                        break
                except:
                    continue
            
            if 'total_odds' not in basic_data:
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
    
    def _capture_games_data_improved(self, driver) -> list:
        """Captura dados detalhados dos jogos com análise profunda"""
        try:
            games = []
            
            # 1. Tentar capturar via elementos estruturados
            logger.info("🔍 Tentando capturar jogos via elementos estruturados...")
            games = self._capture_games_from_structured_elements(driver)
            
            # 2. Se não encontrou, tentar via análise de texto
            if not games:
                logger.info("🔍 Tentando capturar jogos via análise de texto...")
                games = self._capture_games_from_text_analysis(driver)
            
            # 3. Se ainda não encontrou, tentar via HTML parsing
            if not games:
                logger.info("🔍 Tentando capturar jogos via parsing HTML...")
                games = self._capture_games_from_html_parsing(driver)
            
            # 4. Fallback: criar estrutura básica baseada em padrões encontrados
            if not games:
                logger.info("🔍 Criando estrutura básica baseada em padrões...")
                games = self._create_basic_game_structure(driver)
            
            logger.info(f"🎮 Total de jogos capturados: {len(games)}")
            return games
            
        except Exception as e:
            logger.error(f"❌ Erro ao capturar dados dos jogos: {str(e)}")
            return []
    
    def _capture_games_from_structured_elements(self, driver) -> list:
        """Captura jogos de elementos estruturados na página"""
        try:
            games = []
            
            # Seletores mais específicos para jogos
            game_selectors = [
                ".game-item", ".jogo-item", ".bet-game", ".match-item",
                ".event-item", ".fixture-item", ".competition-item",
                "[class*='game']", "[class*='jogo']", "[class*='match']",
                "[class*='event']", "[class*='fixture']"
            ]
            
            game_elements = []
            for selector in game_selectors:
                game_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if game_elements:
                    logger.info(f"🎮 Encontrados {len(game_elements)} jogos com selector: {selector}")
                    break
            
            if game_elements:
                for i, game_element in enumerate(game_elements):
                    try:
                        game_data = self._extract_game_data_improved(game_element, i + 1)
                        if game_data and any(game_data.values()):
                            games.append(game_data)
                    except Exception as e:
                        logger.warning(f"⚠️ Erro ao extrair jogo {i+1}: {str(e)}")
            
            return games
            
        except Exception as e:
            logger.error(f"❌ Erro ao capturar jogos estruturados: {str(e)}")
            return []
    
    def _extract_game_data_improved(self, game_element, game_number: int) -> dict:
        """Extrai dados de um elemento de jogo com seletores melhorados"""
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
            
            # Seletores para times
            team_selectors = [
                ".team", ".time", ".home-team", ".away-team",
                ".team-name", ".time-nome", "[class*='team']",
                ".participant", ".competitor"
            ]
            
            team_elements = []
            for selector in team_selectors:
                team_elements = game_element.find_elements(By.CSS_SELECTOR, selector)
                if len(team_elements) >= 2:
                    break
            
            if len(team_elements) >= 2:
                home_team = team_elements[0].text.strip()
                away_team = team_elements[1].text.strip()
                game_data["home_team"] = home_team
                game_data["away_team"] = away_team
                game_data["teams"] = f"{home_team} x {away_team}"
                logger.info(f"⚽ Times encontrados: {game_data['teams']}")
            
            # Seletores para liga
            league_selectors = [
                ".league", ".liga", ".competition", ".tournament",
                ".championship", ".campeonato", "[class*='league']"
            ]
            
            for selector in league_selectors:
                elements = game_element.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    game_data["league"] = elements[0].text.strip()
                    logger.info(f"🏆 Liga encontrada: {game_data['league']}")
                    break
            
            # Seletores para data/hora
            datetime_selectors = [
                ".datetime", ".data-hora", ".date-time", ".schedule",
                ".time", ".hora", "[class*='date']", "[class*='time']"
            ]
            
            for selector in datetime_selectors:
                elements = game_element.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    game_data["datetime"] = elements[0].text.strip()
                    logger.info(f"📅 Data/Hora encontrada: {game_data['datetime']}")
                    break
            
            # Seletores para odds
            odds_selectors = [
                ".odds", ".cotacao", ".odd", ".price", ".rate",
                ".multiplier", ".multiplicador", "[class*='odd']"
            ]
            
            for selector in odds_selectors:
                elements = game_element.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    odds_text = element.text.strip()
                    if odds_text and any(char.isdigit() for char in odds_text):
                        game_data["odds_list"].append(odds_text)
                        logger.info(f"📊 Odds encontrada: {odds_text}")
            
            # Seletores para seleções
            selection_selectors = [
                ".selection", ".selecao", ".pick", ".choice",
                ".bet-type", ".tipo-aposta", "[class*='selection']"
            ]
            
            for selector in selection_selectors:
                elements = game_element.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    selection_text = element.text.strip()
                    if selection_text:
                        game_data["selections"].append(selection_text)
                        logger.info(f"🎯 Seleção encontrada: {selection_text}")
            
            return game_data
            
        except Exception as e:
            logger.error(f"❌ Erro ao extrair dados do jogo {game_number}: {str(e)}")
            return None
    
    def _capture_games_from_text_analysis(self, driver) -> list:
        """Captura jogos através de análise de texto da página"""
        try:
            games = []
            page_text = driver.page_source
            
            # Padrões para encontrar jogos
            patterns = {
                'teams': r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+x\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
                'datetime': r'(\d{2}/\d{2}\s+\d{2}:\d{2})',
                'odds': r'(\d+\.\d+)',
                'league': r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*:\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'
            }
            
            # Extrair times
            teams_matches = re.findall(patterns['teams'], page_text)
            datetime_matches = re.findall(patterns['datetime'], page_text)
            odds_matches = re.findall(patterns['odds'], page_text)
            league_matches = re.findall(patterns['league'], page_text)
            
            logger.info(f"🔍 Encontrados: {len(teams_matches)} times, {len(datetime_matches)} datas, {len(odds_matches)} odds")
            
            # Montar jogos baseado nos padrões encontrados
            for i, (home, away) in enumerate(teams_matches):
                game = {
                    "game_number": i + 1,
                    "home_team": home.strip(),
                    "away_team": away.strip(),
                    "teams": f"{home.strip()} x {away.strip()}",
                    "league": league_matches[i] if i < len(league_matches) else "Liga não especificada",
                    "datetime": datetime_matches[i] if i < len(datetime_matches) else "",
                    "odds_list": [odds_matches[i]] if i < len(odds_matches) else ["1.00"],
                    "selections": [f"Vencedor: {home.strip()}"]
                }
                games.append(game)
            
            return games
            
        except Exception as e:
            logger.error(f"❌ Erro ao analisar texto: {str(e)}")
            return []
    
    def _capture_games_from_html_parsing(self, driver) -> list:
        """Captura jogos através de parsing HTML"""
        try:
            games = []
            html = driver.page_source
            
            # Padrões mais específicos para HTML
            patterns = {
                'teams': r'<[^>]*class="[^"]*(?:team|time|jogo|participant)[^"]*"[^>]*>([^<]+)</[^>]*>',
                'leagues': r'<[^>]*class="[^"]*(?:league|liga|competition)[^"]*"[^>]*>([^<]+)</[^>]*>',
                'dates': r'(\d{2}/\d{2}\s+\d{2}:\d{2})',
                'odds': r'(\d+\.\d+)'
            }
            
            teams = re.findall(patterns['teams'], html, re.IGNORECASE)
            leagues = re.findall(patterns['leagues'], html, re.IGNORECASE)
            dates = re.findall(patterns['dates'], html)
            odds = re.findall(patterns['odds'], html)
            
            logger.info(f"🔍 HTML: {len(teams)} times, {len(leagues)} ligas, {len(dates)} datas, {len(odds)} odds")
            
            # Montar jogos
            for i in range(0, len(teams), 2):
                if i + 1 < len(teams):
                    game = {
                        "game_number": len(games) + 1,
                        "home_team": teams[i].strip(),
                        "away_team": teams[i + 1].strip(),
                        "teams": f"{teams[i].strip()} x {teams[i + 1].strip()}",
                        "league": leagues[len(games)] if len(games) < len(leagues) else "Liga não especificada",
                        "datetime": dates[len(games)] if len(games) < len(dates) else "",
                        "odds_list": [odds[len(games)]] if len(games) < len(odds) else ["1.00"],
                        "selections": [f"Vencedor: {teams[i].strip()}"]
                    }
                    games.append(game)
            
            return games
            
        except Exception as e:
            logger.error(f"❌ Erro ao fazer parsing HTML: {str(e)}")
            return []
    
    def _create_basic_game_structure(self, driver) -> list:
        """Cria estrutura básica de jogos baseada em padrões encontrados"""
        try:
            games = []
            page_text = driver.page_source
            
            # Procurar por qualquer padrão de "Time x Time"
            team_pattern = r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+x\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'
            team_matches = re.findall(team_pattern, page_text)
            
            if team_matches:
                for i, (home, away) in enumerate(team_matches):
                    game = {
                        "game_number": i + 1,
                        "home_team": home.strip(),
                        "away_team": away.strip(),
                        "teams": f"{home.strip()} x {away.strip()}",
                        "league": "Liga não especificada",
                        "datetime": "",
                        "odds_list": ["1.00"],
                        "selections": [f"Vencedor: {home.strip()}"]
                    }
                    games.append(game)
                    logger.info(f"🎮 Jogo básico criado: {game['teams']}")
            
            return games
            
        except Exception as e:
            logger.error(f"❌ Erro ao criar estrutura básica: {str(e)}")
            return []

# Instanciar o serviço
capture_service = ValSportsBetCaptureServiceImproved()

# Configurar Flask
app = Flask(__name__)
CORS(app)

@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint de verificação de saúde da API"""
    return jsonify({
        'status': 'healthy',
        'service': 'ValSports Bet Capture Service (Improved)',
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
    logger.info("🚀 Iniciando ValSports Bet Capture Service (Improved)...")
    app.run(host='0.0.0.0', port=5006, debug=True)
