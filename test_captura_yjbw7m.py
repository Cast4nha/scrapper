#!/usr/bin/env python3
"""
Teste específico de CAPTURA DE DADOS do bilhete yjbw7m
Foco apenas na extração de dados, sem confirmação
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
        logging.FileHandler(f'logs/test_captura_yjbw7m_{int(time.time())}.log')
    ]
)

logger = logging.getLogger(__name__)

def test_captura_yjbw7m():
    """Teste específico de captura de dados do bilhete yjbw7m"""
    
    logger.info("🚀 TESTE CAPTURA DE DADOS - yjbw7m")
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
        bet_code = "yjbw7m"
        logger.info(f"📊 Capturando dados do bilhete {bet_code}...")
        capture_start = time.time()
        
        result = scraper.scrape_bet_ticket(bet_code)
        capture_time = time.time() - capture_start
        
        if not result:
            logger.error("❌ Falha na captura dos dados")
            return False
        
        logger.info(f"✅ Dados capturados em {capture_time:.2f}s")
        
        # Análise detalhada dos dados
        games = result.get('games', [])
        total_games = result.get('total_games', 0)
        
        logger.info("=" * 60)
        logger.info("📋 ANÁLISE DETALHADA DOS DADOS")
        logger.info("=" * 60)
        logger.info(f"🎫 Bilhete: {bet_code}")
        logger.info(f"📊 Total de jogos (contador): {total_games}")
        logger.info(f"🎮 Jogos extraídos: {len(games)}")
        logger.info(f"💰 Odds: {result.get('total_odds', 'N/A')}")
        logger.info(f"🏆 Prêmio: {result.get('possible_prize', 'N/A')}")
        logger.info(f"👤 Apostador: {result.get('bettor_name', 'N/A')}")
        logger.info(f"💵 Valor: {result.get('bet_value', 'N/A')}")
        
        # Verificar se todos os jogos foram extraídos
        if len(games) != total_games:
            logger.warning(f"⚠️ PROBLEMA: Extraídos {len(games)} de {total_games} jogos")
        else:
            logger.info(f"✅ SUCESSO: Todos os {total_games} jogos foram extraídos")
        
        # Mostrar detalhes de cada jogo
        logger.info("=" * 60)
        logger.info("🎮 DETALHES DOS JOGOS EXTRAÍDOS")
        logger.info("=" * 60)
        for i, game in enumerate(games, 1):
            logger.info(f"Jogo {i}:")
            logger.info(f"  🏆 Liga: {game.get('league', 'N/A')}")
            logger.info(f"  🏠 Casa: {game.get('home_team', 'N/A')}")
            logger.info(f"  🚌 Fora: {game.get('away_team', 'N/A')}")
            logger.info(f"  ⏰ Data/Hora: {game.get('datetime', 'N/A')}")
            logger.info(f"  🎯 Seleção: {game.get('selection', 'N/A')}")
            logger.info(f"  📈 Odds: {game.get('odds', 'N/A')}")
            logger.info("")
        
        # Salvar resultado
        timestamp = int(time.time())
        filename = f"result_{bet_code}_{timestamp}.json"
        import json
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        logger.info(f"💾 Resultado salvo em: {filename}")
        
        total_time = time.time() - start_time
        
        # Resumo final
        logger.info("=" * 60)
        logger.info("📋 RESUMO FINAL")
        logger.info("=" * 60)
        logger.info(f"⏱️ Tempo total: {total_time:.2f}s")
        logger.info(f"🔐 Login: {login_time:.2f}s")
        logger.info(f"📊 Captura: {capture_time:.2f}s")
        logger.info(f"🎮 Jogos extraídos: {len(games)}/{total_games}")
        
        if len(games) == total_games:
            logger.info("✅ TESTE DE CAPTURA CONCLUÍDO COM SUCESSO")
            return True
        else:
            logger.info("⚠️ TESTE DE CAPTURA CONCLUÍDO COM PROBLEMAS")
            return False
        
    except Exception as e:
        logger.error(f"❌ Erro no teste: {str(e)}")
        return False
    finally:
        if scraper:
            scraper.close()

if __name__ == "__main__":
    success = test_captura_yjbw7m()
    
    if success:
        print("\n🎉 CAPTURA DE DADOS CONCLUÍDA COM SUCESSO!")
    else:
        print("\n⚠️ CAPTURA DE DADOS CONCLUÍDA COM PROBLEMAS!")
