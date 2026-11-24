"""Controller de categorias."""
from flask import jsonify, request

from controllers.validation import require_json_object
from services import category_service


def list_categories():
    return jsonify(category_service.list_categories()), 200


def create_category():
    data = require_json_object(request.get_json())
    category = category_service.create_category(data)
    return jsonify(category.to_dict()), 201


def update_category(cat_id):
    category = category_service.get_category(cat_id)
    # Um objeto vazio é aceito: a categoria é devolvida sem alterações.
    data = require_json_object(request.get_json(), allow_empty=True)
    category = category_service.update_category(category, data)
    return jsonify(category.to_dict()), 200


def delete_category(cat_id):
    category_service.delete_category(cat_id)
    return jsonify({'message': 'Categoria deletada'}), 200
