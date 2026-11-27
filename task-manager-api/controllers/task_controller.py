from flask import jsonify, request

from controllers import validation
from middlewares.auth import current_user, ensure_owner_or_admin
from middlewares.errors import ForbiddenError
from services import task_service


def _ensure_can_assign(data):
    """Quem não é admin só atribui a task a si mesmo."""
    user = current_user()
    if 'user_id' in data and not user.is_admin() and data['user_id'] != user.id:
        raise ForbiddenError('Acesso negado')


def list_tasks():
    return jsonify(task_service.list_tasks()), 200


def get_task(task_id):
    task = task_service.get_task(task_id)
    ensure_owner_or_admin(task.user_id)
    return jsonify(task.to_detail_dict()), 200


def create_task():
    data = validation.require_object(request.get_json())
    _ensure_can_assign(data)
    fields = validation.task_payload(data, creating=True,
                                     check_references=task_service.ensure_references)
    task = task_service.create_task(fields)
    return jsonify(task.to_dict()), 201


def update_task(task_id):
    task = task_service.get_task(task_id)
    ensure_owner_or_admin(task.user_id)
    data = validation.require_object(request.get_json())
    _ensure_can_assign(data)
    fields = validation.task_payload(data, creating=False,
                                     check_references=task_service.ensure_references)
    task = task_service.update_task(task, fields)
    return jsonify(task.to_dict()), 200


def delete_task(task_id):
    task = task_service.get_task(task_id)
    ensure_owner_or_admin(task.user_id)
    task_service.delete_task(task)
    return jsonify({'message': 'Task deletada com sucesso'}), 200


def search_tasks():
    text = request.args.get('q', '')
    status = request.args.get('status', '')
    priority = validation.parse_int_param(request.args.get('priority', ''), 'priority')
    user_id = validation.parse_int_param(request.args.get('user_id', ''), 'user_id')
    return jsonify(task_service.search_tasks(text, status, priority, user_id)), 200


def task_stats():
    return jsonify(task_service.task_stats()), 200
