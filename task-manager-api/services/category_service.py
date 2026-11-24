"""Casos de uso de categorias."""
from database import commit_session, db
from middlewares.errors import NotFoundError, ValidationError
from models.category import Category
from models.task import Task
from utils.helpers import DEFAULT_COLOR, is_valid_color


# --- regras dos campos ------------------------------------------------------

def _validate_name(name):
    if not name:
        raise ValidationError('Nome é obrigatório')
    if not isinstance(name, str):
        raise ValidationError('Nome inválido')
    return name


def _validate_description(description):
    if description is not None and not isinstance(description, str):
        raise ValidationError('Descrição inválida')
    return description


def _validate_color(color):
    if color is not None and not is_valid_color(color):
        raise ValidationError('Cor inválida')
    return color


# --- casos de uso -----------------------------------------------------------

def list_categories():
    """Categorias com a quantidade de tasks de cada uma, contada em uma única query."""
    task_counts = Task.count_by_category()
    return [
        {**category.to_dict(), 'task_count': task_counts.get(category.id, 0)}
        for category in Category.find_all()
    ]


def get_category(category_id):
    category = Category.find_by_id(category_id)
    if category is None:
        raise NotFoundError('Categoria não encontrada')
    return category


def create_category(data):
    category = Category(
        name=_validate_name(data.get('name')),
        description=_validate_description(data.get('description', '')),
        color=_validate_color(data.get('color', DEFAULT_COLOR)),
    )
    db.session.add(category)
    commit_session('Erro ao criar categoria')
    return category


def update_category(category, data):
    changes = {}
    if 'name' in data:
        changes['name'] = _validate_name(data['name'])
    if 'description' in data:
        changes['description'] = _validate_description(data['description'])
    if 'color' in data:
        changes['color'] = _validate_color(data['color'])

    for field, value in changes.items():
        setattr(category, field, value)
    commit_session('Erro ao atualizar')
    return category


def delete_category(category_id):
    category = get_category(category_id)
    db.session.delete(category)
    commit_session('Erro ao deletar')
