from flask import Flask

def create_app():
	app = Flask(_name_)
	app.config.from_object('app.config.Config')

	from . import models, routes
	app.register_blueprint(routes.bp)

	return app
