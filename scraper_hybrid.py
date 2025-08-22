#!/usr/bin/env python3
"""
Scraper Híbrido para ValSports.net
Combina Selenium para login + ScrapingDog para captura de dados
"""

import os
import time
import json
import logging
import requests
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class HybridValSportsScraper:
    def __init__(self, scrapingdog_api_key=None):
        self.base_url = "https://www.valsports.net"
        self.scrapingdog_api_key = scrapingdog_api_key or os.getenv('SCRAPINGDOG_API_KEY')
        self.session_cookies = None
        self.is_logged_in = False
        
        # Configurar Firefox para login
        firefox_options = Options()
        firefox_options.add_argument("--headless")
        firefox_options.add_argument("--no-sandbox")
        firefox_options.add_argument("--disable-dev-shm-usage")
        firefox_options.add_argument("--disable-gpu")
        
        self.driver = webdriver.Firefox(options=firefox_options)
        self.driver.set_window_size(1200, 800)
        self.driver.implicitly_wait(3)
        
        logger.info("🚀 Scraper Híbrido inicializado")
    
    def login_with_selenium(self, username, password):
        """Faz login usando Selenium e captura cookies"""
        try:
            logger.info(f"🔐 Fazendo login com Selenium: {username}")
            
            self.driver.get(f"{self.base_url}/login")
            time.sleep(5)  # Aumentar tempo de espera
            
            # Aguardar carregamento da página
            wait = WebDriverWait(self.driver, 15)
            
            # Tentar diferentes seletores para os campos de login
            username_selectors = [
                ".form-group:nth-child(1) > .form-control",  # Seletor correto
                "input[type='text']",
                ".form-control[type='text']",
                "input[name='username']",
                "input[placeholder*='usuário']",
                "input[placeholder*='user']",
                "input[placeholder*='email']",
                "#username",
                "#email"
            ]
            
            password_selectors = [
                ".form-group:nth-child(2) > .form-control",  # Seletor correto
                "input[type='password']",
                ".form-control[type='password']",
                "input[name='password']",
                "input[placeholder*='senha']",
                "input[placeholder*='password']",
                "#password"
            ]
            
            # Encontrar campo de usuário
            username_field = None
            for selector in username_selectors:
                try:
                    username_field = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                    logger.info(f"✅ Campo usuário encontrado com selector: {selector}")
                    break
                except:
                    continue
            
            if not username_field:
                logger.error("❌ Campo de usuário não encontrado")
                # Salvar screenshot para debug
                self.driver.save_screenshot(f"login_error_{int(time.time())}.png")
                return False
            
            # Encontrar campo de senha
            password_field = None
            for selector in password_selectors:
                try:
                    password_field = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                    logger.info(f"✅ Campo senha encontrado com selector: {selector}")
                    break
                except:
                    continue
            
            if not password_field:
                logger.error("❌ Campo de senha não encontrado")
                return False
            
            # Preencher credenciais
            username_field.clear()
            username_field.send_keys(username)
            time.sleep(1)
            
            password_field.clear()
            password_field.send_keys(password)
            time.sleep(1)
            
            # Tentar diferentes seletores para o botão de login
            login_button_selectors = [
                "button[type='submit']",
                ".btn-success",
                ".btn-primary",
                "button:contains('Fazer login')",
                "button:contains('Entrar')",
                "button:contains('Login')",
                "button:contains('Sign in')",
                ".btn-login",
                "input[type='submit']",
                "[class*='btn'][class*='login']",
                "[class*='btn'][class*='submit']"
            ]
            
            # Encontrar botão de login
            login_button = None
            for selector in login_button_selectors:
                try:
                    login_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                    logger.info(f"✅ Botão login encontrado com selector: {selector}")
                    break
                except:
                    continue
            
            if not login_button:
                # Tentar encontrar por texto
                try:
                    login_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Fazer login')]")
                    logger.info("✅ Botão login encontrado por texto 'Fazer login'")
                except:
                    try:
                        login_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Entrar')]")
                        logger.info("✅ Botão login encontrado por texto 'Entrar'")
                    except:
                        logger.error("❌ Botão de login não encontrado")
                        return False
            
            # Clicar no botão de login
            login_button.click()
            logger.info("🔄 Botão de login clicado")
            
            time.sleep(8)  # Aguardar redirecionamento
            
            # Verificar se o login foi bem-sucedido
            current_url = self.driver.current_url
            page_source = self.driver.page_source.lower()
            
            logger.info(f"📍 URL atual: {current_url}")
            
            # Verificar se saiu da página de login (redirecionamento indica sucesso)
            if ("login" not in current_url and 
                (current_url.endswith("/") or 
                 "dashboard" in current_url or 
                 "logout" in page_source or 
                 "perfil" in page_source or
                 "conta" in page_source or
                 "welcome" in page_source)):
                
                # Aguardar um pouco para cookies serem definidos
                time.sleep(2)
                
                # Capturar cookies da sessão
                self.session_cookies = self.driver.get_cookies()
                self.is_logged_in = True
                logger.info("✅ Login realizado com sucesso via Selenium")
                logger.info(f"🍪 {len(self.session_cookies)} cookies capturados")
                
                # Log dos cookies principais
                for cookie in self.session_cookies:
                    if 'session' in cookie['name'].lower() or 'auth' in cookie['name'].lower():
                        logger.info(f"🔑 Cookie importante: {cookie['name']}")
                
                return True
            else:
                logger.error("❌ Login falhou - não redirecionou para área logada")
                # Salvar screenshot para debug
                self.driver.save_screenshot(f"login_failed_{int(time.time())}.png")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro no login: {str(e)}")
            # Salvar screenshot para debug
            try:
                self.driver.save_screenshot(f"login_exception_{int(time.time())}.png")
            except:
                pass
            return False
    
    def get_cookies_dict(self):
        """Converte cookies do Selenium para formato de requests"""
        if not self.session_cookies:
            return {}
        
        cookies_dict = {}
        for cookie in self.session_cookies:
            cookies_dict[cookie['name']] = cookie['value']
        
        return cookies_dict
    
    def scrape_with_scrapingdog(self, bet_code):
        """Captura dados usando ScrapingDog com cookies de sessão"""
        try:
            if not self.is_logged_in:
                logger.error("❌ Usuário não está logado")
                return None
            
            logger.info(f"🎯 Capturando bilhete {bet_code} com ScrapingDog")
            
            bet_url = f"{self.base_url}/prebet/{bet_code}"
            
            # Preparar headers e cookies
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            
            cookies = self.get_cookies_dict()
            
            # URL do ScrapingDog
            scrapingdog_url = "https://api.scrapingdog.com/scrape"
            
            params = {
                'api_key': self.scrapingdog_api_key,
                'url': bet_url,
                'render': 'true',  # Renderização JavaScript
                'wait': '5000',    # Aguardar 5 segundos para carregamento
                'country': 'br',   # Proxy do Brasil
                'premium': 'true'  # Usar proxy premium
            }
            
            logger.info(f"🌐 Fazendo requisição para ScrapingDog: {bet_url}")
            
            response = requests.get(scrapingdog_url, params=params, headers=headers, cookies=cookies, timeout=60)
            
            if response.status_code == 200:
                logger.info("✅ Resposta recebida do ScrapingDog")
                
                # Salvar HTML para debug
                html_filename = f"scrapingdog_response_{bet_code}_{int(time.time())}.html"
                with open(html_filename, 'w', encoding='utf-8') as f:
                    f.write(response.text)
                
                # Parsear HTML
                return self._parse_html_response(response.text, bet_code)
            else:
                logger.error(f"❌ Erro na requisição ScrapingDog: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Erro ao usar ScrapingDog: {str(e)}")
            return None
    
    def _parse_html_response(self, html_content, bet_code):
        """Parse do HTML retornado pelo ScrapingDog"""
        try:
            logger.info("🔍 Parseando HTML do ScrapingDog")
            
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Método 1: Procurar por containers de jogos
            games = self._extract_games_from_soup(soup)
            
            if games:
                logger.info(f"✅ {len(games)} jogos encontrados via BeautifulSoup")
                return self._extract_bet_data(soup, games, bet_code)
            
            # Método 2: Análise de texto completo
            games = self._extract_games_from_text(html_content)
            
            if games:
                logger.info(f"✅ {len(games)} jogos encontrados via análise de texto")
                return self._extract_bet_data(soup, games, bet_code)
            
            logger.error("❌ Nenhum jogo encontrado")
            return None
            
        except Exception as e:
            logger.error(f"❌ Erro ao parsear HTML: {str(e)}")
            return None
    
    def _extract_games_from_soup(self, soup):
        """Extrai jogos usando BeautifulSoup"""
        games = []
        
        # Procurar por diferentes tipos de containers
        selectors = [
            ".l-item",
            ".game-item", 
            ".bet-item",
            "[class*='game']",
            "[class*='bet']",
            "[class*='item']",
            "div[class*='row'] div[class*='col']"
        ]
        
        for selector in selectors:
            try:
                elements = soup.select(selector)
                if elements and len(elements) > 0:
                    logger.info(f"🎯 Encontrados {len(elements)} elementos com selector: {selector}")
                    
                    for element in elements:
                        game_data = self._parse_game_element(element)
                        if game_data:
                            games.append(game_data)
                    
                    if games:
                        break
            except Exception as e:
                logger.warning(f"⚠️ Erro com selector {selector}: {str(e)}")
                continue
        
        return games
    
    def _extract_games_from_text(self, html_content):
        """Extrai jogos usando regex no texto"""
        games = []
        
        # Padrões para encontrar jogos no texto
        game_patterns = [
            r'([A-Za-zÀ-ÿ\s]+):\s*([A-Za-zÀ-ÿ\s]+)\s+(\d{2}/\d{2}\s+\d{2}:\d{2})\s+([A-Za-zÀ-ÿ\s]+)\s+x\s+([A-Za-zÀ-ÿ\s]+)\s+Vencedor:\s+([A-Za-zÀ-ÿ\s]+)\s+(\d+\.\d+)',
            r'([A-Za-zÀ-ÿ\s]+)\s+(\d{2}/\d{2}\s+\d{2}:\d{2})\s+([A-Za-zÀ-ÿ\s]+)\s+x\s+([A-Za-zÀ-ÿ\s]+)\s+Vencedor:\s+([A-Za-zÀ-ÿ\s]+)\s+(\d+\.\d+)',
            r'([A-Za-zÀ-ÿ\s]+)\s+x\s+([A-Za-zÀ-ÿ\s]+)\s+Vencedor:\s+([A-Za-zÀ-ÿ\s]+)\s+(\d+\.\d+)'
        ]
        
        for pattern in game_patterns:
            matches = re.findall(pattern, html_content, re.MULTILINE)
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
    
    def _parse_game_element(self, element):
        """Parse de um elemento de jogo"""
        try:
            text = element.get_text(strip=True)
            if not text or len(text) < 10:
                return None
            
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
            logger.warning(f"⚠️ Erro ao parsear elemento: {str(e)}")
            return None
    
    def _extract_bet_data(self, soup, games, bet_code):
        """Extrai dados gerais do bilhete"""
        try:
            # Extrair total das odds
            total_odds = "0,00"
            total_odds_elements = soup.find_all(text=re.compile(r'Total odds', re.IGNORECASE))
            if total_odds_elements:
                for element in total_odds_elements:
                    parent = element.parent
                    if parent:
                        text = parent.get_text()
                        odds_match = re.search(r'Total odds\s*(\d+[,\d]*)', text, re.IGNORECASE)
                        if odds_match:
                            total_odds = odds_match.group(1)
                            break
            
            # Extrair possível prêmio
            possible_prize = "R$ 0,00"
            prize_elements = soup.find_all(text=re.compile(r'Possível prêmio', re.IGNORECASE))
            if prize_elements:
                for element in prize_elements:
                    parent = element.parent
                    if parent:
                        text = parent.get_text()
                        prize_match = re.search(r'Possível prêmio\s*(R\$\s*\d+[,\d]*)', text, re.IGNORECASE)
                        if prize_match:
                            possible_prize = prize_match.group(1)
                            break
            
            # Extrair nome do apostador
            bettor_name = ""
            name_inputs = soup.find_all('input', {'placeholder': 'Apostador'})
            if name_inputs:
                bettor_name = name_inputs[0].get('value', '')
            
            # Extrair valor da aposta
            bet_value = ""
            value_inputs = soup.find_all('input', {'placeholder': 'Valor'})
            if value_inputs:
                bet_value = value_inputs[0].get('value', '')
            
            return {
                'bet_code': bet_code,
                'games': games,
                'total_odds': total_odds,
                'possible_prize': possible_prize,
                'bettor_name': bettor_name,
                'bet_value': bet_value,
                'total_games': len(games)
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao extrair dados do bilhete: {str(e)}")
            return None
    
    def close(self):
        """Fecha o driver"""
        try:
            self.driver.quit()
            logger.info("🔒 Driver fechado")
        except:
            pass

def test_hybrid_scraper():
    """Teste do scraper híbrido"""
    print("🧪 TESTE DO SCRAPER HÍBRIDO")
    print("=" * 50)
    
    # Verificar se tem API key do ScrapingDog
    api_key = os.getenv('SCRAPINGDOG_API_KEY')
    if not api_key:
        print("⚠️  SCRAPINGDOG_API_KEY não encontrada no ambiente")
        print("   Configure: export SCRAPINGDOG_API_KEY='sua_chave_aqui'")
        return
    
    scraper = HybridValSportsScraper(api_key)
    
    try:
        # Credenciais de teste (substitua pelas reais)
        username = os.getenv('VALSPORTS_USERNAME', 'teste')
        password = os.getenv('VALSPORTS_PASSWORD', 'teste')
        
        print(f"🔐 Fazendo login com: {username}")
        
        # Fazer login
        if scraper.login_with_selenium(username, password):
            print("✅ Login realizado com sucesso")
            
            # Testar com diferentes bilhetes
            test_codes = ["ELM5IM", "TQE4X1", "5pfin1"]
            
            for bet_code in test_codes:
                print(f"\n🎯 Testando bilhete: {bet_code}")
                
                result = scraper.scrape_with_scrapingdog(bet_code)
                
                if result:
                    print(f"📊 Resultado: {result['total_games']} jogos encontrados")
                    print(f"💰 Total odds: {result['total_odds']}")
                    print(f"🏆 Possível prêmio: {result['possible_prize']}")
                    print(f"👤 Apostador: {result['bettor_name']}")
                    print(f"💵 Valor: {result['bet_value']}")
                    
                    for i, game in enumerate(result['games'], 1):
                        print(f"   🎮 Jogo {i}:")
                        print(f"      🏆 Liga: {game.get('league')}")
                        print(f"      ⚽ Times: {game.get('teams')}")
                        print(f"      🎯 Seleção: {game.get('selection')}")
                        print(f"      📅 Data/Hora: {game.get('datetime')}")
                        print(f"      📈 Odds: {game.get('odds')}")
                        print()
                else:
                    print("❌ Falha ao capturar dados")
                
                time.sleep(2)
        else:
            print("❌ Falha no login")
    
    finally:
        scraper.close()

if __name__ == "__main__":
    test_hybrid_scraper()
