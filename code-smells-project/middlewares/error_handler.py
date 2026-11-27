"""Tratamento de erro central: exceções de domínio viram resposta, o resto vira 500 genérico."""
import logging

from flask import jsonify
from werkzeug.exceptions import HTTPException

from middlewares.erros import ErroAplicacao

logger = logging.getLogger(__name__)


def registrar_tratamento_de_erros(app):
    @app.errorhandler(ErroAplicacao)
    def tratar_erro_de_aplicacao(erro):
        return jsonify({"erro": erro.mensagem, **erro.extras}), erro.status_code

    @app.errorhandler(HTTPException)
    def tratar_erro_http(erro):
        return erro  # respostas padrão do Flask (rota inexistente, método não permitido)

    @app.errorhandler(Exception)
    def tratar_erro_inesperado(_erro):
        logger.exception("Erro não tratado")
        return jsonify({"erro": "Erro interno do servidor"}), 500
