"""Relatórios: agregações que cruzam tasks, usuários e categorias."""
from collections import Counter
from datetime import timedelta

from middlewares.errors import NotFoundError
from models.category import Category
from models.task import Task
from models.user import User
from utils.helpers import (
    DONE_STATUS,
    HIGH_PRIORITY_THRESHOLD,
    PRIORITY_LABELS,
    RECENT_ACTIVITY_DAYS,
    VALID_STATUSES,
    calculate_percentage,
    utcnow,
)


def _user_productivity():
    """Total e concluídas por usuário, a partir de uma única contagem agrupada."""
    totals, completed = Counter(), Counter()
    for (user_id, status), task_count in Task.count_by_user_and_status().items():
        totals[user_id] += task_count
        if status == DONE_STATUS:
            completed[user_id] += task_count

    return [
        {
            'user_id': user.id,
            'user_name': user.name,
            'total_tasks': totals[user.id],
            'completed_tasks': completed[user.id],
            'completion_rate': calculate_percentage(completed[user.id], totals[user.id]),
        }
        for user in User.find_all()
    ]


def build_summary():
    now = utcnow()
    status_counts = Task.count_by_status()
    priority_counts = Task.count_by_priority()
    overdue_tasks = Task.find_overdue()
    recent_since = now - timedelta(days=RECENT_ACTIVITY_DAYS)

    return {
        'generated_at': str(now),
        'overview': {
            'total_tasks': sum(status_counts.values()),
            'total_users': User.count(),
            'total_categories': Category.count(),
        },
        'tasks_by_status': {status: status_counts.get(status, 0) for status in VALID_STATUSES},
        'tasks_by_priority': {
            label: priority_counts.get(priority, 0) for priority, label in PRIORITY_LABELS.items()
        },
        'overdue': {
            'count': len(overdue_tasks),
            'tasks': [
                {
                    'id': task.id,
                    'title': task.title,
                    'due_date': str(task.due_date),
                    'days_overdue': (now - task.due_date).days,
                }
                for task in overdue_tasks
            ],
        },
        'recent_activity': {
            f'tasks_created_last_{RECENT_ACTIVITY_DAYS}_days': Task.count_created_since(recent_since),
            f'tasks_completed_last_{RECENT_ACTIVITY_DAYS}_days': Task.count_completed_since(recent_since),
        },
        'user_productivity': _user_productivity(),
    }


def build_user_report(user_id):
    user = User.find_by_id(user_id)
    if user is None:
        raise NotFoundError('Usuário não encontrado')

    tasks = Task.find_by_user(user_id)
    status_counts = Counter(task.status for task in tasks)
    statistics = {status: status_counts[status] for status in VALID_STATUSES}
    statistics['total_tasks'] = len(tasks)
    statistics['overdue'] = sum(1 for task in tasks if task.is_overdue())
    statistics['high_priority'] = sum(
        1 for task in tasks if task.priority <= HIGH_PRIORITY_THRESHOLD
    )
    statistics['completion_rate'] = calculate_percentage(status_counts[DONE_STATUS], len(tasks))

    return {
        'user': {'id': user.id, 'name': user.name, 'email': user.email},
        'statistics': statistics,
    }
