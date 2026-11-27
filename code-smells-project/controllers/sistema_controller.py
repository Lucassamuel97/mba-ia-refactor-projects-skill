"""Rotas institucionais: índice e health check."""
from flask import jsonify

from config.settings import AMBIENTE, VERSAO_API


class SistemaController:
    def __init__(self, sistema_model):
        self._sistema_model = sistema_model

    def index(self):
        return jsonify({
            "mensagem": "Bem-vindo à API da Loja",
            "versao": VERSAO_API,
            "endpoints": {
                "produtos": "/produtos",
                "usuarios": "/usuarios",
                "pedidos": "/pedidos",
                "login": "/login",
                "relatorios": "/relatorios/vendas",
                "health": "/health",
            },
        })

    def health(self):
        return jsonify({
            "status": "ok",
            "database": "connected",
            "counts": self._sistema_model.contagens(),
            "versao": VERSAO_API,
            "ambiente": AMBIENTE,
        }), 200
