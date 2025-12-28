"""WSGI entry point for production deployment."""
import os
from app import create_app, socketio
from app.extensions import db

# Use FLASK_ENV or default to production for Azure
config_name = os.environ.get('FLASK_ENV', 'production')
app = create_app(config_name)

# Auto-create database tables on startup (for Azure deployment)
with app.app_context():
    try:
        db.create_all()
        print("✅ Database tables created/verified")
    except Exception as e:
        print(f"⚠️ Database init warning: {e}")

if __name__ == "__main__":
    socketio.run(app, debug=False)

