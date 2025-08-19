#!/usr/bin/env python3
"""
Script simples para testar acesso ao site ValSports
"""

import os
import sys
import time
from dotenv import load_dotenv

# Adicionar o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scraper.valsports_scraper import ValSportsScraper

def test_access():
    """Testa acesso básico ao site"""
    
    print("🔍 Teste de Acesso - ValSports")
    print("=" * 40)
    
    # Carregar variáveis de ambiente
    load_dotenv()
    
    scraper = None
    
    try:
        print("\n1. Inicializando scraper...")
        scraper = ValSportsScraper()
        print("✓ Scraper inicializado")
        
        print("\n2. Acessando página inicial...")
        scraper.driver.get("https://www.valsports.net")
        time.sleep(3)
        
        print(f"✓ URL atual: {scraper.driver.current_url}")
        print(f"✓ Título da página: {scraper.driver.title}")
        
        # Verificar se foi redirecionado para página de erro
        if "error" in scraper.driver.current_url.lower() or "dns" in scraper.driver.current_url.lower():
            print("❌ Detectado redirecionamento para página de erro")
            print("   O site detectou automação e ativou proteção")
            return False
        
        print("\n3. Acessando página de login...")
        scraper.driver.get("https://www.valsports.net/login")
        time.sleep(3)
        
        print(f"✓ URL atual: {scraper.driver.current_url}")
        print(f"✓ Título da página: {scraper.driver.title}")
        
        # Verificar se conseguiu acessar a página de login
        if "login" in scraper.driver.current_url.lower():
            print("✅ Acesso à página de login bem-sucedido!")
            
            # Verificar se os elementos de login estão presentes
            try:
                username_field = scraper.driver.find_element("css selector", ".form-group:nth-child(1) > .form-control")
                password_field = scraper.driver.find_element("css selector", ".form-group:nth-child(2) > .form-control")
                login_button = scraper.driver.find_element("css selector", ".btn-success")
                
                print("✅ Elementos de login encontrados:")
                print(f"   - Campo usuário: {username_field.get_attribute('placeholder') or 'encontrado'}")
                print(f"   - Campo senha: {password_field.get_attribute('placeholder') or 'encontrado'}")
                print(f"   - Botão login: {login_button.text}")
                
                return True
                
            except Exception as e:
                print(f"❌ Elementos de login não encontrados: {str(e)}")
                return False
        else:
            print("❌ Não conseguiu acessar página de login")
            return False
            
    except Exception as e:
        print(f"❌ Erro durante teste: {str(e)}")
        return False
        
    finally:
        if scraper:
            print("\n4. Fechando scraper...")
            scraper.close()
            print("✓ Scraper fechado")

if __name__ == "__main__":
    success = test_access()
    if success:
        print("\n🎉 Teste de acesso bem-sucedido!")
        print("   O scraper está funcionando sem detecção")
    else:
        print("\n❌ Teste de acesso falhou")
        print("   Precisa ajustar configurações anti-detecção")
