from flask import Blueprint

prod_bp = Blueprint('products', __name__, url_prefix='/products', template_folder='pages')

from products import prod_routes
