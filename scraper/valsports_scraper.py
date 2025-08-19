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
            
            # Extrair dados usando regex otimizado
            import re
            
            # Padrões otimizados para extração
            patterns = {
                'league': r'Liga:\s*([^\n]+)',
                'teams': r'Times:\s*([^\n]+)',
                'selection': r'Seleção:\s*([^\n]+)',
                'datetime': r'Data/Hora:\s*([^\n]+)',
                'odds': r'Odds:\s*([^\n]+)',
                'total_odds': r'Odds Total:\s*([^\n]+)',
                'possible_prize': r'Prêmio Possível:\s*([^\n]+)',
                'bettor_name': r'Nome do Apostador:\s*([^\n]+)',
                'bet_value': r'Valor da Aposta:\s*([^\n]+)'
            }
            
            # Extrair dados
            bet_data = {}
            for key, pattern in patterns.items():
                match = re.search(pattern, ticket_full_text)
                if match:
                    bet_data[key] = match.group(1).strip()
                else:
                    bet_data[key] = "N/A"
            
            # Tentar capturar nome e valor diretamente dos campos
            try:
                # Nome do apostador
                name_field = self.driver.find_element(By.CSS_SELECTOR, ".mb-1:nth-child(3) .form-control")
                bet_data['bettor_name'] = name_field.get_attribute("value") or bet_data['bettor_name']
                
                # Valor da aposta
                value_field = self.driver.find_element(By.CSS_SELECTOR, ".mb-1:nth-child(4) .form-control")
                bet_data['bet_value'] = value_field.get_attribute("value") or bet_data['bet_value']
            except:
                logger.warning("Não foi possível capturar campos específicos")
            
            logger.info(f"Dados do bilhete extraídos com sucesso: {len(bet_data)} campos")
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
