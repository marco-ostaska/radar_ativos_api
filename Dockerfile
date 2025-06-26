FROM python:3.12-alpine

# Configura o timezone para Brasil (America/Sao_Paulo)
ENV TZ=America/Sao_Paulo
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Cria usuário e grupo 'radar'
RUN addgroup -S radar && adduser -S radar -G radar

WORKDIR /radar


RUN apk add --no-cache \
    gcc \
    musl-dev \
    libffi-dev \
    && rm -rf /var/cache/apk/*


COPY requirements.txt /radar

RUN pip install --no-cache-dir  --upgrade pip \
    && pip install  --no-cache-dir -r requirements.txt

COPY app /radar/app

# Ajusta permissões para o usuário 'radar'
RUN chown -R radar:radar /radar

USER radar

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "5"]
