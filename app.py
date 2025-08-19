from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
from scraper.valsports_scraper import ValSportsScraper
import logging

# Carregar variáveis de ambiente
load_dotenv()

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuração de CORS
CORS(app)

# Tratamento de erros global
@app.errorhandler(Exception)
def handle_exception(e):
    """Tratamento global de exceções"""
    return jsonify({
        'error': 'Internal Server Error',
        'message': str(e),
        'status': 'error'
    }), 500

@app.errorhandler(404)
def not_found(e):
    """Tratamento de 404"""
    return jsonify({
        'error': 'Not Found',
        'message': 'Endpoint não encontrado',
        'status': 'error'
    }), 404

# Inicializar o scraper
scraper = None

def get_scraper():
    """Singleton para o scraper"""
    global scraper
    if scraper is None:
        scraper = ValSportsScraper()
    return scraper

@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint de verificação de saúde da API"""
    return jsonify({
        'status': 'healthy',
        'service': 'valsports-scraper-api',
        'version': '1.0.0',
        'timestamp': '2025-08-19 15:05:00'
    })

@app.route('/', methods=['GET'])
def root():
    """Endpoint raiz para teste"""
    return jsonify({
        'message': 'ValSports Scraper API',
        'status': 'running',
        'endpoints': {
            'health': '/health',
            'scrape_bet': '/api/scrape-bet',
            'login': '/api/login',
            'confirm_bet': '/api/confirm-bet'
        }
    })

@app.route('/test', methods=['GET'])
def test_endpoint():
    """Endpoint de teste simples sem dependências"""
    return jsonify({
        'status': 'success',
        'message': 'API está funcionando!',
        'timestamp': '2025-08-19 15:07:00',
        'service': 'valsports-scraper-api'
    })

@app.route('/ping', methods=['GET'])
def ping():
    """Endpoint ping simples"""
    return jsonify({'pong': True})

@app.route('/api/scrape-bet', methods=['POST'])
def scrape_bet():
    """Endpoint para capturar dados de um bilhete específico"""
    try:
        data = request.get_json()
        
        if not data or 'bet_code' not in data:
            return jsonify({
                'success': False,
                'error': 'Código do bilhete é obrigatório'
            }), 400
        
        bet_code = data['bet_code']
        logger.info(f"Recebida requisição para capturar bilhete: {bet_code}")
        
        # Obter instância do scraper
        scraper_instance = get_scraper()
        
        # Capturar dados do bilhete
        bet_data = scraper_instance.scrape_bet_ticket(bet_code)
        
        if bet_data:
            return jsonify({
                'success': True,
                'data': bet_data
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Não foi possível capturar os dados do bilhete'
            }), 404
            
    except Exception as e:
        logger.error(f"Erro ao capturar bilhete: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        }), 500

@app.route('/api/login', methods=['POST'])
def login():
    """Endpoint para fazer login no sistema"""
    try:
        data = request.get_json()
        
        if not data or 'username' not in data or 'password' not in data:
            return jsonify({
                'success': False,
                'error': 'Usuário e senha são obrigatórios'
            }), 400
        
        username = data['username']
        password = data['password']
        
        logger.info(f"Tentativa de login para usuário: {username}")
        
        # Obter instância do scraper
        scraper_instance = get_scraper()
        
        # Fazer login
        login_success = scraper_instance.login(username, password)
        
        if login_success:
            return jsonify({
                'success': True,
                'message': 'Login realizado com sucesso'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Credenciais inválidas'
            }), 401
            
    except Exception as e:
        logger.error(f"Erro no login: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        }), 500

@app.route('/api/confirm-bet', methods=['POST'])
def confirm_bet():
    """Endpoint para confirmar uma aposta"""
    try:
        data = request.get_json()
        
        if not data or 'bet_code' not in data:
            return jsonify({
                'success': False,
                'error': 'Código do bilhete é obrigatório'
            }), 400
        
        bet_code = data['bet_code']
        
        logger.info(f"Confirmando aposta: {bet_code}")
        
        # Obter instância do scraper
        scraper_instance = get_scraper()
        
        # Confirmar aposta
        confirmation_success = scraper_instance.confirm_bet(bet_code)
        
        if confirmation_success:
            return jsonify({
                'success': True,
                'message': 'Aposta confirmada com sucesso',
                'bet_code': bet_code,
                'status': 'confirmed'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Não foi possível confirmar a aposta'
            }), 400
            
    except Exception as e:
        logger.error(f"Erro ao confirmar aposta: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    # Configurar para aceitar tanto HTTP quanto HTTPS
    app.run(
        host='0.0.0.0', 
        port=port, 
        debug=debug,
        threaded=True,
        use_reloader=False
    )
