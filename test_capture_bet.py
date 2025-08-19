#!/usr/bin/env python3
"""
Script de teste para o endpoint otimizado /api/capture-bet
Testa o novo endpoint que faz login + captura em uma única operação
"""

import requests
import json
import time

# Configurações
API_BASE_URL = "https://valsports.qobebrasil.com.br"
ENDPOINT = "/api/capture-bet"

def test_capture_bet(bet_code):
    """Testa o endpoint otimizado de captura de bilhete"""
    
    url = f"{API_BASE_URL}{ENDPOINT}"
    
    # Dados da requisição
    payload = {
        "bet_code": bet_code
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    print(f"🔍 Testando captura do bilhete: {bet_code}")
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

def main():
    """Função principal"""
    print("🚀 TESTE DO ENDPOINT OTIMIZADO - CAPTURE BET")
    print("=" * 60)
    
    # Teste com bilhete válido
    test_capture_bet("dmgkrn")
    
    # Teste com bilhete inválido
    test_capture_bet("invalid_code")
    
    print("✅ Testes concluídos!")

if __name__ == "__main__":
    main()
