"""Casos de uso de usuários: cadastro, atualização, exclusão e login."""
import logging

from database import commit_session, db
from middlewares.errors import (
    ConflictError,
    ForbiddenError,
    NotFoundError,
    UnauthorizedError,
    ValidationError,
)
from models.task import Task
from models.user import User
from utils.helpers import DEFAULT_ROLE, MIN_PASSWORD_LENGTH, validate_email

logger = logging.getLogger(__name__)

# Token de demonstração devolvido pelo login. Nenhuma rota o verifica: a troca por
# um token assinado depende de exigir autenticação nas rotas (ver README).
PLACEHOLDER_TOKEN_PREFIX = 'fake-jwt-token-'


# --- regras dos campos ------------------------------------------------------

def _validate_email(email):
    if not validate_email(email):
        raise ValidationError('Email inválido')
    return email


def _validate_password(password, too_short_message):
    if not isinstance(password, str):
        raise ValidationError('Senha inválida')
    if len(password) < MIN_PASSWORD_LENGTH:
        raise ValidationError(too_short_message)
    return password


def _validate_role(role):
    if not User.validate_role(role):
        raise ValidationError('Role inválido')
    return role


# --- casos de uso -----------------------------------------------------------

def list_users():
    """Usuários com a quantidade de tasks de cada um, contada em uma única query."""
    task_counts = Task.count_by_user()
    return [
        {**user.to_dict(), 'task_count': task_counts.get(user.id, 0)}
        for user in User.find_all()
    ]


def get_user(user_id):
    user = User.find_by_id(user_id)
    if user is None:
        raise NotFoundError('Usuário não encontrado')
    return user


def get_user_details(user_id):
    user = get_user(user_id)
    tasks = Task.find_by_user(user_id)
    return {**user.to_dict(), 'tasks': [task.to_dict() for task in tasks]}


def list_user_tasks(user_id):
    get_user(user_id)
    return Task.find_by_user(user_id)


def create_user(data):
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')

    if not name:
        raise ValidationError('Nome é obrigatório')
    if not email:
        raise ValidationError('Email é obrigatório')
    if not password:
        raise ValidationError('Senha é obrigatória')
    if not isinstance(name, str):
        raise ValidationError('Nome inválido')
    _validate_email(email)
    _validate_password(password, f'Senha deve ter no mínimo {MIN_PASSWORD_LENGTH} caracteres')

    if User.find_by_email(email):
        raise ConflictError('Email já cadastrado')

    user = User(name=name, email=email, role=_validate_role(data.get('role', DEFAULT_ROLE)))
    user.set_password(password)

    db.session.add(user)
    commit_session('Erro ao criar usuário')
    logger.info('Usuário criado: %s - %s', user.id, user.name)
    return user


def update_user(user, data):
    changes = {}
    new_password = None

    if 'name' in data:
        name = data['name']
        if not isinstance(name, str):
            raise ValidationError('Nome inválido')
        if not name:
            raise ValidationError('Nome é obrigatório')
        changes['name'] = name

    if 'email' in data:
        email = _validate_email(data['email'])
        existing = User.find_by_email(email)
        if existing and existing.id != user.id:
            raise ConflictError('Email já cadastrado')
        changes['email'] = email

    if 'password' in data:
        new_password = _validate_password(data['password'], 'Senha muito curta')

    if 'role' in data:
        changes['role'] = _validate_role(data['role'])

    if 'active' in data:
        if not isinstance(data['active'], bool):
            raise ValidationError('Campo active inválido')
        changes['active'] = data['active']

    for field, value in changes.items():
        setattr(user, field, value)
    if new_password is not None:
        user.set_password(new_password)

    commit_session('Erro ao atualizar')
    return user


def delete_user(user_id):
    """Apaga o usuário e as tasks dele na mesma transação."""
    user = get_user(user_id)
    for task in Task.find_by_user(user_id):
        db.session.delete(task)
    db.session.delete(user)
    commit_session('Erro ao deletar')
    logger.info('Usuário deletado: %s', user_id)


def login(email, password):
    """Confere as credenciais e devolve o usuário com o token de sessão."""
    if not email or not password:
        raise ValidationError('Email e senha são obrigatórios')

    user = User.find_by_email(email) if isinstance(email, str) else None
    if user is None or not isinstance(password, str) or not user.check_password(password):
        raise UnauthorizedError('Credenciais inválidas')

    if not user.active:
        raise ForbiddenError('Usuário inativo')

    if user.has_legacy_password():
        # Senha conferida contra um hash MD5 antigo: regrava com o algoritmo atual.
        user.set_password(password)
        commit_session('Erro interno')

    return user, PLACEHOLDER_TOKEN_PREFIX + str(user.id)
