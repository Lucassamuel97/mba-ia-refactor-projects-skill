import re

EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$')
COLOR_LENGTH = 7


def format_date(date_obj):
    return str(date_obj) if date_obj else None


def calculate_percentage(part, total):
    if total == 0:
        return 0
    return round((part / total) * 100, 2)


def validate_email(email):
    return bool(EMAIL_PATTERN.match(email))


def is_valid_color(color):
    return isinstance(color, str) and len(color) == COLOR_LENGTH and color[0] == '#'
