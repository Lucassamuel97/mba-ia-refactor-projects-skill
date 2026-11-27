import logging

from flask import jsonify
from werkzeug.exceptions import HTTPException

from database import db
from middlewares.errors import AppError

logger = logging.getLogger(__name__)


def register_error_handlers(app):
    @app.errorhandler(AppError)
    def handle_app_error(error):
        return jsonify({'error': error.message}), error.status_code

    @app.errorhandler(HTTPException)
    def handle_http_error(error):
        return error  # mantém as respostas padrão do framework (404 de rota, 405, 415)

    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        db.session.rollback()
        logger.exception('Erro não tratado')
        return jsonify({'error': 'Erro interno'}), 500
