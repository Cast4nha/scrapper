# Usar imagem base do Python (sem instalar nada adicional)
FROM python:3.9-slim

# Definir diretório de trabalho
WORKDIR /app

# Copiar arquivos de dependências
COPY requirements.txt .

# Instalar apenas dependências Python essenciais
RUN pip install --no-cache-dir flask flask-cors gunicorn python-dotenv

# Copiar código da aplicação
COPY app.py .
COPY scraper/ ./scraper/

# Expor porta
EXPOSE 5000

# Comando para executar a aplicação
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "1", "--timeout", "300", "app:app"]
