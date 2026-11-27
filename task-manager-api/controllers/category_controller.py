from flask import jsonify, request

from controllers import validation
from services import category_service


def list_categories():
    return jsonify(category_service.list_categories()), 200


def create_category():
    data = validation.require_object(request.get_json())
    category = category_service.create_category(validation.new_category(data))
    return jsonify(category.to_dict()), 201


def update_category(category_id):
    category = category_service.get_category(category_id)
    data = validation.require_object(request.get_json(), allow_empty=True)
    category = category_service.update_category(category, validation.category_changes(data))
    return jsonify(category.to_dict()), 200


def delete_category(category_id):
    category = category_service.get_category(category_id)
    category_service.delete_category(category)
    return jsonify({'message': 'Categoria deletada'}), 200
