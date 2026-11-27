"""Autenticação por token assinado e autorização por papel.

O guard está sempre ligado: rota sem credencial válida responde 401 e rota
com papel insuficiente responde 403. O papel é lido do banco a cada requisição.
"""
from functools import wraps

from flask import current_app, g, request
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from middlewares.errors import ForbiddenError, UnauthorizedError
from models.user import User

TOKEN_MAX_AGE_SECONDS = 8 * 60 * 60
TOKEN_SALT = 'auth-token'


def _serializer():
    return URLSafeTimedSerializer(current_app.config['SECRET_KEY'], salt=TOKEN_SALT)


def issue_token(user_id):
    return _serializer().dumps({'uid': user_id})


def authenticated_user():
    """Usuário dono do token enviado, ou None se não houver credencial válida."""
    scheme, _, token = request.headers.get('Authorization', '').partition(' ')
    if scheme != 'Bearer' or not token:
        return None
    try:
        claims = _serializer().loads(token, max_age=TOKEN_MAX_AGE_SECONDS)
    except (BadSignature, SignatureExpired):
        return None
    user = User.find_by_id(claims.get('uid'))
    if user is None or not user.active:
        return None
    return user


def login_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        user = authenticated_user()
        if user is None:
            raise UnauthorizedError('Autenticação necessária')
        g.current_user = user
        return view(*args, **kwargs)
    return wrapper


def admin_required(view):
    @login_required
    @wraps(view)
    def wrapper(*args, **kwargs):
        if not g.current_user.is_admin():
            raise ForbiddenError('Acesso negado')
        return view(*args, **kwargs)
    return wrapper


def current_user():
    return g.current_user


def ensure_owner_or_admin(owner_id):
    user = g.current_user
    if not user.is_admin() and user.id != owner_id:
        raise ForbiddenError('Acesso negado')
