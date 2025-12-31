"""WSGI entry point for production deployment."""
import os

# Run database migrations BEFORE importing Flask app
# This ensures columns exist before SQLAlchemy models are loaded
def run_migrations():
    """Run database migrations using raw psycopg2 connection."""
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("⚠️ No DATABASE_URL found, skipping migrations")
        return
    
    try:
        import psycopg2
        
        # Parse the database URL
        # Format: postgresql://user:pass@host:port/dbname
        conn = psycopg2.connect(database_url)
        conn.autocommit = True
        cursor = conn.cursor()
        
        migrations = [
            # Users table - add is_approved column
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS is_approved BOOLEAN DEFAULT TRUE",
            # Users table - add account lockout columns
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS failed_login_attempts INTEGER DEFAULT 0",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS locked_until TIMESTAMP",

            # Reports table - add new columns
            "ALTER TABLE reports ADD COLUMN IF NOT EXISTS description TEXT",
            "ALTER TABLE reports ADD COLUMN IF NOT EXISTS resolved_by_id INTEGER",
            "ALTER TABLE reports ADD COLUMN IF NOT EXISTS resolved_at TIMESTAMP",
            "ALTER TABLE reports ADD COLUMN IF NOT EXISTS resolution_notes TEXT",

            # Photos table - add moderation columns
            "ALTER TABLE photos ADD COLUMN IF NOT EXISTS is_approved BOOLEAN DEFAULT FALSE",
            "ALTER TABLE photos ADD COLUMN IF NOT EXISTS moderation_status VARCHAR(20) DEFAULT 'pending'",
            "ALTER TABLE photos ADD COLUMN IF NOT EXISTS moderation_notes TEXT",
            "ALTER TABLE photos ADD COLUMN IF NOT EXISTS moderated_at TIMESTAMP",
            "ALTER TABLE photos ADD COLUMN IF NOT EXISTS moderated_by_id INTEGER REFERENCES users(id)",
        ]
        
        for sql in migrations:
            try:
                cursor.execute(sql)
                print(f"✅ Executed: {sql[:50]}...")
            except Exception as e:
                # Column might already exist
                print(f"⚠️ {e}")
        
        # Create passes table
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS passes (
                    id SERIAL PRIMARY KEY,
                    passer_id INTEGER NOT NULL REFERENCES users(id),
                    passed_id INTEGER NOT NULL REFERENCES users(id),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(passer_id, passed_id)
                )
            """)
            print("✅ Passes table created/verified")
        except Exception as e:
            print(f"⚠️ Passes table: {e}")
        
        cursor.close()
        conn.close()
        print("✅ Database migrations complete")
        
    except Exception as e:
        print(f"⚠️ Migration error: {e}")

# Run migrations before app import
run_migrations()

# Now import and create the Flask app
from app import create_app, socketio
from app.extensions import db

# Use FLASK_ENV or default to production for Azure
config_name = os.environ.get('FLASK_ENV', 'production')
app = create_app(config_name)

# Create any missing tables
with app.app_context():
    try:
        db.create_all()
        print("✅ All database tables verified")
    except Exception as e:
        print(f"⚠️ db.create_all warning: {e}")

if __name__ == "__main__":
    socketio.run(app, debug=False)

