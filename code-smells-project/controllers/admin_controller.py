"""Fluxo HTTP das operações administrativas."""
import logging

from flask import jsonify

logger = logging.getLogger(__name__)


class AdminController:
    def __init__(self, admin_model):
        self._admin_model = admin_model

    def resetar_banco(self):
        self._admin_model.resetar_dados()
        logger.warning("Banco de dados resetado")
        return jsonify({"mensagem": "Banco de dados resetado", "sucesso": True}), 200
