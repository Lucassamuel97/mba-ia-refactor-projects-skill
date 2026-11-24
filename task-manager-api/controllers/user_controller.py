"""Controller de usuários e login."""
from flask import jsonify, request

from controllers.validation import require_json_object
from services import user_service


def list_users():
    return jsonify(user_service.list_users()), 200


def get_user(user_id):
    return jsonify(user_service.get_user_details(user_id)), 200


def create_user():
    data = require_json_object(request.get_json())
    user = user_service.create_user(data)
    return jsonify(user.to_dict()), 201


def update_user(user_id):
    user = user_service.get_user(user_id)
    data = require_json_object(request.get_json())
    user = user_service.update_user(user, data)
    return jsonify(user.to_dict()), 200


def delete_user(user_id):
    user_service.delete_user(user_id)
    return jsonify({'message': 'Usuário deletado com sucesso'}), 200


def list_user_tasks(user_id):
    tasks = user_service.list_user_tasks(user_id)
    return jsonify([task.to_summary_dict() for task in tasks]), 200


def login():
    data = require_json_object(request.get_json())
    user, token = user_service.login(data.get('email'), data.get('password'))
    return jsonify({
        'message': 'Login realizado com sucesso',
        'user': user.to_dict(),
        'token': token,
    }), 200
