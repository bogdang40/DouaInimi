# Gunicorn configuration file
# Azure App Service will automatically pick this up

# Binding
bind = "0.0.0.0:8000"

# Workers and threads - critical for Socket.IO performance
# With threading mode, we need threads to handle concurrent polling requests
workers = 2
threads = 4

# Timeouts
timeout = 120  # Worker timeout (seconds)
graceful_timeout = 30  # Graceful shutdown timeout
keepalive = 5  # Keep connections alive for this many seconds

# Worker class - use sync with threads (most compatible with Azure)
worker_class = "sync"

# Logging
accesslog = "-"  # Log to stdout
errorlog = "-"   # Log to stderr
loglevel = "info"

# Performance tuning
worker_connections = 1000
max_requests = 1000  # Restart workers after this many requests (prevents memory leaks)
max_requests_jitter = 50  # Add randomness to prevent all workers restarting at once

# Preload app for faster worker spawning (but uses more memory)
preload_app = False

