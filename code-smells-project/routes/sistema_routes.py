"""Rotas de apresentação e de saúde da API."""
from flask import Blueprint


def criar_blueprint(controller):
    blueprint = Blueprint("sistema", __name__)
    blueprint.add_url_rule("/", "index", controller.index, methods=["GET"])
    blueprint.add_url_rule("/health", "health_check", controller.health_check, methods=["GET"])
    return blueprint
