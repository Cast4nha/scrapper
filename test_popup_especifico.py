#!/usr/bin/env python3
"""
Teste específico para pop-up de mudança de odds
"""

import sys
import os
import time
import logging
from datetime import datetime

# Adicionar o diretório do scraper ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'scraper'))

from valsports_scraper_final import ValSportsScraper

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:%(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f'logs/test_popup_especifico_{int(time.time())}.log')
    ]
)

logger = logging.getLogger(__name__)

def test_popup_odds_change():
    """Teste específico para pop-up de mudança de odds"""
    
    logger.info("🚀 TESTE ESPECÍFICO POP-UP MUDANÇA DE ODDS")
    logger.info("=" * 60)
    
    scraper = None
    
    try:
        # Inicializar scraper
        scraper = ValSportsScraper()
        
        # Fazer login
        logger.info("🔐 Fazendo login...")
        if not scraper.login("cairovinicius", "279999"):
            logger.error("❌ Falha no login")
            return False
        
        logger.info("✅ Login realizado com sucesso")
        
        # Navegar para o bilhete
        bet_code = "spysgp"
        logger.info(f"🌐 Navegando para bilhete: {bet_code}")
        scraper.driver.get(f"{scraper.base_url}/prebet/{bet_code}")
        time.sleep(3)
        
        # Procurar botão de confirmação
        logger.info("🔍 Procurando botão de confirmação...")
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        
        wait = WebDriverWait(scraper.driver, 10)
        
        # Botão de confirmação
        confirm_selectors = [
            ".btn-group > .text-style",
            "//a[contains(text(), 'Apostar')]",
            "//button[contains(text(), 'Apostar')]"
        ]
        
        confirm_button = None
        for selector in confirm_selectors:
            try:
                if selector.startswith("/"):
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
        
        # Clicar no botão de confirmação
        logger.info("🖱️ Clicando no botão de confirmação...")
        confirm_button.click()
        time.sleep(3)
        
        # Aguardar e procurar primeiro pop-up
        logger.info("🔍 Procurando primeiro pop-up...")
        first_popup_selectors = [
            "//a[contains(text(),'Sim')]",
            "//button[contains(text(),'Sim')]",
            "//a[contains(text(),'SIM')]",
            "//button[contains(text(),'SIM')]"
        ]
        
        first_yes_button = None
        for selector in first_popup_selectors:
            try:
                first_yes_button = wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                logger.info(f"✅ Primeiro pop-up encontrado: {selector}")
                break
            except:
                continue
        
        if first_yes_button:
            logger.info("🖱️ Clicando no primeiro 'Sim'...")
            first_yes_button.click()
            time.sleep(5)  # Aguardar mais tempo para o segundo pop-up aparecer
        
        # Procurar pop-up de mudança de odds
        logger.info("🔍 Procurando pop-up de mudança de odds...")
        
        # Aguardar um pouco mais para o pop-up aparecer
        time.sleep(3)
        
        # Seletores específicos para o pop-up de mudança de odds
        odds_popup_selectors = [
            "/html/body/div[3]/div/div[2]/div[3]/a[2]",  # XPath específico
            "a.v-dialog-btn:nth-child(2)",  # CSS específico
            "//div[contains(text(), 'Mudança de prêmio')]//following-sibling::*//a[contains(text(), 'SIM')]",
            "//div[contains(text(), 'Deseja continuar?')]//following-sibling::*//a[contains(text(), 'SIM')]",
            "//a[contains(@class, 'v-dialog-btn') and contains(text(), 'SIM')]",
            "//a[contains(@class, 'v-dialog-btn') and contains(text(), 'Sim')]"
        ]
        
        odds_yes_button = None
        for selector in odds_popup_selectors:
            try:
                if selector.startswith("/"):
                    odds_yes_button = wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                else:
                    odds_yes_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                logger.info(f"✅ Pop-up de mudança de odds encontrado: {selector}")
                break
            except:
                continue
        
        if odds_yes_button:
            logger.info("🖱️ Clicando no 'SIM' do pop-up de mudança de odds...")
            odds_yes_button.click()
            time.sleep(5)
            
            # Verificar se foi confirmado
            logger.info("🔍 Verificando confirmação...")
            scraper.driver.get(f"{scraper.base_url}/bets")
            time.sleep(3)
            
            try:
                no_bets_element = scraper.driver.find_element(By.XPATH, "//*[contains(text(), 'Nenhuma aposta encontrada')]")
                if no_bets_element:
                    logger.error("❌ Nenhuma aposta encontrada - confirmação falhou")
                    return False
                else:
                    logger.info("✅ Apostas encontradas - confirmação bem-sucedida")
                    return True
            except:
                logger.info("✅ Apostas encontradas - confirmação bem-sucedida")
                return True
        else:
            logger.warning("⚠️ Pop-up de mudança de odds não encontrado")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erro no teste: {str(e)}")
        return False
    finally:
        if scraper:
            scraper.close()

if __name__ == "__main__":
    success = test_popup_odds_change()
    
    logger.info("=" * 60)
    if success:
        logger.info("✅ TESTE CONCLUÍDO COM SUCESSO")
    else:
        logger.info("❌ TESTE FALHOU")
    logger.info("=" * 60)
