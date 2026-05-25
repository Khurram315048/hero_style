import secrets
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY=os.getenv('SECRET_KEY')
TEMPLATES_AUTO_RELOAD=True

MYSQL_HOST=os.getenv('MYSQL_HOST','localhost')
MYSQL_USER=os.getenv('MYSQL_USER','root')
MYSQL_PASSWORD=os.getenv('MYSQL_PASSWORD','')
MYSQL_DB=os.getenv('MYSQL_DB','hero_db')
MYSQL_PORT=int(os.getenv('MYSQL_PORT',3307))
MYSQL_CURSORCLASS='DictCursor'

BASE_DIR=os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER=os.path.join(BASE_DIR,"static","uploads")
os.makedirs(UPLOAD_FOLDER,exist_ok=True)

MAIL_SERVER='smtp.gmail.com'
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=os.getenv('MAIL_USERNAME')
MAIL_PASSWORD=os.getenv('MAIL_PASSWORD')
MAIL_DEFAULT_SENDER=os.getenv('MAIL_DEFAULT_SENDER')





    
   
    
   