#!/usr/bin/env python3
"""
Debug da resposta da API
"""

import requests
import json

# Configuração
ENDPOINT = "https://valsports.qobebrasil.com.br/api/capture-bet"
BET_CODE = "67izkv"

def debug_api_response():
    """Debug da resposta da API"""
    
    print("🔍 DEBUG DA RESPOSTA DA API")
    print("=" * 50)
    
    payload = {
        "bet_code": BET_CODE
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        print("📡 Enviando requisição...")
        response = requests.post(ENDPOINT, json=payload, headers=headers, timeout=120)
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📝 Headers: {dict(response.headers)}")
        print()
        print("📄 RESPOSTA COMPLETA:")
        print("=" * 50)
        print(response.text)
        print("=" * 50)
        
        if response.status_code == 200:
            try:
                data = response.json()
                print("\n🔍 DADOS JSON:")
                print(json.dumps(data, indent=2, ensure_ascii=False))
            except json.JSONDecodeError as e:
                print(f"❌ Erro ao decodificar JSON: {e}")
                
    except Exception as e:
        print(f"❌ ERRO: {str(e)}")

if __name__ == "__main__":
    debug_api_response()
