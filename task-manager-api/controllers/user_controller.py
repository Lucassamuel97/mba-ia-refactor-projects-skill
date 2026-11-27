from flask import jsonify, request

from controllers import validation
from middlewares.auth import authenticated_user, current_user, ensure_owner_or_admin, issue_token
from middlewares.errors import ForbiddenError
from models.user import User
from services import user_service

ADMIN_ONLY_FIELDS = ('role', 'active')


def list_users():
    return jsonify(user_service.list_users()), 200


def get_user(user_id):
    ensure_owner_or_admin(user_id)
    user = user_service.get_user(user_id)
    return jsonify(user_service.user_detail(user)), 200


def create_user():
    data = validation.require_object(request.get_json())
    fields = validation.new_user(data)
    requester = authenticated_user()
    if requester is None or not requester.is_admin():
        fields['role'] = User.DEFAULT_ROLE  # só um admin define o papel no cadastro
    user = user_service.create_user(**fields)
    return jsonify(user.to_dict()), 201


def update_user(user_id):
    ensure_owner_or_admin(user_id)
    user = user_service.get_user(user_id)
    data = validation.require_object(request.get_json())
    if not current_user().is_admin() and any(field in data for field in ADMIN_ONLY_FIELDS):
        raise ForbiddenError('Acesso negado')
    fields = validation.user_changes(data)
    user = user_service.update_user(user, fields)
    return jsonify(user.to_dict()), 200


def delete_user(user_id):
    user = user_service.get_user(user_id)
    user_service.delete_user(user)
    return jsonify({'message': 'Usuário deletado com sucesso'}), 200


def get_user_tasks(user_id):
    ensure_owner_or_admin(user_id)
    user = user_service.get_user(user_id)
    return jsonify(user_service.user_tasks(user)), 200


def login():
    data = validation.require_object(request.get_json())
    email, password = validation.credentials(data)
    user = user_service.authenticate(email, password)
    return jsonify({
        'message': 'Login realizado com sucesso',
        'user': user.to_dict(),
        'token': issue_token(user.id),
    }), 200
