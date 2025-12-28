"""WSGI entry point for production deployment."""
import os
from app import create_app, socketio

# Use FLASK_ENV or default to production for Azure
config_name = os.environ.get('FLASK_ENV', 'production')
app = create_app(config_name)

if __name__ == "__main__":
    socketio.run(app, debug=False)

