#!/usr/bin/env python3
"""
Teste do bilhete cbeo1c com otimizações de tempo
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
        logging.FileHandler(f'logs/test_cbeo1c_{int(time.time())}.log')
    ]
)

logger = logging.getLogger(__name__)

def test_bilhete_cbeo1c():
    """Teste do bilhete cbeo1c com otimizações"""
    
    logger.info("🚀 TESTE BILHETE cbeo1c - OTIMIZADO")
    logger.info("=" * 60)
    
    scraper = None
    start_time = time.time()
    
    try:
        # Inicializar scraper
        scraper = ValSportsScraper()
        
        # Fazer login
        logger.info("🔐 Fazendo login...")
        login_start = time.time()
        if not scraper.login("cairovinicius", "279999"):
            logger.error("❌ Falha no login")
            return False
        login_time = time.time() - login_start
        logger.info(f"✅ Login realizado em {login_time:.2f}s")
        
        # Capturar dados do bilhete
        bet_code = "cbeo1c"
        logger.info(f"📊 Capturando dados do bilhete {bet_code}...")
        capture_start = time.time()
        
        result = scraper.scrape_bet_ticket(bet_code)
        capture_time = time.time() - capture_start
        
        if not result:
            logger.error("❌ Falha na captura dos dados")
            return False
        
        logger.info(f"✅ Dados capturados em {capture_time:.2f}s")
        logger.info(f"   🎮 Jogos: {len(result.get('games', []))}")
        logger.info(f"   💰 Odds: {result.get('total_odds', 'N/A')}")
        logger.info(f"   🏆 Prêmio: {result.get('possible_prize', 'N/A')}")
        
        # Salvar resultado
        timestamp = int(time.time())
        filename = f"result_{bet_code}_{timestamp}.json"
        import json
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        logger.info(f"💾 Resultado salvo em: {filename}")
        
        # Testar confirmação
        logger.info(f"🎯 Testando confirmação do bilhete {bet_code}...")
        logger.info("⚠️ ATENÇÃO: Este teste pode gerar pop-up de mudança de odds")
        
        confirm_start = time.time()
        confirmation_success = scraper.confirm_bet(bet_code)
        confirm_time = time.time() - confirm_start
        
        total_time = time.time() - start_time
        
        # Resumo
        logger.info("=" * 60)
        logger.info("📋 RESUMO DO TESTE")
        logger.info("=" * 60)
        logger.info(f"🎫 Bilhete: {bet_code}")
        logger.info(f"📥 Captura: Sucesso ({capture_time:.2f}s)")
        logger.info(f"🎮 Jogos: {len(result.get('games', []))}")
        logger.info(f"📈 Odds: {result.get('total_odds', 'N/A')}")
        logger.info(f"🏆 Prêmio: {result.get('possible_prize', 'N/A')}")
        logger.info(f"✅ Confirmação: {'Sucesso' if confirmation_success else 'Falha'} ({confirm_time:.2f}s)")
        logger.info(f"⏱️ Tempo total: {total_time:.2f}s")
        logger.info("=" * 60)
        
        if confirmation_success:
            logger.info("✅ TESTE CONCLUÍDO COM SUCESSO")
        else:
            logger.info("⚠️ TESTE FALHOU NA CONFIRMAÇÃO")
        
        return confirmation_success
        
    except Exception as e:
        logger.error(f"❌ Erro no teste: {str(e)}")
        return False
    finally:
        if scraper:
            scraper.close()

if __name__ == "__main__":
    success = test_bilhete_cbeo1c()
    
    if success:
        print("\n🎉 TESTE CONCLUÍDO COM SUCESSO!")
    else:
        print("\n❌ TESTE FALHOU!")
