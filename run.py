"""Development server runner."""
import os
import click

# Run database migrations BEFORE importing Flask app (for Azure)
def run_migrations():
    """Run database migrations using raw psycopg2 connection."""
    database_url = os.environ.get('DATABASE_URL')
    if not database_url or 'sqlite' in database_url.lower():
        print("⚠️ SQLite or no DATABASE_URL, skipping PostgreSQL migrations")
        return
    
    try:
        import psycopg2
        
        print("🔄 Running database migrations...")
        conn = psycopg2.connect(database_url)
        conn.autocommit = True
        cursor = conn.cursor()
        
        migrations = [
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS is_approved BOOLEAN DEFAULT TRUE",
            "UPDATE users SET is_approved = TRUE WHERE is_approved IS NULL OR is_approved = FALSE",  # Auto-approve existing users
            "ALTER TABLE reports ADD COLUMN IF NOT EXISTS description TEXT",
            "ALTER TABLE reports ADD COLUMN IF NOT EXISTS resolved_by_id INTEGER",
            "ALTER TABLE reports ADD COLUMN IF NOT EXISTS resolved_at TIMESTAMP",
            "ALTER TABLE reports ADD COLUMN IF NOT EXISTS resolution_notes TEXT",
        ]
        
        for sql in migrations:
            try:
                cursor.execute(sql)
                print(f"✅ {sql[:60]}...")
            except Exception as e:
                print(f"⚠️ {str(e)[:50]}")
        
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
            print("✅ Passes table ready")
        except Exception as e:
            print(f"⚠️ Passes: {str(e)[:50]}")
        
        cursor.close()
        conn.close()
        print("✅ Database migrations complete!")
        
    except Exception as e:
        print(f"⚠️ Migration error: {e}")

# Run migrations before app import
run_migrations()

from app import create_app, socketio
from app.extensions import db

# Use production config if FLASK_ENV is set, otherwise development
config_name = os.environ.get('FLASK_ENV', 'development')
app = create_app(config_name)


@app.cli.command('make-admin')
@click.argument('email')
def make_admin(email):
    """Make a user an admin by their email."""
    from app.models.user import User
    
    with app.app_context():
        user = User.query.filter_by(email=email).first()
        if not user:
            click.echo(f"❌ User with email '{email}' not found.")
            return
        
        user.is_admin = True
        user.is_approved = True  # Also approve them
        db.session.commit()
        click.echo(f"✅ User '{email}' is now an admin!")


@app.cli.command('approve-all')
def approve_all():
    """Approve all pending users."""
    from app.models.user import User
    
    with app.app_context():
        pending = User.query.filter_by(is_approved=False).all()
        count = len(pending)
        for user in pending:
            user.is_approved = True
        db.session.commit()
        click.echo(f"✅ Approved {count} users!")


if __name__ == '__main__':
    print("🚀 Starting Romanian Christian Dating App...")
    print("📍 Open http://localhost:5001 in your browser")
    print("📍 Admin panel: http://localhost:5001/admin")
    print("-" * 50)
    socketio.run(app, debug=True, host='0.0.0.0', port=5001)

