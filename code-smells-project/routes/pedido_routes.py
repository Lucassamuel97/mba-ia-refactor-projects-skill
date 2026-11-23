"""Rotas de pedidos."""
from flask import Blueprint


def criar_blueprint(controller):
    blueprint = Blueprint("pedidos", __name__)
    blueprint.add_url_rule("/pedidos", "criar", controller.criar, methods=["POST"])
    blueprint.add_url_rule("/pedidos", "listar", controller.listar, methods=["GET"])
    blueprint.add_url_rule(
        "/pedidos/usuario/<int:usuario_id>", "listar_por_usuario", controller.listar_por_usuario, methods=["GET"]
    )
    blueprint.add_url_rule(
        "/pedidos/<int:pedido_id>/status", "atualizar_status", controller.atualizar_status, methods=["PUT"]
    )
    return blueprint
