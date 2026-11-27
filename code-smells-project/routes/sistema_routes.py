"""Rotas institucionais públicas."""
from flask import Blueprint


def criar_sistema_routes(controller):
    bp = Blueprint("sistema", __name__)
    bp.add_url_rule("/", view_func=controller.index, methods=["GET"])
    bp.add_url_rule("/health", view_func=controller.health, methods=["GET"])
    return bp
