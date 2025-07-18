#!/bin/bash
set -e

# Create required directories for webroot challenge
mkdir -p /var/www/certbot/.well-known/acme-challenge

# Start NGINX in the background to handle HTTP-01 challenge
nginx &

# Wait a bit for NGINX to fully start
sleep 3

# Run certbot to obtain certificate (will only run if not already valid)
if [ ! -f /etc/letsencrypt/live/marathon-pacer.com/fullchain.pem ]; then
    certbot certonly --webroot \
        --webroot-path=/var/www/certbot \
        --email angadh.singh@gmail.com \
        --agree-tos --no-eff-email \
        -d marathon-pacer.com
fi

# Start cron to renew cert every night at 3am
echo "0 3 * * * certbot renew --quiet --webroot --webroot-path=/var/www/certbot --deploy-hook 'nginx -s reload'" | crontab -
cron
# Start Gunicorn in background
gunicorn -c gunicorn_config.py wsgi:app &

# Bring NGINX to foreground
wait %1
