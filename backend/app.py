from flask import Flask
from flask_cors import CORS
from config import Config

# Import blueprints
from routes.auth import auth_bp
from routes.survey import survey_bp
from routes.region import region_bp
from routes.action import action_bp
from routes.wilayah import wilayah_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize config
    Config.init_app(app)
    
    # Enable CORS for React frontend
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:5173", "http://127.0.0.1:5173"],
            "methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": ["Content-Type"]
        }
    })
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(survey_bp, url_prefix='/api/surveys')
    app.register_blueprint(region_bp, url_prefix='/api/regions')
    app.register_blueprint(action_bp, url_prefix='/api/action')
    app.register_blueprint(wilayah_bp, url_prefix='/api/wilayah')
    
    @app.route('/')
    def index():
        return {'message': 'FASIH-SM API Server', 'status': 'running'}
    
    return app


if __name__ == '__main__':
    import socket
    
    def get_local_ip():
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "localhost"
    
    local_ip = get_local_ip()
    app = create_app()
    
    print("=" * 50)
    print("🚀 FASIH-SM Backend Server")
    print("=" * 50)
    print(f"📍 Local:   http://localhost:5000")
    print(f"📍 Network: http://{local_ip}:5000")
    print("=" * 50)
    print("⚠️  Pastikan frontend API_URL menggunakan IP yang sama")
    print("=" * 50)
    
    app.run(host='0.0.0.0', debug=True, port=5000, threaded=True)
