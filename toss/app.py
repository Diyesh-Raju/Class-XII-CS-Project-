import os
import sys
# PATH PATCH: Explicitly tells Python to look inside the active root folder for modules
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from config import Config

# Initialize our infrastructure tool handles globally
db = SQLAlchemy()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Enable networking handshakes so your teammates can hit your endpoints
    CORS(app)
    
    # Connect our extension engines to our active application loop
    db.init_app(app)
    jwt.init_app(app)
    
    with app.app_context():
        # 1. Import our database tables so Flask registers them
        from models.models import User, City, AttackLog, DefenseLog, GPSPoint
        
        # 2. Tell SQLite to build the mileage_wars.db file with all relational tables
        db.create_all()
        
        # 3. Register Authentication Router
        from routes.auth import auth_bp
        app.register_blueprint(auth_bp, url_prefix='/api/auth')
        
        # 4. Register Core Gameplay Fitness Router
        from routes.fitness import fitness_bp
        app.register_blueprint(fitness_bp, url_prefix='/api/fitness')

        # 5. Register Master Sync & Notification System
        from routes.game import game_bp
        app.register_blueprint(game_bp, url_prefix='/api/game')
        
    return app

if __name__ == "__main__":
    app = create_app()
    # Boots up on port 5000 with dynamic reload monitoring turned on
    app.run(debug=True, port=5000)