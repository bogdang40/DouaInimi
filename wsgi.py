"""WSGI entry point for production deployment."""
import os
from app import create_app, socketio
from app.extensions import db
from sqlalchemy import text

# Use FLASK_ENV or default to production for Azure
config_name = os.environ.get('FLASK_ENV', 'production')
app = create_app(config_name)

# Auto-create database tables and add missing columns on startup
with app.app_context():
    try:
        # Create any missing tables
        db.create_all()
        print("✅ Database tables created/verified")
        
        # Add missing columns to existing tables (PostgreSQL)
        migrations = [
            # Users table - add is_approved column
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS is_approved BOOLEAN DEFAULT TRUE",
            
            # Reports table - add new columns
            "ALTER TABLE reports ADD COLUMN IF NOT EXISTS description TEXT",
            "ALTER TABLE reports ADD COLUMN IF NOT EXISTS resolved_by_id INTEGER",
            "ALTER TABLE reports ADD COLUMN IF NOT EXISTS resolved_at TIMESTAMP",
            "ALTER TABLE reports ADD COLUMN IF NOT EXISTS resolution_notes TEXT",
            
            # Create passes table if not exists
            """CREATE TABLE IF NOT EXISTS passes (
                id SERIAL PRIMARY KEY,
                passer_id INTEGER NOT NULL REFERENCES users(id),
                passed_id INTEGER NOT NULL REFERENCES users(id),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(passer_id, passed_id)
            )""",
        ]
        
        for migration in migrations:
            try:
                db.session.execute(text(migration))
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                # Ignore errors for columns/tables that already exist
                pass
        
        print("✅ Database migrations applied")
        
    except Exception as e:
        print(f"⚠️ Database init warning: {e}")

if __name__ == "__main__":
    socketio.run(app, debug=False)

