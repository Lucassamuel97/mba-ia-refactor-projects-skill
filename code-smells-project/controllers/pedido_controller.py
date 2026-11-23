"""Fluxo HTTP das rotas de pedidos."""
from flask import jsonify

from controllers.validacao import (
    MENSAGEM_DADOS_INVALIDOS,
    exigir_numero,
    ler_corpo_json,
    normalizar_id,
)
from middlewares.erros import ErroRegraNegocio, ErroValidacao
from models.pedido_model import STATUS_VALIDOS


def _validar_itens(itens):
    if not isinstance(itens, list):
        raise ErroValidacao("Itens inválidos")
    itens_validados = []
    for item in itens:
        if not isinstance(item, dict) or "produto_id" not in item or "quantidade" not in item:
            raise ErroValidacao("Cada item deve ter produto_id e quantidade")
        quantidade = exigir_numero(item["quantidade"], "Quantidade inválida")
        if quantidade <= 0:
            raise ErroValidacao("Quantidade deve ser maior que zero")
        itens_validados.append({
            "produto_id": normalizar_id(item["produto_id"], "Produto ID inválido"),
            "quantidade": quantidade,
        })
    return itens_validados


class PedidoController:
    def __init__(self, pedido_model, pedido_service):
        self._pedido_model = pedido_model
        self._pedido_service = pedido_service

    def criar(self):
        dados = ler_corpo_json()
        if not dados:
            raise ErroValidacao(MENSAGEM_DADOS_INVALIDOS)

        usuario_id = dados.get("usuario_id")
        itens = dados.get("itens", [])
        if not usuario_id:
            raise ErroValidacao("Usuario ID é obrigatório")
        if not itens:
            raise ErroValidacao("Pedido deve ter pelo menos 1 item")
        usuario_id = normalizar_id(usuario_id, "Usuario ID inválido")
        itens = _validar_itens(itens)

        try:
            resultado = self._pedido_service.criar_pedido(usuario_id, itens)
        except ErroRegraNegocio as erro:
            # Os erros de regra desta rota sempre trouxeram "sucesso": false no corpo.
            return jsonify({"erro": erro.mensagem, "sucesso": False}), erro.status_code

        return jsonify({
            "dados": resultado,
            "sucesso": True,
            "mensagem": "Pedido criado com sucesso",
        }), 201

    def listar(self):
        pedidos = self._pedido_model.listar()
        return jsonify({"dados": pedidos, "sucesso": True}), 200

    def listar_por_usuario(self, usuario_id):
        pedidos = self._pedido_model.listar(usuario_id=usuario_id)
        return jsonify({"dados": pedidos, "sucesso": True}), 200

    def atualizar_status(self, pedido_id):
        dados = ler_corpo_json()
        novo_status = dados.get("status", "")
        if novo_status not in STATUS_VALIDOS:
            raise ErroValidacao("Status inválido")

        self._pedido_service.atualizar_status(pedido_id, novo_status)
        return jsonify({"sucesso": True, "mensagem": "Status atualizado"}), 200
