#!/usr/bin/env python3
"""
Script de debug local para verificar estrutura HTML e CSS selectors
"""

import requests
import json
import time

def test_local_debug():
    print("🔍 DEBUG LOCAL - ESTRUTURA HTML")
    print("=" * 50)
    
    # URL local
    url = "http://localhost:5000/api/capture-bet"
    
    # Payload
    payload = {
        "bet_code": "ELM5IM"
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    print(f"📡 URL: {url}")
    print(f"📦 Payload: {json.dumps(payload, indent=2)}")
    print("-" * 50)
    
    try:
        start_time = time.time()
        response = requests.post(url, json=payload, headers=headers, timeout=60)
        end_time = time.time()
        
        print(f"⏱️  Tempo de execução: {end_time - start_time:.2f} segundos")
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ SUCESSO!")
            print(f"📋 Status: {data.get('status')}")
            print(f"💬 Mensagem: {data.get('message')}")
            print(f"⚡ Tempo da API: {data.get('execution_time')}")
            
            # Mostrar dados detalhados
            all_games = data.get('all_games', {})
            print(f"\n🎮 DEBUG - TODOS OS JOGOS:")
            print(f"   📊 Total de jogos: {all_games.get('total_games', 0)}")
            print(f"   ⚽ Times: {all_games.get('teams', [])}")
            print(f"   🎯 Seleções: {all_games.get('selections', [])}")
            print(f"   📅 Datas/Horas: {all_games.get('datetimes', [])}")
            print(f"   📈 Odds: {all_games.get('odds', [])}")
            
            # Mostrar dados principais
            print(f"\n📊 DADOS PRINCIPAIS:")
            print(f"   🏆 Liga: {data.get('league')}")
            print(f"   ⚽ Times: {data.get('teams')}")
            print(f"   🎯 Seleção: {data.get('selection')}")
            print(f"   📅 Data/Hora: {data.get('datetime')}")
            print(f"   📈 Odds: {data.get('odds')}")
            print(f"   📊 Odds Total: {data.get('total_odds')}")
            
        else:
            print("❌ ERRO!")
            print(f"📄 Resposta: {response.text}")
            
    except Exception as e:
        print(f"❌ ERRO: {str(e)}")

if __name__ == "__main__":
    test_local_debug()
