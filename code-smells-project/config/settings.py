"""Configuração lida do ambiente. Único módulo que acessa variáveis de ambiente."""
import os
import secrets

VERSAO_API = "1.0.0"
AMBIENTE = "producao"


def _flag(nome, padrao="false"):
    return os.environ.get(nome, padrao).strip().lower() in ("1", "true", "yes")


def _lista(nome):
    return [valor.strip() for valor in os.environ.get(nome, "").split(",") if valor.strip()]


class Settings:
    # Sem SECRET_KEY no ambiente, gera uma chave efêmera: o desenvolvimento funciona sem
    # configuração e nenhuma chave conhecida fica no repositório. Tokens emitidos com a
    # chave efêmera deixam de valer quando o processo reinicia.
    SECRET_KEY = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
    DEBUG = _flag("APP_DEBUG")
    HOST = os.environ.get("APP_HOST", "0.0.0.0")
    PORT = int(os.environ.get("APP_PORT", "5000"))
    DATABASE_PATH = os.environ.get("DATABASE_PATH", "loja.db")
    CORS_ORIGINS = _lista("CORS_ORIGINS")  # vazio = nenhuma origem externa liberada
    TOKEN_MAX_AGE_SECONDS = 8 * 60 * 60
