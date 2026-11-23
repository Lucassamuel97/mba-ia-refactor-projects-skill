"""Configuração da aplicação. É o único módulo que lê variáveis de ambiente."""
import os
import secrets


def _flag(nome, padrao="false"):
    return os.environ.get(nome, padrao).strip().lower() in ("1", "true", "yes")


class Settings:
    # Sem SECRET_KEY no ambiente, uma chave efêmera é gerada a cada boot: o
    # desenvolvimento funciona sem configuração e nenhuma chave fica no repositório.
    SECRET_KEY = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
    DEBUG = _flag("APP_DEBUG")
    DATABASE_PATH = os.environ.get("DATABASE_PATH", "loja.db")
    HOST = os.environ.get("APP_HOST", "127.0.0.1")
    PORT = int(os.environ.get("APP_PORT", "5000"))
    # Ausente = rotas administrativas desligadas (respondem 403).
    ADMIN_TOKEN = os.environ.get("ADMIN_TOKEN") or None
    AMBIENTE = os.environ.get("APP_ENV", "producao")
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()
    VERSAO = "1.0.0"
