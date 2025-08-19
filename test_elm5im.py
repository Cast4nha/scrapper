#!/usr/bin/env python3
"""
Teste específico para o bilhete ELM5IM
"""

import requests
import json
import time

# Configurações
API_BASE_URL = "https://valsports.qobebrasil.com.br"
ENDPOINT = "/api/capture-bet"

def test_elm5im():
    """Testa especificamente o bilhete TQE4X1 com 15 jogos"""
    
    url = f"{API_BASE_URL}{ENDPOINT}"
    
    # Dados da requisição
    payload = {
        "bet_code": "ELM5IM"
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    print(f"🧪 TESTE ESPECÍFICO - BILHETE ELM5IM (5 JOGOS)")
    print(f"📡 URL: {url}")
    print(f"📦 Payload: {json.dumps(payload, indent=2)}")
    print("-" * 50)
    
    try:
        # Medir tempo de execução
        start_time = time.time()
        
        # Fazer requisição
        response = requests.post(url, json=payload, headers=headers, timeout=120)  # Timeout aumentado para 2 minutos
        
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
                    
                    # Análise específica do bilhete ELM5IM
                    odds_list = all_games.get('odds', [])
                    print(f"\n🔍 ANÁLISE DO BILHETE ELM5IM:")
                    print(f"   📈 Número de odds encontradas: {len(odds_list)}")
                    if len(odds_list) == 5:
                        print("   ✅ CORRETO! Encontrou 5 odds como esperado")
                    else:
                        print(f"   ❌ ERRO! Esperado: 5 odds, Encontrado: {len(odds_list)}")
                    
                    teams_list = all_games.get('teams', [])
                    print(f"   ⚽ Número de times encontrados: {len(teams_list)}")
                    if len(teams_list) == 5:
                        print("   ✅ CORRETO! Encontrou 5 confrontos como esperado")
                    else:
                        print(f"   ❌ ERRO! Esperado: 5 confrontos, Encontrado: {len(teams_list)}")
                    
                    # Mostrar alguns exemplos de jogos
                    if teams_list:
                        print(f"\n📋 EXEMPLOS DE JOGOS CAPTURADOS:")
                        for i, team in enumerate(teams_list[:5]):  # Mostrar apenas os primeiros 5
                            print(f"   {i+1}. {team}")
                        if len(teams_list) > 5:
                            print(f"   ... e mais {len(teams_list) - 5} jogos")
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

if __name__ == "__main__":
    test_elm5im()
