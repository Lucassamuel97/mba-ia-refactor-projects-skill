from flask import Blueprint

from controllers import status_controller

status_bp = Blueprint('status', __name__)

status_bp.add_url_rule('/health', view_func=status_controller.health, methods=['GET'])
status_bp.add_url_rule('/', view_func=status_controller.index, methods=['GET'])
