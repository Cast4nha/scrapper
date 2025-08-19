#!/usr/bin/env python3
"""
Teste de APIs Conhecidas do valsports.net
Testa endpoints que sabemos que existem
"""

import requests
import json
import time

def test_known_apis():
    print("🧪 TESTE DE APIs CONHECIDAS - VALSPORTS.NET")
    print("=" * 50)
    
    # APIs conhecidas para testar
    known_apis = [
        {
            "name": "Login API",
            "url": "https://www.valsports.net/api/login",
            "method": "POST",
            "data": {
                "username": "test",
                "password": "test"
            }
        },
        {
            "name": "Bet Info API",
            "url": "https://www.valsports.net/api/bet-info",
            "method": "GET"
        },
        {
            "name": "Prebet API",
            "url": "https://www.valsports.net/api/prebet/ELM5IM",
            "method": "GET"
        },
        {
            "name": "Confirm Bet API",
            "url": "https://www.valsports.net/api/confirm-bet",
            "method": "POST",
            "data": {
                "bet_code": "ELM5IM"
            }
        },
        {
            "name": "User Info API",
            "url": "https://www.valsports.net/api/user-info",
            "method": "GET"
        },
        {
            "name": "Balance API",
            "url": "https://www.valsports.net/api/balance",
            "method": "GET"
        },
        {
            "name": "Bets History API",
            "url": "https://www.valsports.net/api/bets-history",
            "method": "GET"
        }
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
        'Referer': 'https://www.valsports.net',
        'Origin': 'https://www.valsports.net'
    }
    
    results = []
    
    for api in known_apis:
        print(f"\n🔍 Testando: {api['name']}")
        print(f"   URL: {api['url']}")
        print(f"   Método: {api['method']}")
        
        try:
            if api['method'].upper() == 'GET':
                response = requests.get(api['url'], headers=headers, timeout=10)
            else:
                data = api.get('data', {})
                response = requests.post(api['url'], json=data, headers=headers, timeout=10)
            
            result = {
                'name': api['name'],
                'url': api['url'],
                'method': api['method'],
                'status_code': response.status_code,
                'content_type': response.headers.get('content-type', ''),
                'response_size': len(response.content),
                'is_json': 'application/json' in response.headers.get('content-type', ''),
                'response_preview': response.text[:300] if response.text else '',
                'success': response.status_code < 400
            }
            
            if result['success']:
                print(f"   ✅ Status: {response.status_code}")
                print(f"   📄 Content-Type: {result['content_type']}")
                print(f"   📏 Tamanho: {result['response_size']} bytes")
                
                if result['is_json']:
                    try:
                        json_data = response.json()
                        print(f"   📊 JSON válido: Sim")
                        print(f"   🔍 Estrutura: {list(json_data.keys()) if isinstance(json_data, dict) else 'Array'}")
                    except:
                        print(f"   📊 JSON válido: Não")
            else:
                print(f"   ❌ Status: {response.status_code}")
                print(f"   📄 Resposta: {response.text[:100]}...")
            
            results.append(result)
            
        except Exception as e:
            print(f"   ❌ Erro: {str(e)}")
            results.append({
                'name': api['name'],
                'url': api['url'],
                'method': api['method'],
                'error': str(e),
                'success': False
            })
        
        time.sleep(1)  # Pausa entre requisições
    
    # Salvar resultados
    print(f"\n💾 Salvando resultados...")
    
    import os
    if not os.path.exists('api_test_results'):
        os.makedirs('api_test_results')
    
    with open('api_test_results/known_apis_test.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    # Gerar relatório
    successful_apis = [r for r in results if r.get('success')]
    failed_apis = [r for r in results if not r.get('success')]
    
    print(f"\n📊 RESUMO:")
    print(f"   ✅ APIs funcionando: {len(successful_apis)}")
    print(f"   ❌ APIs com erro: {len(failed_apis)}")
    print(f"   📁 Resultados salvos em: api_test_results/known_apis_test.json")
    
    if successful_apis:
        print(f"\n🎯 APIs FUNCIONANDO:")
        for api in successful_apis:
            print(f"   • {api['name']} - {api['method']} {api['url']}")
    
    if failed_apis:
        print(f"\n❌ APIs COM ERRO:")
        for api in failed_apis:
            print(f"   • {api['name']} - {api.get('error', 'Status ' + str(api.get('status_code', 'N/A')))}")

if __name__ == "__main__":
    test_known_apis()
