#!/usr/bin/env python3
"""
Script de teste específico para o bilhete TQE4X1 (15 jogos)
"""

import requests
import json
import time

def test_tqe4x1():
    print("🧪 TESTE ESPECÍFICO - BILHETE TQE4X1 (15 JOGOS)")
    print("=" * 60)
    
    # URL de produção
    url = "https://valsports.qobebrasil.com.br/api/capture-bet"
    
    # Payload
    payload = {
        "bet_code": "TQE4X1"
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    print(f"📡 URL: {url}")
    print(f"📦 Payload: {json.dumps(payload, indent=2)}")
    print("-" * 60)
    
    try:
        start_time = time.time()
        response = requests.post(url, json=payload, headers=headers, timeout=120)
        end_time = time.time()
        
        print(f"⏱️  Tempo de execução: {end_time - start_time:.2f} segundos")
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ SUCESSO!")
            print(f"📋 Status: {data.get('status')}")
            print(f"💬 Mensagem: {data.get('message')}")
            print(f"⚡ Tempo da API: {data.get('execution_time')}")
            
            # Mostrar dados principais
            print(f"\n📊 DADOS PRINCIPAIS:")
            print(f"   🏆 Liga: {data.get('league')}")
            print(f"   ⚽ Times: {data.get('teams')}")
            print(f"   🎯 Seleção: {data.get('selection')}")
            print(f"   📅 Data/Hora: {data.get('datetime')}")
            print(f"   📈 Odds: {data.get('odds')}")
            print(f"   📊 Odds Total: {data.get('total_odds')}")
            print(f"   💰 Prêmio Possível: {data.get('possible_prize')}")
            print(f"   👤 Nome do Apostador: {data.get('bettor_name')}")
            print(f"   💵 Valor da Aposta: {data.get('bet_value')}")
            
            # Mostrar dados detalhados
            all_games = data.get('all_games', {})
            print(f"\n🎮 TODOS OS JOGOS:")
            print(f"   📊 Total de jogos: {all_games.get('total_games', 0)}")
            print(f"   ⚽ Times: {all_games.get('teams', [])}")
            print(f"   🎯 Seleções: {all_games.get('selections', [])}")
            print(f"   📅 Datas/Horas: {all_games.get('datetimes', [])}")
            print(f"   📈 Odds: {all_games.get('odds', [])}")
            
            # Análise do bilhete
            odds_count = len(all_games.get('odds', []))
            teams_count = len(all_games.get('teams', []))
            selections_count = len(all_games.get('selections', []))
            datetimes_count = len(all_games.get('datetimes', []))
            
            print(f"\n🔍 ANÁLISE DO BILHETE TQE4X1:")
            print(f"   📈 Número de odds encontradas: {odds_count}")
            if odds_count == 15:
                print(f"   ✅ CORRETO! Encontrou 15 odds como esperado")
            else:
                print(f"   ❌ ERRO! Esperado: 15 odds, Encontrado: {odds_count}")
            
            print(f"   ⚽ Número de times encontrados: {teams_count}")
            if teams_count == 15:
                print(f"   ✅ CORRETO! Encontrou 15 confrontos como esperado")
            else:
                print(f"   ❌ ERRO! Esperado: 15 confrontos, Encontrado: {teams_count}")
            
            print(f"   🎯 Número de seleções encontradas: {selections_count}")
            if selections_count == 15:
                print(f"   ✅ CORRETO! Encontrou 15 seleções como esperado")
            else:
                print(f"   ❌ ERRO! Esperado: 15 seleções, Encontrado: {selections_count}")
            
            print(f"   📅 Número de datas/horas encontradas: {datetimes_count}")
            if datetimes_count == 15:
                print(f"   ✅ CORRETO! Encontrou 15 datas/horas como esperado")
            else:
                print(f"   ❌ ERRO! Esperado: 15 datas/horas, Encontrado: {datetimes_count}")
            
        else:
            print("❌ ERRO!")
            print(f"📄 Resposta: {response.text}")
            
    except Exception as e:
        print(f"❌ ERRO: {str(e)}")
    
    print("=" * 60)

if __name__ == "__main__":
    test_tqe4x1()
