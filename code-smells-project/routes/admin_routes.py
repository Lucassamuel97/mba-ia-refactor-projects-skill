"""Rotas administrativas. Todas exigem o token de administrador."""
from flask import Blueprint

from middlewares.auth import exigir_token_admin


def criar_blueprint(controller):
    blueprint = Blueprint("admin", __name__)
    blueprint.add_url_rule(
        "/admin/reset-db", "resetar_banco", exigir_token_admin(controller.resetar_banco), methods=["POST"]
    )
    blueprint.add_url_rule(
        "/admin/query", "executar_query", exigir_token_admin(controller.executar_query), methods=["POST"]
    )
    return blueprint
