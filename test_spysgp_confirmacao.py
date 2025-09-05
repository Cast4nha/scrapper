#!/usr/bin/env python3
"""
Teste de Confirmação do Bilhete spysgp
Testa especificamente a confirmação com pop-up de mudança de odds
"""

import time
import logging
import json
import os
from dotenv import load_dotenv
from scraper.valsports_scraper_final import ValSportsScraper

# Carregar variáveis de ambiente
load_dotenv()

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(message)s')
logger = logging.getLogger(__name__)

def test_spysgp_confirmacao():
    """Testa confirmação do bilhete spysgp com pop-up de mudança de odds"""
    start_time = time.time()
    scraper = None
    
    try:
        logger.info("🚀 TESTE CONFIRMAÇÃO BILHETE spysgp")
        logger.info("=" * 60)
        
        # Criar instância do scraper
        scraper = ValSportsScraper()
        
        # Fazer login
        username = os.getenv('VALSORTS_USERNAME', 'cairovinicius')
        password = os.getenv('VALSORTS_PASSWORD', '279999')
        
        logger.info("🔐 Fazendo login...")
        if not scraper.login(username, password):
            logger.error("❌ Falha no login")
            return False
        
        logger.info("✅ Login realizado com sucesso")
        
        # Capturar dados do bilhete primeiro
        logger.info("📊 Capturando dados do bilhete spysgp...")
        bet_data = scraper.scrape_bet_ticket('spysgp')
        
        if bet_data:
            logger.info("✅ Dados capturados com sucesso")
            logger.info(f"   🎮 Jogos: {bet_data.get('total_games', 0)}")
            logger.info(f"   💰 Odds: {bet_data.get('total_odds', 'N/A')}")
            logger.info(f"   🏆 Prêmio: {bet_data.get('possible_prize', 'N/A')}")
        else:
            logger.error("❌ Falha na captura dos dados")
            return False
        
        # Testar confirmação
        logger.info("🎯 Testando confirmação do bilhete spysgp...")
        logger.info("⚠️ ATENÇÃO: Este teste pode gerar pop-up de mudança de odds")
        
        confirmacao = scraper.confirm_bet('spysgp')
        
        if confirmacao:
            logger.info("✅ Confirmação do bilhete spysgp bem-sucedida")
            status = "Confirmado"
        else:
            logger.warning("⚠️ Falha na confirmação do bilhete spysgp")
            status = "Falha na confirmação"
        
        # Calcular tempo total
        execution_time = time.time() - start_time
        
        # Exibir resumo
        logger.info("=" * 60)
        logger.info("📋 RESUMO DO TESTE DE CONFIRMAÇÃO")
        logger.info("=" * 60)
        logger.info(f"🎫 Bilhete: spysgp")
        logger.info(f"📥 Captura: Sucesso")
        logger.info(f"🎮 Jogos: {bet_data.get('total_games', 0)}")
        logger.info(f"📈 Odds: {bet_data.get('total_odds', 'N/A')}")
        logger.info(f"🏆 Prêmio: {bet_data.get('possible_prize', 'N/A')}")
        logger.info(f"✅ Confirmação: {status}")
        logger.info(f"⏱️ Tempo: {execution_time:.2f}s")
        logger.info("=" * 60)
        
        if confirmacao:
            logger.info("✅ TESTE DE CONFIRMAÇÃO CONCLUÍDO COM SUCESSO!")
        else:
            logger.info("⚠️ TESTE DE CONFIRMAÇÃO FALHOU - Verificar logs")
        
        logger.info("=" * 60)
        
        return confirmacao
        
    except Exception as e:
        logger.error(f"❌ Erro durante o teste: {str(e)}")
        return False
        
    finally:
        if scraper:
            scraper.close()
            logger.info("🔒 Driver fechado")

if __name__ == "__main__":
    test_spysgp_confirmacao()
