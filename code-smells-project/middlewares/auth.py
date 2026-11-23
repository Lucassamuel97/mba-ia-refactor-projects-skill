"""Guard das rotas administrativas."""
import hmac
from functools import wraps

from flask import current_app, jsonify, request

CABECALHO_TOKEN_ADMIN = "X-Admin-Token"


def exigir_token_admin(view):
    """Só deixa passar quem envia o ADMIN_TOKEN configurado no ambiente.

    Sem ADMIN_TOKEN configurado, a rota fica desligada e responde 403 sempre.
    """

    @wraps(view)
    def wrapper(*args, **kwargs):
        esperado = current_app.config.get("ADMIN_TOKEN")
        recebido = request.headers.get(CABECALHO_TOKEN_ADMIN, "")
        if not esperado or not hmac.compare_digest(recebido.encode(), esperado.encode()):
            return jsonify({"erro": "Acesso negado"}), 403
        return view(*args, **kwargs)

    return wrapper
