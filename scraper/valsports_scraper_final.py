import time
import logging
import re
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
        """Configura o driver do Firefox com configurações otimizadas"""
        try:
            # Configurações otimizadas para Firefox
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
            
            # Permitir JavaScript (necessário para o site)
            firefox_options.set_preference("javascript.enabled", True)
            
            # Inicializar driver do Firefox
            self.driver = webdriver.Firefox(options=firefox_options)
            
            # Configurar timeouts otimizados
            self.driver.implicitly_wait(2)  # Reduzido para 2 segundos
            self.driver.set_page_load_timeout(15)  # Reduzido para 15 segundos
            
            # Configurar tamanho da janela
            self.driver.set_window_size(1200, 800)
            
            logger.info("Driver do Firefox configurado com configurações otimizadas")
            
        except Exception as e:
            logger.error(f"Erro ao configurar driver: {str(e)}")
            raise
    
    def login(self, username, password):
        """Faz login no sistema ValSports"""
        try:
            logger.info("Iniciando processo de login")
            
            # 1. open on https://www.valsports.net/login
            self.driver.get(f"{self.base_url}/login")
            time.sleep(2)  # Reduzido para melhorar performance
            
            # Aguardar carregamento da página
            wait = WebDriverWait(self.driver, 15)
            
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
            time.sleep(3)  # Reduzido para melhorar performance
            
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
        """Captura dados de um bilhete específico usando XPaths e CSS selectors específicos"""
        try:
            logger.info(f"🚀 INICIANDO EXTRAÇÃO DO BILHETE: {bet_code}")
            logger.info(f"⏰ Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info(f"🌐 URL Base: {self.base_url}")

            import os
            if not os.path.exists('logs'):
                os.makedirs('logs')
            if not os.path.exists('downloads'):
                os.makedirs('downloads')

            if not self.is_logged_in:
                logger.warning("Não está logado, fazendo login primeiro")
                username = os.environ.get('VALSORTS_USERNAME', 'cairovinicius')
                password = os.environ.get('VALSORTS_PASSWORD', '279999')
                if not self.login(username, password):
                    return None

            bet_url = f"{self.base_url}/prebet/{bet_code}"
            logger.info(f"🌐 Navegando para: {bet_url}")
            self.driver.get(bet_url)
            
            # Aguardar página carregar (reduzido)
            time.sleep(5)
            
            # Aguardar JavaScript carregar
            wait = WebDriverWait(self.driver, 30)
            
            try:
                # Aguardar container principal do bilhete
                wait.until(EC.presence_of_element_located((By.XPATH, "//main/div[3]/div/div/div")))
                logger.info("✅ Container do bilhete carregado")
            except TimeoutException:
                logger.warning("⚠️ Timeout aguardando container - continuando...")
            
            # Aguardar mais um pouco para garantir (reduzido)
            time.sleep(2)
            
            # Salvar debug
            current_url = self.driver.current_url
            logger.info(f"📍 URL atual: {current_url}")
            
            # Salvar screenshot e HTML para debug
            self.driver.save_screenshot(f"scraper_{bet_code}.png")
            
            with open(f"scraper_{bet_code}.html", "w", encoding="utf-8") as f:
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
            
            # 1. Extrair quantidade de jogos do título "Bilhete15"
            try:
                # Procurar por span com classe "text-theme ml-2" que contém o número
                games_count_element = self.driver.find_element(By.CSS_SELECTOR, "span.text-theme.ml-2")
                games_text = games_count_element.text.strip()
                logger.info(f"📊 Texto do contador: {games_text}")
                
                # Extrair número do texto
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
            
            # 3. Extrair possível prêmio "R$ 1.000.000,00"
            try:
                # Procurar por div que contém "R$" e o valor do prêmio
                possible_prize_element = self.driver.find_element(By.XPATH, "//div[contains(text(), 'R$')]")
                bet_data['possible_prize'] = possible_prize_element.text.strip()
                logger.info(f"🏆 Possível prêmio: {bet_data['possible_prize']}")
            except Exception as e:
                logger.warning(f"⚠️ Erro ao extrair possível prêmio: {str(e)}")
            
            # 4. Extrair nome do apostador e valor - usar placeholders específicos
            try:
                # Procurar por placeholder "Apostador"
                apostador_inputs = self.driver.find_elements(By.XPATH, "//input[contains(@placeholder, 'Apostador')]")
                if apostador_inputs:
                    bet_data['bettor_name'] = apostador_inputs[0].get_attribute("value")
                    logger.info(f"👤 Apostador: {bet_data['bettor_name']}")
                
                # Procurar por placeholder "Valor"
                valor_inputs = self.driver.find_elements(By.XPATH, "//input[contains(@placeholder, 'Valor')]")
                if valor_inputs:
                    bet_data['bet_value'] = valor_inputs[0].get_attribute("value")
                    logger.info(f"💵 Valor: {bet_data['bet_value']}")
            except Exception as e:
                logger.warning(f"⚠️ Erro ao extrair campos do apostador: {str(e)}")
            
            # 6. Extrair jogos usando seletores corretos baseados no HTML real
            games = self._extract_games_with_real_selectors()
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
        """Extrai jogos usando iteração dinâmica com .find_elements - versão otimizada"""
        games = []
        
        try:
            logger.info("🎯 Extraindo jogos dinamicamente...")
            
            # Aguardar um pouco para garantir que a página está carregada
            time.sleep(2)
            
            # Encontrar todos os elementos .l-item (jogos)
            game_elements = self.driver.find_elements(By.CSS_SELECTOR, ".l-item")
            
            logger.info(f"🔍 Encontrados {len(game_elements)} elementos .l-item")
            
            # Processar apenas os primeiros 15 elementos (ou o número especificado)
            max_games = min(15, len(game_elements))
            
            for i in range(max_games):
                try:
                    logger.info(f"🎮 Processando jogo {i+1}...")
                    
                    # Recarregar o elemento para evitar stale reference
                    game_elements = self.driver.find_elements(By.CSS_SELECTOR, ".l-item")
                    if i >= len(game_elements):
                        break
                    
                    game_element = game_elements[i]
                    
                    # Capturar texto completo primeiro
                    full_text = game_element.text
                    logger.info(f"   📝 Texto completo do jogo {i+1}: {full_text[:100]}...")
                    
                    game_data = {
                        'game_number': i+1,
                        'league': '',
                        'home_team': '',
                        'away_team': '',
                        'selection': '',
                        'odds': '',
                        'datetime': ''
                    }
                    
                    # Extrair dados usando regex do texto completo
                    try:
                        # Extrair liga (primeira linha geralmente)
                        lines = full_text.split('\n')
                        if lines:
                            game_data['league'] = lines[0].strip()
                            logger.info(f"   Liga: {game_data['league']}")
                    except Exception as e:
                        logger.warning(f"   ⚠️ Erro ao extrair liga: {str(e)}")
                    
                    try:
                        # Extrair data/hora
                        datetime_match = re.search(r'(\d{2}/\d{2}\s+\d{2}:\d{2})', full_text)
                        if datetime_match:
                            game_data['datetime'] = datetime_match.group(1)
                            logger.info(f"   Data/Hora: {game_data['datetime']}")
                    except Exception as e:
                        logger.warning(f"   ⚠️ Erro ao extrair data/hora: {str(e)}")
                    
                    try:
                        # Extrair times - procurar por padrões mais específicos
                        # Primeiro, tentar encontrar times após a data/hora
                        lines = full_text.split('\n')
                        for j, line in enumerate(lines):
                            # Procurar linha que contém " x " (separador de times)
                            if ' x ' in line and not any(keyword in line.lower() for keyword in ['vencedor:', 'empate', 'odds']):
                                # Limpar a linha de possíveis sufixos
                                clean_line = line.strip()
                                if clean_line.endswith('...'):
                                    clean_line = clean_line[:-3]
                                
                                # Dividir por " x "
                                if ' x ' in clean_line:
                                    parts = clean_line.split(' x ')
                                    if len(parts) == 2:
                                        game_data['home_team'] = parts[0].strip()
                                        game_data['away_team'] = parts[1].strip()
                                        logger.info(f"   Times: {game_data['home_team']} x {game_data['away_team']}")
                                        break
                        
                        # Se não encontrou, tentar regex mais flexível
                        if not game_data['home_team']:
                            teams_match = re.search(r'([A-Za-zÀ-ÿ\s]+(?:\s+[A-Za-zÀ-ÿ]+)*)\s+x\s+([A-Za-zÀ-ÿ\s]+(?:\s+[A-Za-zÀ-ÿ]+)*)', full_text)
                            if teams_match:
                                game_data['home_team'] = teams_match.group(1).strip()
                                game_data['away_team'] = teams_match.group(2).strip()
                                logger.info(f"   Times (regex): {game_data['home_team']} x {game_data['away_team']}")
                    except Exception as e:
                        logger.warning(f"   ⚠️ Erro ao extrair times: {str(e)}")
                    
                    try:
                        # Extrair seleção (padrão: "Vencedor: Time" ou "Empate")
                        if 'Vencedor:' in full_text:
                            selection_match = re.search(r'Vencedor:\s*([A-Za-zÀ-ÿ\s]+)', full_text)
                            if selection_match:
                                game_data['selection'] = f"Vencedor: {selection_match.group(1).strip()}"
                        elif 'Empate' in full_text:
                            game_data['selection'] = "Empate"
                        logger.info(f"   Seleção: {game_data['selection']}")
                    except Exception as e:
                        logger.warning(f"   ⚠️ Erro ao extrair seleção: {str(e)}")
                    
                    try:
                        # Extrair odds (padrão: número decimal)
                        odds_match = re.search(r'\b(\d+\.\d+)\b', full_text)
                        if odds_match:
                            game_data['odds'] = odds_match.group(1)
                            logger.info(f"   Odds: {game_data['odds']}")
                    except Exception as e:
                        logger.warning(f"   ⚠️ Erro ao extrair odds: {str(e)}")
                    
                    # Validar se tem dados mínimos (odds e seleção são obrigatórios)
                    if game_data['odds'] and game_data['selection']:
                        # Formatar dados
                        if game_data['home_team'] and game_data['away_team']:
                            game_data['teams'] = f"{game_data['home_team']} x {game_data['away_team']}"
                        else:
                            game_data['teams'] = "Times não identificados"
                        
                        games.append(game_data)
                        logger.info(f"   ✅ Jogo {i+1} adicionado")
                    else:
                        logger.warning(f"   ⚠️ Jogo {i+1} sem dados suficientes - ignorando")
                
                except Exception as e:
                    logger.error(f"   ❌ Erro ao processar jogo {i+1}: {str(e)}")
                    continue
            
            logger.info(f"🎮 Total de jogos válidos extraídos: {len(games)}")
            
        except Exception as e:
            logger.error(f"❌ Erro na extração dinâmica: {str(e)}")
        
        return games
    
    def _extract_games_with_real_selectors(self):
        """Extrai jogos usando seletores baseados no HTML real fornecido pelo usuário - VERSÃO OTIMIZADA PARA MÚLTIPLAS APOSTAS"""
        games = []
        
        try:
            logger.info("🎯 Extraindo jogos com seletores reais (MÚLTIPLAS APOSTAS)...")
            
            # Aguardar menos tempo para carregamento
            time.sleep(1)
            
            # Encontrar todos os elementos .l-item (jogos) que têm a classe d-block
            game_elements = self.driver.find_elements(By.CSS_SELECTOR, ".l-item.d-block")
            
            logger.info(f"🔍 Encontrados {len(game_elements)} elementos .l-item.d-block")
            
            # Pular os primeiros 10 elementos (são elementos de navegação)
            start_index = 10
            valid_games = game_elements[start_index:]
            
            logger.info(f"🎮 Processando {len(valid_games)} jogos válidos (pulando primeiros {start_index})")
            
            current_game = None
            game_counter = 0
            
            for i, game_element in enumerate(valid_games, 1):
                try:
                    # Capturar texto completo primeiro para validação rápida
                    full_text = game_element.text
                    
                    # Verificar se tem dados essenciais antes de processar
                    # Procurar por qualquer tipo de seleção (Vencedor, Empate, Ambas equipes marcam, etc.)
                    has_selection = any(keyword in full_text for keyword in ['Vencedor:', 'Empate', 'Ambas equipes marcam', 'Mais de', 'Menos de', 'Gols', 'Corner', 'Cartão', 'Jogador'])
                    has_odds = bool(re.search(r'\b\d+\.\d+\b', full_text))
                    
                    if not has_selection or not has_odds:
                        continue
                    
                    # Verificar se é um novo jogo (tem liga e times) ou uma aposta adicional do mesmo jogo
                    # Verificar se tem liga
                    league_keywords = ['América do Sul:', 'CONCACAF:', 'Costa Rica:', 'Venezuela:', 'Inglaterra:', 'Brasil:', 'Espanha:', 'Itália:', 'Alemanha:', 'Argentina:', 'Uruguai:', 'Colômbia:', 'Chile:', 'Peru:', 'Equador:', 'Bolívia:', 'Paraguai:', 'UEFA:', 'Copa Libertadores', 'Copa Sul Americana', 'Champions League', 'Europa League', 'Premier League', 'La Liga', 'Serie A', 'Bundesliga', 'Brasileirão', 'Copa do Brasil', 'Copa do Nordeste', 'Primeira Liga', 'Série A', 'Série B', 'Série C', 'Série D', 'França:', 'Internacional:', 'EUA:', 'FIBA', 'WNBA']
                    has_league = any(keyword in full_text for keyword in league_keywords)
                    
                    # Verificar se tem times
                    exclude_keywords = ['Vencedor:', 'Empate', 'Ambas equipes marcam', 'Mais de', 'Menos de', 'Gols', 'Corner', 'Cartão', 'Jogador', 'Odds', 'Data', 'Hora', 'Live']
                    # Verificar se tem times (linha que contém " x " ou linhas 3-4 que não são keywords)
                    lines = full_text.split('\n')
                    has_teams = ' x ' in full_text
                    if not has_teams and len(lines) > 3:
                        for line in lines[2:4]:
                            if line.strip() and not any(keyword in line for keyword in exclude_keywords):
                                has_teams = True
                                break
                    
                    # Verificar se é um jogo único (não duplicado)
                    is_unique_game = True
                    if current_game:
                        # Comparar com o jogo atual para ver se é o mesmo
                        current_teams = current_game.get('teams', '')
                        current_league = current_game.get('league', '')
                        
                        # Extrair times do texto atual
                        current_text_teams = ''
                        current_text_league = ''
                        
                        try:
                            lines = full_text.split('\n')
                            if lines:
                                current_text_league = lines[0].strip()
                            
                            # Extrair times do texto atual
                            for j, line in enumerate(lines):
                                line = line.strip()
                                if (' x ' in line and 
                                    not any(keyword in line.lower() for keyword in ['vencedor:', 'empate', 'odds', 'data', 'hora', 'live']) and
                                    not re.search(r'^\d+\.\d+$', line) and
                                    not re.search(r'^\d{2}/\d{2}', line) and
                                    len(line) > 3):
                                    current_text_teams = line
                                    break
                                elif (j < len(lines) - 1 and 
                                      line and 
                                      not any(keyword in line.lower() for keyword in ['vencedor:', 'empate', 'odds', 'data', 'hora', 'live', 'bundesliga', 'série', 'ligue', 'fiba', 'wnba', 'premier']) and
                                      not re.search(r'^\d+\.\d+$', line) and
                                      not re.search(r'^\d{2}/\d{2}', line) and
                                      len(line) > 2):
                                    next_line = lines[j + 1].strip()
                                    if (next_line and 
                                        not any(keyword in next_line.lower() for keyword in ['vencedor:', 'empate', 'odds', 'data', 'hora', 'live']) and
                                        not re.search(r'^\d+\.\d+$', next_line) and
                                        not re.search(r'^\d{2}/\d{2}', next_line) and
                                        len(next_line) > 2):
                                        current_text_teams = f"{line} x {next_line}"
                                        break
                            
                            # Se tem os mesmos times e liga, é o mesmo jogo
                            if (current_text_teams and current_text_league and 
                                current_text_teams == current_teams and 
                                current_text_league == current_league):
                                is_unique_game = False
                                
                        except Exception as e:
                            pass
                    
                    if has_league and has_teams and is_unique_game:
                        # É um novo jogo
                        game_counter += 1
                        logger.info(f"🎮 Processando NOVO JOGO {game_counter}...")
                        
                        # Extrair dados básicos do jogo
                        current_game = {
                            'game_number': game_counter, 'league': '', 'home_team': '', 'away_team': '',
                            'datetime': '', 'teams': ''
                        }
                        
                        try:
                            # Extrair liga
                            lines = full_text.split('\n')
                            if lines:
                                current_game['league'] = lines[0].strip()
                                logger.info(f"   Liga: {current_game['league']}")
                        except Exception as e: pass
                        
                        try:
                            # Extrair data/hora
                            datetime_match = re.search(r'(\d{2}/\d{2}\s+\d{2}:\d{2})', full_text)
                            if datetime_match:
                                current_game['datetime'] = datetime_match.group(1)
                                logger.info(f"   Data/Hora: {current_game['datetime']}")
                        except Exception as e: pass
                        
                        try:
                            # Extrair times - os times estão em linhas consecutivas
                            lines = full_text.split('\n')
                            for j, line in enumerate(lines):
                                line = line.strip()
                                
                                # Procurar por linha que contém " x " (formato antigo)
                                if (' x ' in line and 
                                    not any(keyword in line.lower() for keyword in ['vencedor:', 'empate', 'odds', 'data', 'hora', 'live']) and
                                    not re.search(r'^\d+\.\d+$', line) and
                                    not re.search(r'^\d{2}/\d{2}', line) and
                                    len(line) > 3):
                                    
                                    teams = line.split(' x ')
                                    if len(teams) == 2:
                                        home_team = teams[0].strip()
                                        away_team = teams[1].strip()
                                        
                                        if home_team and away_team and len(home_team) > 1 and len(away_team) > 1:
                                            current_game['home_team'] = home_team
                                            current_game['away_team'] = away_team
                                            current_game['teams'] = f"{home_team} x {away_team}"
                                            logger.info(f"   Times: {current_game['teams']}")
                                            break
                                
                                # Procurar por times em linhas consecutivas (formato novo)
                                elif (j < len(lines) - 1 and 
                                      line and 
                                      not any(keyword in line.lower() for keyword in ['vencedor:', 'empate', 'odds', 'data', 'hora', 'live', 'bundesliga', 'série', 'ligue', 'fiba', 'wnba', 'premier']) and
                                      not re.search(r'^\d+\.\d+$', line) and
                                      not re.search(r'^\d{2}/\d{2}', line) and
                                      len(line) > 2):
                                    
                                    next_line = lines[j + 1].strip()
                                    if (next_line and 
                                        not any(keyword in next_line.lower() for keyword in ['vencedor:', 'empate', 'odds', 'data', 'hora', 'live']) and
                                        not re.search(r'^\d+\.\d+$', next_line) and
                                        not re.search(r'^\d{2}/\d{2}', next_line) and
                                        len(next_line) > 2):
                                        
                                        home_team = line
                                        away_team = next_line
                                        
                                        if home_team and away_team and len(home_team) > 1 and len(away_team) > 1:
                                            current_game['home_team'] = home_team
                                            current_game['away_team'] = away_team
                                            current_game['teams'] = f"{home_team} x {away_team}"
                                            logger.info(f"   Times: {current_game['teams']}")
                                            break
                        except Exception as e: 
                            logger.warning(f"   ⚠️ Erro ao extrair times: {str(e)}")
                    
                    # Extrair TODAS as apostas do elemento
                    if current_game:
                        try:
                            # Procurar por TODAS as seleções e odds no texto
                            lines = full_text.split('\n')
                            selections = []
                            odds_list = []
                            
                            # Primeiro, coletar todas as seleções e odds
                            for line in lines:
                                line = line.strip()
                                if any(keyword in line for keyword in ['Vencedor:', 'Empate', 'Ambas equipes marcam', 'Mais de', 'Menos de', 'Gols', 'Corner', 'Cartão', 'Jogador']):
                                    selections.append(line)
                                elif re.search(r'^\d+\.\d+$', line):
                                    odds_list.append(line)
                            
                            # Criar uma entrada única para o jogo com todas as apostas
                            if selections and odds_list:
                                # Adicionar o jogo base
                                game_entry = current_game.copy()
                                game_entry['selections'] = []
                                game_entry['odds_list'] = []
                                
                                # Adicionar todas as seleções e odds
                                for selection, odds in zip(selections, odds_list):
                                    if selection and odds:
                                        game_entry['selections'].append(selection)
                                        game_entry['odds_list'].append(odds)
                                        logger.info(f"   ✅ Aposta {len(game_entry['selections'])} do Jogo {game_counter}: {selection} - {odds}")
                                
                                games.append(game_entry)
                            else:
                                logger.warning(f"   ⚠️ Não conseguiu extrair seleções/odds do texto")
                                
                        except Exception as e:
                            logger.warning(f"   ⚠️ Erro ao extrair apostas: {str(e)}")
                
                except Exception as e:
                    logger.error(f"   ❌ Erro ao processar jogo {i}: {str(e)}")
                    continue
            
            logger.info(f"🎮 Total de apostas extraídas: {len(games)}")
            
        except Exception as e:
            logger.error(f"❌ Erro na extração com seletores reais: {str(e)}")
        
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
            logger.info(f"🌐 Navegando para: {bet_url}")
            self.driver.get(bet_url)
            time.sleep(5)
            
            # Aguardar carregamento
            wait = WebDriverWait(self.driver, 20)
            
            # Verificar se a página carregou corretamente
            try:
                # Procurar por vários seletores possíveis do botão de confirmação
                confirm_button = None
                possible_selectors = [
                    ".btn-group > .text-style",
                    ".btn.text-style",
                    "button[type='button'].btn.text-style",
                    ".btn-group button",
                    "//button[contains(text(), 'Apostar')]",
                    "//a[contains(text(), 'Apostar')]"
                ]
                
                for selector in possible_selectors:
                    try:
                        if selector.startswith("//"):
                            confirm_button = wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                        else:
                            confirm_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                        logger.info(f"✅ Botão de confirmação encontrado com seletor: {selector}")
                        break
                    except:
                        continue
                
                if not confirm_button:
                    logger.error("❌ Botão de confirmação não encontrado")
                    self.driver.save_screenshot(f"confirm_button_not_found_{bet_code}.png")
                    return False
                
                # Scroll para o elemento se necessário
                self.driver.execute_script("arguments[0].scrollIntoView(true);", confirm_button)
                time.sleep(1)
                
                # Tentar clicar
                try:
                    confirm_button.click()
                    logger.info("✅ Clique no botão de confirmação realizado")
                except Exception as click_error:
                    logger.warning(f"⚠️ Clique normal falhou, tentando JavaScript: {click_error}")
                    self.driver.execute_script("arguments[0].click();", confirm_button)
                    logger.info("✅ Clique via JavaScript realizado")
                
                time.sleep(5)
                
                # Procurar pelo botão "Sim" para confirmar
                yes_button = None
                yes_selectors = [
                    "//a[contains(text(),'Sim')]",
                    "//button[contains(text(),'Sim')]", 
                    ".btn-success",
                    ".btn[data-dismiss='modal']"
                ]
                
                for selector in yes_selectors:
                    try:
                        yes_button = wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                        logger.info(f"✅ Botão 'Sim' encontrado com seletor: {selector}")
                        break
                    except:
                        continue
                
                if yes_button:
                    # Scroll para o elemento se necessário
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", yes_button)
                    time.sleep(1)
                    
                    try:
                        yes_button.click()
                        logger.info("✅ Clique no botão 'Sim' realizado")
                    except Exception as click_error:
                        logger.warning(f"⚠️ Clique normal no 'Sim' falhou, tentando JavaScript: {click_error}")
                        self.driver.execute_script("arguments[0].click();", yes_button)
                        logger.info("✅ Clique via JavaScript no 'Sim' realizado")
                    
                    time.sleep(8)
                    
                    # Verificar se houve confirmação (procurar por mensagem de sucesso ou mudança na URL)
                    current_url = self.driver.current_url
                    logger.info(f"📍 URL atual após confirmação: {current_url}")
                    
                    # Verificar se ainda está na página do bilhete (confirmação falhou)
                    if f"/prebet/{bet_code}" in current_url:
                        logger.error("❌ Ainda na página do bilhete - confirmação falhou")
                        self.driver.save_screenshot(f"confirmation_failed_{bet_code}.png")
                        return False
                    
                    # Se foi redirecionado para home, pode ter funcionado ou falhado
                    if current_url == f"{self.base_url}/" or current_url == self.base_url:
                        logger.warning("⚠️ Redirecionado para home - verificando se foi confirmado")
                        
                        # Verificar na página "Minhas Apostas" se o bilhete aparece como confirmado
                        self.driver.get(f"{self.base_url}/bets")
                        time.sleep(3)
                        
                        # Procurar pelo código do bilhete nas apostas
                        try:
                            bet_element = self.driver.find_element(By.XPATH, f"//td[contains(text(), '{bet_code}')]")
                            logger.info(f"✅ Bilhete {bet_code} encontrado na lista de apostas")
                            
                            # Verificar o status (deve estar como "ABERTA" e não "PENDENTE")
                            parent_row = bet_element.find_element(By.XPATH, "./parent::tr")
                            status_cell = parent_row.find_elements(By.TAG_NAME, "td")[-1]  # Última coluna
                            status_text = status_cell.text.strip()
                            logger.info(f"📊 Status do bilhete: {status_text}")
                            
                            if "ABERTA" in status_text or "CONFIRMADA" in status_text:
                                logger.info("✅ Bilhete confirmado com sucesso")
                                return True
                            else:
                                logger.error(f"❌ Bilhete não confirmado. Status: {status_text}")
                                return False
                                
                        except Exception as e:
                            logger.error(f"❌ Bilhete não encontrado nas apostas: {str(e)}")
                            return False
                    
                    # Procurar por indicadores de sucesso na página atual
                    success_indicators = [
                        ".alert-success",
                        ".success-message", 
                        "//div[contains(text(), 'confirmad')]",
                        "//div[contains(text(), 'sucesso')]"
                    ]
                    
                    for indicator in success_indicators:
                        try:
                            if indicator.startswith("//"):
                                element = self.driver.find_element(By.XPATH, indicator)
                            else:
                                element = self.driver.find_element(By.CSS_SELECTOR, indicator)
                            logger.info(f"✅ Indicador de sucesso encontrado: {element.text}")
                            return True
                        except:
                            continue
                else:
                    logger.warning("⚠️ Botão 'Sim' não encontrado")
                    # Salvar screenshot para debug
                    self.driver.save_screenshot(f"confirm_final_{bet_code}.png")
                    return False
                
                # Se chegou até aqui, verificar se realmente foi confirmado
                logger.info("✅ Processo de confirmação concluído - verificando resultado")
                
            except TimeoutException:
                logger.error("❌ Timeout - elementos não encontrados")
                self.driver.save_screenshot(f"timeout_error_{bet_code}.png")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro ao confirmar aposta: {str(e)}")
            self.driver.save_screenshot(f"error_{bet_code}.png")
            return False
    
    def close(self):
        """Fecha o driver"""
        try:
            if self.driver:
                self.driver.quit()
                logger.info("🔒 Driver fechado")
        except:
            pass
