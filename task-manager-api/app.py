"""Composition root: monta as camadas da aplicação e inicia o servidor."""
import logging

from flask import Flask
from flask_cors import CORS

import database
from config.settings import Settings
from middlewares.error_handler import register_error_handlers
from routes.category_routes import category_bp
from routes.report_routes import report_bp
from routes.status_routes import status_bp
from routes.task_routes import task_bp
from routes.user_routes import user_bp

BLUEPRINTS = (task_bp, user_bp, report_bp, category_bp, status_bp)


def create_app(settings=Settings):
    app = Flask(__name__)
    app.config.from_object(settings)
    logging.basicConfig(
        level=app.config['LOG_LEVEL'],
        format='%(asctime)s %(levelname)s %(name)s: %(message)s',
    )

    CORS(app, origins=app.config['CORS_ORIGINS'])
    database.init_app(app)
    for blueprint in BLUEPRINTS:
        app.register_blueprint(blueprint)
    register_error_handlers(app)
    return app


app = create_app()

if __name__ == '__main__':
    app.run(debug=app.config['DEBUG'], host=app.config['HOST'], port=app.config['PORT'])
