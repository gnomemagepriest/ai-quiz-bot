from flask import Flask
from .admin import create_admin
from flask_jwt_extended import JWTManager
from .extensions import db, migrate

def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')
    
    app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'  # Change this!
    jwt = JWTManager(app)

    db.init_app(app)
    migrate.init_app(app, db)

    create_admin(app)

    from . import models, routes
    app.register_blueprint(routes.bp)

    return app
