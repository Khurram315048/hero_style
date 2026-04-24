import secrets
import os

SECRET_KEY='SECRET_KEY',secrets.token_hex(16)
TEMPLATES_AUTO_RELOAD=True
MYSQL_HOST='localhost'
MYSQL_USER='root'
MYSQL_PASSWORD=''
MYSQL_DB='hero_db'
MYSQL_PORT=3307
MYSQL_CURSORCLASS='DictCursor'
BASE_DIR=os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER=os.path.join(BASE_DIR, "static", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)



    
   
    
   