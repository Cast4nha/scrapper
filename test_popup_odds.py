#!/usr/bin/env python3
"""
Teste de Pop-up de Mudança de Odds
Testa múltiplas tentativas para verificar se o pop-up aparece consistentemente
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

def test_popup_odds():
    """Testa múltiplas tentativas para verificar pop-up de mudança de odds"""
    start_time = time.time()
    scraper = None
    
    # Número de tentativas
    tentativas = 3
    bilhete = 'spysgp'
    
    try:
        logger.info("🚀 TESTE POP-UP MUDANÇA DE ODDS")
        logger.info("=" * 60)
        logger.info(f"🎫 Bilhete: {bilhete}")
        logger.info(f"🔄 Tentativas: {tentativas}")
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
        
        resultados = []
        
        # Executar múltiplas tentativas
        for tentativa in range(1, tentativas + 1):
            logger.info(f"🔄 TENTATIVA {tentativa}/{tentativas}")
            logger.info("-" * 40)
            
            try:
                # Capturar dados do bilhete
                logger.info("📊 Capturando dados...")
                bet_data = scraper.scrape_bet_ticket(bilhete)
                
                if not bet_data:
                    logger.error("❌ Falha na captura dos dados")
                    resultados.append({
                        'tentativa': tentativa,
                        'captura': 'Falha',
                        'confirmacao': 'Não testado',
                        'popup': 'N/A'
                    })
                    continue
                
                logger.info("✅ Dados capturados")
                logger.info(f"   🎮 Jogos: {bet_data.get('total_games', 0)}")
                logger.info(f"   💰 Odds: {bet_data.get('total_odds', 'N/A')}")
                logger.info(f"   🏆 Prêmio: {bet_data.get('possible_prize', 'N/A')}")
                
                # Testar confirmação
                logger.info("🎯 Testando confirmação...")
                confirmacao = scraper.confirm_bet(bilhete)
                
                if confirmacao:
                    logger.info("✅ Confirmação bem-sucedida")
                    status_confirmacao = "Confirmado"
                    popup_detectado = "Não detectado"
                else:
                    logger.warning("⚠️ Falha na confirmação")
                    status_confirmacao = "Falha"
                    popup_detectado = "Possível pop-up"
                
                resultados.append({
                    'tentativa': tentativa,
                    'captura': 'Sucesso',
                    'jogos': bet_data.get('total_games', 0),
                    'odds': bet_data.get('total_odds', 'N/A'),
                    'premio': bet_data.get('possible_prize', 'N/A'),
                    'confirmacao': status_confirmacao,
                    'popup': popup_detectado
                })
                
            except Exception as e:
                logger.error(f"❌ Erro na tentativa {tentativa}: {str(e)}")
                resultados.append({
                    'tentativa': tentativa,
                    'captura': 'Erro',
                    'confirmacao': 'Erro',
                    'popup': 'N/A'
                })
            
            # Pausa entre tentativas
            if tentativa < tentativas:
                logger.info("⏳ Aguardando 10 segundos antes da próxima tentativa...")
                time.sleep(10)
        
        # Calcular tempo total
        execution_time = time.time() - start_time
        
        # Exibir resumo final
        logger.info("=" * 60)
        logger.info("📋 RESUMO FINAL - TESTE POP-UP ODDS")
        logger.info("=" * 60)
        logger.info(f"⏱️ Tempo total: {execution_time:.2f}s")
        logger.info(f"🔄 Tentativas: {tentativas}")
        logger.info("")
        
        for resultado in resultados:
            logger.info(f"🔄 Tentativa {resultado['tentativa']}:")
            logger.info(f"   📥 Captura: {resultado['captura']}")
            if resultado['captura'] == 'Sucesso':
                logger.info(f"   🎮 Jogos: {resultado['jogos']}")
                logger.info(f"   📈 Odds: {resultado['odds']}")
                logger.info(f"   🏆 Prêmio: {resultado['premio']}")
            logger.info(f"   ✅ Confirmação: {resultado['confirmacao']}")
            logger.info(f"   🚨 Pop-up: {resultado['popup']}")
            logger.info("")
        
        # Salvar resumo
        resumo_filename = f"resumo_popup_odds_{int(time.time())}.json"
        with open(resumo_filename, 'w', encoding='utf-8') as f:
            json.dump({
                'success': True,
                'bilhete': bilhete,
                'tentativas': tentativas,
                'resultados': resultados,
                'execution_time': f"{execution_time:.2f}s",
                'timestamp': int(time.time()),
                'message': 'Teste de pop-up de mudança de odds concluído'
            }, f, indent=2, ensure_ascii=False)
        
        logger.info(f"💾 Resumo salvo em: {resumo_filename}")
        logger.info("=" * 60)
        logger.info("✅ TESTE POP-UP ODDS CONCLUÍDO!")
        logger.info("=" * 60)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro durante o teste: {str(e)}")
        return False
        
    finally:
        if scraper:
            scraper.close()
            logger.info("🔒 Driver fechado")

if __name__ == "__main__":
    test_popup_odds()
