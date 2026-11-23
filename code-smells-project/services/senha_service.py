"""Hash e verificação de senhas com o KDF do Werkzeug (salt por senha)."""
from werkzeug.security import check_password_hash, generate_password_hash

_PREFIXOS_DE_HASH = ("scrypt:", "pbkdf2:")


def gerar_hash(senha):
    return generate_password_hash(senha)


def eh_hash(valor):
    return isinstance(valor, str) and valor.startswith(_PREFIXOS_DE_HASH)


def verificar(senha_hash, senha):
    return eh_hash(senha_hash) and check_password_hash(senha_hash, senha)
