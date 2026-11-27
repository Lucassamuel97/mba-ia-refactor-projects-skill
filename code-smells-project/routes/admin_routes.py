"""Rotas administrativas (somente admin). Não existe rota que execute SQL recebido."""
from flask import Blueprint


def criar_admin_routes(controller, auth):
    bp = Blueprint("admin", __name__)
    bp.add_url_rule("/admin/reset-db", view_func=auth.somente_admin(controller.resetar_banco),
                    methods=["POST"])
    return bp
