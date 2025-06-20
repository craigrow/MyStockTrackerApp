from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()

def create_app(config_name="development"):
    app = Flask(__name__)
    
    # Configuration
    if config_name == "development":
        app.config.from_object('app.config.DevelopmentConfig')
    elif config_name == "testing":
        app.config.from_object('app.config.TestingConfig')
    else:
        app.config.from_object('app.config.ProductionConfig')
    
    # Initialize extensions
    db.init_app(app)
    
    # Register blueprints
    from app.views.main import main_blueprint
    app.register_blueprint(main_blueprint)
    
    return app