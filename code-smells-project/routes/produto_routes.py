"""Rotas de produto. Leitura pública; escrita só para admin."""
from flask import Blueprint


def criar_produto_routes(controller, auth):
    bp = Blueprint("produtos", __name__)
    bp.add_url_rule("/produtos", view_func=controller.listar, methods=["GET"])                       # pública
    bp.add_url_rule("/produtos/busca", view_func=controller.buscar, methods=["GET"])                 # pública
    bp.add_url_rule("/produtos/<int:produto_id>", view_func=controller.buscar_por_id, methods=["GET"])  # pública
    bp.add_url_rule("/produtos", endpoint="criar", view_func=auth.somente_admin(controller.criar),
                    methods=["POST"])
    bp.add_url_rule("/produtos/<int:produto_id>", endpoint="atualizar",
                    view_func=auth.somente_admin(controller.atualizar), methods=["PUT"])
    bp.add_url_rule("/produtos/<int:produto_id>", endpoint="excluir",
                    view_func=auth.somente_admin(controller.excluir), methods=["DELETE"])
    return bp
