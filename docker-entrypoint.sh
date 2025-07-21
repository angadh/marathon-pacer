#!/bin/bash
set -e

gunicorn -c gunicorn_config.py wsgi:app &

# Bring NGINX to foreground
nginx -g "daemon off;"
