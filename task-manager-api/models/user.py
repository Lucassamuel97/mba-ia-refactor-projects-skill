"""Model de usuários: colunas, senha, regras da entidade e consultas."""
import hashlib
import hmac
import re

from werkzeug.security import check_password_hash, generate_password_hash

from database import db
from utils.helpers import DEFAULT_ROLE, VALID_ROLES, utcnow

# Hashes gravados antes da troca de algoritmo: MD5 puro, 32 dígitos hexadecimais.
LEGACY_MD5_HASH = re.compile(r'[0-9a-f]{32}')


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), default=DEFAULT_ROLE)
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=utcnow)

    def to_dict(self):
        """Campos públicos do usuário. O hash da senha nunca sai daqui."""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'active': self.active,
            'created_at': str(self.created_at),
        }

    # --- senha --------------------------------------------------------------

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        if self.has_legacy_password():
            legacy_hash = hashlib.md5(password.encode()).hexdigest()
            return hmac.compare_digest(self.password, legacy_hash)
        return check_password_hash(self.password, password)

    def has_legacy_password(self):
        """Indica um hash MD5 antigo, que deve ser regravado no próximo login."""
        return LEGACY_MD5_HASH.fullmatch(self.password or '') is not None

    # --- regras da entidade ---------------------------------------------------

    @staticmethod
    def validate_role(role):
        return role in VALID_ROLES

    # --- consultas --------------------------------------------------------------

    @classmethod
    def find_by_id(cls, user_id):
        return db.session.get(cls, user_id)

    @classmethod
    def find_by_email(cls, email):
        return db.session.scalars(db.select(cls).where(cls.email == email)).first()

    @classmethod
    def find_all(cls):
        return db.session.scalars(db.select(cls).order_by(cls.id)).all()

    @classmethod
    def count(cls):
        return db.session.scalar(db.select(db.func.count()).select_from(cls))
