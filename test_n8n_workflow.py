#!/usr/bin/env python3
"""
Script de teste para o fluxo n8n ValSports Scraper
"""

import requests
import json
import time

class ValSportsN8nTester:
    def __init__(self, webhook_url):
        self.webhook_url = webhook_url
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json'
        })
    
    def test_login(self, username="cairovinicius", password="279999"):
        """Testa o login no sistema"""
        print("🔐 Testando login...")
        
        payload = {
            "action": "login",
            "username": username,
            "password": password
        }
        
        try:
            response = self.session.post(self.webhook_url, json=payload)
            result = response.json()
            
            if result.get('status') == 'success':
                print("✅ Login realizado com sucesso!")
                return True
            else:
                print(f"❌ Falha no login: {result.get('message', 'Erro desconhecido')}")
                return False
                
        except Exception as e:
            print(f"❌ Erro na requisição: {e}")
            return False
    
    def test_scrape_bet(self, bet_code="dmgkrn"):
        """Testa a captura de dados do bilhete"""
        print(f"📋 Testando captura do bilhete: {bet_code}")
        
        payload = {
            "action": "scrape_bet",
            "bet_code": bet_code
        }
        
        try:
            response = self.session.post(self.webhook_url, json=payload)
            result = response.json()
            
            if result.get('status') == 'success':
                data = result.get('data', {})
                print("✅ Dados capturados com sucesso!")
                print(f"   🏆 Liga: {data.get('league', 'N/A')}")
                print(f"   ⚽ Times: {data.get('teams', 'N/A')}")
                print(f"   🎯 Seleção: {data.get('selection', 'N/A')}")
                print(f"   📅 Data: {data.get('datetime', 'N/A')}")
                print(f"   📊 Odds: {data.get('odds', 'N/A')}")
                print(f"   💰 Valor: {data.get('bet_value', 'N/A')}")
                print(f"   👤 Apostador: {data.get('bettor_name', 'N/A')}")
                return True
            else:
                print(f"❌ Falha na captura: {result.get('message', 'Erro desconhecido')}")
                return False
                
        except Exception as e:
            print(f"❌ Erro na requisição: {e}")
            return False
    
    def test_confirm_bet(self, bet_code="dmgkrn"):
        """Testa a confirmação da aposta"""
        print(f"✅ Testando confirmação da aposta: {bet_code}")
        
        payload = {
            "action": "confirm_bet",
            "bet_code": bet_code
        }
        
        try:
            response = self.session.post(self.webhook_url, json=payload)
            result = response.json()
            
            if result.get('status') == 'success':
                print("✅ Aposta confirmada com sucesso!")
                return True
            else:
                print(f"❌ Falha na confirmação: {result.get('message', 'Erro desconhecido')}")
                return False
                
        except Exception as e:
            print(f"❌ Erro na requisição: {e}")
            return False
    
    def test_invalid_action(self):
        """Testa ação inválida"""
        print("🚫 Testando ação inválida...")
        
        payload = {
            "action": "invalid_action"
        }
        
        try:
            response = self.session.post(self.webhook_url, json=payload)
            result = response.json()
            
            if result.get('status') == 'error':
                print("✅ Erro tratado corretamente!")
                return True
            else:
                print("❌ Erro não foi tratado corretamente")
                return False
                
        except Exception as e:
            print(f"❌ Erro na requisição: {e}")
            return False
    
    def run_full_test(self):
        """Executa todos os testes"""
        print("🚀 Iniciando testes do fluxo n8n ValSports Scraper")
        print("=" * 50)
        
        tests = [
            ("Login", self.test_login),
            ("Captura de Bilhete", lambda: self.test_scrape_bet("dmgkrn")),
            ("Confirmação de Aposta", lambda: self.test_confirm_bet("dmgkrn")),
            ("Ação Inválida", self.test_invalid_action)
        ]
        
        results = []
        
        for test_name, test_func in tests:
            print(f"\n📝 Teste: {test_name}")
            print("-" * 30)
            
            start_time = time.time()
            success = test_func()
            end_time = time.time()
            
            duration = end_time - start_time
            results.append((test_name, success, duration))
            
            print(f"⏱️  Duração: {duration:.2f}s")
            time.sleep(1)  # Pausa entre testes
        
        # Relatório final
        print("\n" + "=" * 50)
        print("📊 RELATÓRIO FINAL")
        print("=" * 50)
        
        passed = 0
        total = len(results)
        
        for test_name, success, duration in results:
            status = "✅ PASSOU" if success else "❌ FALHOU"
            print(f"{status} | {test_name} | {duration:.2f}s")
            if success:
                passed += 1
        
        print(f"\n🎯 Resultado: {passed}/{total} testes passaram")
        
        if passed == total:
            print("🎉 Todos os testes passaram! Fluxo funcionando perfeitamente!")
        else:
            print("⚠️  Alguns testes falharam. Verifique a configuração.")

def main():
    # Configurar URL do webhook n8n
    webhook_url = input("🔗 Digite a URL do webhook n8n: ").strip()
    
    if not webhook_url:
        print("❌ URL do webhook é obrigatória!")
        return
    
    # Criar instância do tester
    tester = ValSportsN8nTester(webhook_url)
    
    # Executar testes
    tester.run_full_test()

if __name__ == "__main__":
    main()
