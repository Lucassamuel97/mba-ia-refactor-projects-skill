"""Configuração da aplicação. É o único módulo que lê variáveis de ambiente."""
import os
import secrets
from pathlib import Path

from dotenv import load_dotenv

# Carrega o .env da raiz do projeto, se existir. Nenhuma variável é obrigatória.
load_dotenv(Path(__file__).resolve().parent.parent / '.env')


def _flag(name, default='false'):
    return os.environ.get(name, default).strip().lower() in ('1', 'true', 'yes', 'on')


def _origins(name, default='*'):
    raw = os.environ.get(name, default).strip()
    if raw == '*':
        return raw
    return [origin.strip() for origin in raw.split(',') if origin.strip()]


class Settings:
    API_NAME = 'Task Manager API'
    API_VERSION = '1.0'

    # Sem SECRET_KEY no ambiente, uma chave efêmera é gerada a cada boot: o
    # desenvolvimento funciona sem configuração e nenhuma chave fica no repositório.
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(32)

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///tasks.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    DEBUG = _flag('FLASK_DEBUG')
    HOST = os.environ.get('APP_HOST', '127.0.0.1')
    PORT = int(os.environ.get('APP_PORT', '5000'))
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO').upper()
    CORS_ORIGINS = _origins('CORS_ORIGINS')

    # Sem SMTP_USER e SMTP_PASSWORD, o envio de email fica desligado.
    SMTP_HOST = os.environ.get('SMTP_HOST', 'smtp.gmail.com')
    SMTP_PORT = int(os.environ.get('SMTP_PORT', '587'))
    SMTP_USER = os.environ.get('SMTP_USER') or None
    SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD') or None
