#!/bin/sh
set -e

# Wait for NGINX to fully start
sleep 10

# 1. Request the cert
certbot certonly --webroot \
    --webroot-path=/var/www/certbot \
    --email angadh.singh@gmail.com --agree-tos --no-eff-email \
    -d marathon-pacer.com \
    --force-renewal

echo "[INFO] Certificate obtained successfully. NGINX is configured for HTTPS."