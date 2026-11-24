"""Model de categorias: colunas e consultas."""
from database import db
from utils.helpers import DEFAULT_COLOR, utcnow


class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(300), nullable=True)
    color = db.Column(db.String(7), default=DEFAULT_COLOR)
    created_at = db.Column(db.DateTime, default=utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'color': self.color,
            'created_at': str(self.created_at),
        }

    @classmethod
    def find_by_id(cls, category_id):
        return db.session.get(cls, category_id)

    @classmethod
    def find_all(cls):
        return db.session.scalars(db.select(cls).order_by(cls.id)).all()

    @classmethod
    def count(cls):
        return db.session.scalar(db.select(db.func.count()).select_from(cls))
