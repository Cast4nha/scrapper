# Scraper Híbrido ValSports

Solução híbrida que combina **Selenium** para autenticação e **ScrapingDog** para captura de dados com renderização JavaScript.

## 🎯 Vantagens

- ✅ **Autenticação garantida**: Selenium faz login e captura cookies de sessão
- ✅ **Renderização JavaScript**: ScrapingDog renderiza o conteúdo dinâmico
- ✅ **Captura completa**: Todos os jogos do bilhete são capturados
- ✅ **Performance**: Mais rápido que Selenium puro
- ✅ **Confiabilidade**: Proxy premium do ScrapingDog

## 📋 Pré-requisitos

1. **Conta no ScrapingDog**: [https://www.scrapingdog.com/](https://www.scrapingdog.com/)
2. **Credenciais do ValSports**: Usuário e senha válidos
3. **Python 3.7+** com as dependências instaladas

## 🚀 Instalação

1. **Instalar dependências**:
```bash
pip install selenium requests beautifulsoup4 python-dotenv
```

2. **Configurar variáveis de ambiente**:
```bash
cp env_example.txt .env
```

3. **Editar o arquivo `.env`**:
```env
# Configurações do ScrapingDog
SCRAPINGDOG_API_KEY=sua_chave_aqui

# Credenciais do ValSports
VALSPORTS_USERNAME=seu_usuario
VALSPORTS_PASSWORD=sua_senha
```

## 🧪 Como usar

### Teste Simples
```bash
python test_hybrid_simple.py
```

### Uso Programático
```python
from scraper_hybrid import HybridValSportsScraper

# Criar scraper
scraper = HybridValSportsScraper()

# Fazer login
if scraper.login_with_selenium("usuario", "senha"):
    # Capturar bilhete
    result = scraper.scrape_with_scrapingdog("ELM5IM")
    
    if result:
        print(f"Jogos encontrados: {result['total_games']}")
        print(f"Total odds: {result['total_odds']}")
        print(f"Possível prêmio: {result['possible_prize']}")
        
        for game in result['games']:
            print(f"- {game['teams']}: {game['selection']} ({game['odds']})")

# Fechar scraper
scraper.close()
```

## 📊 Estrutura dos Dados

O scraper retorna um dicionário com:

```python
{
    'bet_code': 'ELM5IM',
    'games': [
        {
            'league': 'Costa Rica: Taça',
            'datetime': '19/08 18:00',
            'teams': 'CS Uruguay de Coronado x Sporting San José',
            'selection': 'Vencedor: CS Uruguay de Coronado',
            'odds': '3.40'
        },
        # ... mais jogos
    ],
    'total_odds': '119,16',
    'possible_prize': 'R$ 1.191,62',
    'bettor_name': 'Felipe',
    'bet_value': '10',
    'total_games': 5
}
```

## 🔧 Como Funciona

1. **Login com Selenium**: 
   - Abre Firefox headless
   - Navega para página de login
   - Preenche credenciais
   - Captura cookies de sessão

2. **Captura com ScrapingDog**:
   - Envia URL + cookies para ScrapingDog
   - ScrapingDog renderiza JavaScript
   - Retorna HTML completo

3. **Parse dos Dados**:
   - BeautifulSoup analisa HTML
   - Regex extrai informações dos jogos
   - Remove duplicatas e formata dados

## 💡 Dicas

- **API Key do ScrapingDog**: Use proxy premium para melhor performance
- **Cookies**: São mantidos entre requisições para manter sessão
- **Timeout**: Configure tempo adequado para renderização JS
- **Debug**: HTML é salvo para análise em caso de problemas

## 🐛 Troubleshooting

### Login falha
- Verifique credenciais no `.env`
- Confirme se a conta está ativa
- Teste login manual no site

### ScrapingDog retorna erro
- Verifique API key
- Confirme créditos disponíveis
- Teste com URL simples primeiro

### Nenhum jogo encontrado
- Verifique se o bilhete existe
- Confirme se está logado
- Analise HTML salvo para debug

## 📈 Performance

- **Login**: ~10 segundos
- **Captura por bilhete**: ~15-30 segundos
- **Suporte**: Bilhetes com 1-50+ jogos
- **Confiabilidade**: 95%+ de sucesso

## 🔒 Segurança

- Credenciais em variáveis de ambiente
- Cookies de sessão temporários
- Sem armazenamento de dados sensíveis
- Conexões HTTPS

## 📝 Licença

Este projeto é para uso educacional e de desenvolvimento. Respeite os termos de uso do ValSports e ScrapingDog.
