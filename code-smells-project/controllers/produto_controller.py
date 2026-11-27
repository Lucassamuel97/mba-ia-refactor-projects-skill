"""Fluxo HTTP das rotas de produto."""
import logging

from flask import jsonify, request

from controllers import validacao
from middlewares.erros import ErroConflito, ErroNaoEncontrado

logger = logging.getLogger(__name__)


class ProdutoController:
    def __init__(self, produto_model):
        self._produto_model = produto_model

    def listar(self):
        produtos = self._produto_model.listar()
        logger.info("Listando %s produtos", len(produtos))
        return jsonify({"dados": produtos, "sucesso": True}), 200

    def buscar_por_id(self, produto_id):
        produto = self._produto_model.buscar_por_id(produto_id)
        if not produto:
            raise ErroNaoEncontrado("Produto não encontrado", sucesso=False)
        return jsonify({"dados": produto, "sucesso": True}), 200

    def buscar(self):
        termo = request.args.get("q", "")
        categoria = request.args.get("categoria", None)
        preco_min = validacao.parametro_preco(request.args.get("preco_min"), "preco_min")
        preco_max = validacao.parametro_preco(request.args.get("preco_max"), "preco_max")
        resultados = self._produto_model.buscar(termo, categoria, preco_min, preco_max)
        return jsonify({"dados": resultados, "total": len(resultados), "sucesso": True}), 200

    def criar(self):
        campos = validacao.validar_produto(request.get_json(silent=True))
        novo_id = self._produto_model.criar(*campos)
        logger.info("Produto criado com ID: %s", novo_id)
        return jsonify({"dados": {"id": novo_id}, "sucesso": True, "mensagem": "Produto criado"}), 201

    def atualizar(self, produto_id):
        if not self._produto_model.buscar_por_id(produto_id):
            raise ErroNaoEncontrado("Produto não encontrado")
        campos = validacao.validar_produto(request.get_json(silent=True))
        self._produto_model.atualizar(produto_id, *campos)
        return jsonify({"sucesso": True, "mensagem": "Produto atualizado"}), 200

    def excluir(self, produto_id):
        if not self._produto_model.buscar_por_id(produto_id):
            raise ErroNaoEncontrado("Produto não encontrado")
        if not self._produto_model.excluir_sem_pedidos(produto_id):
            raise ErroConflito("Produto possui pedidos registrados")
        logger.info("Produto %s deletado", produto_id)
        return jsonify({"sucesso": True, "mensagem": "Produto deletado"}), 200
