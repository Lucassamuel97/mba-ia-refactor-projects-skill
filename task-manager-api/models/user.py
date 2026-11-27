from werkzeug.security import check_password_hash, generate_password_hash

from database import db
from utils.clock import utcnow


class User(db.Model):
    __tablename__ = 'users'

    VALID_ROLES = ('user', 'admin', 'manager')
    DEFAULT_ROLE = 'user'
    ADMIN_ROLE = 'admin'
    MIN_PASSWORD_LENGTH = 4

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), default=DEFAULT_ROLE)
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'active': self.active,
            'created_at': str(self.created_at),
        }

    def set_password(self, raw_password):
        self.password = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password, raw_password)

    def is_admin(self):
        return self.role == self.ADMIN_ROLE

    def add(self):
        db.session.add(self)

    def delete(self):
        db.session.delete(self)

    @classmethod
    def find_by_id(cls, user_id):
        return db.session.get(cls, user_id)

    @classmethod
    def find_by_email(cls, email):
        return db.session.scalars(db.select(cls).filter_by(email=email)).first()

    @classmethod
    def find_all(cls):
        return db.session.scalars(db.select(cls).order_by(cls.id)).all()

    @classmethod
    def count_all(cls):
        return db.session.scalar(db.select(db.func.count()).select_from(cls))
