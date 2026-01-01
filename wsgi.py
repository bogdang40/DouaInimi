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

            # Performance indices for messages
            "CREATE INDEX IF NOT EXISTS ix_messages_match_id ON messages(match_id)",
            "CREATE INDEX IF NOT EXISTS ix_messages_sender_id ON messages(sender_id)",
            "CREATE INDEX IF NOT EXISTS ix_messages_unread ON messages(match_id, sender_id, is_read)",
            "CREATE INDEX IF NOT EXISTS ix_messages_match_created ON messages(match_id, created_at)",

            # Performance indices for matches
            "CREATE INDEX IF NOT EXISTS ix_matches_user1_id ON matches(user1_id)",
            "CREATE INDEX IF NOT EXISTS ix_matches_user2_id ON matches(user2_id)",
            "CREATE INDEX IF NOT EXISTS ix_matches_is_active ON matches(is_active)",
            "CREATE INDEX IF NOT EXISTS ix_matches_user1_active ON matches(user1_id, is_active)",
            "CREATE INDEX IF NOT EXISTS ix_matches_user2_active ON matches(user2_id, is_active)",

            # Performance indices for likes
            "CREATE INDEX IF NOT EXISTS ix_likes_liker_id ON likes(liker_id)",
            "CREATE INDEX IF NOT EXISTS ix_likes_liked_id ON likes(liked_id)",
            "CREATE INDEX IF NOT EXISTS ix_likes_created_at ON likes(created_at)",
            "CREATE INDEX IF NOT EXISTS ix_likes_super ON likes(liker_id, is_super_like, created_at)",
            "CREATE INDEX IF NOT EXISTS ix_likes_received ON likes(liked_id, created_at)",

            # Performance indices for reports
            "CREATE INDEX IF NOT EXISTS ix_reports_reporter_id ON reports(reporter_id)",
            "CREATE INDEX IF NOT EXISTS ix_reports_reported_id ON reports(reported_id)",
            "CREATE INDEX IF NOT EXISTS ix_reports_status ON reports(status)",
            "CREATE INDEX IF NOT EXISTS ix_reports_reported_status ON reports(reported_id, status)",

            # Performance indices for blocks
            "CREATE INDEX IF NOT EXISTS ix_blocks_blocker_id ON blocks(blocker_id)",
            "CREATE INDEX IF NOT EXISTS ix_blocks_blocked_id ON blocks(blocked_id)",

            # Performance indices for passes
            "CREATE INDEX IF NOT EXISTS ix_passes_passer_id ON passes(passer_id)",
            "CREATE INDEX IF NOT EXISTS ix_passes_passed_id ON passes(passed_id)",

            # Orthodox-specific profile fields
            "ALTER TABLE profiles ADD COLUMN IF NOT EXISTS church_attire_women VARCHAR(30)",
            "ALTER TABLE profiles ADD COLUMN IF NOT EXISTS modesty_level VARCHAR(30)",
            "ALTER TABLE profiles ADD COLUMN IF NOT EXISTS confession_frequency VARCHAR(30)",
            "ALTER TABLE profiles ADD COLUMN IF NOT EXISTS communion_frequency VARCHAR(30)",
            "ALTER TABLE profiles ADD COLUMN IF NOT EXISTS icons_in_home BOOLEAN DEFAULT TRUE",
            "ALTER TABLE profiles ADD COLUMN IF NOT EXISTS saints_nameday VARCHAR(100)",
            "ALTER TABLE profiles ADD COLUMN IF NOT EXISTS marital_history VARCHAR(30)",
            "ALTER TABLE profiles ADD COLUMN IF NOT EXISTS desired_children_count VARCHAR(20)",
            "ALTER TABLE profiles ADD COLUMN IF NOT EXISTS children_education_preference VARCHAR(50)",
            "ALTER TABLE profiles ADD COLUMN IF NOT EXISTS seeks_modest_spouse BOOLEAN DEFAULT FALSE",
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

