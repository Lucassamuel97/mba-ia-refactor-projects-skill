"""Rotas de relatório (somente admin)."""
from flask import Blueprint


def criar_relatorio_routes(controller, auth):
    bp = Blueprint("relatorios", __name__)
    bp.add_url_rule("/relatorios/vendas", view_func=auth.somente_admin(controller.vendas), methods=["GET"])
    return bp
