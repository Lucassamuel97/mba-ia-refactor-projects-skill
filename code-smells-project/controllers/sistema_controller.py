"""Fluxo HTTP das rotas de apresentação e de saúde da API."""
import logging

from flask import current_app, jsonify

from database.connection import ErroBancoDeDados

logger = logging.getLogger(__name__)


class SistemaController:
    def __init__(self, produto_model, usuario_model, pedido_model):
        self._produto_model = produto_model
        self._usuario_model = usuario_model
        self._pedido_model = pedido_model

    def index(self):
        return jsonify({
            "mensagem": "Bem-vindo à API da Loja",
            "versao": current_app.config["VERSAO"],
            "endpoints": {
                "produtos": "/produtos",
                "usuarios": "/usuarios",
                "pedidos": "/pedidos",
                "login": "/login",
                "relatorios": "/relatorios/vendas",
                "health": "/health",
            },
        })

    def health_check(self):
        try:
            contagens = {
                "produtos": self._produto_model.contar(),
                "usuarios": self._usuario_model.contar(),
                "pedidos": self._pedido_model.contar(),
            }
        except ErroBancoDeDados:
            logger.exception("Health check: banco de dados indisponível")
            return jsonify({"status": "erro", "detalhes": "Banco de dados indisponível"}), 500

        return jsonify({
            "status": "ok",
            "database": "connected",
            "counts": contagens,
            "versao": current_app.config["VERSAO"],
            "ambiente": current_app.config["AMBIENTE"],
        }), 200
