FROM python:3.12-slim

# Cria usuário e grupo 'radar'
RUN groupadd -r radar && useradd --no-log-init -r -g radar radar

WORKDIR /radar


RUN apt-get update && apt-get install -y \
    gcc vim \
    && apt-get auto-remove -y \
    && rm -rf /var/lib/apt/lists/*


COPY requirements.txt /radar

RUN pip install --no-cache-dir  --upgrade pip \
    && pip install  --no-cache-dir -r requirements.txt

COPY app /radar/app

# Ajusta permissões para o usuário 'radar'
RUN chown -R radar:radar /radar

USER radar

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "5"]


