"""Fluxo HTTP das rotas de relatório."""
from flask import jsonify


class RelatorioController:
    def __init__(self, relatorio_service):
        self._relatorio_service = relatorio_service

    def vendas(self):
        return jsonify({"dados": self._relatorio_service.vendas(), "sucesso": True}), 200
