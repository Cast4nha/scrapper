#!/usr/bin/env python3
"""
Script de teste para o endpoint otimizado /api/capture-bet
Testa o novo endpoint que faz login + captura em uma única operação
Com otimizações de cache e performance
"""

import requests
import json
import time

# Configurações
API_BASE_URL = "https://valsports.qobebrasil.com.br"
ENDPOINT = "/api/capture-bet"

def test_capture_bet(bet_code, test_number=1):
    """Testa o endpoint otimizado de captura de bilhete"""
    
    url = f"{API_BASE_URL}{ENDPOINT}"
    
    # Dados da requisição
    payload = {
        "bet_code": bet_code
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    print(f"🔍 Teste #{test_number} - Captura do bilhete: {bet_code}")
    print(f"📡 URL: {url}")
    print(f"📦 Payload: {json.dumps(payload, indent=2)}")
    print("-" * 50)
    
    try:
        # Medir tempo de execução
        start_time = time.time()
        
        # Fazer requisição
        response = requests.post(url, json=payload, headers=headers, timeout=60)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        print(f"⏱️  Tempo de execução: {execution_time:.2f} segundos")
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ SUCESSO!")
            print(f"📋 Status: {data.get('status')}")
            print(f"💬 Mensagem: {data.get('message')}")
            
            # Mostrar tempo de execução da API se disponível
            if 'execution_time' in data:
                print(f"⚡ Tempo da API: {data.get('execution_time')}")
            
            if 'data' in data:
                bet_data = data['data']
                print("\n📊 Dados do Bilhete:")
                print(f"   🏆 Liga: {bet_data.get('league', 'N/A')}")
                print(f"   ⚽ Times: {bet_data.get('teams', 'N/A')}")
                print(f"   🎯 Seleção: {bet_data.get('selection', 'N/A')}")
                print(f"   📅 Data/Hora: {bet_data.get('datetime', 'N/A')}")
                print(f"   📈 Odds: {bet_data.get('odds', 'N/A')}")
                print(f"   📊 Odds Total: {bet_data.get('total_odds', 'N/A')}")
                print(f"   💰 Prêmio Possível: {bet_data.get('possible_prize', 'N/A')}")
                print(f"   👤 Nome do Apostador: {bet_data.get('bettor_name', 'N/A')}")
                print(f"   💵 Valor da Aposta: {bet_data.get('bet_value', 'N/A')}")
                
                # Mostrar detalhes do campo all_games
                if 'all_games' in bet_data:
                    all_games = bet_data['all_games']
                    print(f"\n🎮 TODOS OS JOGOS:")
                    print(f"   📊 Total de jogos: {all_games.get('total_games', 0)}")
                    print(f"   ⚽ Times: {all_games.get('teams', [])}")
                    print(f"   🎯 Seleções: {all_games.get('selections', [])}")
                    print(f"   📅 Datas/Horas: {all_games.get('datetimes', [])}")
                    print(f"   📈 Odds: {all_games.get('odds', [])}")
                else:
                    print(f"\n❌ Campo 'all_games' não encontrado!")
        else:
            print("❌ ERRO!")
            try:
                error_data = response.json()
                print(f"📋 Status: {error_data.get('status')}")
                print(f"💬 Mensagem: {error_data.get('message')}")
            except:
                print(f"📄 Resposta: {response.text}")
                
    except requests.exceptions.Timeout:
        print("⏰ TIMEOUT - A requisição demorou muito para responder")
    except requests.exceptions.ConnectionError:
        print("🔌 ERRO DE CONEXÃO - Não foi possível conectar ao servidor")
    except Exception as e:
        print(f"💥 ERRO INESPERADO: {str(e)}")
    
    print("=" * 60)
    return execution_time

def test_cache_performance():
    """Testa a performance do cache fazendo múltiplas requisições"""
    print("🚀 TESTE DE PERFORMANCE DO CACHE")
    print("=" * 60)
    
    bet_code = "dmgkrn"
    times = []
    
    # Primeira requisição (criação da sessão)
    print("🔄 Primeira requisição (criação da sessão):")
    time1 = test_capture_bet(bet_code, 1)
    times.append(time1)
    
    # Aguardar um pouco
    print("⏳ Aguardando 2 segundos...")
    time.sleep(2)
    
    # Segunda requisição (reutilização da sessão)
    print("🔄 Segunda requisição (reutilização da sessão):")
    time2 = test_capture_bet(bet_code, 2)
    times.append(time2)
    
    # Terceira requisição (reutilização da sessão)
    print("🔄 Terceira requisição (reutilização da sessão):")
    time3 = test_capture_bet(bet_code, 3)
    times.append(time3)
    
    # Análise de performance
    print("📊 ANÁLISE DE PERFORMANCE:")
    print(f"   ⏱️  Primeira requisição: {times[0]:.2f}s")
    print(f"   ⚡ Segunda requisição: {times[1]:.2f}s")
    print(f"   ⚡ Terceira requisição: {times[2]:.2f}s")
    
    if len(times) >= 2:
        improvement = ((times[0] - times[1]) / times[0]) * 100
        print(f"   🎯 Melhoria na segunda requisição: {improvement:.1f}%")
    
    if len(times) >= 3:
        avg_cache_time = (times[1] + times[2]) / 2
        total_improvement = ((times[0] - avg_cache_time) / times[0]) * 100
        print(f"   🚀 Melhoria média com cache: {total_improvement:.1f}%")

def main():
    """Função principal"""
    print("🚀 TESTE DO ENDPOINT OTIMIZADO - CAPTURE BET")
    print("=" * 60)
    
    # Teste específico com o bilhete z1iym4
    print("🧪 TESTE ESPECÍFICO - BILHETE z1iym4")
    print("=" * 60)
    test_capture_bet("z1iym4", 1)
    
    # Teste de performance do cache
    test_cache_performance()
    
    print("\n" + "=" * 60)
    print("🧪 TESTES ADICIONAIS")
    print("=" * 60)
    
    # Teste com bilhete válido
    test_capture_bet("dmgkrn", 2)
    
    # Teste com bilhete inválido
    test_capture_bet("invalid_code", 3)
    
    print("✅ Todos os testes concluídos!")

if __name__ == "__main__":
    main()
