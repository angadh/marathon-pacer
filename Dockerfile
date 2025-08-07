FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN apt-get update && apt-get install -y nginx procps gcc linux-libc-dev musl-tools && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /etc/nginx/conf.d && rm -f /etc/nginx/conf.d/*

ENV FLASK_RUN_HOST=0.0.0.0
EXPOSE 5000

RUN chmod +x docker-entrypoint.sh

CMD ["/bin/bash", "docker-entrypoint.sh"]
