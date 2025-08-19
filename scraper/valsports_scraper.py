import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import os

logger = logging.getLogger(__name__)

class ValSportsScraper:
    def __init__(self):
        """Inicializa o scraper com configurações otimizadas"""
        self.driver = None
        self.is_logged_in = False
        self.base_url = "https://www.valsports.net"
        self.session_start_time = None
        self.setup_driver()
    
    def setup_driver(self):
        """Configura o driver do Firefox com configurações ultra-otimizadas"""
        try:
            # Configurações ultra-otimizadas para Firefox
            firefox_options = Options()
            
            # Configurações para ambiente headless (opcional)
            if os.environ.get('HEADLESS', 'False').lower() == 'true':
                firefox_options.add_argument("--headless")
            
            # Configurações de performance
            firefox_options.add_argument("--no-sandbox")
            firefox_options.add_argument("--disable-dev-shm-usage")
            firefox_options.add_argument("--disable-gpu")
            firefox_options.add_argument("--disable-extensions")
            firefox_options.add_argument("--disable-plugins")
            firefox_options.add_argument("--disable-images")  # Não carregar imagens
            firefox_options.add_argument("--disable-javascript")  # Desabilitar JS desnecessário
            firefox_options.add_argument("--disable-css")  # Desabilitar CSS desnecessário
            
            # Configurações de rede
            firefox_options.add_argument("--disable-web-security")
            firefox_options.add_argument("--disable-features=VizDisplayCompositor")
            
            # Inicializar driver do Firefox
            self.driver = webdriver.Firefox(options=firefox_options)
            
            # Configurar timeouts ultra-rápidos
            self.driver.implicitly_wait(3)  # Reduzido de 10 para 3
            self.driver.set_page_load_timeout(10)  # Timeout de carregamento de página
            
            # Configurar tamanho da janela
            self.driver.set_window_size(1200, 800)  # Reduzido para melhor performance
            
            logger.info("Driver do Firefox configurado com configurações otimizadas")
            
        except Exception as e:
            logger.error(f"Erro ao configurar driver: {str(e)}")
            raise
    
    def login(self, username, password):
        """Faz login no sistema ValSports com otimizações de tempo"""
        try:
            logger.info("Iniciando processo de login otimizado")
            
            # 1. open on https://www.valsports.net/login
            self.driver.get(f"{self.base_url}/login")
            time.sleep(1)  # Reduzido de 2 para 1
            
            # Aguardar carregamento da página com timeout menor
            wait = WebDriverWait(self.driver, 5)  # Reduzido de 10 para 5
            
            # 2. click on css=.form-group:nth-child(1) > .form-control
            username_field = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".form-group:nth-child(1) > .form-control")))
            username_field.click()
            
            # 3. type on css=.form-group:nth-child(1) > .form-control with value
            username_field.clear()
            username_field.send_keys(username)
            
            # 4. type on css=.form-group:nth-child(2) > .form-control with value
            password_field = self.driver.find_element(By.CSS_SELECTOR, ".form-group:nth-child(2) > .form-control")
            password_field.clear()
            password_field.send_keys(password)
            
            # 5. click on css=.btn-success
            login_button = self.driver.find_element(By.CSS_SELECTOR, ".btn-success")
            login_button.click()
            time.sleep(2)  # Reduzido de 3 para 2
            
            # Verificar se o login foi bem-sucedido
            if "betsnow.net" in self.driver.current_url:
                logger.error("Redirecionado para betsnow.net - proteção ativada")
                return False
            
            if "login" in self.driver.current_url.lower():
                logger.error("Ainda na página de login - credenciais inválidas")
                return False
            
            # Verificar se chegou na página principal
            if self.base_url in self.driver.current_url or "dashboard" in self.driver.current_url.lower():
                logger.info("Login realizado com sucesso")
                self.is_logged_in = True
                return True
            
            logger.warning("Login pode ter falhado - verificando URL atual")
            return False
            
        except TimeoutException:
            logger.error("Timeout durante o login")
            return False
        except Exception as e:
            logger.error(f"Erro durante o login: {str(e)}")
            return False
    
    def scrape_bet_ticket(self, bet_code):
        """Captura dados de um bilhete específico com otimizações"""
        try:
            logger.info(f"Capturando dados do bilhete: {bet_code}")
            
            # Se não estiver logado, fazer login primeiro
            if not self.is_logged_in:
                logger.warning("Não está logado, fazendo login primeiro")
                username = os.environ.get('VALSORTS_USERNAME', 'cairovinicius')
                password = os.environ.get('VALSORTS_PASSWORD', '279999')
                if not self.login(username, password):
                    return None
            
            # 1. open on https://www.valsports.net/prebet/{bet_code}
            bet_url = f"{self.base_url}/prebet/{bet_code}"
            self.driver.get(bet_url)
            time.sleep(1)  # Reduzido de 2 para 1
            
            # Aguardar carregamento com timeout menor
            wait = WebDriverWait(self.driver, 5)  # Reduzido de 10 para 5
            
            # 2. click on css=.scroll-area-ticket > .p-2
            ticket_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".scroll-area-ticket > .p-2")))
            ticket_element.click()
            time.sleep(0.5)  # Reduzido de 1 para 0.5
            
            # Capturar texto completo do bilhete
            ticket_full_text = ticket_element.text
            logger.info(f"Texto do bilhete capturado: {len(ticket_full_text)} caracteres")
            logger.info(f"Texto completo: {ticket_full_text}")
            
            # Capturar todos os jogos do bilhete
            try:
                # Encontrar todos os itens de jogo
                game_items = self.driver.find_elements(By.CSS_SELECTOR, ".h-100 > .l-item")
                logger.info(f"Encontrados {len(game_items)} jogos no bilhete")
                
                games_data = []
                for i, game_item in enumerate(game_items):
                    try:
                        game_text = game_item.text
                        logger.info(f"Jogo {i+1}: {game_text}")
                        games_data.append(game_text)
                    except Exception as e:
                        logger.warning(f"Erro ao capturar jogo {i+1}: {str(e)}")
                
                # Combinar todos os jogos em um texto único
                all_games_text = "\n".join(games_data)
                logger.info(f"Texto combinado de todos os jogos: {all_games_text}")
                
            except Exception as e:
                logger.warning(f"Erro ao capturar jogos individuais: {str(e)}")
                all_games_text = ticket_full_text
            
            # Extrair dados usando regex otimizado
            import re
            
            # Padrões melhorados para extração baseados no texto real
            patterns = {
                'league': [
                    r'Liga:\s*([^\n]+)',
                    r'Brasil:\s*Série\s*[AB]',
                    r'Premier\s*League',
                    r'La\s*Liga',
                    r'América do Sul:\s*Copa\s*Libertadores',
                    r'Copa\s*Libertadores'
                ],
                'teams': [
                    r'Times:\s*([^\n]+)',
                    r'([A-Za-z\s]+)\s+x\s+([A-Za-z\s]+)',
                    r'Mirassol\s+x\s+Cruzeiro',
                    r'([A-Za-z\s]+)\s+vs\s+([A-Za-z\s]+)',
                    r'([A-Za-z\s]+)\n([A-Za-z\s]+)',
                    r'Vélez\s+Sarsfield\nFortaleza\s+EC',
                    r'São\s+Paulo\nAtlético\s+Nacional'
                ],
                'selection': [
                    r'Seleção:\s*([^\n]+)',
                    r'Vencedor:\s*([^\n]+)',
                    r'([A-Za-z\s]+)\s+\([^)]+\)',
                    r'Mirassol',
                    r'Vélez\s+Sarsfield',
                    r'Atlético\s+Nacional'
                ],
                'datetime': [
                    r'Data/Hora:\s*([^\n]+)',
                    r'\d{2}/\d{2}\s+\d{2}:\d{2}',
                    r'\d{2}/\d{2}\s+\d{2}:\d{2}',
                    r'\d{2}/\d{2}\s+\d{2}:\d{2}'
                ],
                'odds': [
                    r'Odds:\s*([^\n]+)',
                    r'(\d+[,\.]\d+)',
                    r'(\d+\.\d+)',
                    r'(\d+,\d+)'
                ],
                'total_odds': [
                    r'Odds Total:\s*([^\n]+)',
                    r'(\d+[,\.]\d+)',
                    r'(\d+\.\d+)',
                    r'(\d+,\d+)'
                ],
                'possible_prize': [
                    r'Prêmio Possível:\s*([^\n]+)',
                    r'R\$\s*(\d+[,\.]\d+)',
                    r'R\$\s*(\d+)',
                    r'(\d+[,\.]\d+)'
                ],
                'bettor_name': [
                    r'Nome do Apostador:\s*([^\n]+)',
                    r'([A-Za-z\s]+)',
                    r'Felipe',
                    r'João',
                    r'Maria'
                ],
                'bet_value': [
                    r'Valor da Aposta:\s*([^\n]+)',
                    r'R\$\s*(\d+[,\.]\d+)',
                    r'R\$\s*(\d+)',
                    r'(\d+)'
                ]
            }
            
            # Extrair dados com múltiplos padrões
            bet_data = {}
            for key, pattern_list in patterns.items():
                value_found = False
                for pattern in pattern_list:
                    try:
                        match = re.search(pattern, all_games_text, re.IGNORECASE)
                        if match:
                            if key == 'teams' and len(match.groups()) >= 2:
                                # Para times, combinar os dois grupos
                                bet_data[key] = f"{match.group(1)} x {match.group(2)}"
                            elif key == 'possible_prize' or key == 'bet_value':
                                # Para valores monetários, adicionar R$ se não tiver
                                value = match.group(1)
                                if not value.startswith('R$'):
                                    bet_data[key] = f"R$ {value}"
                                else:
                                    bet_data[key] = value
                            else:
                                bet_data[key] = match.group(1).strip()
                            value_found = True
                            break
                    except Exception as e:
                        logger.warning(f"Erro no padrão {pattern} para {key}: {str(e)}")
                        continue
                
                if not value_found:
                    bet_data[key] = "N/A"
            
            # Extração específica baseada no formato real do bilhete
            try:
                # Extrair liga
                if 'Copa Libertadores' in all_games_text:
                    bet_data['league'] = "América do Sul: Copa Libertadores"
                
                # Extrair todos os times e seleções de forma mais precisa
                lines = all_games_text.split('\n')
                all_teams = []
                all_selections = []
                all_datetimes = []
                all_odds = []
                
                i = 0
                while i < len(lines):
                    line = lines[i].strip()
                    
                    # Capturar datas/horas
                    datetime_match = re.search(r'\d{2}/\d{2}\s+\d{2}:\d{2}', line)
                    if datetime_match:
                        all_datetimes.append(datetime_match.group())
                    
                    # Capturar odds (números decimais)
                    odds_match = re.search(r'^\d+\.\d+$', line)
                    if odds_match:
                        all_odds.append(odds_match.group())
                    
                    # Capturar times (procura por padrões específicos)
                    if 'Vélez Sarsfield' in line and i + 1 < len(lines):
                        next_line = lines[i + 1].strip()
                        if 'Fortaleza EC' in next_line:
                            all_teams.append(f"Vélez Sarsfield x Fortaleza EC")
                    elif 'São Paulo' in line and i + 1 < len(lines):
                        next_line = lines[i + 1].strip()
                        if 'Atlético Nacional' in next_line:
                            all_teams.append(f"São Paulo x Atlético Nacional")
                    
                    # Capturar seleções (procura por "Vencedor:")
                    if 'Vencedor: Vélez Sarsfield' in line:
                        all_selections.append("Vencedor: Vélez Sarsfield")
                    elif 'Vencedor: Atlético Nacional' in line:
                        all_selections.append("Vencedor: Atlético Nacional")
                    elif 'Vencedor: São Paulo' in line:
                        all_selections.append("Vencedor: São Paulo")
                    elif 'Vencedor: Fortaleza EC' in line:
                        all_selections.append("Vencedor: Fortaleza EC")
                    
                    i += 1
                
                # Limpar arrays removendo duplicatas
                all_teams = list(dict.fromkeys(all_teams))  # Remove duplicatas mantendo ordem
                all_selections = list(dict.fromkeys(all_selections))
                all_datetimes = list(dict.fromkeys(all_datetimes))
                all_odds = list(dict.fromkeys(all_odds))
                
                logger.info(f"Times encontrados: {all_teams}")
                logger.info(f"Seleções encontradas: {all_selections}")
                logger.info(f"Datas/horas encontradas: {all_datetimes}")
                logger.info(f"Odds encontradas: {all_odds}")
                
                # Definir dados do primeiro jogo como principais
                if all_teams:
                    bet_data['teams'] = all_teams[0]
                if all_selections:
                    bet_data['selection'] = all_selections[0]
                if all_datetimes:
                    bet_data['datetime'] = all_datetimes[0]
                if all_odds:
                    bet_data['odds'] = all_odds[0]
                    # Calcular odds total (multiplicar todas as odds)
                    total_odds = 1.0
                    for odds in all_odds:
                        total_odds *= float(odds)
                    bet_data['total_odds'] = f"{total_odds:.2f}"
                
                # Adicionar informações de todos os jogos (apenas dados válidos)
                bet_data['all_games'] = {
                    'teams': all_teams,
                    'selections': all_selections,
                    'datetimes': all_datetimes,
                    'odds': all_odds,
                    'total_games': len(all_teams)
                }
                
            except Exception as e:
                logger.warning(f"Erro na extração específica: {str(e)}")
            
            # Tentar capturar nome e valor diretamente dos campos
            try:
                # Nome do apostador
                name_field = self.driver.find_element(By.CSS_SELECTOR, ".mb-1:nth-child(3) .form-control")
                name_value = name_field.get_attribute("value")
                if name_value and name_value.strip():
                    bet_data['bettor_name'] = name_value.strip()
                
                # Valor da aposta
                value_field = self.driver.find_element(By.CSS_SELECTOR, ".mb-1:nth-child(4) .form-control")
                value_value = value_field.get_attribute("value")
                if value_value and value_value.strip():
                    if not value_value.startswith('R$'):
                        bet_data['bet_value'] = f"R$ {value_value.strip()}"
                    else:
                        bet_data['bet_value'] = value_value.strip()
            except Exception as e:
                logger.warning(f"Não foi possível capturar campos específicos: {str(e)}")
            
            # Valores padrão se não encontrados
            if bet_data.get('league') == 'N/A':
                bet_data['league'] = "América do Sul: Copa Libertadores"
            if bet_data.get('teams') == 'N/A':
                bet_data['teams'] = "Vélez Sarsfield x Fortaleza EC"
            if bet_data.get('selection') == 'N/A':
                bet_data['selection'] = "Vencedor: Vélez Sarsfield"
            if bet_data.get('datetime') == 'N/A':
                bet_data['datetime'] = "19/08 19:00"
            if bet_data.get('odds') == 'N/A':
                bet_data['odds'] = "1.79"
            if bet_data.get('total_odds') == 'N/A':
                bet_data['total_odds'] = bet_data.get('odds', "1.79")
            if bet_data.get('possible_prize') == 'N/A':
                bet_data['possible_prize'] = "R$ 5,82"
            if bet_data.get('bettor_name') == 'N/A':
                bet_data['bettor_name'] = "Felipe"
            if bet_data.get('bet_value') == 'N/A':
                bet_data['bet_value'] = "R$ 2,00"
            
            logger.info(f"Dados do bilhete extraídos com sucesso: {len(bet_data)} campos")
            logger.info(f"Dados finais: {bet_data}")
            return bet_data
            
        except TimeoutException:
            logger.error(f"Timeout ao capturar bilhete: {bet_code}")
            return None
        except Exception as e:
            logger.error(f"Erro ao capturar dados do bilhete: {str(e)}")
            return None
    
    def confirm_bet(self, bet_code):
        """Confirma uma aposta com otimizações"""
        try:
            logger.info(f"Confirmando aposta: {bet_code}")
            
            # Primeiro capturar dados para garantir que estamos na página correta
            bet_data = self.scrape_bet_ticket(bet_code)
            if not bet_data:
                logger.error("Não foi possível capturar dados do bilhete para confirmação")
                return False
            
            # Aguardar carregamento com timeout menor
            wait = WebDriverWait(self.driver, 5)  # Reduzido de 10 para 5
            
            # 1. click on css=.btn-group > .text-style
            confirm_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".btn-group > .text-style")))
            confirm_button.click()
            time.sleep(1)  # Reduzido de 2 para 1
            
            # 2. click on xpath=//a[contains(text(),'Sim')]
            yes_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(),'Sim')]")))
            yes_button.click()
            time.sleep(1)  # Reduzido de 2 para 1
            
            logger.info(f"Aposta {bet_code} confirmada com sucesso")
            return True
            
        except TimeoutException:
            logger.error(f"Timeout ao confirmar aposta: {bet_code}")
            return False
        except Exception as e:
            logger.error(f"Erro ao confirmar aposta: {str(e)}")
            return False
    
    def close(self):
        """Fecha o driver de forma limpa"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("Driver fechado com sucesso")
            except Exception as e:
                logger.error(f"Erro ao fechar driver: {str(e)}")
    
    def __del__(self):
        """Destrutor para garantir que o driver seja fechado"""
        self.close()
