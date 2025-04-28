FROM python:3.12-slim

WORKDIR /radar


RUN apt-get update && apt-get install -y \
    gcc \
    && apt-get auto-remove -y \
    && rm -rf /var/lib/apt/lists/*


COPY requirements.txt .env /radar

RUN pip install --no-cache-dir  --upgrade pip \
    && pip install  --no-cache-dir -r requirements.txt

COPY app /radar/app

EXPOSE 8000

CMD [ "uvicorn", "app.main:app" ]
