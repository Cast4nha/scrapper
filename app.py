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

# Sistema de fila para processamento sequencial
request_queue = Queue()
processing_lock = threading.Lock()
active_scrapers = {}  # Cache de scrapers por sessão
scraper_lock = threading.Lock()
CACHE_TIMEOUT = 600  # 10 minutos (aumentado para melhor reutilização)
SESSION_TIMEOUT = 1800  # 30 minutos para sessão completa

def cleanup_expired_scrapers():
    """Limpa scrapers expirados do cache"""
    current_time = time.time()
    expired_sessions = []

    with scraper_lock:
        for session_id, scraper_data in active_scrapers.items():
            if current_time - scraper_data['last_used'] > CACHE_TIMEOUT:
                expired_sessions.append(session_id)

        for session_id in expired_sessions:
            try:
                scraper = active_scrapers[session_id]['scraper']
                scraper.close()
                del active_scrapers[session_id]
                logger.info(f"Scraper expirado removido: {session_id}")
            except Exception as e:
                logger.error(f"Erro ao limpar scraper {session_id}: {e}")

def get_or_create_scraper(session_id=None):
    """Obtém ou cria um scraper para a sessão específica"""
    if session_id is None:
        session_id = str(uuid.uuid4())

    current_time = time.time()

    with scraper_lock:
        # Limpar scrapers expirados
        cleanup_expired_scrapers()

        # Verificar se existe scraper para esta sessão
        if session_id in active_scrapers:
            scraper_data = active_scrapers[session_id]
            if current_time - scraper_data['created_at'] < SESSION_TIMEOUT:
                scraper_data['last_used'] = current_time
                logger.info(f"Reutilizando scraper da sessão: {session_id}")
                return scraper_data['scraper'], session_id
            else:
                # Sessão expirada, remover
                try:
                    scraper_data['scraper'].close()
                except:
                    pass
                del active_scrapers[session_id]

        # Criar novo scraper para nova sessão
        logger.info(f"Criando novo scraper para sessão: {session_id}")
        scraper = ValSportsScraper()
        active_scrapers[session_id] = {
            'scraper': scraper,
            'created_at': current_time,
            'last_used': current_time
        }

        return scraper, session_id

def process_request_sequentially(func, *args, **kwargs):
    """Processa requisições sequencialmente para evitar conflitos"""
    request_id = str(uuid.uuid4())

    with processing_lock:
        logger.info(f"Enfileirando requisição: {request_id}")
        request_queue.put((request_id, func, args, kwargs))

        # Processar a fila
        while not request_queue.empty():
            current_id, current_func, current_args, current_kwargs = request_queue.get()

            try:
                logger.info(f"Processando requisição: {current_id}")
                result = current_func(*current_args, **current_kwargs)

                if current_id == request_id:
                    return result

            except Exception as e:
                logger.error(f"Erro na requisição {current_id}: {e}")
                if current_id == request_id:
                    raise e
            finally:
                request_queue.task_done()

# Registrar limpeza na saída
atexit.register(lambda: [scraper.close() for scraper in active_scrapers.values() if 'scraper' in scraper])

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
    # Obter informações sobre sessões ativas
    active_sessions_count = len(active_scrapers)
    session_info = []

    with scraper_lock:
        for session_id, scraper_data in active_scrapers.items():
            session_info.append({
                'session_id': session_id,
                'created_at': scraper_data['created_at'],
                'last_used': scraper_data['last_used'],
                'age_minutes': (time.time() - scraper_data['created_at']) / 60,
                'idle_minutes': (time.time() - scraper_data['last_used']) / 60
            })

    return jsonify({
        'status': 'healthy',
        'service': 'valsports-scraper-api',
        'version': '2.0.0',
        'features': ['queue_processing', 'session_caching', 'concurrent_safe'],
        'active_sessions': active_sessions_count,
        'session_details': session_info,
        'queue_size': request_queue.qsize(),
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
    })

@app.route('/sessions', methods=['GET'])
def get_sessions():
    """Endpoint para visualizar sessões ativas"""
    session_info = []

    with scraper_lock:
        for session_id, scraper_data in active_scrapers.items():
            session_info.append({
                'session_id': session_id,
                'created_at': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(scraper_data['created_at'])),
                'last_used': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(scraper_data['last_used'])),
                'age_minutes': round((time.time() - scraper_data['created_at']) / 60, 2),
                'idle_minutes': round((time.time() - scraper_data['last_used']) / 60, 2),
                'logged_in': scraper_data['scraper'].is_logged_in
            })

    return jsonify({
        'active_sessions': len(session_info),
        'sessions': session_info,
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
    })

@app.route('/sessions/<session_id>', methods=['DELETE'])
def delete_session(session_id):
    """Endpoint para remover uma sessão específica"""
    with scraper_lock:
        if session_id in active_scrapers:
            try:
                scraper = active_scrapers[session_id]['scraper']
                scraper.close()
                del active_scrapers[session_id]
                logger.info(f"Sessão {session_id} removida manualmente")
                return jsonify({
                    'success': True,
                    'message': f'Sessão {session_id} removida com sucesso'
                })
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': f'Erro ao remover sessão: {str(e)}'
                }), 500
        else:
            return jsonify({
                'success': False,
                'error': 'Sessão não encontrada'
            }), 404

@app.route('/', methods=['GET'])
def root():
    """Endpoint raiz para teste"""
    return jsonify({
        'message': 'ValSports Scraper API v2.0',
        'status': 'running',
        'features': ['queue_processing', 'session_caching', 'concurrent_safe'],
        'endpoints': {
            'health': '/health',
            'sessions': '/sessions',
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

def confirm_bet_worker(bet_code, session_id):
    """Worker function para confirmação de bilhete"""
    try:
        logger.info(f"Confirmando bilhete {bet_code} na sessão {session_id}")

        # Obter credenciais do ambiente
        username = os.environ.get('VALSORTS_USERNAME', 'cairovinicius')
        password = os.environ.get('VALSORTS_PASSWORD', '279999')

        # Obter scraper para esta sessão
        scraper_instance, actual_session_id = get_or_create_scraper(session_id)

        # Fazer login automático (se necessário)
        if not scraper_instance.is_logged_in:
            logger.info(f"Fazendo login para usuário: {username} (sessão: {actual_session_id})")
            login_success = scraper_instance.login(username, password)

            if not login_success:
                logger.error("Falha no login")
                return {
                    'status': 'error',
                    'message': 'Falha no login - credenciais inválidas'
                }, 401
        else:
            logger.info(f"Usando sessão existente (sessão: {actual_session_id})")

        # Confirmar bilhete
        logger.info(f"Confirmando bilhete: {bet_code} (sessão: {actual_session_id})")
        confirmation_success = scraper_instance.confirm_bet(bet_code)

        if confirmation_success:
            return {
                'status': 'success',
                'bet_code': bet_code,
                'message': 'Bilhete confirmado com sucesso',
                'confirmed_at': time.strftime('%Y-%m-%d %H:%M:%S'),
                'session_id': actual_session_id
            }, 200
        else:
            return {
                'status': 'error',
                'message': 'Não foi possível confirmar o bilhete'
            }, 400

    except Exception as e:
        logger.error(f"Erro ao confirmar bilhete {bet_code}: {str(e)}")
        return {
            'status': 'error',
            'message': f'Erro interno: {str(e)}'
        }, 500

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
        session_id = data.get('session_id')  # Opcional: permite reutilizar sessão específica

        logger.info(f"Recebida requisição para confirmar bilhete: {bet_code}")

        # Processar sequencialmente para evitar conflitos
        result, status_code = process_request_sequentially(
            confirm_bet_worker,
            bet_code,
            session_id
        )

        return jsonify(result), status_code

    except Exception as e:
        logger.error(f"Erro ao processar requisição de confirmação: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Erro interno: {str(e)}'
        }), 500

def capture_bet_worker(bet_code, session_id):
    """Worker function para captura de bilhete"""
    try:
        start_time = time.time()

        logger.info(f"Capturando bilhete {bet_code} na sessão {session_id}")

        # Obter credenciais do ambiente
        username = os.environ.get('VALSORTS_USERNAME', 'cairovinicius')
        password = os.environ.get('VALSORTS_PASSWORD', '279999')

        # Obter scraper para esta sessão
        scraper_instance, actual_session_id = get_or_create_scraper(session_id)

        # Fazer login automático (se necessário)
        if not scraper_instance.is_logged_in:
            logger.info(f"Fazendo login para usuário: {username} (sessão: {actual_session_id})")
            login_success = scraper_instance.login(username, password)

            if not login_success:
                logger.error("Falha no login")
                return {
                    'status': 'error',
                    'message': 'Falha no login - credenciais inválidas'
                }, 401
        else:
            logger.info(f"Usando sessão existente (sessão: {actual_session_id})")

        # Capturar dados do bilhete
        logger.info(f"Capturando dados do bilhete: {bet_code} (sessão: {actual_session_id})")
        bet_data = scraper_instance.scrape_bet_ticket(bet_code)

        if not bet_data:
            logger.error(f"Falha ao capturar dados do bilhete: {bet_code}")
            return {
                'status': 'error',
                'message': 'Falha ao capturar dados do bilhete'
            }, 404

        execution_time = time.time() - start_time
        logger.info(f"Dados capturados com sucesso para bilhete: {bet_code} em {execution_time:.2f}s")

        return {
            'status': 'success',
            'bet_code': bet_code,
            'data': bet_data,
            'message': 'Dados capturados com sucesso',
            'execution_time': f"{execution_time:.2f}s",
            'session_id': actual_session_id
        }, 200

    except Exception as e:
        logger.error(f"Erro ao capturar bilhete {bet_code}: {str(e)}")
        return {
            'status': 'error',
            'message': f'Erro interno: {str(e)}'
        }, 500

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
        session_id = data.get('session_id')  # Opcional: permite reutilizar sessão específica

        logger.info(f"Recebida requisição para capturar bilhete: {bet_code}")

        # Processar sequencialmente para evitar conflitos
        result, status_code = process_request_sequentially(
            capture_bet_worker,
            bet_code,
            session_id
        )

        execution_time = time.time() - start_time
        logger.info(f"Requisição processada em {execution_time:.2f}s")

        return jsonify(result), status_code

    except Exception as e:
        logger.error(f"Erro ao processar requisição: {str(e)}")
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
