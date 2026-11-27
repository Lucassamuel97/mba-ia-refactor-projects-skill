"""Rotas de usuário e login."""
from flask import Blueprint


def criar_usuario_routes(controller, auth):
    bp = Blueprint("usuarios", __name__)
    bp.add_url_rule("/usuarios", view_func=auth.somente_admin(controller.listar), methods=["GET"])
    bp.add_url_rule("/usuarios/<int:usuario_id>",                                # dono ou admin
                    view_func=auth.login_obrigatorio(controller.buscar_por_id), methods=["GET"])
    bp.add_url_rule("/usuarios", endpoint="criar", view_func=controller.criar, methods=["POST"])  # pública
    bp.add_url_rule("/login", view_func=controller.login, methods=["POST"])                     # pública
    return bp
