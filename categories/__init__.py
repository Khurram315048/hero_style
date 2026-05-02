from flask import Blueprint

cat_bp = Blueprint('categories', __name__, url_prefix='/categories',template_folder='views')

from categories import categ_routes