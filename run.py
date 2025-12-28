"""Development server runner."""
import click
from app import create_app, socketio
from app.extensions import db

app = create_app('development')


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

