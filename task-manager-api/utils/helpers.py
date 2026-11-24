"""Constantes de domínio e funções puras usadas pelas camadas."""
import re
from datetime import datetime, timezone

VALID_STATUSES = ['pending', 'in_progress', 'done', 'cancelled']
DEFAULT_STATUS = 'pending'
DONE_STATUS = 'done'
CLOSED_STATUSES = ('done', 'cancelled')  # status em que uma task não conta como atrasada

VALID_ROLES = ['user', 'admin', 'manager']
DEFAULT_ROLE = 'user'

MAX_TITLE_LENGTH = 200
MIN_TITLE_LENGTH = 3
MIN_PASSWORD_LENGTH = 4

MIN_PRIORITY = 1
MAX_PRIORITY = 5
DEFAULT_PRIORITY = 3
HIGH_PRIORITY_THRESHOLD = 2  # prioridades 1 e 2 contam como alta prioridade
PRIORITY_LABELS = {1: 'critical', 2: 'high', 3: 'medium', 4: 'low', 5: 'minimal'}

DEFAULT_COLOR = '#000000'
COLOR_LENGTH = 7  # formato #RRGGBB

RECENT_ACTIVITY_DAYS = 7
DATE_FORMAT = '%Y-%m-%d'
EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$')


def utcnow():
    """UTC sem tzinfo, igual ao que o banco já armazena e ao que a API já devolve."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


def format_date(date_obj):
    if date_obj:
        return str(date_obj)
    return None


def calculate_percentage(part, total):
    if total == 0:
        return 0
    return round((part / total) * 100, 2)


def validate_email(email):
    return isinstance(email, str) and EMAIL_PATTERN.match(email) is not None


def parse_date(date_string):
    """Converte uma data YYYY-MM-DD; devolve None se o valor não estiver nesse formato."""
    try:
        return datetime.strptime(date_string, DATE_FORMAT)
    except (TypeError, ValueError):
        return None


def is_valid_color(color):
    return isinstance(color, str) and len(color) == COLOR_LENGTH and color[0] == '#'
