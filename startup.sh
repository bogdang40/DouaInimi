#!/bin/bash

# Azure App Service startup script
# This ensures our gunicorn.conf.py is used

# Run gunicorn with our config file
gunicorn --config gunicorn.conf.py wsgi:app
