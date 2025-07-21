FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN apt-get update && apt-get install -y nginx procps && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /etc/nginx/conf.d && rm -f /etc/nginx/conf.d/*

RUN chmod +x docker-entrypoint.sh

CMD ["/bin/bash", "docker-entrypoint.sh"]
