"""Fluxo HTTP das rotas de usuários e de login."""
import logging
import re

from flask import jsonify

from controllers.validacao import MENSAGEM_DADOS_INVALIDOS, exigir_texto, ler_corpo_json
from middlewares.erros import ErroNaoEncontrado, ErroValidacao

logger = logging.getLogger(__name__)

FORMATO_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+$")


class UsuarioController:
    def __init__(self, usuario_model, usuario_service):
        self._usuario_model = usuario_model
        self._usuario_service = usuario_service

    def listar(self):
        usuarios = self._usuario_model.listar()
        return jsonify({"dados": usuarios, "sucesso": True}), 200

    def buscar_por_id(self, usuario_id):
        usuario = self._usuario_model.buscar_por_id(usuario_id)
        if usuario is None:
            raise ErroNaoEncontrado("Usuário não encontrado")
        return jsonify({"dados": usuario, "sucesso": True}), 200

    def criar(self):
        dados = ler_corpo_json()
        if not dados:
            raise ErroValidacao(MENSAGEM_DADOS_INVALIDOS)

        nome = dados.get("nome", "")
        email = dados.get("email", "")
        senha = dados.get("senha", "")
        if not nome or not email or not senha:
            raise ErroValidacao("Nome, email e senha são obrigatórios")
        for valor in (nome, email, senha):
            exigir_texto(valor, "Nome, email e senha devem ser texto")
        if not FORMATO_EMAIL.match(email):
            raise ErroValidacao("Email inválido")

        usuario_id = self._usuario_service.criar_usuario(nome, email, senha)
        logger.info("Usuário criado com ID: %s", usuario_id)
        return jsonify({"dados": {"id": usuario_id}, "sucesso": True}), 201

    def login(self):
        dados = ler_corpo_json()
        email = dados.get("email", "")
        senha = dados.get("senha", "")
        if not email or not senha:
            raise ErroValidacao("Email e senha são obrigatórios")
        for valor in (email, senha):
            exigir_texto(valor, "Email e senha devem ser texto")

        usuario = self._usuario_service.autenticar(email, senha)
        if usuario is None:
            logger.info("Login falhou")
            return jsonify({"erro": "Email ou senha inválidos", "sucesso": False}), 401

        logger.info("Login bem-sucedido: usuário %s", usuario["id"])
        return jsonify({"dados": usuario, "sucesso": True, "mensagem": "Login OK"}), 200
