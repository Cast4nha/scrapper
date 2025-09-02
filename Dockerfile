# Dockerfile para ValSports Capture Service
FROM python:3.9-slim

# Variáveis de ambiente
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV DEBIAN_FRONTEND=noninteractive

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Instalar Firefox ESR usando método moderno
RUN wget -qO- https://packages.mozilla.org/apt/repo-signing-key.gpg | gpg --dearmor -o /usr/share/keyrings/mozilla-archive-keyring.gpg \
    && echo "deb [signed-by=/usr/share/keyrings/mozilla-archive-keyring.gpg] https://packages.mozilla.org/apt/ firefox-esr main" | tee /etc/apt/sources.list.d/firefox-esr.list \
    && apt-get update \
    && apt-get install -y firefox-esr \
    && rm -rf /var/lib/apt/lists/*

# Instalar GeckoDriver
RUN wget -q https://github.com/mozilla/geckodriver/releases/download/v0.33.0/geckodriver-v0.33.0-linux64.tar.gz \
    && tar -xzf geckodriver-v0.33.0-linux64.tar.gz \
    && mv geckodriver /usr/local/bin/ \
    && chmod +x /usr/local/bin/geckodriver \
    && rm geckodriver-v0.33.0-linux64.tar.gz

# Criar diretório de trabalho
WORKDIR /app

# Copiar requirements primeiro para aproveitar cache do Docker
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY . .

# Criar diretório para logs
RUN mkdir -p /app/logs

# Expor porta
EXPOSE 5000

# Comando para executar o serviço
CMD ["python3", "api_capture_service_final.py"]
