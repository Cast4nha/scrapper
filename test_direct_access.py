#!/usr/bin/env python3
"""
Script para testar acesso direto à URL do bilhete
"""

import os
import sys
import time
from dotenv import load_dotenv

# Adicionar o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scraper.valsports_scraper import ValSportsScraper

def test_direct_access():
    """Testa acesso direto à URL do bilhete"""
    
    print("🔍 Teste de Acesso Direto - ValSports")
    print("=" * 45)
    
    # Carregar variáveis de ambiente
    load_dotenv()
    
    scraper = None
    
    try:
        print("\n1. Inicializando scraper...")
        scraper = ValSportsScraper()
        print("✓ Scraper inicializado")
        
        # URL do bilhete de teste
        bet_url = "https://www.valsports.net/prebet/dmgkrn"
        
        print(f"\n2. Acessando diretamente: {bet_url}")
        scraper.driver.get(bet_url)
        time.sleep(5)
        
        print(f"✓ URL atual: {scraper.driver.current_url}")
        print(f"✓ Título da página: {scraper.driver.title}")
        
        # Verificar se foi redirecionado
        if "betsnow.net" in scraper.driver.current_url:
            print("❌ Redirecionado para betsnow.net")
            return False
        
        # Verificar se conseguiu acessar a página do bilhete
        if "prebet" in scraper.driver.current_url or "dmgkrn" in scraper.driver.current_url:
            print("✅ Acesso direto ao bilhete bem-sucedido!")
            
            # Tentar capturar alguns elementos básicos
            try:
                # Procurar por elementos que indicam que é uma página de bilhete
                page_text = scraper.driver.page_source.lower()
                
                if "bilhete" in page_text:
                    print("✅ Página contém 'bilhete'")
                if "aposta" in page_text:
                    print("✅ Página contém 'aposta'")
                if "mirassol" in page_text:
                    print("✅ Página contém 'Mirassol'")
                if "cruzeiro" in page_text:
                    print("✅ Página contém 'Cruzeiro'")
                
                # Salvar screenshot para análise
                scraper.driver.save_screenshot("bet_page.png")
                print("📸 Screenshot salvo como bet_page.png")
                
                return True
                
            except Exception as e:
                print(f"❌ Erro ao analisar página: {str(e)}")
                return False
        else:
            print("❌ Não conseguiu acessar página do bilhete")
            return False
            
    except Exception as e:
        print(f"❌ Erro durante teste: {str(e)}")
        return False
        
    finally:
        if scraper:
            print("\n3. Fechando scraper...")
            scraper.close()
            print("✓ Scraper fechado")

if __name__ == "__main__":
    success = test_direct_access()
    if success:
        print("\n🎉 Acesso direto bem-sucedido!")
        print("   Pode ser possível capturar dados sem login")
    else:
        print("\n❌ Acesso direto falhou")
        print("   Precisa de autenticação ou o site bloqueia acesso direto")
