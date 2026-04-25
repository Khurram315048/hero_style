from flask import Blueprint

admin_bp = Blueprint('admin', __name__, url_prefix='/admin', template_folder='admin_views')

from admin import admin_routes