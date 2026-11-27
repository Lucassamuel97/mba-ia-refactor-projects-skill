from database import transaction
from middlewares.errors import NotFoundError
from models.category import Category
from models.task import Task


def get_category(category_id):
    category = Category.find_by_id(category_id)
    if category is None:
        raise NotFoundError('Categoria não encontrada')
    return category


def list_categories():
    task_counts = Task.count_by_category()
    result = []
    for category in Category.find_all():
        data = category.to_dict()
        data['task_count'] = task_counts.get(category.id, 0)
        result.append(data)
    return result


def create_category(fields):
    category = Category(**fields)
    with transaction():
        category.add()
    return category


def update_category(category, fields):
    with transaction():
        for name, value in fields.items():
            setattr(category, name, value)
    return category


def delete_category(category):
    """As tasks da categoria continuam existindo, sem categoria."""
    with transaction():
        Task.clear_category(category.id)
        category.delete()
