# Gunicorn configuration file
# Azure App Service will automatically pick this up

# Binding
bind = "0.0.0.0:8000"

# Workers - use multiple workers for parallel request handling
# Rule of thumb: (2 x CPU cores) + 1
workers = 4

# Worker class - use gevent for async I/O (required for Socket.IO)
# gevent enables cooperative multitasking, allowing thousands of concurrent connections
worker_class = "gevent"

# Gevent worker connections - how many simultaneous connections per worker
worker_connections = 1000

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
# Note: With gevent, preload_app=True can cause issues with monkey-patching
preload_app = False

