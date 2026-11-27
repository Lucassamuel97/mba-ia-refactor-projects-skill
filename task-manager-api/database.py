from contextlib import contextmanager

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


@contextmanager
def transaction():
    """Confirma as escritas do bloco de uma vez; desfaz tudo se algo falhar."""
    try:
        yield
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise
