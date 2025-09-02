#!/usr/bin/env python3
"""
Serviço Final de Captura de Dados ValSports
Baseado na implementação funcional do commit b2cc471
"""

import time
import logging
import json
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
from dotenv import load_dotenv
from scraper.valsports_scraper_final import ValSportsScraper

# Carregar variáveis de ambiente
load_dotenv()

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

class ValSportsCaptureService:
    """Serviço de captura baseado na implementação funcional"""
    
    def __init__(self):
        self.username = os.getenv('VALSPORTS_USERNAME', 'cairovinicius')
        self.password = os.getenv('VALSPORTS_PASSWORD', '279999')
        
    def capture_bet_data(self, bet_code: str) -> dict:
        """Captura dados de uma aposta usando a implementação funcional"""
        start_time = time.time()
        scraper = None
        
        try:
            logger.info(f"🎯 Capturando dados do bilhete: {bet_code}")
            
            # 1. Criar instância do scraper
            scraper = ValSportsScraper()
            
            # 2. Fazer login
            logger.info("🔐 Fazendo login no sistema...")
            login_success = scraper.login(self.username, self.password)
            
            if not login_success:
                return {
                    'success': False,
                    'error': 'Falha na autenticação',
                    'message': 'Credenciais inválidas ou erro no login'
                }
            
            # 3. Capturar dados do bilhete
            logger.info(f"🌐 Capturando dados do bilhete: {bet_code}")
            bet_data = scraper.scrape_bet_ticket(bet_code)
            
            if not bet_data:
                return {
                    'success': False,
                    'error': 'Falha na captura',
                    'message': f'Não foi possível capturar dados do bilhete {bet_code}'
                }
            
            # 4. Calcular tempo de execução
            execution_time = f"{time.time() - start_time:.2f}s"
            
            # 5. Formatar resposta no formato especificado
            formatted_data = self._format_response_data(bet_data, bet_code)
            
            logger.info(f"✅ Dados capturados com sucesso em {execution_time}")
            
            return {
                'success': True,
                'bet_code': bet_code,
                'data': formatted_data,
                'execution_time': execution_time,
                'message': 'Dados capturados com sucesso',
                'status': 'success'
            }
            
        except Exception as e:
            logger.error(f"❌ Erro durante captura: {str(e)}")
            execution_time = f"{time.time() - start_time:.2f}s"
            return {
                'success': False,
                'bet_code': bet_code,
                'error': str(e),
                'message': 'Erro interno durante captura',
                'execution_time': execution_time
            }
        finally:
            if scraper:
                try:
                    scraper.close()
                except:
                    pass
    
    def _format_response_data(self, bet_data: dict, bet_code: str) -> dict:
        """Formata os dados para o formato especificado"""
        try:
            # Estrutura base
            formatted_data = {
                "bet_code": bet_code,
                "bet_value": bet_data.get('bet_value', 'R$ 2,00'),
                "bettor_name": bet_data.get('bettor_name', 'Usuário'),
                "games": [],
                "possible_prize": bet_data.get('possible_prize', 'R$ 0,00'),
                "total_games": bet_data.get('total_games', 0),
                "total_odds": bet_data.get('total_odds', '0,00')
            }
            
            # Formatar jogos
            if 'games' in bet_data and bet_data['games']:
                for game in bet_data['games']:
                    formatted_game = {
                        "away_team": game.get('away_team', ''),
                        "datetime": game.get('datetime', ''),
                        "game_number": game.get('game_number', 0),
                        "home_team": game.get('home_team', ''),
                        "league": game.get('league', ''),
                        "odds_list": [game.get('odds', '1.00')] if game.get('odds') else ['1.00'],
                        "selections": [game.get('selection', '')] if game.get('selection') else [],
                        "teams": f"{game.get('home_team', '')} x {game.get('away_team', '')}" if game.get('home_team') and game.get('away_team') else ''
                    }
                    formatted_data['games'].append(formatted_game)
            
            return formatted_data
            
        except Exception as e:
            logger.error(f"❌ Erro ao formatar dados: {str(e)}")
            return {
                "bet_code": bet_code,
                "bet_value": "R$ 2,00",
                "bettor_name": "Usuário",
                "games": [],
                "possible_prize": "R$ 0,00",
                "total_games": 0,
                "total_odds": "0,00"
            }

# Instanciar o serviço
capture_service = ValSportsCaptureService()

# Configurar Flask
app = Flask(__name__)
CORS(app)

@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint de verificação de saúde da API"""
    return jsonify({
        'status': 'healthy',
        'service': 'ValSports Capture Service (Final)',
        'implementation': 'Based on commit b2cc471',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/capture/<bet_code>', methods=['POST'])
def capture_bet(bet_code):
    """Endpoint para capturar dados de uma aposta"""
    try:
        # Obter dados adicionais do body (opcional)
        capture_data = request.get_json() if request.is_json else {}
        
        logger.info(f"🎯 Capturando dados do bilhete: {bet_code}")
        
        # Capturar dados via scraper funcional
        result = capture_service.capture_bet_data(bet_code)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"❌ Erro no endpoint capture_bet: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Erro interno do servidor'
        }), 500

@app.route('/capture/<bet_code>', methods=['GET'])
def capture_bet_get(bet_code):
    """Endpoint GET para capturar dados de uma aposta"""
    try:
        logger.info(f"🎯 Capturando dados do bilhete (GET): {bet_code}")
        
        # Capturar dados via scraper funcional
        result = capture_service.capture_bet_data(bet_code)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"❌ Erro no endpoint capture_bet_get: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Erro interno do servidor'
        }), 500

@app.route('/api/capture-bet', methods=['POST'])
def api_capture_bet():
    """Endpoint compatível com a implementação original"""
    try:
        data = request.get_json()
        
        if not data or 'bet_code' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Código do bilhete é obrigatório'
            }), 400
        
        bet_code = data['bet_code']
        logger.info(f"🎯 Capturando bilhete via API: {bet_code}")
        
        # Capturar dados via scraper funcional
        result = capture_service.capture_bet_data(bet_code)
        
        if result['success']:
            return jsonify({
                'status': 'success',
                'bet_code': bet_code,
                'data': result['data'],
                'message': 'Dados capturados com sucesso',
                'execution_time': result['execution_time']
            })
        else:
            return jsonify({
                'status': 'error',
                'message': result.get('message', 'Falha na captura')
            }), 404
        
    except Exception as e:
        logger.error(f"❌ Erro no endpoint api_capture_bet: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Erro interno: {str(e)}'
        }), 500

if __name__ == '__main__':
    logger.info("🚀 Iniciando ValSports Capture Service (Final)...")
    logger.info("📋 Baseado na implementação funcional do commit b2cc471")
    
    # Configurações para produção
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'false').lower() == 'true'
    
    logger.info(f"🌐 Serviço rodando na porta: {port}")
    logger.info(f"🔧 Modo debug: {debug}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
