"""Autenticação por token assinado e guards de autorização.

O token carrega só o id do usuário; o papel é lido do banco a cada requisição,
para que rebaixar alguém tenha efeito imediato.
"""
from functools import wraps

from flask import current_app, g, request
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from middlewares.erros import ErroAcessoNegado, ErroNaoAutenticado
from models.usuario_model import TIPO_ADMIN

_SALT_TOKEN = "auth-token"


class Autenticacao:
    def __init__(self, usuario_model):
        self._usuario_model = usuario_model

    @staticmethod
    def _serializador():
        return URLSafeTimedSerializer(current_app.config["SECRET_KEY"], salt=_SALT_TOKEN)

    def emitir_token(self, usuario_id):
        return self._serializador().dumps({"uid": usuario_id})

    def _usuario_autenticado(self):
        esquema, _, token = request.headers.get("Authorization", "").partition(" ")
        if esquema != "Bearer" or not token.strip():
            return None
        try:
            dados = self._serializador().loads(
                token.strip(), max_age=current_app.config["TOKEN_MAX_AGE_SECONDS"]
            )
        except (BadSignature, SignatureExpired):
            return None
        return self._usuario_model.buscar_por_id(dados.get("uid"))

    def login_obrigatorio(self, view):
        @wraps(view)
        def wrapper(*args, **kwargs):
            usuario = self._usuario_autenticado()
            if usuario is None:
                raise ErroNaoAutenticado("Autenticação necessária")
            g.usuario_atual = usuario
            return view(*args, **kwargs)
        return wrapper

    def somente_admin(self, view):
        @wraps(view)
        def checar_papel(*args, **kwargs):
            if g.usuario_atual["tipo"] != TIPO_ADMIN:
                raise ErroAcessoNegado("Acesso negado")
            return view(*args, **kwargs)
        return self.login_obrigatorio(checar_papel)

    @staticmethod
    def garantir_dono_ou_admin(dono_id):
        usuario = g.usuario_atual
        if usuario["tipo"] != TIPO_ADMIN and usuario["id"] != dono_id:
            raise ErroAcessoNegado("Acesso negado")
