"""Fluxo HTTP das rotas administrativas (protegidas por token nas rotas)."""
import logging

from flask import jsonify

from controllers.validacao import exigir_texto, ler_corpo_json
from middlewares.erros import ErroValidacao

logger = logging.getLogger(__name__)

PREFIXO_CONSULTA = "SELECT"


class AdminController:
    def __init__(self, admin_model):
        self._admin_model = admin_model

    def resetar_banco(self):
        self._admin_model.resetar_dados()
        logger.warning("Banco de dados resetado por rota administrativa")
        return jsonify({"mensagem": "Banco de dados resetado", "sucesso": True}), 200

    def executar_query(self):
        dados = ler_corpo_json()
        sql = dados.get("sql", "")
        if not sql:
            raise ErroValidacao("Query não informada")
        exigir_texto(sql, "Query inválida")

        logger.warning("Query administrativa executada")
        if sql.strip().upper().startswith(PREFIXO_CONSULTA):
            linhas = self._admin_model.consultar(sql)
            return jsonify({"dados": linhas, "sucesso": True}), 200
        self._admin_model.executar(sql)
        return jsonify({"mensagem": "Query executada", "sucesso": True}), 200
