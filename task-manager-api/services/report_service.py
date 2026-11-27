from datetime import timedelta

from models.category import Category
from models.task import Task
from models.user import User
from utils.clock import utcnow
from utils.helpers import calculate_percentage

RECENT_ACTIVITY_DAYS = 7


def summary():
    now = utcnow()
    tasks = Task.find_all()
    users = User.find_all()

    status_counts = dict.fromkeys(Task.VALID_STATUSES, 0)
    priority_counts = dict.fromkeys(Task.PRIORITY_LABELS, 0)
    totals_by_user = {}
    done_by_user = {}
    for user_id, status, priority, count in Task.count_by_user_status_priority():
        if status in status_counts:
            status_counts[status] += count
        if priority in priority_counts:
            priority_counts[priority] += count
        totals_by_user[user_id] = totals_by_user.get(user_id, 0) + count
        if status == Task.DONE_STATUS:
            done_by_user[user_id] = done_by_user.get(user_id, 0) + count

    overdue_tasks = [
        {
            'id': task.id,
            'title': task.title,
            'due_date': str(task.due_date),
            'days_overdue': (now - task.due_date).days,
        }
        for task in tasks if task.is_overdue(now)
    ]

    since = now - timedelta(days=RECENT_ACTIVITY_DAYS)
    created_recently, completed_recently = Task.count_recent_activity(since)

    user_productivity = []
    for user in users:
        total = totals_by_user.get(user.id, 0)
        completed = done_by_user.get(user.id, 0)
        user_productivity.append({
            'user_id': user.id,
            'user_name': user.name,
            'total_tasks': total,
            'completed_tasks': completed,
            'completion_rate': calculate_percentage(completed, total),
        })

    return {
        'generated_at': str(utcnow()),
        'overview': {
            'total_tasks': len(tasks),
            'total_users': len(users),
            'total_categories': Category.count_all(),
        },
        'tasks_by_status': status_counts,
        'tasks_by_priority': {
            label: priority_counts[priority] for priority, label in Task.PRIORITY_LABELS.items()
        },
        'overdue': {
            'count': len(overdue_tasks),
            'tasks': overdue_tasks,
        },
        'recent_activity': {
            'tasks_created_last_7_days': created_recently,
            'tasks_completed_last_7_days': completed_recently,
        },
        'user_productivity': user_productivity,
    }


def user_report(user):
    now = utcnow()
    tasks = Task.find_by_user(user.id)
    status_counts = dict.fromkeys(Task.VALID_STATUSES, 0)
    for task in tasks:
        if task.status in status_counts:
            status_counts[task.status] += 1
    total = len(tasks)
    done = status_counts['done']
    return {
        'user': {
            'id': user.id,
            'name': user.name,
            'email': user.email,
        },
        'statistics': {
            'total_tasks': total,
            'done': done,
            'pending': status_counts['pending'],
            'in_progress': status_counts['in_progress'],
            'cancelled': status_counts['cancelled'],
            'overdue': sum(1 for task in tasks if task.is_overdue(now)),
            'high_priority': sum(1 for task in tasks if task.is_high_priority()),
            'completion_rate': calculate_percentage(done, total),
        },
    }
