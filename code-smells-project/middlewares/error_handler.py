"""Tratamento de erro central."""
import logging

from flask import jsonify
from werkzeug.exceptions import HTTPException

from middlewares.erros import ErroAplicacao

logger = logging.getLogger(__name__)

MENSAGEM_ERRO_INTERNO = "Erro interno do servidor"


def registrar_tratadores_de_erro(app):
    @app.errorhandler(ErroAplicacao)
    def tratar_erro_aplicacao(erro):
        return jsonify({"erro": erro.mensagem, **erro.extras}), erro.status_code

    @app.errorhandler(HTTPException)
    def tratar_erro_http(erro):
        # Mantém as respostas padrão do framework (404 de rota, 405).
        return erro

    @app.errorhandler(Exception)
    def tratar_erro_inesperado(erro):
        logger.exception("Erro não tratado")
        return jsonify({"erro": MENSAGEM_ERRO_INTERNO}), 500
