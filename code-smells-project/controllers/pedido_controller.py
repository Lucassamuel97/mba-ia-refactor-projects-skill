"""Fluxo HTTP das rotas de pedido."""
from flask import jsonify, request

from controllers import validacao


class PedidoController:
    def __init__(self, pedido_service, pedido_model, autenticacao):
        self._pedido_service = pedido_service
        self._pedido_model = pedido_model
        self._autenticacao = autenticacao

    def criar(self):
        dados = validacao.validar_corpo_pedido(request.get_json(silent=True))
        usuario_id = validacao.validar_usuario_id(dados)
        self._autenticacao.garantir_dono_ou_admin(usuario_id)
        itens = validacao.validar_itens(dados)
        resultado = self._pedido_service.criar_pedido(usuario_id, itens)
        return jsonify({
            "dados": resultado,
            "sucesso": True,
            "mensagem": "Pedido criado com sucesso",
        }), 201

    def listar_todos(self):
        return jsonify({"dados": self._pedido_model.listar(), "sucesso": True}), 200

    def listar_do_usuario(self, usuario_id):
        self._autenticacao.garantir_dono_ou_admin(usuario_id)
        return jsonify({"dados": self._pedido_model.listar(usuario_id), "sucesso": True}), 200

    def atualizar_status(self, pedido_id):
        novo_status = validacao.validar_status(request.get_json(silent=True))
        self._pedido_service.atualizar_status(pedido_id, novo_status)
        return jsonify({"sucesso": True, "mensagem": "Status atualizado"}), 200
