import logging

from database import transaction
from middlewares.errors import NotFoundError
from models.category import Category
from models.task import Task
from models.user import User
from utils.clock import utcnow
from utils.helpers import calculate_percentage

logger = logging.getLogger(__name__)


def ensure_references(user_id, category_id):
    if user_id and User.find_by_id(user_id) is None:
        raise NotFoundError('Usuário não encontrado')
    if category_id and Category.find_by_id(category_id) is None:
        raise NotFoundError('Categoria não encontrada')


def get_task(task_id):
    task = Task.find_by_id(task_id)
    if task is None:
        raise NotFoundError('Task não encontrada')
    return task


def list_tasks():
    now = utcnow()
    return [task.to_list_dict(now) for task in Task.find_all(with_relations=True)]


def search_tasks(text, status, priority, user_id):
    return [task.to_dict() for task in Task.search(text, status, priority, user_id)]


def create_task(fields):
    task = Task(**fields)
    with transaction():
        task.add()
    logger.info('Task criada: %s - %s', task.id, task.title)
    return task


def update_task(task, fields):
    with transaction():
        for name, value in fields.items():
            setattr(task, name, value)
        task.updated_at = utcnow()
    logger.info('Task atualizada: %s', task.id)
    return task


def delete_task(task):
    task_id = task.id
    with transaction():
        task.delete()
    logger.info('Task deletada: %s', task_id)


def task_stats():
    tasks = Task.find_all()
    counts = Task.count_by_status()
    total = len(tasks)
    done = counts.get('done', 0)
    now = utcnow()
    return {
        'total': total,
        'pending': counts.get('pending', 0),
        'in_progress': counts.get('in_progress', 0),
        'done': done,
        'cancelled': counts.get('cancelled', 0),
        'overdue': sum(1 for task in tasks if task.is_overdue(now)),
        'completion_rate': calculate_percentage(done, total),
    }
