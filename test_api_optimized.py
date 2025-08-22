#!/usr/bin/env python3
"""
Teste do endpoint otimizado /api/capture-bet
"""

import requests
import json
import time

# Configuração
ENDPOINT = "https://valsports.qobebrasil.com.br/api/capture-bet"
BET_CODE = "67izkv"  # Bilhete que testamos localmente

def test_api_capture_bet():
    """Testa o endpoint /api/capture-bet com o bilhete otimizado"""
    
    print("🧪 TESTE DO ENDPOINT OTIMIZADO")
    print("=" * 50)
    print(f"🌐 Endpoint: {ENDPOINT}")
    print(f"🎯 Bilhete: {BET_CODE}")
    print()
    
    # Dados da requisição
    payload = {
        "bet_code": BET_CODE
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        print("📡 Enviando requisição...")
        start_time = time.time()
        
        response = requests.post(ENDPOINT, json=payload, headers=headers, timeout=120)
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"⏱️ Tempo de resposta: {duration:.2f} segundos")
        print(f"📊 Status Code: {response.status_code}")
        print()
        
        if response.status_code == 200:
            data = response.json()
            
            # Extrair dados da estrutura aninhada
            bet_data = data.get('data', {})
            execution_time = data.get('execution_time', 'N/A')
            message = data.get('message', 'N/A')
            
            print("✅ SUCESSO! Dados extraídos:")
            print(f"⏱️ Tempo de execução: {execution_time}")
            print(f"📝 Mensagem: {message}")
            print(f"📊 Total de jogos: {bet_data.get('total_games', 'N/A')}")
            print(f"💰 Total odds: {bet_data.get('total_odds', 'N/A')}")
            print(f"🏆 Possível prêmio: {bet_data.get('possible_prize', 'N/A')}")
            print(f"👤 Apostador: {bet_data.get('bettor_name', 'N/A')}")
            print(f"💵 Valor: {bet_data.get('bet_value', 'N/A')}")
            
            games = bet_data.get('games', [])
            print(f"\n🎮 Jogos encontrados: {len(games)}")
            
            for i, game in enumerate(games, 1):
                print(f"\n🎯 Jogo {i}:")
                print(f"   Liga: {game.get('league', 'N/A')}")
                print(f"   Times: {game.get('teams', 'N/A')}")
                print(f"   Data/Hora: {game.get('datetime', 'N/A')}")
                print(f"   Seleção: {game.get('selection', 'N/A')}")
                print(f"   Odds: {game.get('odds', 'N/A')}")
                
        else:
            print(f"❌ ERRO: {response.status_code}")
            print(f"📝 Resposta: {response.text}")
            
    except requests.exceptions.Timeout:
        print("❌ TIMEOUT: A requisição demorou mais de 2 minutos")
    except requests.exceptions.ConnectionError:
        print("❌ ERRO DE CONEXÃO: Não foi possível conectar ao servidor")
    except Exception as e:
        print(f"❌ ERRO: {str(e)}")

if __name__ == "__main__":
    test_api_capture_bet()
