from flask import Blueprint

order_bp = Blueprint('orders', __name__, url_prefix='/orders', template_folder='order_views')

from orders import order_routes
