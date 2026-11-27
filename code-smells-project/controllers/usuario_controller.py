"""Fluxo HTTP das rotas de usuário e login."""
import logging

from flask import jsonify, request

from controllers import validacao
from middlewares.erros import ErroConflito, ErroNaoAutenticado, ErroNaoEncontrado

logger = logging.getLogger(__name__)


class UsuarioController:
    def __init__(self, usuario_model, autenticacao):
        self._usuario_model = usuario_model
        self._autenticacao = autenticacao

    def listar(self):
        return jsonify({"dados": self._usuario_model.listar(), "sucesso": True}), 200

    def buscar_por_id(self, usuario_id):
        self._autenticacao.garantir_dono_ou_admin(usuario_id)
        usuario = self._usuario_model.buscar_por_id(usuario_id)
        if not usuario:
            raise ErroNaoEncontrado("Usuário não encontrado")
        return jsonify({"dados": usuario, "sucesso": True}), 200

    def criar(self):
        nome, email, senha = validacao.validar_usuario(request.get_json(silent=True))
        if self._usuario_model.email_cadastrado(email):
            raise ErroConflito("Email já cadastrado")
        novo_id = self._usuario_model.criar(nome, email, senha)
        logger.info("Usuário criado: id %s", novo_id)
        return jsonify({"dados": {"id": novo_id}, "sucesso": True}), 201

    def login(self):
        email, senha = validacao.validar_credenciais(request.get_json(silent=True))
        usuario = self._usuario_model.autenticar(email, senha)
        if usuario is None:
            logger.info("Login falhou")
            raise ErroNaoAutenticado("Email ou senha inválidos", sucesso=False)
        logger.info("Login bem-sucedido: usuario %s", usuario["id"])
        return jsonify({
            "dados": usuario,
            "sucesso": True,
            "mensagem": "Login OK",
            "token": self._autenticacao.emitir_token(usuario["id"]),
        }), 200
