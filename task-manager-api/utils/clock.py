from datetime import datetime, timezone


def utcnow():
    """UTC sem tzinfo, igual ao que o banco já armazena e ao que a API já devolve."""
    return datetime.now(timezone.utc).replace(tzinfo=None)
