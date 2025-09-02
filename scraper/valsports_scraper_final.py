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
                    
                    # 3. Extrair times - PROCURAR POR ELEMENTOS SEPARADOS
                    try:
                        logger.info(f"   🔍 PROCURANDO TIMES NO JOGO {i+1}...")
                        
                        # Procurar por todas as divs com text-truncate que podem conter times
                        team_elements = game_element.find_elements(By.CSS_SELECTOR, ".text-truncate")
                        logger.info(f"   📋 Elementos .text-truncate encontrados: {len(team_elements)}")
                        
                        home_team = ""
                        away_team = ""
                        
                        for j, team_element in enumerate(team_elements):
                            team_text = team_element.text.strip()
                            team_class = team_element.get_attribute('class')
                            logger.info(f"     Elemento {j+1}: '{team_text}' (classe: {team_class})")
                            
                            # Pular se contém palavras-chave que não são times
                            if any(keyword in team_text.lower() for keyword in ['vencedor:', 'empate', 'odds', 'brasil:', 'colômbia:', 'copa', 'série']):
                                logger.info(f"       ⏭️ Pulado (palavra-chave): {team_text}")
                                continue
                            
                            # Pular se é a liga (já extraída)
                            if team_text == game_data['league']:
                                logger.info(f"       ⏭️ Pulado (liga): {team_text}")
                                continue
                            
                            # Pular se é a seleção (já extraída)
                            if 'vencedor:' in team_text.lower():
                                logger.info(f"       ⏭️ Pulado (seleção): {team_text}")
                                continue
                            
                            # Pular se é a data/hora (já extraída)
                            if re.search(r'\d{2}/\d{2}\s+\d{2}:\d{2}', team_text):
                                logger.info(f"       ⏭️ Pulado (data/hora): {team_text}")
                                continue
                            
                            # Pular se é odds (já extraída)
                            if re.search(r'^\d+\.\d+$', team_text):
                                logger.info(f"       ⏭️ Pulado (odds): {team_text}")
                                continue
                            
                            # Se não é nenhum dos acima, é um time
                            if not home_team:
                                home_team = team_text
                                logger.info(f"       🏠 Time da casa identificado: {home_team}")
                            elif not away_team:
                                away_team = team_text
                                logger.info(f"       ✈️ Time visitante identificado: {away_team}")
                                break  # Já temos os dois times
                        
                        game_data['home_team'] = home_team
                        game_data['away_team'] = away_team
                        
                        if home_team and away_team:
                            logger.info(f"   ✅ Times extraídos com sucesso: {home_team} x {away_team}")
                        else:
                            logger.warning(f"   ⚠️ Times não encontrados: casa='{home_team}', visitante='{away_team}'")
                            
                            # Tentar método alternativo - procurar por todos os elementos
                            logger.info(f"   🔍 TENTANDO MÉTODO ALTERNATIVO...")
                            all_elements = game_element.find_elements(By.CSS_SELECTOR, "*")
                            potential_teams = []
                            
                            for elem in all_elements:
                                try:
                                    text = elem.text.strip()
                                    if text and len(text) > 2 and not any(keyword in text.lower() for keyword in ['vencedor:', 'empate', 'odds', 'brasil:', 'colômbia:', 'copa', 'série', 'r$', 'total']):
                                        # Verificar se parece ser um nome de time
                                        if re.search(r'^[A-Za-zÀ-ÿ\s]+$', text) and len(text.split()) >= 1:
                                            potential_teams.append(text)
                                except:
                                    continue
                            
                            logger.info(f"   🎯 Possíveis times encontrados: {potential_teams}")
                            
                            # Se encontrou times potenciais, usar os primeiros dois
                            if len(potential_teams) >= 2:
                                game_data['home_team'] = potential_teams[0]
                                game_data['away_team'] = potential_teams[1]
                                logger.info(f"   ✅ Times extraídos via método alternativo: {potential_teams[0]} x {potential_teams[1]}")
                    
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
                            'datetime': '', 'teams': '', 'selections': [], 'odds_list': []
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
        """Confirma a aposta no sistema - VERSÃO ATUALIZADA PARA O SISTEMA ATUAL"""
        try:
            if not self.is_logged_in:
                logger.error("❌ Usuário não está logado")
                return False

            logger.info(f"✅ Confirmando aposta: {bet_code}")

            # PASSO 1: Ir para a página inicial
            logger.info("🏠 Indo para página inicial...")
            self.driver.get(self.base_url)
            time.sleep(3)

            # PASSO 2: Clicar em "Pré-aposta"
            logger.info("📋 Clicando em 'Pré-aposta'...")
            wait = WebDriverWait(self.driver, 10)

            try:
                pre_bet_link = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "PRÉ-APOSTA")))
                pre_bet_link.click()
                logger.info("✅ Clicou em 'Pré-aposta'")
                time.sleep(3)
            except Exception as e:
                logger.error(f"❌ Erro ao clicar em Pré-aposta: {str(e)}")
                self.driver.save_screenshot(f"pre_bet_click_error_{bet_code}.png")
                return False

            # PASSO 3: Encontrar o campo para código da pré-aposta
            logger.info("🔍 Procurando campo para código da pré-aposta...")

            # O sistema atual tem um campo específico com classe 'v-dialog-input' para o código
            bet_code_field = None
            try:
                # Primeiro tentar o campo específico identificado na investigação
                bet_code_field = self.driver.find_element(By.CSS_SELECTOR, ".v-dialog-input")
                logger.info("✅ Campo de código encontrado (classe v-dialog-input)")
            except:
                # Fallback: procurar por campo vazio que apareceu após Pré-aposta
                try:
                    inputs = self.driver.find_elements(By.TAG_NAME, "input")
                    for input_field in inputs:
                        placeholder = input_field.get_attribute("placeholder") or ""
                        if not placeholder.strip() and input_field.is_displayed():
                            # Verificar se não é o campo de pesquisa
                            if "pesquisar" not in (input_field.get_attribute("placeholder") or "").lower():
                                bet_code_field = input_field
                                logger.info("✅ Campo de código encontrado (campo vazio)")
                                break
                except Exception as e:
                    logger.error(f"❌ Erro ao procurar campo de código: {str(e)}")

            if not bet_code_field:
                logger.error("❌ Campo para código da pré-aposta não encontrado")
                self.driver.save_screenshot(f"no_bet_code_field_{bet_code}.png")
                return False

            # PASSO 4: Inserir o código do bilhete
            logger.info(f"⌨️ Digitando código: {bet_code}")
            bet_code_field.clear()
            bet_code_field.send_keys(bet_code)
            time.sleep(1)

            # PASSO 5: Procurar botão de busca/confirmação
            logger.info("🔍 Procurando botão de busca...")
            search_button = None

            # Possíveis seletores para o botão
            search_selectors = [
                "//button[contains(text(),'Buscar')]",
                "//a[contains(text(),'Buscar')]",
                "//button[contains(text(),'Confirmar')]",
                "//a[contains(text(),'Confirmar')]",
                "//button[contains(text(),'OK')]",
                "//a[contains(text(),'OK')]",
                "button.btn-success",
                "a.btn-success",
                ".btn-success"
            ]

            for selector in search_selectors:
                try:
                    if selector.startswith("//"):
                        search_button = wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                    else:
                        search_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                    logger.info(f"✅ Botão encontrado com seletor: {selector}")
                    break
                except:
                    continue

            # Se não encontrou botão específico, tentar submit do form
            if not search_button:
                logger.info("ℹ️ Botão específico não encontrado, tentando submit do form...")
                try:
                    # Procurar pelo form e fazer submit
                    form = self.driver.find_element(By.TAG_NAME, "form")
                    form.submit()
                    logger.info("✅ Form submetido")
                    time.sleep(5)
                except Exception as form_error:
                    logger.warning(f"⚠️ Erro ao submeter form: {str(form_error)}")
                    # Tentar pressionar Enter no campo
                    try:
                        bet_code_field.send_keys("\n")
                        logger.info("✅ Enter pressionado no campo")
                        time.sleep(3)
                    except Exception as enter_error:
                        logger.error(f"❌ Erro ao pressionar Enter: {str(enter_error)}")
                        return False
            else:
                # Clicar no botão encontrado
                try:
                    search_button.click()
                    logger.info("✅ Botão clicado")
                    time.sleep(5)
                except Exception as click_error:
                    logger.warning(f"⚠️ Erro ao clicar botão, tentando JavaScript: {str(click_error)}")
                    self.driver.execute_script("arguments[0].click();", search_button)
                    logger.info("✅ Botão clicado via JavaScript")
                    time.sleep(5)

            # PASSO 6: Verificar resultado
            current_url = self.driver.current_url
            logger.info(f"📍 URL após busca: {current_url}")

            # Verificar se foi redirecionado para a página do bilhete
            if f"/prebet/{bet_code}" in current_url:
                logger.info("✅ Bilhete carregado - continuando com confirmação...")
                return self._confirm_loaded_bet(bet_code)

            # Verificar se ainda está na página inicial (pode ter carregado inline)
            elif current_url == self.base_url or current_url == f"{self.base_url}/":
                logger.info("ℹ️ Ainda na página inicial - verificando se bilhete carregou inline...")

                # Verificar se apareceu botão de confirmação APOSTAR
                logger.info("🔍 Procurando botão 'APOSTAR'...")
                apostar_selectors = [
                    "button.btn.text-style span",  # Seletor CSS específico fornecido pelo usuário
                    "//button[contains(text(), 'Apostar')]",
                    "//a[contains(text(), 'Apostar')]",
                    "//button[contains(text(), 'APOSTAR')]",
                    "//a[contains(text(), 'APOSTAR')]",
                    "//button[contains(text(), 'Confirmar')]",
                    "//a[contains(text(), 'Confirmar')]"
                ]

                apostar_button = None
                for selector in apostar_selectors:
                    try:
                        if selector.startswith("//"):
                            apostar_button = self.driver.find_element(By.XPATH, selector)
                        else:
                            apostar_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                        
                        if apostar_button and apostar_button.is_displayed():
                            button_text = apostar_button.text.strip()
                            logger.info(f"✅ Botão 'APOSTAR' encontrado: '{button_text}'")
                            break
                    except:
                        continue

                if apostar_button:
                    logger.info("🎯 Clicando no botão 'APOSTAR'...")
                    try:
                        apostar_button.click()
                        logger.info("✅ Botão 'APOSTAR' clicado")
                        time.sleep(3)
                        
                        # Agora verificar se apareceu modal de confirmação
                        return self._handle_confirmation_modal(bet_code)
                        
                    except Exception as click_error:
                        logger.warning(f"⚠️ Erro ao clicar em 'APOSTAR', tentando JavaScript: {str(click_error)}")
                        try:
                            self.driver.execute_script("arguments[0].click();", apostar_button)
                            logger.info("✅ Botão 'APOSTAR' clicado via JavaScript")
                            time.sleep(3)
                            return self._handle_confirmation_modal(bet_code)
                        except Exception as js_error:
                            logger.error(f"❌ Erro ao clicar via JavaScript: {str(js_error)}")
                            return False
                else:
                    logger.warning("⚠️ Botão 'APOSTAR' não encontrado - verificando se bilhete foi processado...")

                    # Verificar mensagens de erro
                    page_text = self.driver.find_element(By.TAG_NAME, "body").text

                    # Verificar mensagens de erro específicas
                    if "não encontrado" in page_text.lower() or "inválido" in page_text.lower():
                        logger.error("❌ Bilhete não encontrado ou inválido")
                        return False
                    elif "expirado" in page_text.lower():
                        logger.error("❌ Bilhete expirado")
                        return False

                    # Verificar se há indicação de sucesso
                    success_indicators = [
                        "aposta realizada", "confirmada com sucesso", "bilhete confirmado",
                        "sucesso", "realizada", "aprovada"
                    ]

                    has_success_indicator = any(indicator in page_text.lower() for indicator in success_indicators)

                    # Verificar se há elementos relacionados a apostas realizadas
                    try:
                        bet_related_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'aposta') or contains(text(), 'bilhete')]")
                        has_bet_elements = len(bet_related_elements) > 0
                    except:
                        has_bet_elements = False

                    # Se encontrou indicadores de sucesso OU elementos relacionados a apostas, considerar sucesso
                    if has_success_indicator or has_bet_elements:
                        logger.info("✅ Indicação de sucesso encontrada na página")
                        return True
                    else:
                        logger.warning("⚠️ Status do bilhete desconhecido - mas pode ter sido confirmado")
                        self.driver.save_screenshot(f"unknown_bet_status_{bet_code}.png")

                        # IMPORTANTE: Se chegamos até aqui, pode ser que o bilhete tenha sido processado
                        # mas não haja indicação visual clara. Vamos assumir sucesso por enquanto
                        # e deixar a verificação de saldo (no método chamador) decidir.
                        logger.info("ℹ️ Assumindo sucesso temporariamente - verificar saldo para confirmar")
                        return True

            else:
                logger.warning(f"⚠️ Redirecionamento inesperado: {current_url}")
                self.driver.save_screenshot(f"unexpected_redirect_{bet_code}.png")
                return False

        except Exception as e:
            logger.error(f"❌ Erro ao confirmar aposta: {str(e)}")
            self.driver.save_screenshot(f"confirmation_error_{bet_code}.png")
            return False

    def _confirm_loaded_bet(self, bet_code):
        """Confirma bilhete quando foi carregado em página separada"""
        try:
            logger.info("🎯 Confirmando bilhete em página separada...")
            wait = WebDriverWait(self.driver, 10)

            # Procurar botão de confirmação
            confirm_button = None
            confirm_selectors = [
                ".btn-group > .text-style",
                ".btn.text-style",
                "button[type='button'].btn.text-style",
                ".btn-group button",
                "//button[contains(text(), 'Apostar')]",
                "//a[contains(text(), 'Apostar')]"
            ]

            for selector in confirm_selectors:
                try:
                    if selector.startswith("//"):
                        confirm_button = wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                    else:
                        confirm_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                    logger.info(f"✅ Botão de confirmação encontrado: {selector}")
                    break
                except:
                    continue

            if not confirm_button:
                logger.error("❌ Botão de confirmação não encontrado")
                return False

            # Clicar no botão
            confirm_button.click()
            time.sleep(3)

            return self._handle_confirmation_modal(bet_code)

        except Exception as e:
            logger.error(f"❌ Erro na confirmação de página separada: {str(e)}")
            return False

    def _confirm_inline_bet(self, confirm_button, bet_code):
        """Confirma bilhete quando carregado inline na mesma página"""
        try:
            logger.info("🎯 Confirmando bilhete inline...")

            # Clicar no botão de confirmação
            confirm_button.click()
            time.sleep(3)

            return self._handle_confirmation_modal(bet_code)

        except Exception as e:
            logger.error(f"❌ Erro na confirmação inline: {str(e)}")
            return False

    def _handle_confirmation_modal(self, bet_code):
        """Lida com modal de confirmação e mudança de prêmio - VERSÃO MELHORADA"""
        try:
            logger.info("🎯 Lidando com modal de confirmação...")
            wait = WebDriverWait(self.driver, 10)
            
            # CONTADOR PARA CONTROLAR QUANTAS CAIXAS DE CONFIRMAÇÃO FORAM TRATADAS
            confirmation_boxes_handled = 0
            max_confirmations = 5  # Limite de segurança para evitar loop infinito
            
            while confirmation_boxes_handled < max_confirmations:
                logger.info(f"🔄 Verificando caixa de confirmação #{confirmation_boxes_handled + 1}...")
                
                # Aguardar um pouco para carregar possíveis modais
                time.sleep(2)
                
                # VERIFICAR SE HÁ ALGUMA CAIXA DE DIÁLOGO ATIVA
                active_modals = self._find_active_modals()
                
                if not active_modals:
                    logger.info("✅ Nenhuma caixa de confirmação ativa encontrada")
                    break
                
                # TRATAR CADA MODAL ATIVO
                for i, modal in enumerate(active_modals):
                    logger.info(f"🎭 Tratando modal #{i+1} de {len(active_modals)}")
                    
                    try:
                        # Tentar tratar o modal
                        modal_handled = self._handle_single_modal(modal)
                        
                        if modal_handled:
                            confirmation_boxes_handled += 1
                            logger.info(f"✅ Modal #{i+1} tratado com sucesso")
                            time.sleep(3)  # Aguardar fechamento do modal
                        else:
                            logger.warning(f"⚠️ Modal #{i+1} não pôde ser tratado")
                            
                    except Exception as e:
                        logger.error(f"❌ Erro ao tratar modal #{i+1}: {str(e)}")
                        continue
                
                # Verificar se ainda há modais ativos após o tratamento
                remaining_modals = self._find_active_modals()
                if not remaining_modals:
                    logger.info("✅ Todos os modais foram fechados")
                    break
                
                logger.info(f"⚠️ Ainda há {len(remaining_modals)} modais ativos, continuando...")
            
            logger.info(f"📊 Total de caixas de confirmação tratadas: {confirmation_boxes_handled}")
            
            # APÓS TRATAR TODAS AS CAIXAS, VERIFICAR SE A APOSTA FOI CONFIRMADA
            return self._verify_final_confirmation()
            
        except Exception as e:
            logger.error(f"❌ Erro ao lidar com modais de confirmação: {str(e)}")
            return False
    
    def _find_active_modals(self):
        """Encontra todas as caixas de diálogo ativas na página"""
        try:
            # Procurar por diferentes tipos de modais
            modal_selectors = [
                "div.v-dialog.active",  # Modal Vuetify ativo
                "div.v-dialog-container",  # Container de modal
                ".modal.show",  # Modal Bootstrap ativo
                ".popup.active",  # Popup ativo
                "[role='dialog']"  # Elementos com role dialog
            ]
            
            active_modals = []
            
            for selector in modal_selectors:
                try:
                    modals = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for modal in modals:
                        if modal.is_displayed():
                            active_modals.append(modal)
                except:
                    continue
            
            # Remover duplicatas
            unique_modals = []
            for modal in active_modals:
                if modal not in unique_modals:
                    unique_modals.append(modal)
            
            logger.info(f"🔍 Encontrados {len(unique_modals)} modais ativos")
            return unique_modals
            
        except Exception as e:
            logger.warning(f"⚠️ Erro ao procurar modais ativos: {str(e)}")
            return []
    
    def _handle_single_modal(self, modal):
        """Trata uma única caixa de diálogo"""
        try:
            # Obter informações do modal
            modal_text = modal.text.lower()
            logger.info(f"📋 Conteúdo do modal: {modal_text[:100]}...")
            
            # DETERMINAR O TIPO DE MODAL E COMO TRATÁ-LO
            if any(word in modal_text for word in ["mudança de prêmio", "cotações mudaram", "atenção", "odds", "prêmio"]):
                logger.info("🎯 Modal de mudança de odds detectado")
                return self._handle_odds_change_modal(modal)
            elif any(word in modal_text for word in ["confirma", "confirmar", "deseja continuar", "sim", "não"]):
                logger.info("🎯 Modal de confirmação detectado")
                return self._handle_confirmation_modal_simple(modal)
            else:
                logger.info("🎯 Modal de tipo desconhecido - tentando tratamento genérico")
                return self._handle_generic_modal(modal)
                
        except Exception as e:
            logger.error(f"❌ Erro ao tratar modal individual: {str(e)}")
            return False
    
    def _handle_odds_change_modal(self, modal):
        """Trata especificamente modal de mudança de odds"""
        try:
            logger.info("🎯 Tratando modal de mudança de odds...")
            
            # Procurar botão "Sim" (success) no footer do modal
            success_selectors = [
                "a.v-dialog-btn.success",  # Seletor específico da imagem
                "div.v-dialog-footer a.v-dialog-btn.success",
                "//a[contains(text(),'Sim') and contains(@class,'success')]",
                "//a[contains(text(),'Sim')]",
                ".v-dialog-btn.success"
            ]
            
            for selector in success_selectors:
                try:
                    if selector.startswith("//"):
                        button = modal.find_element(By.XPATH, selector)
                    else:
                        button = modal.find_element(By.CSS_SELECTOR, selector)
                    
                    if button.is_displayed() and button.is_enabled():
                        button_text = button.text.strip()
                        logger.info(f"✅ Botão 'Sim' encontrado: '{button_text}'")
                        
                        # Clicar no botão
                        button.click()
                        logger.info("✅ Clique realizado com sucesso")
                        return True
                        
                except:
                    continue
            
            logger.warning("⚠️ Botão 'Sim' não encontrado no modal de odds")
            return False
            
        except Exception as e:
            logger.error(f"❌ Erro ao tratar modal de odds: {str(e)}")
            return False
    
    def _handle_confirmation_modal_simple(self, modal):
        """Trata modal de confirmação simples"""
        try:
            logger.info("🎯 Tratando modal de confirmação simples...")
            
            # Procurar botão de confirmação
            confirm_selectors = [
                "a.v-dialog-btn.success",
                "//a[contains(text(),'Sim')]",
                "//button[contains(text(),'Sim')]",
                "//a[contains(text(),'Continuar')]",
                "//button[contains(text(),'Continuar')]",
                ".btn-success"
            ]
            
            for selector in confirm_selectors:
                try:
                    if selector.startswith("//"):
                        button = modal.find_element(By.XPATH, selector)
                    else:
                        button = modal.find_element(By.CSS_SELECTOR, selector)
                    
                    if button.is_displayed() and button.is_enabled():
                        button_text = button.text.strip()
                        logger.info(f"✅ Botão de confirmação encontrado: '{button_text}'")
                        
                        # Clicar no botão
                        button.click()
                        logger.info("✅ Clique realizado com sucesso")
                        return True
                        
                except:
                    continue
            
            logger.warning("⚠️ Botão de confirmação não encontrado")
            return False
            
        except Exception as e:
            logger.error(f"❌ Erro ao tratar modal de confirmação: {str(e)}")
            return False
    
    def _handle_generic_modal(self, modal):
        """Trata modal de tipo desconhecido"""
        try:
            logger.info("🎯 Tratando modal genérico...")
            
            # Procurar qualquer botão clicável
            buttons = modal.find_elements(By.CSS_SELECTOR, "button, a, input[type='button']")
            
            for button in buttons:
                try:
                    if button.is_displayed() and button.is_enabled():
                        button_text = button.text.strip()
                        
                        # Preferir botões positivos
                        if any(word in button_text.lower() for word in ["sim", "sim", "ok", "continuar", "aceitar"]):
                            logger.info(f"✅ Botão positivo encontrado: '{button_text}'")
                            button.click()
                            logger.info("✅ Clique realizado com sucesso")
                            return True
                            
                except:
                    continue
            
            logger.warning("⚠️ Nenhum botão adequado encontrado no modal genérico")
            return False
            
        except Exception as e:
            logger.error(f"❌ Erro ao tratar modal genérico: {str(e)}")
            return False
    
    def _verify_final_confirmation(self):
        """Verifica se a aposta foi confirmada após tratar todos os modais"""
        try:
            logger.info("🔍 Verificando confirmação final...")
            
            # Aguardar um pouco para a página processar
            time.sleep(3)
            
            # Verificar se há indicações de sucesso
            page_text = self.driver.find_element(By.TAG_NAME, "body").text.lower()
            success_indicators = [
                "aposta realizada", "confirmada com sucesso", "bilhete confirmado",
                "sucesso", "realizada", "aprovada", "confirmação", "aposta aprovada"
            ]
            
            has_success = any(indicator in page_text for indicator in success_indicators)
            
            if has_success:
                logger.info("✅ Confirmação final bem-sucedida")
                return True
            else:
                logger.warning("⚠️ Nenhuma indicação clara de sucesso encontrada")
                
                # Verificar se há mensagens de erro
                error_indicators = [
                    "erro", "falha", "não foi possível", "tente novamente",
                    "bilhete não encontrado", "bilhete inválido", "bilhete expirado"
                ]
                
                has_error = any(indicator in page_text for indicator in error_indicators)
                
                if has_error:
                    logger.error("❌ Indicações de erro encontradas")
                    return False
                else:
                    # Salvar screenshot para análise
                    self.driver.save_screenshot(f"final_confirmation_check_{int(time.time())}.png")
                    logger.info("🔍 Screenshot salvo para análise manual")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Erro ao verificar confirmação final: {str(e)}")
            return False

    def _handle_prize_change_modal(self):
        """Lida especificamente com modal de mudança de prêmio"""
        try:
            logger.info("🎯 Lidando com mudança de prêmio...")
            wait = WebDriverWait(self.driver, 10)  # Aumentar timeout

            # Primeiro, verificar se o modal ainda está visível
            try:
                modal = self.driver.find_element("css selector", "div.v-dialog-container")
                if not modal.is_displayed():
                    logger.warning("⚠️ Modal de mudança de prêmio não está mais visível")
                    return True  # Modal já foi fechado
                
                modal_text = modal.text
                logger.info(f"📋 Conteúdo do modal:\n{modal_text}")
                
                # Verificar se é realmente o modal de mudança de prêmio
                if "mudança de prêmio" not in modal_text.lower():
                    logger.warning("⚠️ Modal encontrado mas não é de mudança de prêmio")
                    return True
                
                logger.info("✅ Modal de mudança de prêmio confirmado")
                
            except Exception as e:
                logger.warning(f"⚠️ Modal não encontrado: {str(e)}")
                return True  # Modal não existe mais

            # Procurar botão para aceitar mudança usando seletores específicos
            accept_buttons = [
                "a.v-dialog-btn.success",  # Seletor CSS específico fornecido pelo usuário
                "div.v-dialog-footer a.v-dialog-btn.success",  # Mais específico
                "//a[contains(text(),'Sim') and contains(@class,'success')]",  # XPath mais específico
                "//a[contains(text(),'Sim')]",
                "//button[contains(text(),'Sim')]",
                "//a[contains(text(),'Continuar')]",
                "//button[contains(text(),'Continuar')]",
                "//button[contains(text(),'OK')]",
                "//a[contains(text(),'OK')]"
            ]

            logger.info("🔍 Procurando botão para aceitar mudança de prêmio...")
            
            # Primeiro, listar todos os botões visíveis no modal
            try:
                all_buttons = self.driver.find_elements("css selector", "div.v-dialog-footer a, div.v-dialog-footer button")
                logger.info(f"📊 Encontrados {len(all_buttons)} botões no footer do modal")
                
                for i, btn in enumerate(all_buttons):
                    if btn.is_displayed():
                        btn_text = btn.text.strip()
                        btn_class = btn.get_attribute('class')
                        logger.info(f"   Botão {i+1}: '{btn_text}' (classe: {btn_class})")
            except Exception as e:
                logger.warning(f"⚠️ Erro ao listar botões: {str(e)}")
            
            for selector in accept_buttons:
                try:
                    logger.info(f"🔍 Tentando seletor: {selector}")
                    
                    if selector.startswith("//"):
                        button = wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                    else:
                        button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                    
                    button_text = button.text.strip()
                    button_class = button.get_attribute('class')
                    logger.info(f"✅ Botão para aceitar mudança encontrado: '{button_text}' (classe: {button_class}) - clicando...")
                    
                    # Verificar se o botão está realmente visível e clicável
                    if not button.is_displayed():
                        logger.warning("⚠️ Botão encontrado mas não está visível")
                        continue
                    
                    # Scroll para o elemento
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", button)
                    time.sleep(1)
                    
                    # Tentar clique normal primeiro
                    try:
                        button.click()
                        logger.info("✅ Clique normal realizado com sucesso")
                    except Exception as click_error:
                        logger.warning(f"⚠️ Clique normal falhou, tentando JavaScript: {str(click_error)}")
                        self.driver.execute_script("arguments[0].click();", button)
                        logger.info("✅ Clique via JavaScript realizado")
                    
                    logger.info("✅ Mudança de prêmio aceita")
                    time.sleep(3)  # Aguardar mais tempo
                    
                    # Verificar se o modal foi fechado
                    try:
                        modal_after = self.driver.find_element("css selector", "div.v-dialog-container")
                        if not modal_after.is_displayed():
                            logger.info("✅ Modal fechado com sucesso")
                        else:
                            logger.warning("⚠️ Modal ainda está visível após clique")
                    except:
                        logger.info("✅ Modal não encontrado após clique - provavelmente fechado")
                    
                    return True
                    
                except Exception as selector_error:
                    logger.debug(f"⚠️ Seletor {selector} falhou: {str(selector_error)}")
                    continue

            logger.error("❌ Nenhum botão para aceitar mudança foi encontrado")
            # Salvar screenshot para debug
            self.driver.save_screenshot(f"prize_change_modal_error_{int(time.time())}.png")
            return False

        except Exception as e:
            logger.error(f"❌ Erro ao lidar com mudança de prêmio: {str(e)}")
            # Salvar screenshot para debug
            self.driver.save_screenshot(f"prize_change_modal_exception_{int(time.time())}.png")
            return False
    
    def close(self):
        """Fecha o driver"""
        try:
            if self.driver:
                self.driver.quit()
                logger.info("🔒 Driver fechado")
        except:
            pass
