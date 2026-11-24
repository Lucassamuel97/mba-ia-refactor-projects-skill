"""Controller das rotas de status da API."""
from datetime import datetime

from flask import current_app


def index():
    return {
        'message': current_app.config['API_NAME'],
        'version': current_app.config['API_VERSION'],
    }


def health():
    return {'status': 'ok', 'timestamp': str(datetime.now())}
