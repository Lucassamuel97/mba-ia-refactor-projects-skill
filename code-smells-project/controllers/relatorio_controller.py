"""Fluxo HTTP das rotas de relatórios."""
from flask import jsonify


class RelatorioController:
    def __init__(self, relatorio_service):
        self._relatorio_service = relatorio_service

    def vendas(self):
        relatorio = self._relatorio_service.relatorio_vendas()
        return jsonify({"dados": relatorio, "sucesso": True}), 200
