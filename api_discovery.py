#!/usr/bin/env python3
"""
Sistema de Descoberta de APIs do valsports.net
Descobre e analisa todas as APIs disponíveis no site
"""

import requests
import json
import time
import re
from urllib.parse import urljoin, urlparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class APIDiscovery:
    def __init__(self):
        self.base_url = "https://www.valsports.net"
        self.discovered_apis = []
        self.network_requests = []
        
        # Configurar Firefox
        firefox_options = Options()
        firefox_options.add_argument("--headless")
        firefox_options.add_argument("--no-sandbox")
        firefox_options.add_argument("--disable-dev-shm-usage")
        
        # Adicionar listener para capturar requisições de rede
        self.driver = webdriver.Firefox(options=firefox_options)
        
    def setup_network_monitoring(self):
        """Configura monitoramento de rede"""
        logger.info("🔧 Configurando monitoramento de rede...")
        
        # Script para interceptar requisições
        script = """
        window.networkRequests = [];
        
        // Interceptar XMLHttpRequest
        const originalXHR = window.XMLHttpRequest;
        window.XMLHttpRequest = function() {
            const xhr = new originalXHR();
            const originalOpen = xhr.open;
            const originalSend = xhr.send;
            
            xhr.open = function(method, url, ...args) {
                this._method = method;
                this._url = url;
                return originalOpen.apply(this, arguments);
            };
            
            xhr.send = function(data) {
                this._data = data;
                window.networkRequests.push({
                    type: 'XHR',
                    method: this._method,
                    url: this._url,
                    data: data,
                    timestamp: new Date().toISOString()
                });
                return originalSend.apply(this, arguments);
            };
            
            return xhr;
        };
        
        // Interceptar fetch
        const originalFetch = window.fetch;
        window.fetch = function(url, options = {}) {
            window.networkRequests.push({
                type: 'FETCH',
                method: options.method || 'GET',
                url: url,
                data: options.body,
                timestamp: new Date().toISOString()
            });
            return originalFetch.apply(this, arguments);
        };
        
        console.log('Network monitoring enabled');
        """
        
        self.driver.execute_script(script)
        logger.info("✅ Monitoramento de rede configurado")
    
    def navigate_and_monitor(self, url):
        """Navega para uma URL e monitora requisições"""
        logger.info(f"🌐 Navegando para: {url}")
        
        try:
            self.driver.get(url)
            time.sleep(5)  # Aguardar carregamento
            
            # Capturar requisições de rede
            network_data = self.driver.execute_script("return window.networkRequests;")
            
            if network_data:
                logger.info(f"📡 Capturadas {len(network_data)} requisições de rede")
                for req in network_data:
                    self.analyze_request(req)
            
            # Salvar página HTML
            page_source = self.driver.page_source
            self.analyze_page_for_apis(page_source, url)
            
        except Exception as e:
            logger.error(f"❌ Erro ao navegar para {url}: {str(e)}")
    
    def analyze_request(self, request):
        """Analisa uma requisição de rede"""
        logger.info(f"🔍 Analisando requisição: {request['method']} {request['url']}")
        
        api_info = {
            'type': request['type'],
            'method': request['method'],
            'url': request['url'],
            'data': request.get('data'),
            'timestamp': request['timestamp']
        }
        
        # Verificar se é uma API
        if self.is_api_endpoint(request['url']):
            api_info['is_api'] = True
            api_info['endpoint'] = self.extract_endpoint(request['url'])
            self.discovered_apis.append(api_info)
            logger.info(f"🎯 API descoberta: {api_info['endpoint']}")
        
        self.network_requests.append(api_info)
    
    def is_api_endpoint(self, url):
        """Verifica se uma URL é um endpoint de API"""
        api_indicators = [
            '/api/',
            '/v1/',
            '/v2/',
            '/rest/',
            '/graphql',
            '.json',
            'bet_code',
            'prebet',
            'login',
            'auth'
        ]
        
        url_lower = url.lower()
        return any(indicator in url_lower for indicator in api_indicators)
    
    def extract_endpoint(self, url):
        """Extrai o endpoint da URL"""
        parsed = urlparse(url)
        return parsed.path
    
    def analyze_page_for_apis(self, html_content, base_url):
        """Analisa o HTML em busca de referências a APIs"""
        logger.info("🔍 Analisando HTML em busca de APIs...")
        
        # Padrões para encontrar URLs de API
        patterns = [
            r'["\']([^"\']*api[^"\']*)["\']',
            r'["\']([^"\']*\/v\d+[^"\']*)["\']',
            r'["\']([^"\']*\/rest[^"\']*)["\']',
            r'["\']([^"\']*\.json[^"\']*)["\']',
            r'["\']([^"\']*bet_code[^"\']*)["\']',
            r'["\']([^"\']*prebet[^"\']*)["\']',
            r'["\']([^"\']*login[^"\']*)["\']',
            r'["\']([^"\']*auth[^"\']*)["\']'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, html_content, re.IGNORECASE)
            for match in matches:
                if match.startswith('http'):
                    full_url = match
                else:
                    full_url = urljoin(base_url, match)
                
                if self.is_api_endpoint(full_url):
                    api_info = {
                        'type': 'HTML_REFERENCE',
                        'method': 'GET',
                        'url': full_url,
                        'endpoint': self.extract_endpoint(full_url),
                        'source': 'HTML_ANALYSIS',
                        'is_api': True
                    }
                    
                    if api_info not in self.discovered_apis:
                        self.discovered_apis.append(api_info)
                        logger.info(f"🎯 API encontrada no HTML: {api_info['endpoint']}")
    
    def test_api_endpoints(self):
        """Testa os endpoints de API descobertos"""
        logger.info("🧪 Testando endpoints de API...")
        
        for api in self.discovered_apis:
            if api.get('is_api'):
                self.test_endpoint(api)
    
    def test_endpoint(self, api_info):
        """Testa um endpoint específico"""
        url = api_info['url']
        method = api_info.get('method', 'GET')
        
        logger.info(f"🧪 Testando: {method} {url}")
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
                'Referer': self.base_url
            }
            
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            else:
                response = requests.post(url, headers=headers, timeout=10)
            
            api_info['test_result'] = {
                'status_code': response.status_code,
                'content_type': response.headers.get('content-type', ''),
                'response_size': len(response.content),
                'is_json': 'application/json' in response.headers.get('content-type', ''),
                'response_preview': response.text[:200] if response.text else ''
            }
            
            logger.info(f"✅ {method} {url} - Status: {response.status_code}")
            
        except Exception as e:
            api_info['test_result'] = {
                'error': str(e)
            }
            logger.error(f"❌ Erro ao testar {method} {url}: {str(e)}")
    
    def save_results(self):
        """Salva os resultados da descoberta"""
        logger.info("💾 Salvando resultados...")
        
        # Criar diretório se não existir
        import os
        if not os.path.exists('api_discovery_results'):
            os.makedirs('api_discovery_results')
        
        # Salvar APIs descobertas
        with open('api_discovery_results/discovered_apis.json', 'w', encoding='utf-8') as f:
            json.dump(self.discovered_apis, f, indent=2, ensure_ascii=False)
        
        # Salvar todas as requisições
        with open('api_discovery_results/network_requests.json', 'w', encoding='utf-8') as f:
            json.dump(self.network_requests, f, indent=2, ensure_ascii=False)
        
        # Gerar relatório
        self.generate_report()
        
        logger.info("✅ Resultados salvos em api_discovery_results/")
    
    def generate_report(self):
        """Gera um relatório em texto"""
        report = []
        report.append("=" * 60)
        report.append("RELATÓRIO DE DESCOBERTA DE APIs - VALSPORTS.NET")
        report.append("=" * 60)
        report.append(f"Data/Hora: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Total de APIs descobertas: {len([api for api in self.discovered_apis if api.get('is_api')])}")
        report.append(f"Total de requisições capturadas: {len(self.network_requests)}")
        report.append("")
        
        # APIs descobertas
        report.append("🎯 APIs DESCOBERTAS:")
        report.append("-" * 30)
        
        for api in self.discovered_apis:
            if api.get('is_api'):
                report.append(f"Endpoint: {api.get('endpoint', 'N/A')}")
                report.append(f"Método: {api.get('method', 'N/A')}")
                report.append(f"URL: {api.get('url', 'N/A')}")
                report.append(f"Tipo: {api.get('type', 'N/A')}")
                
                if 'test_result' in api:
                    test = api['test_result']
                    if 'error' in test:
                        report.append(f"Status: ❌ Erro - {test['error']}")
                    else:
                        report.append(f"Status: ✅ {test['status_code']}")
                        report.append(f"Content-Type: {test['content_type']}")
                        report.append(f"Tamanho: {test['response_size']} bytes")
                
                report.append("")
        
        # Salvar relatório
        with open('api_discovery_results/report.txt', 'w', encoding='utf-8') as f:
            f.write('\n'.join(report))
    
    def run_discovery(self):
        """Executa o processo completo de descoberta"""
        logger.info("🚀 Iniciando descoberta de APIs do valsports.net")
        
        try:
            # Configurar monitoramento
            self.setup_network_monitoring()
            
            # URLs para analisar
            urls_to_analyze = [
                "https://www.valsports.net",
                "https://www.valsports.net/login",
                "https://www.valsports.net/prebet/ELM5IM",
                "https://www.valsports.net/prebet/TQE4X1"
            ]
            
            # Analisar cada URL
            for url in urls_to_analyze:
                self.navigate_and_monitor(url)
                time.sleep(2)
            
            # Testar endpoints descobertos
            self.test_api_endpoints()
            
            # Salvar resultados
            self.save_results()
            
            logger.info("🎉 Descoberta de APIs concluída!")
            
        except Exception as e:
            logger.error(f"❌ Erro durante descoberta: {str(e)}")
        
        finally:
            self.driver.quit()

def main():
    """Função principal"""
    print("🔍 SISTEMA DE DESCOBERTA DE APIs - VALSPORTS.NET")
    print("=" * 50)
    
    discovery = APIDiscovery()
    discovery.run_discovery()
    
    print("\n📊 RESULTADOS:")
    print(f"APIs descobertas: {len([api for api in discovery.discovered_apis if api.get('is_api')])}")
    print(f"Requisições capturadas: {len(discovery.network_requests)}")
    print("📁 Resultados salvos em: api_discovery_results/")

if __name__ == "__main__":
    main()
