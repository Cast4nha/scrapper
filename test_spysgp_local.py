#!/usr/bin/env python3
"""
Teste Local do Bilhete spysgp
Executa diretamente o scraper local para testar o bilhete
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

def test_bilhete_spysgp():
    """Testa o bilhete spysgp localmente"""
    start_time = time.time()
    scraper = None
    
    try:
        logger.info("🚀 TESTE LOCAL: Iniciando captura do bilhete spysgp")
        
        # Criar instância do scraper
        scraper = ValSportsScraper()
        
        # Fazer login
        username = os.getenv('VALSORTS_USERNAME', 'cairovinicius')
        password = os.getenv('VALSORTS_PASSWORD', '279999')
        
        logger.info("🔐 Fazendo login...")
        login_success = scraper.login(username, password)
        
        if not login_success:
            logger.error("❌ Falha no login")
            return False
        
        logger.info("✅ Login realizado com sucesso")
        
        # Capturar dados do bilhete
        logger.info("📊 Capturando dados do bilhete spysgp...")
        bet_data = scraper.scrape_bet_ticket("spysgp")
        
        if not bet_data:
            logger.error("❌ Falha ao capturar dados do bilhete")
            return False
        
        # Calcular tempo de execução
        execution_time = time.time() - start_time
        
        # Mostrar resultados
        logger.info("=" * 60)
        logger.info("📋 RESULTADOS DO TESTE LOCAL - BILHETE spysgp")
        logger.info("=" * 60)
        
        logger.info(f"✅ Bilhete: {bet_data.get('bet_code', 'spysgp')}")
        logger.info(f"💰 Valor: {bet_data.get('bet_value', 'N/A')}")
        logger.info(f"👤 Apostador: {bet_data.get('bettor_name', 'N/A')}")
        logger.info(f"🎮 Total de Jogos: {bet_data.get('total_games', 0)}")
        logger.info(f"📈 Odds Totais: {bet_data.get('total_odds', 'N/A')}")
        logger.info(f"🏆 Prêmio: {bet_data.get('possible_prize', 'N/A')}")
        logger.info(f"⏱️ Tempo: {execution_time:.2f}s")
        
        # Mostrar detalhes dos jogos
        games = bet_data.get('games', [])
        if games:
            logger.info(f"\n🎮 DETALHES DOS {len(games)} JOGOS:")
            for i, game in enumerate(games, 1):
                logger.info(f"  Jogo {i}:")
                logger.info(f"    Times: {game.get('teams', 'N/A')}")
                logger.info(f"    Liga: {game.get('league', 'N/A')}")
                logger.info(f"    Data/Hora: {game.get('datetime', 'N/A')}")
                logger.info(f"    Odds: {game.get('odds_list', [])}")
                logger.info(f"    Seleções: {game.get('selections', [])}")
                logger.info("")
        else:
            logger.warning("⚠️ Nenhum jogo encontrado!")
        
        # Salvar resultado em arquivo
        result_file = f"result_spysgp_{int(time.time())}.json"
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump({
                'success': True,
                'bet_code': 'spysgp',
                'data': bet_data,
                'execution_time': f"{execution_time:.2f}s",
                'message': 'Dados capturados com sucesso',
                'status': 'success'
            }, f, indent=2, ensure_ascii=False)
        
        logger.info(f"💾 Resultado salvo em: {result_file}")
        logger.info("=" * 60)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro durante teste: {str(e)}")
        return False
    finally:
        if scraper:
            scraper.close()

def main():
    """Função principal"""
    print("🚀 TESTE LOCAL DO BILHETE spysgp")
    print("=" * 60)
    
    success = test_bilhete_spysgp()
    
    if success:
        print("✅ TESTE CONCLUÍDO COM SUCESSO!")
    else:
        print("❌ TESTE FALHOU!")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
