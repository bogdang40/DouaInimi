# Gunicorn configuration file for Azure App Service

# Binding
bind = "0.0.0.0:8000"

# Workers and threads - optimized for Azure App Service
# More workers + threads = more concurrent request handling
workers = 4
threads = 4  # 4 workers x 4 threads = 16 concurrent requests

# Worker class - use gthread (threaded) for best Azure compatibility
# This supports concurrent requests without needing gevent/eventlet
worker_class = "gthread"

# Timeouts
timeout = 120  # Worker timeout (seconds)
graceful_timeout = 30  # Graceful shutdown timeout
keepalive = 5  # Keep connections alive for this many seconds

# Logging
accesslog = "-"  # Log to stdout
errorlog = "-"   # Log to stderr
loglevel = "info"

# Performance tuning
max_requests = 1000  # Restart workers after this many requests (prevents memory leaks)
max_requests_jitter = 50  # Add randomness to prevent all workers restarting at once

# Preload app for faster worker spawning
preload_app = False

