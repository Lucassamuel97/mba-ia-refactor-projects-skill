"""Rotas de usuários e de login."""
from flask import Blueprint


def criar_blueprint(controller):
    blueprint = Blueprint("usuarios", __name__)
    blueprint.add_url_rule("/usuarios", "listar", controller.listar, methods=["GET"])
    blueprint.add_url_rule("/usuarios/<int:usuario_id>", "buscar_por_id", controller.buscar_por_id, methods=["GET"])
    blueprint.add_url_rule("/usuarios", "criar", controller.criar, methods=["POST"])
    blueprint.add_url_rule("/login", "login", controller.login, methods=["POST"])
    return blueprint
