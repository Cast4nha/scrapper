#!/usr/bin/env python3
"""
Teste do endpoint de confirmação de bilhete
"""

import requests
import json
import time

def test_confirm_bet():
    """Testa o endpoint de confirmação de bilhete"""
    
    print("🧪 TESTE DE CONFIRMAÇÃO DE BILHETE")
    print("=" * 50)
    
    # Configurações
    api_url = "https://valsports.qobebrasil.com.br/api/confirm-bet"
    bet_code = "n6e2er"  # Bilhete de teste
    
    # Dados da requisição
    payload = {
        "bet_code": bet_code
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    print(f"🌐 Endpoint: {api_url}")
    print(f"🎯 Bilhete: {bet_code}")
    print(f"📡 Enviando requisição...")
    
    try:
        # Fazer requisição
        start_time = time.time()
        response = requests.post(api_url, json=payload, headers=headers)
        end_time = time.time()
        
        print(f"⏱️ Tempo de resposta: {end_time - start_time:.2f} segundos")
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("\n✅ SUCESSO! Bilhete confirmado:")
            print(f"📝 Status: {data.get('status', 'N/A')}")
            print(f"🎯 Código: {data.get('bet_code', 'N/A')}")
            print(f"📝 Mensagem: {data.get('message', 'N/A')}")
            print(f"⏰ Confirmado em: {data.get('confirmed_at', 'N/A')}")
        else:
            print(f"\n❌ ERRO! Status: {response.status_code}")
            try:
                error_data = response.json()
                print(f"📝 Erro: {error_data.get('message', 'Erro desconhecido')}")
            except:
                print(f"📝 Erro: {response.text}")
                
    except Exception as e:
        print(f"❌ Erro na requisição: {str(e)}")

if __name__ == "__main__":
    test_confirm_bet()
