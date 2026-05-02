from flask import Flask, render_template,request,flash,url_for,redirect
from utils.db import mysql
from config import *
from config import *
from datetime import timedelta
import os
from werkzeug.utils import secure_filename
from products import prod_bp
from orders import order_bp
from users import user_bp
from admin import admin_bp
from categories import cat_bp
from orders.order_routes import get_cart_count

app=Flask(__name__,static_folder='static',template_folder='templates')


ALLOWED_EXTENSIONS={'png', 'jpg', 'jpeg', 'pdf'}
UPLOAD_FOLDER='static/uploads/support_forms'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

app.register_blueprint(prod_bp)
app.register_blueprint(order_bp)
app.register_blueprint(user_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(cat_bp)

app.config['UPLOAD_FOLDER']=UPLOAD_FOLDER
app.config['TEMPLATES_AUTO_RELOAD']=TEMPLATES_AUTO_RELOAD
app.config['SECRET_KEY']=SECRET_KEY
app.permanent_session_lifetime=timedelta(minutes=7)

app.config['MYSQL_HOST']=MYSQL_HOST
app.config['MYSQL_USER']=MYSQL_USER
app.config['MYSQL_PASSWORD']=MYSQL_PASSWORD
app.config['MYSQL_DB']=MYSQL_DB
app.config['MYSQL_PORT']=3307
app.config['MYSQL_CURSORCLASS']='DictCursor'

mysql.init_app(app)







@app.route('/')
def homepage():
    cursor=mysql.connection.cursor()
 
    cursor.execute(""" SELECT p.product_id,p.product_no,p.title,
            p.base_price,p.sale_price,p.status,c.name  AS category_name,
            pd.short_description,pi.image_url,pi.alt_text
        FROM products p
        LEFT JOIN categories c  ON p.category_id =c.category_id
        LEFT JOIN product_details pd ON p.product_id=pd.product_id
        LEFT JOIN product_images pi  ON p.product_id=pi.product_id
        AND pi.is_active=1
        WHERE p.status='active'
        ORDER BY RAND()
        LIMIT 5
    """)
 
    products=cursor.fetchall()
    cursor.close()
 
    return render_template('homepage.htm',products=products)


@app.route('/support',methods=['GET','POST'])
def support():
    cursor=mysql.connection.cursor()
    if request.method=='POST':
        fullName=request.form.get('fullName')
        email=request.form.get('email')
        phone=request.form.get('phone')
        category=request.form.get('category')
        subject=request.form.get('subject')
        message=request.form.get('message')
        overall_rating=request.form.get('rating') or None
        order_id_raw=request.form.get('orderId', '').strip()
        order_id=str(order_id_raw) if order_id_raw.isdigit() else None

        form_path=None
        file=request.files.get('attachment')
        if file and file.filename != '' and allowed_file(file.filename):
            os.makedirs(UPLOAD_FOLDER,exist_ok=True)
            filename =secure_filename(file.filename)
            save_path=os.path.join(UPLOAD_FOLDER, filename)
            file.save(save_path)
            form_path=save_path 
        cursor.execute('''INSERT INTO forms(order_id,full_name,email,phone_number,category,subject,message,form_path,overall_rating)
                       VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)''',(order_id,fullName,email,phone,category,subject,message,form_path,overall_rating))
        mysql.connection.commit()
        cursor.close()
        flash('Message sent successfully','success')
        return redirect(url_for('support'))     
    return render_template('support.htm')


@app.context_processor
def inject_cart_count():
    
    return dict(cart_count=get_cart_count())


if __name__ == '__main__':
    app.run(port=5000,debug=True)