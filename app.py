from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
from scraper.valsports_scraper_final import ValSportsScraper
import logging
import time
import threading
import uuid
from queue import Queue
import atexit

# Carregar variáveis de ambiente
load_dotenv()

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuração de CORS
CORS(app)

# Sistema de processamento sequencial simplificado
processing_lock = threading.Lock()
CACHE_TIMEOUT = 300  # 5 minutos
last_cleanup = time.time()

def get_scraper_instance():
    """Obtém uma instância única do scraper com lock para concorrência"""
    # Usar uma abordagem mais simples e robusta
    with processing_lock:
        # Criar uma nova instância para cada requisição (mais seguro)
        scraper = ValSportsScraper()
        return scraper

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

@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint de verificação de saúde da API"""
    return jsonify({
        'status': 'healthy',
        'service': 'valsports-scraper-api',
        'version': '2.1.0',
        'features': ['sequential_processing', 'thread_safe', 'concurrent_safe'],
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
    })

@app.route('/', methods=['GET'])
def root():
    """Endpoint raiz para teste"""
    return jsonify({
        'message': 'ValSports Scraper API v2.1',
        'status': 'running',
        'features': ['sequential_processing', 'thread_safe', 'concurrent_safe'],
        'endpoints': {
            'health': '/health',
            'scrape_bet': '/api/scrape-bet',
            'capture_bet': '/api/capture-bet',
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

def scrape_bet_worker(bet_code, session_id):
    """Worker function para scrape de bilhete"""
    try:
        logger.info(f"Capturando bilhete {bet_code} na sessão {session_id}")

        # Obter scraper para esta sessão
        scraper_instance, actual_session_id = get_or_create_scraper(session_id)

        # Capturar dados do bilhete
        bet_data = scraper_instance.scrape_bet_ticket(bet_code)

        if not bet_data:
            return {
                'success': False,
                'error': 'Não foi possível capturar dados do bilhete'
            }, 404

        return {
            'success': True,
            'data': bet_data,
            'bet_code': bet_code,
            'session_id': actual_session_id
        }, 200

    except Exception as e:
        logger.error(f"Erro ao capturar bilhete {bet_code}: {str(e)}")
        return {
            'success': False,
            'error': f'Erro interno: {str(e)}'
        }, 500

@app.route('/api/scrape-bet', methods=['POST'])
def scrape_bet():
    """Endpoint para capturar dados de um bilhete específico com processamento sequencial"""
    try:
        data = request.get_json()

        if not data or 'bet_code' not in data:
            return jsonify({
                'success': False,
                'error': 'Código do bilhete é obrigatório'
            }), 400

        bet_code = data['bet_code']
        session_id = data.get('session_id')  # Opcional: permite reutilizar sessão específica

        logger.info(f"Capturando bilhete: {bet_code}")

        # Processar sequencialmente para evitar conflitos
        result, status_code = process_request_sequentially(
            scrape_bet_worker,
            bet_code,
            session_id
        )

        return jsonify(result), status_code

    except Exception as e:
        logger.error(f"Erro ao processar scrape: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        }), 500

def login_worker(username, password, session_id):
    """Worker function para login"""
    try:
        logger.info(f"Tentativa de login para usuário: {username} (sessão: {session_id})")

        # Obter scraper para esta sessão
        scraper_instance, actual_session_id = get_or_create_scraper(session_id)

        # Fazer login
        login_success = scraper_instance.login(username, password)

        if login_success:
            return {
                'success': True,
                'message': 'Login realizado com sucesso',
                'session_id': actual_session_id
            }, 200
        else:
            return {
                'success': False,
                'error': 'Credenciais inválidas'
            }, 401

    except Exception as e:
        logger.error(f"Erro no login: {str(e)}")
        return {
            'success': False,
            'error': f'Erro interno: {str(e)}'
        }, 500

@app.route('/api/login', methods=['POST'])
def login():
    """Endpoint para fazer login no sistema com processamento sequencial"""
    try:
        data = request.get_json()

        if not data or 'username' not in data or 'password' not in data:
            return jsonify({
                'success': False,
                'error': 'Usuário e senha são obrigatórios'
            }), 400

        username = data['username']
        password = data['password']
        session_id = data.get('session_id')  # Opcional: permite reutilizar sessão específica

        logger.info(f"Tentativa de login para usuário: {username}")

        # Processar sequencialmente para evitar conflitos
        result, status_code = process_request_sequentially(
            login_worker,
            username,
            password,
            session_id
        )

        return jsonify(result), status_code

    except Exception as e:
        logger.error(f"Erro ao processar login: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        }), 500

@app.route('/api/confirm-bet', methods=['POST'])
def confirm_bet():
    """Endpoint para confirmar bilhete após pagamento aprovado com processamento sequencial"""
    try:
        data = request.get_json()

        if not data or 'bet_code' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Código do bilhete é obrigatório'
            }), 400

        bet_code = data['bet_code']

        logger.info(f"Confirmando bilhete: {bet_code}")

        # Processar com lock sequencial para evitar conflitos
        with processing_lock:
            # Obter credenciais do ambiente
            username = os.environ.get('VALSORTS_USERNAME', 'cairovinicius')
            password = os.environ.get('VALSORTS_PASSWORD', '279999')

            # Obter instância do scraper
            scraper_instance = get_scraper_instance()

            try:
                # Fazer login
                if not scraper_instance.is_logged_in:
                    logger.info(f"Fazendo login para usuário: {username}")
                    login_success = scraper_instance.login(username, password)

                    if not login_success:
                        logger.error("Falha no login")
                        return jsonify({
                            'status': 'error',
                            'message': 'Falha no login - credenciais inválidas'
                        }), 401

                # Confirmar bilhete
                logger.info(f"Confirmando bilhete: {bet_code}")
                confirmation_success = scraper_instance.confirm_bet(bet_code)

                if confirmation_success:
                    return jsonify({
                        'status': 'success',
                        'bet_code': bet_code,
                        'message': 'Bilhete confirmado com sucesso',
                        'confirmed_at': time.strftime('%Y-%m-%d %H:%M:%S')
                    })
                else:
                    return jsonify({
                        'status': 'error',
                        'message': 'Não foi possível confirmar o bilhete'
                    }), 400

            finally:
                # Sempre fechar o scraper após uso
                try:
                    scraper_instance.close()
                except:
                    pass

    except Exception as e:
        logger.error(f"Erro ao confirmar bilhete: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Erro interno: {str(e)}'
        }), 500

@app.route('/api/capture-bet', methods=['POST'])
def capture_bet():
    """Endpoint otimizado: Login + Captura em uma única operação com processamento sequencial"""
    try:
        start_time = time.time()
        data = request.get_json()

        if not data or 'bet_code' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Código do bilhete é obrigatório'
            }), 400

        bet_code = data['bet_code']

        logger.info(f"Capturando bilhete: {bet_code}")

        # Processar com lock sequencial para evitar conflitos
        with processing_lock:
            # Obter credenciais do ambiente
            username = os.environ.get('VALSORTS_USERNAME', 'cairovinicius')
            password = os.environ.get('VALSORTS_PASSWORD', '279999')

            # Obter instância do scraper
            scraper_instance = get_scraper_instance()

            try:
                # Fazer login
                if not scraper_instance.is_logged_in:
                    logger.info(f"Fazendo login para usuário: {username}")
                    login_success = scraper_instance.login(username, password)

                    if not login_success:
                        logger.error("Falha no login")
                        return jsonify({
                            'status': 'error',
                            'message': 'Falha no login - credenciais inválidas'
                        }), 401

                # Capturar dados do bilhete
                logger.info(f"Capturando dados do bilhete: {bet_code}")
                bet_data = scraper_instance.scrape_bet_ticket(bet_code)

                if not bet_data:
                    logger.error(f"Falha ao capturar dados do bilhete: {bet_code}")
                    return jsonify({
                        'status': 'error',
                        'message': 'Falha ao capturar dados do bilhete'
                    }), 404

                execution_time = time.time() - start_time
                logger.info(f"Dados capturados com sucesso para bilhete: {bet_code} em {execution_time:.2f}s")

                return jsonify({
                    'status': 'success',
                    'bet_code': bet_code,
                    'data': bet_data,
                    'message': 'Dados capturados com sucesso',
                    'execution_time': f"{execution_time:.2f}s"
                })

            finally:
                # Sempre fechar o scraper após uso
                try:
                    scraper_instance.close()
                except:
                    pass

    except Exception as e:
        logger.error(f"Erro ao capturar bilhete: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Erro interno: {str(e)}'
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
