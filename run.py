"""Development server runner."""
from app import create_app, socketio

app = create_app('development')

if __name__ == '__main__':
    print("🚀 Starting Romanian Christian Dating App...")
    print("📍 Open http://localhost:5001 in your browser")
    print("-" * 50)
    socketio.run(app, debug=True, host='0.0.0.0', port=5001)

