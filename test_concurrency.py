#!/usr/bin/env python3
"""
Script para testar concorrência múltipla de bilhetes
Testa o problema de concorrência que foi corrigido
"""

import requests
import threading
import time
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

API_URL = "https://valsports.qobebrasil.com.br/api/capture-bet"

# Bilhetes para teste
TEST_BETS = ["za26k1", "fe6h3n"]

def test_single_bet(bet_code, request_id):
    """Testa um único bilhete"""
    print(f"[Request {request_id}] Iniciando teste do bilhete: {bet_code}")

    try:
        start_time = time.time()

        response = requests.post(
            API_URL,
            json={"bet_code": bet_code},
            timeout=120,
            headers={'Content-Type': 'application/json'}
        )

        execution_time = time.time() - start_time

        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                print(f"[Request {request_id}] ✅ Bilhete {bet_code}: Sucesso em {execution_time:.2f}s")
                return True
            else:
                print(f"[Request {request_id}] ❌ Bilhete {bet_code}: Falha na captura - {data.get('message', 'Erro desconhecido')}")
                return False
        elif response.status_code == 429:
            print(f"[Request {request_id}] ⚠️ Bilhete {bet_code}: Sistema ocupado (HTTP 429)")
            return False
        else:
            print(f"[Request {request_id}] ❌ Bilhete {bet_code}: Erro HTTP {response.status_code}")
            return False

    except requests.exceptions.Timeout:
        print(f"[Request {request_id}] ❌ Bilhete {bet_code}: Timeout")
        return False
    except Exception as e:
        print(f"[Request {request_id}] ❌ Bilhete {bet_code}: Erro - {str(e)}")
        return False

def test_concurrent_requests(num_concurrent=5):
    """Testa múltiplas requisições simultâneas"""
    print(f"\n🧪 Iniciando teste de concorrência com {num_concurrent} requisições simultâneas...")

    results = []
    request_id = 1

    with ThreadPoolExecutor(max_workers=num_concurrent) as executor:
        # Criar tarefas para cada bilhete
        futures = []
        for bet_code in TEST_BETS:
            for i in range(num_concurrent):
                future = executor.submit(test_single_bet, bet_code, request_id)
                futures.append(future)
                request_id += 1

        # Aguardar todas as tarefas completarem
        for future in as_completed(futures):
            result = future.result()
            results.append(result)

    # Análise dos resultados
    success_count = sum(1 for result in results if result)
    total_count = len(results)
    success_rate = (success_count / total_count) * 100

    print("\n📊 RESULTADOS DO TESTE:")
    print(f"   Total de requisições: {total_count}")
    print(f"   Sucessos: {success_count}")
    print(f"   Falhas: {total_count - success_count}")
    print(f"   Taxa de sucesso: {success_rate:.1f}%")

    if success_rate >= 80:
        print("   ✅ Status: EXCELENTE - Sistema suportando concorrência adequadamente")
    else:
        print("   ❌ Status: PROBLEMA - Sistema com dificuldades de concorrência")
    return success_rate

def test_sequential_requests():
    """Testa requisições sequenciais para comparação"""
    print("\n🔄 Testando requisições sequenciais (para comparação)...")
    results = []

    for bet_code in TEST_BETS:
        print(f"\n📝 Testando bilhete {bet_code} sequencialmente:")
        success = test_single_bet(bet_code, 0)
        results.append(success)
        time.sleep(1)  # Pequena pausa entre requisições

    success_count = sum(1 for result in results if result)
    success_rate = (success_count / len(results)) * 100

    print("\n📊 RESULTADOS SEQUENCIAIS:")
    print(f"   Taxa de sucesso: {success_rate:.1f}%")
    return success_rate

def main():
    """Função principal"""
    print("🚀 TESTE DE CONCORRÊNCIA - ValSports Scraper API")
    print("=" * 60)

    # Teste sequencial primeiro
    sequential_rate = test_sequential_requests()

    # Teste de concorrência
    concurrent_rate = test_concurrent_requests(3)  # 3 requisições simultâneas

    # Análise final
    print("\n🎯 ANÁLISE FINAL:")
    print(f"   Taxa sequencial: {sequential_rate:.1f}%")
    print(f"   Taxa concorrente: {concurrent_rate:.1f}%")

    if concurrent_rate >= 90:
        print("   ✅ SISTEMA FUNCIONANDO PERFEITAMENTE!")
        print("   💡 O pool de scrapers está gerenciando a concorrência adequadamente.")
    elif concurrent_rate >= 70:
        print("   ⚠️ SISTEMA FUNCIONANDO COM LIMITAÇÕES")
        print("   💡 Algumas requisições simultâneas falharam, mas o sistema está funcionando.")
    else:
        print("   ❌ PROBLEMAS DE CONCORRÊNCIA DETECTADOS")
        print("   💡 Muitas requisições simultâneas falharam. Pode haver problemas no pool.")

    print("\n💡 RECOMENDAÇÕES:")
    print("   - Monitorar logs do servidor durante picos de uso")
    print("   - Considerar aumentar POOL_SIZE se necessário")
    print("   - Implementar rate limiting no cliente se apropriado")

if __name__ == "__main__":
    main()
