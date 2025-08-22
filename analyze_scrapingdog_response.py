#!/usr/bin/env python3
"""
Analisa a resposta do ScrapingDog
"""

import os
import glob
from bs4 import BeautifulSoup

def analyze_scrapingdog_response():
    """Analisa a resposta do ScrapingDog"""
    print("🔍 ANALISANDO RESPOSTA DO SCRAPINGDOG")
    print("=" * 50)
    
    # Encontrar arquivo de resposta
    response_files = glob.glob("scrapingdog_response_*.html")
    
    if not response_files:
        print("❌ Nenhum arquivo de resposta encontrado")
        return
    
    response_file = response_files[0]
    print(f"📄 Analisando: {response_file}")
    
    try:
        # Ler arquivo
        with open(response_file, 'r', encoding='utf-8', errors='ignore') as f:
            html_content = f.read()
        
        print(f"📏 Tamanho do HTML: {len(html_content)} caracteres")
        
        # Parsear HTML
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Verificar título
        title = soup.title.string if soup.title else "Sem título"
        print(f"📰 Título: {title}")
        
        # Verificar URL atual
        current_url = soup.find('meta', {'property': 'og:url'})
        if current_url:
            print(f"🌐 URL: {current_url.get('content')}")
        
        # Procurar por elementos de bilhete
        print("\n🔍 PROCURANDO ELEMENTOS DO BILHETE:")
        print("-" * 40)
        
        # Procurar por containers de jogos
        game_containers = soup.find_all(['div', 'section'], class_=lambda x: x and any(word in x.lower() for word in ['game', 'bet', 'item', 'ticket']))
        print(f"🎮 Containers de jogos encontrados: {len(game_containers)}")
        
        # Procurar por texto que contenha padrões de jogos
        text_content = soup.get_text()
        
        # Padrões para encontrar jogos
        import re
        
        patterns = [
            r'([A-Za-zÀ-ÿ\s]+):\s*([A-Za-zÀ-ÿ\s]+)\s+(\d{2}/\d{2}\s+\d{2}:\d{2})',
            r'([A-Za-zÀ-ÿ\s]+)\s+x\s+([A-Za-zÀ-ÿ\s]+)',
            r'Vencedor:\s*([A-Za-zÀ-ÿ\s]+)',
            r'(\d+\.\d+)',  # Odds
            r'Total odds\s*(\d+[,\d]*)',
            r'Possível prêmio\s*(R\$\s*\d+[,\d]*)'
        ]
        
        print("\n🔍 PADRÕES ENCONTRADOS:")
        print("-" * 30)
        
        for i, pattern in enumerate(patterns):
            matches = re.findall(pattern, text_content, re.MULTILINE)
            if matches:
                print(f"Padrão {i+1}: {len(matches)} matches")
                for match in matches[:3]:  # Mostrar apenas os primeiros 3
                    print(f"   - {match}")
                if len(matches) > 3:
                    print(f"   ... e mais {len(matches) - 3}")
            else:
                print(f"Padrão {i+1}: Nenhum match")
        
        # Procurar por inputs
        inputs = soup.find_all('input')
        print(f"\n📝 Inputs encontrados: {len(inputs)}")
        
        for i, input_elem in enumerate(inputs):
            input_type = input_elem.get('type', '')
            input_placeholder = input_elem.get('placeholder', '')
            input_value = input_elem.get('value', '')
            
            if input_placeholder or input_value:
                print(f"   Input {i+1}: tipo={input_type}, placeholder='{input_placeholder}', value='{input_value}'")
        
        # Procurar por botões
        buttons = soup.find_all('button')
        print(f"\n🔘 Botões encontrados: {len(buttons)}")
        
        for i, button in enumerate(buttons):
            button_text = button.get_text(strip=True)
            button_class = button.get('class', [])
            if button_text:
                print(f"   Botão {i+1}: '{button_text}' (classes: {button_class})")
        
        # Verificar se há redirecionamento ou erro
        error_indicators = ['error', 'not found', '404', 'access denied', 'forbidden']
        for indicator in error_indicators:
            if indicator in text_content.lower():
                print(f"\n⚠️  Indicador de erro encontrado: '{indicator}'")
        
        # Salvar texto limpo para análise
        clean_text_file = "scrapingdog_clean_text.txt"
        with open(clean_text_file, 'w', encoding='utf-8') as f:
            f.write(text_content)
        print(f"\n📄 Texto limpo salvo em: {clean_text_file}")
        
        print("\n✅ Análise concluída!")
        
    except Exception as e:
        print(f"❌ Erro ao analisar: {str(e)}")

if __name__ == "__main__":
    analyze_scrapingdog_response()
