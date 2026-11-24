"""Validação do formato da requisição, compartilhada pelos controllers."""
from middlewares.errors import ValidationError


def require_json_object(data, allow_empty=False):
    """Garante que o corpo é um objeto JSON; por padrão, um objeto vazio também é recusado."""
    if not isinstance(data, dict) or (not data and not allow_empty):
        raise ValidationError('Dados inválidos')
    return data


def parse_optional_int(raw_value, error_message):
    """Converte um parâmetro de query string opcional em inteiro; vazio vira None."""
    if not raw_value:
        return None
    try:
        return int(raw_value)
    except ValueError:
        raise ValidationError(error_message)
