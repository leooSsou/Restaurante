FROM python:3.12-slim

# Evita que o Python escreva arquivos .pyc no disco
ENV PYTHONDONTWRITEBYTECODE=1
# Evita que o Python faça buffer do stdout e stderr
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Instala dependências do sistema necessárias se houver
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copia e instala requisitos de dependência
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do código (em desenvolvimento isso será sobrescrito pelo volume)
COPY . .

EXPOSE 8000

CMD ["uvicorn", "src.infrastructure.web.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
