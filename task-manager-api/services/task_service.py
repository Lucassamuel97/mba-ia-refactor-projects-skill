"""Casos de uso de tasks: validação das regras, referências e persistência."""
import logging

from database import commit_session, db
from middlewares.errors import NotFoundError, ValidationError
from models.category import Category
from models.task import Task
from models.user import User
from utils.helpers import (
    DEFAULT_PRIORITY,
    DEFAULT_STATUS,
    DONE_STATUS,
    MAX_PRIORITY,
    MAX_TITLE_LENGTH,
    MIN_PRIORITY,
    MIN_TITLE_LENGTH,
    VALID_STATUSES,
    calculate_percentage,
    parse_date,
    utcnow,
)

logger = logging.getLogger(__name__)


# --- regras dos campos ------------------------------------------------------

def _validate_title(title):
    if not isinstance(title, str):
        raise ValidationError('Título inválido')
    if len(title) < MIN_TITLE_LENGTH:
        raise ValidationError('Título muito curto')
    if len(title) > MAX_TITLE_LENGTH:
        raise ValidationError('Título muito longo')
    return title


def _validate_description(description):
    if description is not None and not isinstance(description, str):
        raise ValidationError('Descrição inválida')
    return description


def _validate_status(status):
    if not Task.validate_status(status):
        raise ValidationError('Status inválido')
    return status


def _validate_priority(priority):
    if isinstance(priority, bool) or not isinstance(priority, int):
        raise ValidationError('Prioridade inválida')
    if not Task.validate_priority(priority):
        raise ValidationError(f'Prioridade deve ser entre {MIN_PRIORITY} e {MAX_PRIORITY}')
    return priority


def _validate_reference(model, reference_id, invalid_message, not_found_message):
    """Confere que o registro referenciado existe. Valores vazios significam "sem vínculo"."""
    if isinstance(reference_id, (list, dict)):
        raise ValidationError(invalid_message)
    if reference_id and model.find_by_id(reference_id) is None:
        raise NotFoundError(not_found_message)
    return reference_id


def _validate_user_reference(user_id):
    return _validate_reference(User, user_id, 'Usuário inválido', 'Usuário não encontrado')


def _validate_category_reference(category_id):
    return _validate_reference(
        Category, category_id, 'Categoria inválida', 'Categoria não encontrada'
    )


def _parse_due_date(raw_due_date, error_message):
    due_date = parse_date(raw_due_date)
    if due_date is None:
        raise ValidationError(error_message)
    return due_date


def _normalize_tags(tags):
    """Tags chegam como lista ou como texto separado por vírgulas; são gravadas como texto."""
    if isinstance(tags, list):
        if not all(isinstance(tag, str) for tag in tags):
            raise ValidationError('Tags inválidas')
        return ','.join(tags)
    if isinstance(tags, dict):
        raise ValidationError('Tags inválidas')
    return tags


# --- casos de uso -----------------------------------------------------------

def list_tasks():
    return Task.find_all_with_relations()


def get_task(task_id):
    task = Task.find_by_id(task_id)
    if task is None:
        raise NotFoundError('Task não encontrada')
    return task


def create_task(data):
    title = data.get('title')
    if not title:
        raise ValidationError('Título é obrigatório')

    task = Task(
        title=_validate_title(title),
        description=_validate_description(data.get('description', '')),
        status=_validate_status(data.get('status', DEFAULT_STATUS)),
        priority=_validate_priority(data.get('priority', DEFAULT_PRIORITY)),
        user_id=_validate_user_reference(data.get('user_id')),
        category_id=_validate_category_reference(data.get('category_id')),
    )

    due_date = data.get('due_date')
    if due_date:
        task.due_date = _parse_due_date(due_date, 'Formato de data inválido. Use YYYY-MM-DD')

    tags = data.get('tags')
    if tags:
        task.tags = _normalize_tags(tags)

    db.session.add(task)
    commit_session('Erro ao criar task')
    logger.info('Task criada: %s - %s', task.id, task.title)
    return task


def update_task(task, data):
    changes = {}
    if 'title' in data:
        changes['title'] = _validate_title(data['title'])
    if 'description' in data:
        changes['description'] = _validate_description(data['description'])
    if 'status' in data:
        changes['status'] = _validate_status(data['status'])
    if 'priority' in data:
        changes['priority'] = _validate_priority(data['priority'])
    if 'user_id' in data:
        changes['user_id'] = _validate_user_reference(data['user_id'])
    if 'category_id' in data:
        changes['category_id'] = _validate_category_reference(data['category_id'])
    if 'due_date' in data:
        raw_due_date = data['due_date']
        changes['due_date'] = (
            _parse_due_date(raw_due_date, 'Formato de data inválido') if raw_due_date else None
        )
    if 'tags' in data:
        changes['tags'] = _normalize_tags(data['tags'])

    for field, value in changes.items():
        setattr(task, field, value)
    task.updated_at = utcnow()

    commit_session('Erro ao atualizar')
    logger.info('Task atualizada: %s', task.id)
    return task


def delete_task(task_id):
    task = get_task(task_id)
    db.session.delete(task)
    commit_session('Erro ao deletar')
    logger.info('Task deletada: %s', task_id)


def search_tasks(text='', status='', priority=None, user_id=None):
    return Task.search(text=text, status=status, priority=priority, user_id=user_id)


def get_stats():
    counts = Task.count_by_status()
    total = sum(counts.values())
    stats = {status: counts.get(status, 0) for status in VALID_STATUSES}
    stats['total'] = total
    stats['overdue'] = Task.count_overdue()
    stats['completion_rate'] = calculate_percentage(counts.get(DONE_STATUS, 0), total)
    return stats
