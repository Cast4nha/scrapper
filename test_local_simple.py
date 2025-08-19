#!/usr/bin/env python3
"""
Teste local simples para verificar se o sistema está funcionando
"""

import requests
import json
import time

def test_local_simple():
    print("🧪 TESTE LOCAL SIMPLES")
    print("=" * 40)
    
    # URL local
    url = "http://localhost:5000/ping"
    
    print(f"📡 URL: {url}")
    print("-" * 40)
    
    try:
        response = requests.get(url, timeout=10)
        print(f"📊 Status Code: {response.status_code}")
        print(f"📄 Resposta: {response.text}")
        
        if response.status_code == 200:
            print("✅ Servidor local funcionando!")
        else:
            print("❌ Servidor local com problema")
            
    except Exception as e:
        print(f"❌ ERRO: {str(e)}")
        print("💡 Dica: Execute 'python3 app.py' para iniciar o servidor local")
    
    print("=" * 40)

if __name__ == "__main__":
    test_local_simple()
