#!/usr/bin/env python3
"""
Análise de Páginas HTML que funcionam como APIs
Extrai dados das páginas que retornam HTML
"""

import requests
import json
import time
from bs4 import BeautifulSoup
import re

def analyze_html_apis():
    print("🔍 ANÁLISE DE PÁGINAS HTML - VALSPORTS.NET")
    print("=" * 50)
    
    # Páginas que funcionam
    working_pages = [
        {
            "name": "Bet Info Page",
            "url": "https://www.valsports.net/api/bet-info"
        },
        {
            "name": "Prebet Page",
            "url": "https://www.valsports.net/api/prebet/ELM5IM"
        },
        {
            "name": "User Info Page",
            "url": "https://www.valsports.net/api/user-info"
        },
        {
            "name": "Balance Page",
            "url": "https://www.valsports.net/api/balance"
        },
        {
            "name": "Bets History Page",
            "url": "https://www.valsports.net/api/bets-history"
        }
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
        'Referer': 'https://www.valsports.net'
    }
    
    results = []
    
    for page in working_pages:
        print(f"\n🔍 Analisando: {page['name']}")
        print(f"   URL: {page['url']}")
        
        try:
            response = requests.get(page['url'], headers=headers, timeout=10)
            
            if response.status_code == 200:
                print(f"   ✅ Status: {response.status_code}")
                print(f"   📏 Tamanho: {len(response.content)} bytes")
                
                # Analisar HTML
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extrair informações básicas
                title = soup.find('title')
                title_text = title.get_text() if title else "Sem título"
                
                # Procurar por dados JSON embutidos
                scripts = soup.find_all('script')
                json_data = []
                
                for script in scripts:
                    if script.string:
                        # Procurar por objetos JSON
                        json_matches = re.findall(r'\{[^{}]*"[^"]*"[^{}]*\}', script.string)
                        for match in json_matches:
                            try:
                                data = json.loads(match)
                                json_data.append(data)
                            except:
                                pass
                
                # Procurar por elementos com dados
                data_elements = []
                
                # Procurar por elementos com atributos data-*
                for element in soup.find_all(attrs={"data-": True}):
                    data_elements.append({
                        'tag': element.name,
                        'attrs': dict(element.attrs),
                        'text': element.get_text()[:100]
                    })
                
                # Procurar por IDs que podem conter dados
                id_elements = []
                for element in soup.find_all(id=True):
                    if any(keyword in element.get('id', '').lower() for keyword in ['bet', 'user', 'balance', 'data', 'info']):
                        id_elements.append({
                            'id': element.get('id'),
                            'tag': element.name,
                            'text': element.get_text()[:100]
                        })
                
                # Procurar por classes que podem conter dados
                class_elements = []
                for element in soup.find_all(class_=True):
                    classes = element.get('class', [])
                    if any(keyword in ' '.join(classes).lower() for keyword in ['bet', 'user', 'balance', 'data', 'info', 'ticket']):
                        class_elements.append({
                            'classes': classes,
                            'tag': element.name,
                            'text': element.get_text()[:100]
                        })
                
                result = {
                    'name': page['name'],
                    'url': page['url'],
                    'status_code': response.status_code,
                    'title': title_text,
                    'json_data_found': len(json_data),
                    'data_elements': len(data_elements),
                    'id_elements': len(id_elements),
                    'class_elements': len(class_elements),
                    'json_data': json_data,
                    'data_elements_details': data_elements[:5],  # Limitar a 5
                    'id_elements_details': id_elements[:5],      # Limitar a 5
                    'class_elements_details': class_elements[:5] # Limitar a 5
                }
                
                print(f"   📄 Título: {title_text}")
                print(f"   📊 JSON encontrado: {len(json_data)} objetos")
                print(f"   🏷️  Elementos data-*: {len(data_elements)}")
                print(f"   🆔 Elementos ID: {len(id_elements)}")
                print(f"   🎨 Elementos classe: {len(class_elements)}")
                
                if json_data:
                    print(f"   📋 Dados JSON: {[list(data.keys()) for data in json_data]}")
                
            else:
                print(f"   ❌ Status: {response.status_code}")
                result = {
                    'name': page['name'],
                    'url': page['url'],
                    'status_code': response.status_code,
                    'error': f"Status {response.status_code}"
                }
            
            results.append(result)
            
        except Exception as e:
            print(f"   ❌ Erro: {str(e)}")
            results.append({
                'name': page['name'],
                'url': page['url'],
                'error': str(e)
            })
        
        time.sleep(1)  # Pausa entre requisições
    
    # Salvar resultados
    print(f"\n💾 Salvando resultados...")
    
    import os
    if not os.path.exists('api_test_results'):
        os.makedirs('api_test_results')
    
    with open('api_test_results/html_analysis.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    # Gerar relatório
    successful_pages = [r for r in results if r.get('status_code') == 200]
    
    print(f"\n📊 RESUMO:")
    print(f"   ✅ Páginas analisadas: {len(successful_pages)}")
    print(f"   📁 Resultados salvos em: api_test_results/html_analysis.json")
    
    if successful_pages:
        print(f"\n🎯 DADOS ENCONTRADOS:")
        for page in successful_pages:
            print(f"   • {page['name']}:")
            print(f"     - JSON: {page.get('json_data_found', 0)} objetos")
            print(f"     - Data elements: {page.get('data_elements', 0)}")
            print(f"     - ID elements: {page.get('id_elements', 0)}")
            print(f"     - Class elements: {page.get('class_elements', 0)}")

if __name__ == "__main__":
    analyze_html_apis()
