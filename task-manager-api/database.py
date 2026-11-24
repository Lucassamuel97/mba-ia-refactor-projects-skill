"""Banco de dados: instância do ORM, criação do schema e commit com rollback."""
import logging

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError

from middlewares.errors import PersistenceError

logger = logging.getLogger(__name__)

db = SQLAlchemy()


def init_app(app):
    """Liga o ORM à aplicação e cria as tabelas que ainda não existem."""
    db.init_app(app)
    with app.app_context():
        import models  # noqa: F401  registra as tabelas antes do create_all
        db.create_all()


def commit_session(error_message):
    """Confirma a transação; em falha, desfaz, registra e sinaliza com a mensagem da operação."""
    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        logger.exception(error_message)
        raise PersistenceError(error_message)
