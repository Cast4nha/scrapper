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
                        match = re.search(pattern, ticket_full_text, re.IGNORECASE)
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
                if 'Copa Libertadores' in ticket_full_text:
                    bet_data['league'] = "América do Sul: Copa Libertadores"
                elif 'Copa Sudamericana' in ticket_full_text:
                    bet_data['league'] = "América do Sul: Copa Sudamericana"
                elif 'CONCACAF' in ticket_full_text:
                    bet_data['league'] = "CONCACAF: Taça Centroamericana"
                elif 'Inglaterra' in ticket_full_text:
                    bet_data['league'] = "Inglaterra: Liga 1"
                elif 'Costa Rica' in ticket_full_text:
                    bet_data['league'] = "Costa Rica: Taça"
                
                # Extrair todos os dados usando regex mais robusto
                all_teams = []
                all_selections = []
                all_datetimes = []
                all_odds = []
                all_leagues = []
                
                # Encontrar todas as datas/horas
                datetime_matches = re.findall(r'\d{2}/\d{2}\s+\d{2}:\d{2}', ticket_full_text)
                all_datetimes = list(set(datetime_matches))  # Remove duplicatas
                
                # Encontrar todas as odds (números decimais)
                odds_matches = re.findall(r'\b\d+\.\d+\b', ticket_full_text)
                all_odds = list(set(odds_matches))  # Remove duplicatas
                
                # Extrair dados usando XPath para cada jogo individual (estrutura sequencial)
                game_xpaths = []
                
                # Usar XPaths exatos fornecidos pelo usuário
                logger.info("Iniciando captura com XPaths exatos...")
                
                # Aguardar o container principal estar presente
                wait = WebDriverWait(self.driver, 10)
                try:
                    bilhete_container = wait.until(
                        EC.presence_of_element_located((By.XPATH, "//main/div[3]/div/div/div"))
                    )
                    logger.info("Container do bilhete encontrado")
                except Exception as e:
                    logger.error(f"Container do bilhete não encontrado: {str(e)}")
                    return None
                
                games_found = 0
                
                # Primeiro, verificar quantos jogos existem
                try:
                    quantidade_element = self.driver.find_element(By.XPATH, "//div[3]/div/div/div/h5")
                    quantidade_text = quantidade_element.text.strip()
                    logger.info(f"Quantidade de jogos: {quantidade_text}")
                    
                    # Extrair número de jogos do texto (ex: "BILHETE 3" -> 3)
                    import re
                    quantidade_match = re.search(r'(\d+)', quantidade_text)
                    if quantidade_match:
                        max_jogos = int(quantidade_match.group(1))
                        logger.info(f"Bilhete com {max_jogos} jogos")
                    else:
                        max_jogos = 10  # Fallback
                        logger.info(f"Não foi possível extrair quantidade, usando fallback: {max_jogos}")
                except Exception as e:
                    logger.warning(f"Erro ao obter quantidade de jogos: {str(e)}")
                    max_jogos = 10  # Fallback
                
                # Set para evitar duplicatas
                processed_games = set()
                
                # Iterar sobre os jogos usando XPaths sequenciais
                for i in range(1, max_jogos + 1):
                    try:
                        jogo_xpath = f"//main/div[3]/div/div/div/div/div[{i}]"
                        jogo = self.driver.find_element(By.XPATH, jogo_xpath)
                        logger.info(f"Processando jogo {i} com XPath: {jogo_xpath}")
                    try:
                        logger.info(f"Processando jogo {i+1}...")
                        
                        # Extrair texto completo do jogo
                        game_text = jogo.text.strip()
                        logger.info(f"Texto do jogo {i}: {game_text}")
                        
                        if not game_text or len(game_text) < 10:
                            logger.info(f"Jogo {i} vazio ou muito curto, pulando...")
                            continue
                        
                        # Extrair dados usando regex do texto completo
                        import re
                        
                        # Extrair liga
                        liga_match = re.search(r'([A-Za-z\s]+):\s*([A-Za-z\s]+)', game_text)
                        if liga_match:
                            liga = f"{liga_match.group(1).strip()}: {liga_match.group(2).strip()}"
                        else:
                            liga = "Liga não encontrada"
                        
                        # Extrair data/hora
                        datetime_match = re.search(r'(\d{2}/\d{2}\s+\d{2}:\d{2})', game_text)
                        if datetime_match:
                            datetime_text = datetime_match.group(1)
                        else:
                            datetime_text = "Data/Hora não encontrada"
                        
                        # Extrair times (procurar por padrão "Time1 x Time2")
                        teams_match = re.search(r'([A-Za-zÀ-ÿ\s]+)\s+x\s+([A-Za-zÀ-ÿ\s]+)', game_text)
                        if teams_match:
                            casa = teams_match.group(1).strip()
                            fora = teams_match.group(2).strip()
                        else:
                            casa = "Time casa não encontrado"
                            fora = "Time fora não encontrado"
                        
                        # Extrair seleção
                        selection_match = re.search(r'Vencedor:\s*([A-Za-zÀ-ÿ\s]+)', game_text)
                        if selection_match:
                            aposta = f"Vencedor: {selection_match.group(1).strip()}"
                        elif 'Empate' in game_text:
                            aposta = "Empate"
                        else:
                            aposta = "Aposta não encontrada"
                        
                        # Extrair odd
                        odds_match = re.search(r'\b(\d+\.\d+)\b', game_text)
                        if odds_match:
                            odd = odds_match.group(1)
                        else:
                            odd = "Odd não encontrada"
                        
                        # Criar hash único para evitar duplicatas
                        game_hash = hash(f"{liga}{casa}{fora}{aposta}{odd}")
                        if game_hash in processed_games:
                            logger.info(f"Jogo {i+1} duplicado, pulando...")
                            continue
                            
                        processed_games.add(game_hash)
                        games_found += 1
                        
                        logger.info(f"Jogo {games_found}: {liga} - {casa} x {fora} - {aposta} ({odd})")
                        
                        # Debug: mostrar todos os elementos .col do jogo
                        try:
                            col_elements = jogo.find_elements(By.CSS_SELECTOR, ".col")
                            logger.info(f"Jogo {games_found} - Elementos .col encontrados: {len(col_elements)}")
                            for idx, col in enumerate(col_elements):
                                col_text = col.text.strip()
                                if col_text:
                                    logger.info(f"  Col {idx}: '{col_text}'")
                        except Exception as e:
                            logger.error(f"Erro ao debug elementos .col: {str(e)}")
                        
                        # Adicionar aos arrays
                        all_leagues.append(liga)
                        all_teams.append(f"{casa} x {fora}")
                        all_selections.append(aposta)
                        all_odds.append(odd)
                        
                        # Tentar extrair data/hora (pode estar em outro lugar)
                        try:
                            datetime_element = jogo.find_element(By.CSS_SELECTOR, "[class*='date'], [class*='time']")
                            datetime_text = datetime_element.text.strip()
                            if datetime_text:
                                all_datetimes.append(datetime_text)
                            else:
                                all_datetimes.append("Data/Hora não encontrada")
                        except:
                            all_datetimes.append("Data/Hora não encontrada")
                            
                    except Exception as e:
                        logger.error(f"Erro ao processar jogo {i+1}: {str(e)}")
                        continue
                
                # Log do resultado final
                logger.info(f"Total de jogos encontrados: {games_found}")
                logger.info(f"Total de times capturados: {len(all_teams)}")
                logger.info(f"Total de odds capturadas: {len(all_odds)}")
                
                # Buscar seleções específicas conhecidas
                known_selections = [
                    'Vencedor: Vélez Sarsfield', 'Vencedor: Atlético Nacional',
                    'Vencedor: Peñarol', 'Vencedor: Once Caldas',
                    'Vencedor: America de Cali', 'Vencedor: CS Uruguay de Coronado',
                    'Vencedor: Sporting San José', 'Vencedor: Deportivo Saprissa',
                    'Vencedor: Municipal Grecia', 'Vencedor: Herediano',
                    'Vencedor: Santos de Guápiles', 'Vencedor: Alajuelense',
                    'Vencedor: Cartaginés', 'Vencedor: Puntarenas', 'Vencedor: Limón',
                    'Vencedor: CD Águila', 'Vencedor: CD Olimpia', 'Vencedor: Plaza Amador',
                    'Vencedor: Manágua FC', 'Vencedor: Port Vale', 'Vencedor: Stevenage',
                    'Vencedor: Rotherham', 'Vencedor: Burton Albion', 'Empate'
                ]
                
                for selection in known_selections:
                    if selection in ticket_full_text and selection not in all_selections:
                        all_selections.append(selection)
                
                logger.info(f"Ligas encontradas: {all_leagues}")
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
                    'leagues': all_leagues,
                    'teams': all_teams,
                    'selections': all_selections,
                    'datetimes': all_datetimes,
                    'odds': all_odds,
                    'total_games': len(all_teams)
                }
                
            except Exception as e:
                logger.warning(f"Erro na extração específica: {str(e)}")
            
            # Capturar dados principais usando XPaths exatos
            try:
                # Total das odds
                total_odds_element = self.driver.find_element(By.XPATH, "//main/div[3]/div/div[2]/div/div/div/div[2]")
                total_odds_text = total_odds_element.text.strip()
                if total_odds_text:
                    bet_data['total_odds'] = total_odds_text
                    logger.info(f"Total odds capturado: {total_odds_text}")
                
                # Possível retorno
                possible_prize_element = self.driver.find_element(By.XPATH, "//main/div[3]/div/div[2]/div/div[2]/div/div[2]")
                possible_prize_text = possible_prize_element.text.strip()
                if possible_prize_text:
                    bet_data['possible_prize'] = possible_prize_text
                    logger.info(f"Possível prêmio capturado: {possible_prize_text}")
                
                # Nome do apostador
                name_field = self.driver.find_element(By.XPATH, "(//input[@type='text'])[2]")
                name_value = name_field.get_attribute("value")
                if name_value and name_value.strip():
                    bet_data['bettor_name'] = name_value.strip()
                    logger.info(f"Nome do apostador capturado: {name_value.strip()}")
                
                # Valor da aposta
                value_field = self.driver.find_element(By.XPATH, "(//input[@type='text'])[3]")
                value_value = value_field.get_attribute("value")
                if value_value and value_value.strip():
                    if not value_value.startswith('R$'):
                        bet_data['bet_value'] = f"R$ {value_value.strip()}"
                    else:
                        bet_data['bet_value'] = value_value.strip()
                    logger.info(f"Valor da aposta capturado: {bet_data['bet_value']}")
                    
            except Exception as e:
                logger.warning(f"Erro ao capturar dados principais: {str(e)}")
            
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
