FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN apt-get update && apt-get install -y nginx certbot cron procps && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /etc/nginx/conf.d && rm -f /etc/nginx/conf.d/*

RUN mkdir -p /var/www/certbot

RUN mkdir -p /var/www/certbot/.well-known/acme-challenge

RUN chmod +x docker-entrypoint.sh

CMD ["/bin/bash", "docker-entrypoint.sh"]
