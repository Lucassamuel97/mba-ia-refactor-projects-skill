"""Fluxo HTTP das rotas de produtos."""
import logging

from flask import jsonify, request

from controllers.validacao import (
    MENSAGEM_DADOS_INVALIDOS,
    converter_decimal,
    exigir_numero,
    exigir_texto,
    ler_corpo_json,
)
from middlewares.erros import ErroNaoEncontrado, ErroValidacao
from models.produto_model import (
    CATEGORIA_PADRAO,
    CATEGORIAS_VALIDAS,
    NOME_TAMANHO_MAXIMO,
    NOME_TAMANHO_MINIMO,
)

logger = logging.getLogger(__name__)

MENSAGEM_NAO_ENCONTRADO = "Produto não encontrado"


def _validar_dados_produto(dados, validar_nome_e_categoria):
    """Valida o corpo de criação ou de atualização de produto.

    A atualização nunca validou tamanho do nome nem categoria; `validar_nome_e_categoria`
    preserva essa diferença do contrato atual.
    """
    if not dados:
        raise ErroValidacao(MENSAGEM_DADOS_INVALIDOS)
    if "nome" not in dados:
        raise ErroValidacao("Nome é obrigatório")
    if "preco" not in dados:
        raise ErroValidacao("Preço é obrigatório")
    if "estoque" not in dados:
        raise ErroValidacao("Estoque é obrigatório")

    nome = dados["nome"]
    descricao = dados.get("descricao", "")
    categoria = dados.get("categoria", CATEGORIA_PADRAO)

    preco = exigir_numero(dados["preco"], "Preço inválido")
    if preco < 0:
        raise ErroValidacao("Preço não pode ser negativo")
    estoque = exigir_numero(dados["estoque"], "Estoque inválido")
    if estoque < 0:
        raise ErroValidacao("Estoque não pode ser negativo")

    exigir_texto(nome, "Nome inválido")
    if validar_nome_e_categoria:
        if len(nome) < NOME_TAMANHO_MINIMO:
            raise ErroValidacao("Nome muito curto")
        if len(nome) > NOME_TAMANHO_MAXIMO:
            raise ErroValidacao("Nome muito longo")
    exigir_texto(descricao, "Descrição inválida")

    if validar_nome_e_categoria:
        if categoria not in CATEGORIAS_VALIDAS:
            raise ErroValidacao("Categoria inválida. Válidas: " + str(list(CATEGORIAS_VALIDAS)))
    else:
        exigir_texto(categoria, "Categoria inválida")

    return {
        "nome": nome,
        "descricao": descricao,
        "preco": preco,
        "estoque": estoque,
        "categoria": categoria,
    }


class ProdutoController:
    def __init__(self, produto_model):
        self._produto_model = produto_model

    def listar(self):
        produtos = self._produto_model.listar()
        logger.info("Listando %s produtos", len(produtos))
        return jsonify({"dados": produtos, "sucesso": True}), 200

    def buscar_por_id(self, produto_id):
        produto = self._produto_model.buscar_por_id(produto_id)
        if produto is None:
            raise ErroNaoEncontrado(MENSAGEM_NAO_ENCONTRADO, extras={"sucesso": False})
        return jsonify({"dados": produto, "sucesso": True}), 200

    def buscar(self):
        termo = request.args.get("q", "")
        categoria = request.args.get("categoria")
        preco_min = request.args.get("preco_min")
        preco_max = request.args.get("preco_max")
        if preco_min:
            preco_min = converter_decimal(preco_min, "preco_min")
        if preco_max:
            preco_max = converter_decimal(preco_max, "preco_max")

        produtos = self._produto_model.buscar(termo, categoria, preco_min, preco_max)
        return jsonify({"dados": produtos, "total": len(produtos), "sucesso": True}), 200

    def criar(self):
        campos = _validar_dados_produto(ler_corpo_json(), validar_nome_e_categoria=True)
        produto_id = self._produto_model.criar(**campos)
        logger.info("Produto criado com ID: %s", produto_id)
        return jsonify({"dados": {"id": produto_id}, "sucesso": True, "mensagem": "Produto criado"}), 201

    def atualizar(self, produto_id):
        dados = ler_corpo_json()
        if self._produto_model.buscar_por_id(produto_id) is None:
            raise ErroNaoEncontrado(MENSAGEM_NAO_ENCONTRADO)
        campos = _validar_dados_produto(dados, validar_nome_e_categoria=False)
        self._produto_model.atualizar(produto_id, **campos)
        return jsonify({"sucesso": True, "mensagem": "Produto atualizado"}), 200

    def deletar(self, produto_id):
        if self._produto_model.buscar_por_id(produto_id) is None:
            raise ErroNaoEncontrado(MENSAGEM_NAO_ENCONTRADO)
        self._produto_model.deletar(produto_id)
        logger.info("Produto %s deletado", produto_id)
        return jsonify({"sucesso": True, "mensagem": "Produto deletado"}), 200
