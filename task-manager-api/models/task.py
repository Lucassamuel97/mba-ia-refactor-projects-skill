from sqlalchemy.orm import selectinload

from database import db
from utils.clock import utcnow
from utils.helpers import format_date


class Task(db.Model):
    __tablename__ = 'tasks'

    VALID_STATUSES = ('pending', 'in_progress', 'done', 'cancelled')
    CLOSED_STATUSES = ('done', 'cancelled')
    DONE_STATUS = 'done'
    DEFAULT_STATUS = 'pending'
    MIN_TITLE_LENGTH = 3
    MAX_TITLE_LENGTH = 200
    MIN_PRIORITY = 1
    MAX_PRIORITY = 5
    DEFAULT_PRIORITY = 3
    HIGH_PRIORITY_MAX = 2
    PRIORITY_LABELS = {1: 'critical', 2: 'high', 3: 'medium', 4: 'low', 5: 'minimal'}
    TAG_SEPARATOR = ','

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

    # --- serialização -------------------------------------------------------

    def tag_list(self):
        return self.tags.split(self.TAG_SEPARATOR) if self.tags else []

    def to_dict(self):
        return {
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
            'tags': self.tag_list(),
        }

    def to_detail_dict(self, now=None):
        data = self.to_dict()
        data['overdue'] = self.is_overdue(now)
        return data

    def to_list_dict(self, now=None):
        data = self.to_detail_dict(now)
        data['user_name'] = self.user.name if self.user else None
        data['category_name'] = self.category.name if self.category else None
        return data

    def to_summary_dict(self, now=None):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'priority': self.priority,
            'created_at': str(self.created_at),
            'due_date': format_date(self.due_date),
            'overdue': self.is_overdue(now),
        }

    # --- regras da entidade -------------------------------------------------

    @classmethod
    def validate_status(cls, new_status):
        return new_status in cls.VALID_STATUSES

    @classmethod
    def validate_priority(cls, priority):
        return (isinstance(priority, int) and not isinstance(priority, bool)
                and cls.MIN_PRIORITY <= priority <= cls.MAX_PRIORITY)

    @classmethod
    def join_tags(cls, tags):
        return cls.TAG_SEPARATOR.join(tags) if isinstance(tags, list) else tags

    def is_overdue(self, now=None):
        return (bool(self.due_date)
                and self.due_date < (now or utcnow())
                and self.status not in self.CLOSED_STATUSES)

    def is_high_priority(self):
        return self.priority <= self.HIGH_PRIORITY_MAX

    # --- persistência -------------------------------------------------------

    def add(self):
        db.session.add(self)

    def delete(self):
        db.session.delete(self)

    @classmethod
    def find_by_id(cls, task_id):
        return db.session.get(cls, task_id)

    @classmethod
    def find_all(cls, with_relations=False):
        query = db.select(cls).order_by(cls.id)
        if with_relations:
            query = query.options(selectinload(cls.user), selectinload(cls.category))
        return db.session.scalars(query).all()

    @classmethod
    def find_by_user(cls, user_id):
        return db.session.scalars(db.select(cls).filter_by(user_id=user_id).order_by(cls.id)).all()

    @classmethod
    def search(cls, text=None, status=None, priority=None, user_id=None):
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
    def count_by_status(cls):
        rows = db.session.execute(db.select(cls.status, db.func.count()).group_by(cls.status)).all()
        return {status: count for status, count in rows}

    @classmethod
    def count_by_user_status_priority(cls):
        """Uma linha por (user_id, status, priority) com a contagem de tasks."""
        return db.session.execute(
            db.select(cls.user_id, cls.status, cls.priority, db.func.count())
            .group_by(cls.user_id, cls.status, cls.priority)
        ).all()

    @classmethod
    def count_by_user(cls):
        rows = db.session.execute(
            db.select(cls.user_id, db.func.count()).group_by(cls.user_id)
        ).all()
        return {user_id: count for user_id, count in rows}

    @classmethod
    def count_by_category(cls):
        rows = db.session.execute(
            db.select(cls.category_id, db.func.count()).group_by(cls.category_id)
        ).all()
        return {category_id: count for category_id, count in rows}

    @classmethod
    def count_recent_activity(cls, since):
        """(tasks criadas desde `since`, tasks concluídas e atualizadas desde `since`)."""
        created = db.func.count(db.case((cls.created_at >= since, 1)))
        completed = db.func.count(db.case(
            (db.and_(cls.status == cls.DONE_STATUS, cls.updated_at >= since), 1)))
        return tuple(db.session.execute(db.select(created, completed)).one())

    @classmethod
    def clear_category(cls, category_id):
        db.session.execute(
            db.update(cls).where(cls.category_id == category_id).values(category_id=None)
        )

    @classmethod
    def delete_by_user(cls, user_id):
        for task in cls.find_by_user(user_id):
            task.delete()
