#!/bin/bash
set -e

# Start the Flask app
gunicorn -c gunicorn_config.py wsgi:app &

# Start Nginx
nginx -g "daemon off;"
