from flask import Flask
from .extensions import db, migrate

def create_app():
	app = Flask(_name_)
	app.config.from_object('app.config.Config')

	db.init_app(app)
	migrate.init_app(app, db)

	from . import models, routes
	app.register_blueprint(routes.bp)

	return app
