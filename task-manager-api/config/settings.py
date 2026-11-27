"""Configuração da aplicação: único módulo que lê o ambiente."""
import os
import secrets

from dotenv import load_dotenv

load_dotenv()


def _flag(name, default='false'):
    return os.environ.get(name, default).strip().lower() in ('1', 'true', 'yes')


def _list(name):
    raw = os.environ.get(name, '')
    return [item.strip() for item in raw.split(',') if item.strip()]


class Settings:
    # Sem SECRET_KEY no ambiente, gera uma chave efêmera: o desenvolvimento funciona
    # sem configuração e nenhuma chave conhecida fica no repositório.
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(32)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///tasks.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = _flag('APP_DEBUG')
    HOST = os.environ.get('APP_HOST', '0.0.0.0')
    PORT = int(os.environ.get('APP_PORT', '5000'))
    # Sem CORS_ORIGINS, nenhuma origem externa é liberada.
    CORS_ORIGINS = _list('CORS_ORIGINS')
