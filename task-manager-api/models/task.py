"""Model de tasks: colunas, regras da entidade e consultas."""
from sqlalchemy.orm import joinedload

from database import db
from utils.helpers import (
    CLOSED_STATUSES,
    DEFAULT_PRIORITY,
    DEFAULT_STATUS,
    DONE_STATUS,
    MAX_PRIORITY,
    MIN_PRIORITY,
    VALID_STATUSES,
    format_date,
    utcnow,
)


class Task(db.Model):
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), default=DEFAULT_STATUS)
    priority = db.Column(db.Integer, default=DEFAULT_PRIORITY)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=utcnow)
    updated_at = db.Column(db.DateTime, default=utcnow, onupdate=utcnow)
    due_date = db.Column(db.DateTime, nullable=True)
    tags = db.Column(db.String(500), nullable=True)

    user = db.relationship('User', backref='tasks')
    category = db.relationship('Category', backref='tasks')

    # --- serialização -----------------------------------------------------

    def to_dict(self, include_overdue=False, include_relations=False):
        data = {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'priority': self.priority,
            'user_id': self.user_id,
            'category_id': self.category_id,
            'created_at': str(self.created_at),
            'updated_at': str(self.updated_at),
            'due_date': format_date(self.due_date),
            'tags': self.tags.split(',') if self.tags else [],
        }
        if include_overdue:
            data['overdue'] = self.is_overdue()
        if include_relations:
            data['user_name'] = self.user.name if self.user else None
            data['category_name'] = self.category.name if self.category else None
        return data

    def to_summary_dict(self):
        """Versão resumida, usada na listagem de tasks de um usuário."""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'priority': self.priority,
            'created_at': str(self.created_at),
            'due_date': format_date(self.due_date),
            'overdue': self.is_overdue(),
        }

    # --- regras da entidade -----------------------------------------------

    @staticmethod
    def validate_status(new_status):
        return new_status in VALID_STATUSES

    @staticmethod
    def validate_priority(priority):
        return MIN_PRIORITY <= priority <= MAX_PRIORITY

    def is_overdue(self):
        return (
            bool(self.due_date)
            and self.due_date < utcnow()
            and self.status not in CLOSED_STATUSES
        )

    @classmethod
    def _overdue_criteria(cls):
        """A mesma regra de `is_overdue`, como filtro de consulta."""
        return (
            cls.due_date < utcnow(),
            db.or_(cls.status.is_(None), cls.status.not_in(CLOSED_STATUSES)),
        )

    # --- consultas ----------------------------------------------------------

    @classmethod
    def find_by_id(cls, task_id):
        return db.session.get(cls, task_id)

    @classmethod
    def find_all_with_relations(cls):
        """Todas as tasks, com usuário e categoria carregados na mesma query."""
        query = (
            db.select(cls)
            .options(joinedload(cls.user), joinedload(cls.category))
            .order_by(cls.id)
        )
        return db.session.scalars(query).all()

    @classmethod
    def find_by_user(cls, user_id):
        query = db.select(cls).where(cls.user_id == user_id).order_by(cls.id)
        return db.session.scalars(query).all()

    @classmethod
    def find_overdue(cls):
        query = db.select(cls).where(*cls._overdue_criteria()).order_by(cls.id)
        return db.session.scalars(query).all()

    @classmethod
    def search(cls, text='', status='', priority=None, user_id=None):
        query = db.select(cls)
        if text:
            pattern = f'%{text}%'
            query = query.where(db.or_(cls.title.like(pattern), cls.description.like(pattern)))
        if status:
            query = query.where(cls.status == status)
        if priority is not None:
            query = query.where(cls.priority == priority)
        if user_id is not None:
            query = query.where(cls.user_id == user_id)
        return db.session.scalars(query.order_by(cls.id)).all()

    @classmethod
    def count(cls):
        return db.session.scalar(db.select(db.func.count()).select_from(cls))

    @classmethod
    def count_overdue(cls):
        query = db.select(db.func.count()).select_from(cls).where(*cls._overdue_criteria())
        return db.session.scalar(query)

    @classmethod
    def count_created_since(cls, since):
        query = db.select(db.func.count()).select_from(cls).where(cls.created_at >= since)
        return db.session.scalar(query)

    @classmethod
    def count_completed_since(cls, since):
        query = (
            db.select(db.func.count())
            .select_from(cls)
            .where(cls.status == DONE_STATUS, cls.updated_at >= since)
        )
        return db.session.scalar(query)

    @classmethod
    def _count_grouped_by(cls, column):
        rows = db.session.execute(db.select(column, db.func.count()).group_by(column)).all()
        return {value: total for value, total in rows}

    @classmethod
    def count_by_status(cls):
        return cls._count_grouped_by(cls.status)

    @classmethod
    def count_by_priority(cls):
        return cls._count_grouped_by(cls.priority)

    @classmethod
    def count_by_user(cls):
        return cls._count_grouped_by(cls.user_id)

    @classmethod
    def count_by_category(cls):
        return cls._count_grouped_by(cls.category_id)

    @classmethod
    def count_by_user_and_status(cls):
        """Contagem por (user_id, status), em uma única query."""
        query = db.select(cls.user_id, cls.status, db.func.count()).group_by(cls.user_id, cls.status)
        return {(user_id, status): total for user_id, status, total in db.session.execute(query)}
