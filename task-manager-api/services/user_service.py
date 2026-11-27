import logging

from database import transaction
from middlewares.errors import ConflictError, NotFoundError, UnauthorizedError, ForbiddenError
from models.task import Task
from models.user import User
from utils.clock import utcnow

logger = logging.getLogger(__name__)


def get_user(user_id):
    user = User.find_by_id(user_id)
    if user is None:
        raise NotFoundError('Usuário não encontrado')
    return user


def list_users():
    task_counts = Task.count_by_user()
    result = []
    for user in User.find_all():
        data = user.to_dict()
        data['task_count'] = task_counts.get(user.id, 0)
        result.append(data)
    return result


def user_detail(user):
    data = user.to_dict()
    data['tasks'] = [task.to_dict() for task in Task.find_by_user(user.id)]
    return data


def user_tasks(user):
    now = utcnow()
    return [task.to_summary_dict(now) for task in Task.find_by_user(user.id)]


def _ensure_email_available(email, current_user_id=None):
    existing = User.find_by_email(email)
    if existing is not None and existing.id != current_user_id:
        raise ConflictError('Email já cadastrado')


def create_user(name, email, password, role):
    _ensure_email_available(email)
    user = User(name=name, email=email, role=role)
    user.set_password(password)
    with transaction():
        user.add()
    logger.info('Usuário criado: %s - %s', user.id, user.name)
    return user


def update_user(user, fields):
    if 'email' in fields:
        _ensure_email_available(fields['email'], user.id)
    with transaction():
        for name, value in fields.items():
            if name == 'password':
                user.set_password(value)
            else:
                setattr(user, name, value)
    return user


def delete_user(user):
    user_id = user.id
    with transaction():
        Task.delete_by_user(user_id)
        user.delete()
    logger.info('Usuário deletado: %s', user_id)


def authenticate(email, password):
    user = User.find_by_email(email)
    if user is None or not user.check_password(password):
        raise UnauthorizedError('Credenciais inválidas')
    if not user.active:
        raise ForbiddenError('Usuário inativo')
    return user
