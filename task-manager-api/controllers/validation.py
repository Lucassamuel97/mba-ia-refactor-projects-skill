"""Validação de entrada: presença, tipo, formato e faixa, antes de qualquer regra."""
from datetime import datetime

from middlewares.errors import ValidationError
from models.category import Category
from models.task import Task
from models.user import User
from utils.helpers import is_valid_color, validate_email

DATE_FORMAT = '%Y-%m-%d'


def _is_text(value):
    return isinstance(value, str)


def require_object(data, allow_empty=False):
    if not isinstance(data, dict) or (not data and not allow_empty):
        raise ValidationError('Dados inválidos')
    return data


def parse_int_param(raw, field):
    if not raw:
        return None
    try:
        return int(raw)
    except ValueError:
        raise ValidationError(f'Parâmetro {field} inválido')


def _optional_text(value, message):
    if value is not None and not _is_text(value):
        raise ValidationError(message)
    return value


# --- tasks --------------------------------------------------------------------

def _task_title(title, creating):
    if creating and not title:
        raise ValidationError('Título é obrigatório')
    if not _is_text(title):
        raise ValidationError('Título inválido')
    if len(title) < Task.MIN_TITLE_LENGTH:
        raise ValidationError('Título muito curto')
    if len(title) > Task.MAX_TITLE_LENGTH:
        raise ValidationError('Título muito longo')
    return title


def _task_status(status):
    if not Task.validate_status(status):
        raise ValidationError('Status inválido')
    return status


def _task_priority(priority):
    if not Task.validate_priority(priority):
        raise ValidationError('Prioridade deve ser entre 1 e 5')
    return priority


def _task_due_date(raw, message):
    if not raw:
        return None
    try:
        return datetime.strptime(raw, DATE_FORMAT)
    except (TypeError, ValueError):
        raise ValidationError(message)


def _task_tags(tags):
    valid = tags is None or _is_text(tags) or (
        isinstance(tags, list) and all(_is_text(tag) for tag in tags))
    if not valid:
        raise ValidationError('Tags inválidas')
    return Task.join_tags(tags)


def task_payload(data, creating, check_references):
    """Campos validados de uma task, na mesma ordem de checagem do contrato original.

    `check_references(user_id, category_id)` confere a existência dos registros
    referenciados (404) entre as checagens de formato.
    """
    fields = {}
    if creating:
        fields['title'] = _task_title(data.get('title'), creating=True)
        fields['status'] = _task_status(data.get('status', Task.DEFAULT_STATUS))
        fields['priority'] = _task_priority(data.get('priority', Task.DEFAULT_PRIORITY))
        fields['user_id'] = data.get('user_id')
        fields['category_id'] = data.get('category_id')
        check_references(fields['user_id'], fields['category_id'])
        fields['due_date'] = _task_due_date(
            data.get('due_date'), 'Formato de data inválido. Use YYYY-MM-DD')
        fields['description'] = _optional_text(data.get('description', ''), 'Descrição inválida')
        tags = data.get('tags')
        joined = _task_tags(tags)
        fields['tags'] = joined if tags else None
        return fields

    if 'title' in data:
        fields['title'] = _task_title(data['title'], creating=False)
    if 'status' in data:
        fields['status'] = _task_status(data['status'])
    if 'priority' in data:
        fields['priority'] = _task_priority(data['priority'])
    check_references(data.get('user_id'), data.get('category_id'))
    for reference in ('user_id', 'category_id'):
        if reference in data:
            fields[reference] = data[reference]
    if 'due_date' in data:
        fields['due_date'] = _task_due_date(data['due_date'], 'Formato de data inválido')
    if 'description' in data:
        fields['description'] = _optional_text(data['description'], 'Descrição inválida')
    if 'tags' in data:
        fields['tags'] = _task_tags(data['tags'])
    return fields


# --- users --------------------------------------------------------------------

def _user_name(name):
    if not name or not _is_text(name):
        raise ValidationError('Nome é obrigatório')
    return name


def _user_email(email):
    if not _is_text(email) or not validate_email(email):
        raise ValidationError('Email inválido')
    return email


def _user_role(role):
    if role not in User.VALID_ROLES:
        raise ValidationError('Role inválido')
    return role


def new_user(data):
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role', User.DEFAULT_ROLE)
    _user_name(name)
    if not email:
        raise ValidationError('Email é obrigatório')
    if not password:
        raise ValidationError('Senha é obrigatória')
    _user_email(email)
    if not _is_text(password):
        raise ValidationError('Senha inválida')
    if len(password) < User.MIN_PASSWORD_LENGTH:
        raise ValidationError('Senha deve ter no mínimo 4 caracteres')
    _user_role(role)
    return {'name': name, 'email': email, 'password': password, 'role': role}


def user_changes(data):
    fields = {}
    if 'name' in data:
        fields['name'] = _user_name(data['name'])
    if 'email' in data:
        fields['email'] = _user_email(data['email'])
    if 'password' in data:
        password = data['password']
        if not _is_text(password):
            raise ValidationError('Senha inválida')
        if len(password) < User.MIN_PASSWORD_LENGTH:
            raise ValidationError('Senha muito curta')
        fields['password'] = password
    if 'role' in data:
        fields['role'] = _user_role(data['role'])
    if 'active' in data:
        if not isinstance(data['active'], bool):
            raise ValidationError('Campo active inválido')
        fields['active'] = data['active']
    return fields


def credentials(data):
    email = data.get('email')
    password = data.get('password')
    if not email or not password or not _is_text(email) or not _is_text(password):
        raise ValidationError('Email e senha são obrigatórios')
    return email, password


# --- categories ---------------------------------------------------------------

def _category_color(color):
    if not is_valid_color(color):
        raise ValidationError('Cor inválida')
    return color


def new_category(data):
    return {
        'name': _user_name(data.get('name')),
        'description': _optional_text(data.get('description', ''), 'Descrição inválida'),
        'color': _category_color(data.get('color', Category.DEFAULT_COLOR)),
    }


def category_changes(data):
    fields = {}
    if 'name' in data:
        fields['name'] = _user_name(data['name'])
    if 'description' in data:
        fields['description'] = _optional_text(data['description'], 'Descrição inválida')
    if 'color' in data:
        fields['color'] = _category_color(data['color'])
    return fields
