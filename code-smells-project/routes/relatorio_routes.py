"""Rotas de relatórios."""
from flask import Blueprint


def criar_blueprint(controller):
    blueprint = Blueprint("relatorios", __name__)
    blueprint.add_url_rule("/relatorios/vendas", "vendas", controller.vendas, methods=["GET"])
    return blueprint
