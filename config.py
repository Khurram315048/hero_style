import secrets
import os

SECRET_KEY=os.environ.get('SECRET_KEY', 'your-fallback-secret')
TEMPLATES_AUTO_RELOAD=True
MYSQL_HOST     = os.environ.get('MYSQLHOST', 'localhost')
MYSQL_USER     = os.environ.get('MYSQLUSER', 'root')
MYSQL_PASSWORD = os.environ.get('MYSQLPASSWORD', '')
MYSQL_DB       = os.environ.get('MYSQLDATABASE', 'hero_watches')
MYSQL_PORT     = int(os.environ.get('MYSQLPORT', 3306))
SECRET_KEY=secrets.token_hex(16)
MYSQL_CURSORCLASS='DictCursor'
BASE_DIR=os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER=os.path.join(BASE_DIR, "static", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)



    
   
    
   