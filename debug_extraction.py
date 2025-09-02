#!/usr/bin/env python3
"""
Script de Debug para Extração de Jogos
Testa a extração diretamente para identificar problemas
"""

import time
import logging
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(message)s')
logger = logging.getLogger(__name__)

def debug_extraction():
    """Debug da extração de jogos"""
    driver = None
    
    try:
        logger.info("🔍 INICIANDO DEBUG DA EXTRAÇÃO")
        
        # Configurar driver
        firefox_options = Options()
        firefox_options.add_argument("--headless")
        firefox_options.add_argument("--no-sandbox")
        firefox_options.add_argument("--disable-dev-shm-usage")
        
        driver = webdriver.Firefox(options=firefox_options)
        driver.set_page_load_timeout(30)
        driver.implicitly_wait(10)
        
        # Fazer login
        logger.info("🔐 Fazendo login...")
        driver.get("https://www.valsports.net/login")
        time.sleep(3)
        
        username = os.getenv('VALSPORTS_USERNAME', 'cairovinicius')
        password = os.getenv('VALSPORTS_PASSWORD', '279999')
        
        username_field = driver.find_element(By.CSS_SELECTOR, ".form-group:nth-child(1) > .form-control")
        username_field.clear()
        username_field.send_keys(username)
        
        password_field = driver.find_element(By.CSS_SELECTOR, ".form-group:nth-child(2) > .form-control")
        password_field.clear()
        password_field.send_keys(password)
        
        login_button = driver.find_element(By.CSS_SELECTOR, ".btn-success")
        login_button.click()
        time.sleep(5)
        
        # Navegar para o bilhete
        bet_code = "7hfqpy"
        logger.info(f"🌐 Navegando para bilhete: {bet_code}")
        driver.get(f"https://www.valsports.net/prebet/{bet_code}")
        time.sleep(8)
        
        # Salvar screenshot e HTML para debug
        driver.save_screenshot(f"debug_{bet_code}.png")
        with open(f"debug_{bet_code}.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        
        logger.info("📸 Screenshot e HTML salvos para debug")
        
        # Testar extração de jogos
        logger.info("🎯 TESTANDO EXTRAÇÃO DE JOGOS")
        
        # 1. Encontrar elementos .l-item
        game_elements = driver.find_elements(By.CSS_SELECTOR, ".l-item")
        logger.info(f"🔍 Encontrados {len(game_elements)} elementos .l-item")
        
        # 2. Analisar cada elemento
        for i, element in enumerate(game_elements):
            try:
                text = element.text.strip()
                logger.info(f"📝 Elemento {i+1}: {text[:200]}...")
                
                # Verificar se tem times
                has_teams = ' x ' in text
                has_selection = any(keyword in text for keyword in ['Vencedor:', 'Empate', 'Ambas equipes marcam'])
                has_odds = bool(re.search(r'\b\d+\.\d+\b', text))
                
                logger.info(f"   ✅ Tem times: {has_teams}")
                logger.info(f"   ✅ Tem seleção: {has_selection}")
                logger.info(f"   ✅ Tem odds: {has_odds}")
                
                if has_teams and has_selection and has_odds:
                    logger.info(f"🎮 ELEMENTO VÁLIDO ENCONTRADO: {i+1}")
                    
                    # Extrair dados
                    game_data = extract_game_data(text, i+1)
                    if game_data:
                        logger.info(f"📊 Dados extraídos: {game_data}")
                
            except Exception as e:
                logger.error(f"❌ Erro ao analisar elemento {i+1}: {str(e)}")
        
        logger.info("✅ DEBUG CONCLUÍDO")
        
    except Exception as e:
        logger.error(f"❌ Erro durante debug: {str(e)}")
    finally:
        if driver:
            driver.quit()

def extract_game_data(full_text: str, game_number: int) -> dict:
    """Extrai dados de um jogo individual"""
    try:
        game_data = {
            'game_number': game_number,
            'home_team': '',
            'away_team': '',
            'teams': '',
            'league': '',
            'datetime': '',
            'odds_list': [],
            'selections': []
        }
        
        # Dividir em linhas
        lines = [line.strip() for line in full_text.split('\n') if line.strip()]
        
        # Extrair liga (primeira linha geralmente)
        if lines:
            game_data['league'] = lines[0]
            logger.info(f"   🏆 Liga: {game_data['league']}")
        
        # Extrair data/hora
        datetime_match = re.search(r'(\d{2}/\d{2}\s+\d{2}:\d{2})', full_text)
        if datetime_match:
            game_data['datetime'] = datetime_match.group(1)
            logger.info(f"   📅 Data/Hora: {game_data['datetime']}")
        
        # Extrair times (procurar por "Time x Time")
        teams_match = re.search(r'([A-Za-zÀ-ÿ\s]+(?:\s+[A-Za-zÀ-ÿ]+)*)\s+x\s+([A-Za-zÀ-ÿ\s]+(?:\s+[A-Za-zÀ-ÿ]+)*)', full_text)
        if teams_match:
            game_data['home_team'] = teams_match.group(1).strip()
            game_data['away_team'] = teams_match.group(2).strip()
            game_data['teams'] = f"{game_data['home_team']} x {game_data['away_team']}"
            logger.info(f"   ⚽ Times: {game_data['teams']}")
        
        # Extrair seleções
        if 'Vencedor:' in full_text:
            selection_match = re.search(r'Vencedor:\s*([A-Za-zÀ-ÿ\s]+)', full_text)
            if selection_match:
                selection = f"Vencedor: {selection_match.group(1).strip()}"
                game_data['selections'].append(selection)
                logger.info(f"   🎯 Seleção: {selection}")
        elif 'Empate' in full_text:
            game_data['selections'].append("Empate")
            logger.info(f"   🎯 Seleção: Empate")
        elif 'Ambas equipes marcam' in full_text:
            game_data['selections'].append("Ambas equipes marcam")
            logger.info(f"   🎯 Seleção: Ambas equipes marcam")
        
        # Extrair odds
        odds_matches = re.findall(r'\b(\d+\.\d+)\b', full_text)
        if odds_matches:
            game_data['odds_list'] = odds_matches
            logger.info(f"   📊 Odds: {odds_matches}")
        
        return game_data
        
    except Exception as e:
        logger.error(f"❌ Erro ao extrair dados do jogo {game_number}: {str(e)}")
        return None

if __name__ == "__main__":
    debug_extraction()
