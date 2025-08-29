from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
from scraper.valsports_scraper_final import ValSportsScraper
import logging
import time
import threading

# Carregar variáveis de ambiente
load_dotenv()

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuração de CORS
CORS(app)

# Pool de scrapers para gerenciar concorrência
scraper_pool = []
scraper_pool_lock = threading.Lock()
POOL_SIZE = 3  # Máximo de 3 instâncias simultâneas
POOL_TIMEOUT = 300  # 5 minutos

class ScraperPool:
    """Pool de scrapers para gerenciar múltiplas instâncias simultâneas"""

    def __init__(self, pool_size=POOL_SIZE):
        self.pool_size = pool_size
        self.pool = []
        self.lock = threading.Lock()
        self.logger = logging.getLogger(__name__)

    def get_scraper(self):
        """Obtém uma instância do scraper do pool ou cria uma nova"""
        with self.lock:
            # Procurar instância disponível
            for scraper_info in self.pool:
                scraper, last_used, in_use = scraper_info
                if not in_use:
                    current_time = time.time()
                    # Verificar se expirou
                    if current_time - last_used > POOL_TIMEOUT:
                        try:
                            scraper.close()
                        except:
                            pass
                        self.pool.remove(scraper_info)
                        continue

                    # Marcar como em uso
                    scraper_info[2] = True
                    scraper_info[1] = current_time
                    self.logger.info(f"Reutilizando scraper do pool (total: {len(self.pool)})")
                    return scraper

            # Se não encontrou disponível e pool não está cheio, criar nova
            if len(self.pool) < self.pool_size:
                scraper = ValSportsScraper()
                self.pool.append([scraper, time.time(), True])
                self.logger.info(f"Nova instância criada no pool (total: {len(self.pool)})")
                return scraper

            # Se pool está cheio, aguardar por uma instância livre
            self.logger.warning("Pool de scrapers cheio, aguardando liberação...")
            # Retornar None se não conseguir uma instância
            return None

    def release_scraper(self, scraper):
        """Libera uma instância do scraper de volta ao pool"""
        with self.lock:
            for scraper_info in self.pool:
                if scraper_info[0] == scraper:
                    scraper_info[2] = False
                    scraper_info[1] = time.time()
                    self.logger.info(f"Scraper liberado no pool")
                    return

    def cleanup_expired(self):
        """Limpa instâncias expiradas do pool"""
        with self.lock:
            current_time = time.time()
            expired = []
            for scraper_info in self.pool:
                scraper, last_used, in_use = scraper_info
                if current_time - last_used > POOL_TIMEOUT:
                    expired.append(scraper_info)

            for scraper_info in expired:
                try:
                    scraper_info[0].close()
                except:
                    pass
                self.pool.remove(scraper_info)

            if expired:
                self.logger.info(f"Limpou {len(expired)} scrapers expirados")

    def close_all(self):
        """Fecha todas as instâncias do pool"""
        with self.lock:
            for scraper_info in self.pool:
                try:
                    scraper_info[0].close()
                except:
                    pass
            self.pool.clear()

# Instância global do pool
scraper_pool_manager = ScraperPool()

def get_scraper():
    """Obtém uma instância do scraper do pool"""
    return scraper_pool_manager.get_scraper()

def release_scraper(scraper):
    """Libera uma instância do scraper de volta ao pool"""
    scraper_pool_manager.release_scraper(scraper)

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

@app.route('/api/scrape-bet', methods=['POST'])
def scrape_bet():
    """Endpoint para capturar dados de um bilhete específico"""
    scraper_instance = None
    try:
        data = request.get_json()

        if not data or 'bet_code' not in data:
            return jsonify({
                'success': False,
                'error': 'Código do bilhete é obrigatório'
            }), 400

        bet_code = data['bet_code']

        logger.info(f"Capturando bilhete: {bet_code}")

        # Obter instância do scraper do pool
        scraper_instance = get_scraper()
        if not scraper_instance:
            return jsonify({
                'success': False,
                'error': 'Sistema ocupado. Tente novamente em alguns segundos.'
            }), 429

        # Capturar dados do bilhete
        bet_data = scraper_instance.scrape_bet_ticket(bet_code)

        if not bet_data:
            return jsonify({
                'success': False,
                'error': 'Não foi possível capturar dados do bilhete'
            }), 404

        return jsonify({
            'success': True,
            'data': bet_data,
            'bet_code': bet_code
        })

    except Exception as e:
        logger.error(f"Erro ao capturar bilhete: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        }), 500
    finally:
        # Sempre liberar a instância de volta ao pool
        if scraper_instance:
            release_scraper(scraper_instance)

@app.route('/api/login', methods=['POST'])
def login():
    """Endpoint para fazer login no sistema"""
    scraper_instance = None
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

        # Obter instância do scraper do pool
        scraper_instance = get_scraper()
        if not scraper_instance:
            return jsonify({
                'success': False,
                'error': 'Sistema ocupado. Tente novamente em alguns segundos.'
            }), 429

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
    finally:
        # Sempre liberar a instância de volta ao pool
        if scraper_instance:
            release_scraper(scraper_instance)

@app.route('/api/confirm-bet', methods=['POST'])
def confirm_bet():
    """Endpoint para confirmar bilhete após pagamento aprovado"""
    scraper_instance = None
    try:
        data = request.get_json()

        if not data or 'bet_code' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Código do bilhete é obrigatório'
            }), 400

        bet_code = data['bet_code']

        logger.info(f"Confirmando bilhete: {bet_code}")

        # Obter credenciais do ambiente
        username = os.environ.get('VALSORTS_USERNAME', 'cairovinicius')
        password = os.environ.get('VALSORTS_PASSWORD', '279999')

        # Obter instância do scraper do pool
        scraper_instance = get_scraper()
        if not scraper_instance:
            return jsonify({
                'status': 'error',
                'message': 'Sistema ocupado. Tente novamente em alguns segundos.'
            }), 429

        # Fazer login automático (se necessário)
        if not scraper_instance.is_logged_in:
            logger.info(f"Fazendo login para usuário: {username}")
            login_success = scraper_instance.login(username, password)

            if not login_success:
                logger.error("Falha no login")
                return jsonify({
                    'status': 'error',
                    'message': 'Falha no login - credenciais inválidas'
                }), 401
        else:
            logger.info("Usando sessão existente")

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

    except Exception as e:
        logger.error(f"Erro ao confirmar bilhete: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Erro interno: {str(e)}'
        }), 500
    finally:
        # Sempre liberar a instância de volta ao pool
        if scraper_instance:
            release_scraper(scraper_instance)

@app.route('/api/capture-bet', methods=['POST'])
def capture_bet():
    """Endpoint otimizado: Login + Captura em uma única operação"""
    scraper_instance = None
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

        # Obter credenciais do ambiente
        username = os.environ.get('VALSORTS_USERNAME', 'cairovinicius')
        password = os.environ.get('VALSORTS_PASSWORD', '279999')

        # Obter instância do scraper do pool
        scraper_instance = get_scraper()
        if not scraper_instance:
            return jsonify({
                'status': 'error',
                'message': 'Sistema ocupado. Tente novamente em alguns segundos.'
            }), 429

        # Fazer login automático (se necessário)
        if not scraper_instance.is_logged_in:
            logger.info(f"Fazendo login para usuário: {username}")
            login_success = scraper_instance.login(username, password)

            if not login_success:
                logger.error("Falha no login")
                return jsonify({
                    'status': 'error',
                    'message': 'Falha no login - credenciais inválidas'
                }), 401
        else:
            logger.info("Usando sessão existente")

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

    except Exception as e:
        logger.error(f"Erro ao capturar bilhete: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Erro interno: {str(e)}'
        }), 500
    finally:
        # Sempre liberar a instância de volta ao pool
        if scraper_instance:
            release_scraper(scraper_instance)

def cleanup_expired_scrapers():
    """Função para limpar scrapers expirados periodicamente"""
    while True:
        try:
            scraper_pool_manager.cleanup_expired()
            time.sleep(60)  # Executa a cada 60 segundos
        except Exception as e:
            logger.error(f"Erro na limpeza de scrapers expirados: {str(e)}")
            time.sleep(60)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'

    # Iniciar thread de limpeza em background
    cleanup_thread = threading.Thread(target=cleanup_expired_scrapers, daemon=True)
    cleanup_thread.start()
    logger.info("Thread de limpeza de scrapers expirados iniciada")

    # Configurar para aceitar tanto HTTP quanto HTTPS
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug,
        threaded=True,
        use_reloader=False
    )
