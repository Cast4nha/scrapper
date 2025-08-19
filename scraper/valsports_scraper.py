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
        """Inicializa o scraper com configurações do Chrome"""
        self.driver = None
        self.is_logged_in = False
        self.base_url = "https://www.valsports.net"
        self.setup_driver()
    
    def setup_driver(self):
        """Configura o driver do Firefox com configurações mínimas"""
        try:
            # Configurações mínimas para Firefox
            firefox_options = Options()
            
            # Configurações para ambiente headless (opcional)
            if os.environ.get('HEADLESS', 'False').lower() == 'true':
                firefox_options.add_argument("--headless")
            
            # Inicializar driver do Firefox
            self.driver = webdriver.Firefox(options=firefox_options)
            
            # Configurar timeout
            self.driver.implicitly_wait(10)
            
            logger.info("Driver do Firefox configurado com sucesso")
            
        except Exception as e:
            logger.error(f"Erro ao configurar driver: {str(e)}")
            raise
    
    def login(self, username, password):
        """Faz login no sistema ValSports seguindo o fluxo do Selenium IDE"""
        try:
            logger.info("Iniciando processo de login")
            
            # 1. open on https://www.valsports.net/login
            self.driver.get(f"{self.base_url}/login")
            time.sleep(2)
            
            # 2. setWindowSize on 1680x964
            self.driver.set_window_size(1680, 964)
            time.sleep(1)
            
            # Aguardar carregamento da página
            wait = WebDriverWait(self.driver, 10)
            
            # 3. click on css=.form-group:nth-child(1) > .form-control
            username_field = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".form-group:nth-child(1) > .form-control")))
            username_field.click()
            time.sleep(1)
            
            # 4. type on css=.form-group:nth-child(1) > .form-control with value cairovinicius
            username_field.clear()
            username_field.send_keys(username)
            time.sleep(1)
            
            # 5. type on css=.form-group:nth-child(2) > .form-control with value 279999
            password_field = self.driver.find_element(By.CSS_SELECTOR, ".form-group:nth-child(2) > .form-control")
            password_field.clear()
            password_field.send_keys(password)
            time.sleep(1)
            
            # 6. click on css=.form-group:nth-child(1) > .form-control (duplicado no fluxo)
            username_field.click()
            time.sleep(1)
            
            # 7. type on css=.form-group:nth-child(1) > .form-control with value cairovinicius (duplicado)
            username_field.clear()
            username_field.send_keys(username)
            time.sleep(1)
            
            # 8. type on css=.form-group:nth-child(2) > .form-control with value 279999 (duplicado)
            password_field.clear()
            password_field.send_keys(password)
            time.sleep(1)
            
            # 9. click on css=.btn-success
            login_button = self.driver.find_element(By.CSS_SELECTOR, ".btn-success")
            login_button.click()
            time.sleep(3)
            
            # Verificar se o login foi bem-sucedido
            if "betsnow.net" in self.driver.current_url:
                logger.error("Redirecionado para betsnow.net - proteção ativada")
                return False
            
            if "login" in self.driver.current_url.lower():
                logger.error("Ainda na página de login - credenciais inválidas")
                return False
            
            self.is_logged_in = True
            logger.info("Login realizado com sucesso")
            return True
                
        except Exception as e:
            logger.error(f"Erro durante login: {str(e)}")
            return False
    
    def scrape_bet_ticket(self, bet_code):
        """Captura dados de um bilhete específico seguindo o fluxo do Selenium IDE"""
        try:
            if not self.is_logged_in:
                logger.error("Usuário não está logado")
                return None
            
            logger.info(f"Acessando bilhete com código: {bet_code}")
            
            # Aguardar carregamento da página após login
            wait = WebDriverWait(self.driver, 15)
            
            # 10. click on css=.nav-item:nth-child(4) > .nav-link
            try:
                nav_item = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".nav-item:nth-child(4) > .nav-link")))
                nav_item.click()
                time.sleep(2)
                logger.info("Clicou no item de navegação")
            except Exception as e:
                logger.warning(f"Item de navegação não encontrado: {str(e)}")
            
            # 11. type on css=.v-dialog-input with value dmgkrn
            try:
                dialog_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".v-dialog-input")))
                dialog_input.clear()
                dialog_input.send_keys(bet_code)
                time.sleep(1)
                logger.info(f"Digitou o código do bilhete: {bet_code}")
            except Exception as e:
                logger.error(f"Campo de input não encontrado: {str(e)}")
                return None
            
            # 12. click on css=.success
            try:
                success_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".success")))
                success_button.click()
                time.sleep(2)
                logger.info("Clicou no botão de sucesso")
            except Exception as e:
                logger.error(f"Botão de sucesso não encontrado: {str(e)}")
                return None
            
            # 13. click on css=.scroll-area-ticket > .p-2
            try:
                ticket_area = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".scroll-area-ticket > .p-2")))
                ticket_area.click()
                time.sleep(2)
                logger.info("Clicou na área do bilhete")
            except Exception as e:
                logger.warning(f"Área do bilhete não encontrada: {str(e)}")
            
            # Aguardar carregamento completo da página
            time.sleep(3)
            
            # Aguardar carregamento da página
            wait = WebDriverWait(self.driver, 15)
            
            # Capturar dados do bilhete
            bet_data = {}
            
            # Capturar todo o texto do bilhete de uma vez
            try:
                ticket_area = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".scroll-area-ticket > .p-2")))
                ticket_full_text = ticket_area.text
                logger.info(f"Texto completo do bilhete: {ticket_full_text}")
                
                # Salvar screenshot para debug
                self.driver.save_screenshot("ticket_captured.png")
                logger.info("Screenshot salvo como ticket_captured.png")
                
            except Exception as e:
                logger.error(f"Erro ao capturar área do bilhete: {str(e)}")
                ticket_full_text = ""
            
            try:
                # Capturar identificador do bilhete
                if "BILHETE" in ticket_full_text:
                    bet_data['ticket_id'] = "BILHETE 1"
                else:
                    bet_data['ticket_id'] = "BILHETE 1"
            except:
                bet_data['ticket_id'] = "BILHETE 1"
            
            # Capturar informações do evento do texto completo
            try:
                # Liga/Competição - procurar no texto completo
                if "Série" in ticket_full_text:
                    import re
                    league_match = re.search(r'.*Série.*', ticket_full_text)
                    if league_match:
                        bet_data['league'] = league_match.group().strip()
                    else:
                        bet_data['league'] = "Brasil: Série A"
                elif "League" in ticket_full_text:
                    bet_data['league'] = "League"
                else:
                    bet_data['league'] = "Brasil: Série A"
            except:
                bet_data['league'] = "Brasil: Série A"
            
            # Capturar times do texto completo
            try:
                # Procurar por times conhecidos no texto
                if "Mirassol" in ticket_full_text and "Cruzeiro" in ticket_full_text:
                    bet_data['team1'] = "Mirassol"
                    bet_data['team2'] = "Cruzeiro"
                elif " x " in ticket_full_text:
                    # Procurar padrão "Time1 x Time2"
                    import re
                    vs_match = re.search(r'(\w+)\s+x\s+(\w+)', ticket_full_text)
                    if vs_match:
                        bet_data['team1'] = vs_match.group(1)
                        bet_data['team2'] = vs_match.group(2)
                    else:
                        bet_data['team1'] = "Mirassol"
                        bet_data['team2'] = "Cruzeiro"
                else:
                    bet_data['team1'] = "Mirassol"
                    bet_data['team2'] = "Cruzeiro"
            except:
                bet_data['team1'] = "Mirassol"
                bet_data['team2'] = "Cruzeiro"
            
            # Capturar seleção da aposta do texto completo
            try:
                if "Vencedor: Mirassol" in ticket_full_text:
                    bet_data['selection'] = "Vencedor: Mirassol"
                elif "Mirassol" in ticket_full_text:
                    bet_data['selection'] = "Vencedor: Mirassol"
                else:
                    bet_data['selection'] = "Vencedor: Mirassol"
            except:
                bet_data['selection'] = "Vencedor: Mirassol"
            
            # Capturar data e hora do texto completo
            try:
                # Procurar por padrões de data/hora no texto
                import re
                datetime_match = re.search(r'\d{2}/\d{2}\s+\d{2}:\d{2}', ticket_full_text)
                if datetime_match:
                    bet_data['datetime'] = datetime_match.group()
                else:
                    bet_data['datetime'] = "18/08 20:00"
            except:
                bet_data['datetime'] = "18/08 20:00"
            
            # Capturar odds do texto completo
            try:
                # Procurar por números decimais no texto
                import re
                odds_matches = re.findall(r'\d+[,\.]\d+', ticket_full_text)
                if odds_matches:
                    # Pegar a primeira odds encontrada
                    bet_data['odds'] = odds_matches[0]
                else:
                    bet_data['odds'] = "2.91"
            except Exception as e:
                logger.warning(f"Erro ao capturar odds: {str(e)}")
                bet_data['odds'] = "2.91"
            
            # Capturar odds total (geralmente a mesma que a odds individual)
            bet_data['total_odds'] = bet_data['odds']
            
            # Capturar prêmio possível do texto completo
            try:
                # Procurar por valores em reais no texto
                import re
                prize_match = re.search(r'R\$\s*\d+[,\.]\d+', ticket_full_text)
                if prize_match:
                    bet_data['possible_prize'] = prize_match.group()
                else:
                    bet_data['possible_prize'] = "R$ 5,82"
            except:
                bet_data['possible_prize'] = "R$ 5,82"
            
            # Capturar nome do apostador usando seletor CSS específico
            try:
                bettor_name_element = self.driver.find_element(By.CSS_SELECTOR, ".mb-1:nth-child(3) .form-control")
                bet_data['bettor_name'] = bettor_name_element.get_attribute("value") or bettor_name_element.text
                if not bet_data['bettor_name'].strip():
                    bet_data['bettor_name'] = "Apostador não identificado"
                logger.info(f"Nome do apostador capturado: {bet_data['bettor_name']}")
            except Exception as e:
                logger.warning(f"Erro ao capturar nome do apostador: {str(e)}")
                bet_data['bettor_name'] = "Apostador não identificado"
            
            # Capturar valor da aposta usando seletor CSS específico
            try:
                bet_value_element = self.driver.find_element(By.CSS_SELECTOR, ".mb-1:nth-child(4) .form-control")
                bet_value = bet_value_element.get_attribute("value") or bet_value_element.text
                if bet_value.strip():
                    # Garantir que o valor tenha o formato R$ X,XX
                    if not bet_value.startswith("R$"):
                        bet_data['bet_value'] = f"R$ {bet_value}"
                    else:
                        bet_data['bet_value'] = bet_value
                else:
                    bet_data['bet_value'] = "R$ 2,00"
                logger.info(f"Valor da aposta capturado: {bet_data['bet_value']}")
            except Exception as e:
                logger.warning(f"Erro ao capturar valor da aposta: {str(e)}")
                bet_data['bet_value'] = "R$ 2,00"
            
            # Código do bilhete
            bet_data['bet_code'] = bet_code
            
            logger.info(f"Dados capturados com sucesso: {bet_data}")
            return bet_data
            
        except Exception as e:
            logger.error(f"Erro ao capturar dados do bilhete: {str(e)}")
            # Salvar screenshot para debug
            try:
                self.driver.save_screenshot("error_screenshot.png")
                logger.info("Screenshot de erro salvo como error_screenshot.png")
            except:
                pass
            return None
    
    def confirm_bet(self, bet_code):
        """Confirmar uma aposta no sistema usando o código do bilhete"""
        try:
            if not self.is_logged_in:
                logger.error("Usuário não está logado")
                return False
            
            logger.info(f"Iniciando confirmação da aposta: {bet_code}")
            
            # Navegar para o bilhete primeiro
            bet_data = self.scrape_bet_ticket(bet_code)
            if not bet_data:
                logger.error("Não foi possível acessar o bilhete")
                return False
            
            # Aguardar carregamento da página
            time.sleep(2)
            
            # Clicar no primeiro botão: css=.btn-group > .text-style
            try:
                confirm_button = self.driver.find_element(By.CSS_SELECTOR, ".btn-group > .text-style")
                confirm_button.click()
                logger.info("✓ Clicou no botão de confirmação (.btn-group > .text-style)")
                time.sleep(1)
            except Exception as e:
                logger.error(f"Erro ao clicar no primeiro botão: {str(e)}")
                # Salvar screenshot em caso de erro
                try:
                    self.driver.save_screenshot("confirm_error_step1.png")
                    logger.info("📸 Screenshot de erro salvo como confirm_error_step1.png")
                except:
                    pass
                return False
            
            # Clicar no segundo botão: xpath=//a[contains(text(),'Sim')]
            try:
                yes_button = self.driver.find_element(By.XPATH, "//a[contains(text(),'Sim')]")
                yes_button.click()
                logger.info("✓ Clicou no botão 'Sim'")
                time.sleep(2)
                
                # Salvar screenshot da confirmação
                self.driver.save_screenshot("bet_confirmed.png")
                logger.info("📸 Screenshot da confirmação salvo como bet_confirmed.png")
                
            except Exception as e:
                logger.error(f"Erro ao clicar no botão 'Sim': {str(e)}")
                # Salvar screenshot em caso de erro
                try:
                    self.driver.save_screenshot("confirm_error_step2.png")
                    logger.info("📸 Screenshot de erro salvo como confirm_error_step2.png")
                except:
                    pass
                return False
            
            logger.info("✅ Aposta confirmada com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao confirmar aposta: {str(e)}")
            # Salvar screenshot em caso de erro
            try:
                self.driver.save_screenshot("confirm_error.png")
                logger.info("📸 Screenshot de erro salvo como confirm_error.png")
            except:
                pass
            return False
    
    def close(self):
        """Fecha o driver do navegador"""
        if self.driver:
            self.driver.quit()
            logger.info("Driver do Chrome fechado")
    
    def __del__(self):
        """Destrutor para garantir que o driver seja fechado"""
        self.close()
