from flask import Blueprint, jsonify, request

bp = Bluepring('api', __name__, url_prefix='/api')

@app.route('/')
def index():
	return 'Index Page'
