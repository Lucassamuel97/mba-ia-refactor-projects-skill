"""Controller de tasks: lê a requisição, chama o service e monta a resposta."""
from flask import jsonify, request

from controllers.validation import parse_optional_int, require_json_object
from services import task_service


def list_tasks():
    tasks = task_service.list_tasks()
    return jsonify([
        task.to_dict(include_overdue=True, include_relations=True) for task in tasks
    ]), 200


def get_task(task_id):
    task = task_service.get_task(task_id)
    return jsonify(task.to_dict(include_overdue=True)), 200


def create_task():
    data = require_json_object(request.get_json())
    task = task_service.create_task(data)
    return jsonify(task.to_dict()), 201


def update_task(task_id):
    task = task_service.get_task(task_id)
    data = require_json_object(request.get_json())
    task = task_service.update_task(task, data)
    return jsonify(task.to_dict()), 200


def delete_task(task_id):
    task_service.delete_task(task_id)
    return jsonify({'message': 'Task deletada com sucesso'}), 200


def search_tasks():
    tasks = task_service.search_tasks(
        text=request.args.get('q', ''),
        status=request.args.get('status', ''),
        priority=parse_optional_int(request.args.get('priority', ''), 'Prioridade inválida'),
        user_id=parse_optional_int(request.args.get('user_id', ''), 'Usuário inválido'),
    )
    return jsonify([task.to_dict() for task in tasks]), 200


def task_stats():
    return jsonify(task_service.get_stats()), 200
