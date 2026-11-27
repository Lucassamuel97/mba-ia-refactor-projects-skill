"""Rotas de pedido."""
from flask import Blueprint


def criar_pedido_routes(controller, auth):
    bp = Blueprint("pedidos", __name__)
    bp.add_url_rule("/pedidos", endpoint="criar",                                 # autenticado (dono ou admin)
                    view_func=auth.login_obrigatorio(controller.criar), methods=["POST"])
    bp.add_url_rule("/pedidos", endpoint="listar_todos",
                    view_func=auth.somente_admin(controller.listar_todos), methods=["GET"])
    bp.add_url_rule("/pedidos/usuario/<int:usuario_id>",                         # dono ou admin
                    view_func=auth.login_obrigatorio(controller.listar_do_usuario), methods=["GET"])
    bp.add_url_rule("/pedidos/<int:pedido_id>/status",
                    view_func=auth.somente_admin(controller.atualizar_status), methods=["PUT"])
    return bp
