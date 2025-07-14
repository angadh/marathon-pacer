#!/bin/bash
set -e

# Start Gunicorn in foreground
gunicorn -c gunicorn_config.py wsgi:app

# Start NGINX in foreground
nginx -g 'daemon off;'
