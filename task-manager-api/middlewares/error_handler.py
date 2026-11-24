"""Tratamento de erro central: único lugar que converte exceções em respostas."""
from flask import jsonify
from werkzeug.exceptions import HTTPException

from middlewares.errors import AppError


def register_error_handlers(app):
    @app.errorhandler(AppError)
    def handle_app_error(error):
        return jsonify({'error': error.message}), error.status_code

    @app.errorhandler(HTTPException)
    def handle_http_error(error):
        # Mantém as respostas padrão do framework (404 de rota, 405, 415).
        return error

    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        app.logger.exception('Erro não tratado')
        return jsonify({'error': 'Erro interno'}), 500
