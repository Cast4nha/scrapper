#!/usr/bin/env python3
"""
Teste de Múltiplos Bilhetes com Confirmação
Testa captura e confirmação de múltiplos bilhetes simultaneamente
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

def test_multiplos_bilhetes():
    """Testa múltiplos bilhetes com confirmação"""
    start_time = time.time()
    scraper = None
    
    # Lista de bilhetes para testar
    bilhetes = ['ebg2cq', 'spysgp']
    
    try:
        logger.info("🚀 TESTE MÚLTIPLOS BILHETES: Iniciando captura e confirmação")
        logger.info(f"📋 Bilhetes: {', '.join(bilhetes)}")
        
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
        
        resultados = {}
        
        # Processar cada bilhete
        for i, bilhete in enumerate(bilhetes, 1):
            logger.info(f"📊 Processando bilhete {i}/{len(bilhetes)}: {bilhete}")
            
            # Capturar dados do bilhete
            logger.info(f"🔍 Capturando dados do bilhete {bilhete}...")
            bet_data = scraper.scrape_bet_ticket(bilhete)
            
            if bet_data:
                logger.info(f"✅ Bilhete {bilhete} capturado com sucesso")
                logger.info(f"   🎮 Jogos: {bet_data.get('total_games', 0)}")
                logger.info(f"   💰 Odds: {bet_data.get('total_odds', 'N/A')}")
                logger.info(f"   🏆 Prêmio: {bet_data.get('possible_prize', 'N/A')}")
                
                # Salvar dados capturados
                timestamp = int(time.time())
                filename = f"capture_{bilhete}_{timestamp}.json"
                
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump({
                        'success': True,
                        'bet_code': bilhete,
                        'data': bet_data,
                        'timestamp': timestamp,
                        'message': 'Dados capturados com sucesso'
                    }, f, indent=2, ensure_ascii=False)
                
                logger.info(f"💾 Dados salvos em: {filename}")
                
                # Testar confirmação
                logger.info(f"🎯 Testando confirmação do bilhete {bilhete}...")
                confirmacao = scraper.confirm_bet(bilhete)
                
                if confirmacao:
                    logger.info(f"✅ Confirmação do bilhete {bilhete} bem-sucedida")
                    status_confirmacao = "Confirmado"
                else:
                    logger.warning(f"⚠️ Falha na confirmação do bilhete {bilhete}")
                    status_confirmacao = "Falha na confirmação"
                
                resultados[bilhete] = {
                    'captura': 'Sucesso',
                    'jogos': bet_data.get('total_games', 0),
                    'odds': bet_data.get('total_odds', 'N/A'),
                    'premio': bet_data.get('possible_prize', 'N/A'),
                    'confirmacao': status_confirmacao,
                    'arquivo': filename
                }
                
            else:
                logger.error(f"❌ Falha na captura do bilhete {bilhete}")
                resultados[bilhete] = {
                    'captura': 'Falha',
                    'jogos': 0,
                    'odds': 'N/A',
                    'premio': 'N/A',
                    'confirmacao': 'Não testado',
                    'arquivo': 'N/A'
                }
            
            # Pausa entre bilhetes para evitar sobrecarga
            if i < len(bilhetes):
                logger.info("⏳ Aguardando 5 segundos antes do próximo bilhete...")
                time.sleep(5)
        
        # Calcular tempo total
        execution_time = time.time() - start_time
        
        # Exibir resumo final
        logger.info("=" * 80)
        logger.info("📋 RESUMO FINAL - TESTE MÚLTIPLOS BILHETES")
        logger.info("=" * 80)
        logger.info(f"⏱️ Tempo total: {execution_time:.2f}s")
        logger.info(f"📊 Bilhetes processados: {len(bilhetes)}")
        logger.info("")
        
        for bilhete, resultado in resultados.items():
            logger.info(f"🎫 Bilhete: {bilhete}")
            logger.info(f"   📥 Captura: {resultado['captura']}")
            logger.info(f"   🎮 Jogos: {resultado['jogos']}")
            logger.info(f"   📈 Odds: {resultado['odds']}")
            logger.info(f"   🏆 Prêmio: {resultado['premio']}")
            logger.info(f"   ✅ Confirmação: {resultado['confirmacao']}")
            logger.info(f"   💾 Arquivo: {resultado['arquivo']}")
            logger.info("")
        
        # Salvar resumo geral
        resumo_filename = f"resumo_multiplos_bilhetes_{int(time.time())}.json"
        with open(resumo_filename, 'w', encoding='utf-8') as f:
            json.dump({
                'success': True,
                'bilhetes_testados': bilhetes,
                'resultados': resultados,
                'execution_time': f"{execution_time:.2f}s",
                'timestamp': int(time.time()),
                'message': 'Teste de múltiplos bilhetes concluído'
            }, f, indent=2, ensure_ascii=False)
        
        logger.info(f"💾 Resumo salvo em: {resumo_filename}")
        logger.info("=" * 80)
        logger.info("✅ TESTE MÚLTIPLOS BILHETES CONCLUÍDO COM SUCESSO!")
        logger.info("=" * 80)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro durante o teste: {str(e)}")
        return False
        
    finally:
        if scraper:
            scraper.close()
            logger.info("🔒 Driver fechado")

if __name__ == "__main__":
    test_multiplos_bilhetes()
