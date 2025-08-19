#!/usr/bin/env python3
"""
Script de debug para capturar estrutura HTML da página
Ajuda a identificar os seletores corretos para o scraping
"""

import os
import sys
import json
from dotenv import load_dotenv

# Adicionar o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scraper.valsports_scraper import ValSportsScraper

def debug_page():
    """Captura e analisa a estrutura HTML da página"""
    
    print("🔍 Debug da Página - ValSports Scraper")
    print("=" * 50)
    
    # Carregar variáveis de ambiente
    load_dotenv()
    
    # Credenciais de teste
    username = "cairovinicius"
    password = "279999"
    test_url = "https://www.valsports.net/prebet/dmgkrn"
    
    scraper = None
    
    try:
        print("\n1. Inicializando scraper...")
        scraper = ValSportsScraper()
        print("✓ Scraper inicializado")
        
        print("\n2. Fazendo login...")
        login_success = scraper.login(username, password)
        
        if login_success:
            print("✓ Login realizado com sucesso")
            
            print("\n3. Acessando página do bilhete...")
            scraper.driver.get(test_url)
            
            # Aguardar carregamento
            import time
            time.sleep(5)
            
            print("\n4. Capturando estrutura HTML...")
            
            # Capturar HTML da página
            page_source = scraper.driver.page_source
            
            # Salvar HTML em arquivo
            with open('debug_page.html', 'w', encoding='utf-8') as f:
                f.write(page_source)
            print("✓ HTML salvo em debug_page.html")
            
            # Analisar elementos importantes
            print("\n5. Analisando elementos importantes...")
            
            # Procurar por elementos com texto específico
            important_texts = [
                'BILHETE', 'Série', 'Mirassol', 'Cruzeiro', 'Vencedor',
                'TOTAL ODDS', 'POSSÍVEL PRÊMIO', 'APOSTAR', 'R$'
            ]
            
            for text in important_texts:
                elements = scraper.driver.find_elements("xpath", f"//*[contains(text(), '{text}')]")
                if elements:
                    print(f"✓ '{text}' encontrado em {len(elements)} elemento(s)")
                    for i, elem in enumerate(elements[:3]):  # Mostrar apenas os 3 primeiros
                        print(f"   {i+1}. Tag: {elem.tag_name}, Texto: {elem.text[:50]}...")
                else:
                    print(f"❌ '{text}' não encontrado")
            
            # Procurar por inputs
            print("\n6. Analisando campos de input...")
            inputs = scraper.driver.find_elements("xpath", "//input")
            for i, inp in enumerate(inputs):
                input_type = inp.get_attribute('type')
                input_class = inp.get_attribute('class')
                input_id = inp.get_attribute('id')
                input_name = inp.get_attribute('name')
                input_placeholder = inp.get_attribute('placeholder')
                
                print(f"   Input {i+1}: type={input_type}, class={input_class}, id={input_id}, name={input_name}, placeholder={input_placeholder}")
            
            # Procurar por botões
            print("\n7. Analisando botões...")
            buttons = scraper.driver.find_elements("xpath", "//button")
            for i, btn in enumerate(buttons):
                button_text = btn.text
                button_class = btn.get_attribute('class')
                button_id = btn.get_attribute('id')
                
                print(f"   Botão {i+1}: texto='{button_text}', class={button_class}, id={button_id}")
            
            # Procurar por elementos com classes específicas
            print("\n8. Analisando classes CSS...")
            important_classes = ['form-control', 'btn', 'team', 'match', 'odds', 'price', 'stake']
            
            for class_name in important_classes:
                elements = scraper.driver.find_elements("css selector", f".{class_name}")
                if elements:
                    print(f"✓ Classe '{class_name}' encontrada em {len(elements)} elemento(s)")
                else:
                    print(f"❌ Classe '{class_name}' não encontrada")
            
            print("\n✅ Debug concluído!")
            print("📁 Verifique o arquivo debug_page.html para análise detalhada")
            
        else:
            print("❌ Falha no login")
            
    except Exception as e:
        print(f"❌ Erro durante debug: {str(e)}")
        
    finally:
        if scraper:
            print("\n9. Fechando scraper...")
            scraper.close()
            print("✓ Scraper fechado")

if __name__ == "__main__":
    debug_page()
