from flask import Flask, render_template,request,flash,url_for,redirect
from utils.db import mysql
from config import *
from datetime import timedelta
import os
import re
from werkzeug.utils import secure_filename
from products import prod_bp
from orders import order_bp
from users import user_bp
from admin import admin_bp
from categories import cat_bp
from orders.order_routes import get_cart_count
from flask_mail import Mail
from flask_wtf.csrf import CSRFProtect

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
app.permanent_session_lifetime=timedelta(days=7)

app.config['MYSQL_HOST']=MYSQL_HOST
app.config['MYSQL_USER']=MYSQL_USER
app.config['MYSQL_PASSWORD']=MYSQL_PASSWORD
app.config['MYSQL_DB']=MYSQL_DB
app.config['MYSQL_PORT']=MYSQL_PORT
app.config['MYSQL_CURSORCLASS']='DictCursor'

mysql.init_app(app)

app.config['MAIL_SERVER']=MAIL_SERVER
app.config['MAIL_PORT']=MAIL_PORT
app.config['MAIL_USE_TLS']=MAIL_USE_TLS
app.config['MAIL_USERNAME']=MAIL_USERNAME
app.config['MAIL_PASSWORD']=MAIL_PASSWORD
app.config['MAIL_DEFAULT_SENDER']=MAIL_DEFAULT_SENDER

csrf=CSRFProtect(app)
mail= Mail(app)


@app.template_filter('slugify')
def slugify_filter(text):
    text=str(text).lower().strip()
    text=re.sub(r'[^\w\s-]', '', text)
    text=re.sub(r'[\s_]+', '-', text)
    return text



@app.route('/')
def homepage():
    cursor=mysql.connection.cursor()
    

    cursor.execute("""
        SELECT p.product_id,p.product_no,p.title,p.category_id,p.stock_quantity,
            p.base_price,p.sale_price,p.status,c.name AS category_name,
            pd.short_description,pd.long_description,
            (SELECT GROUP_CONCAT(image_url ORDER BY image_id ASC SEPARATOR '|||')
                FROM product_images
                WHERE product_id=p.product_id AND is_active=1
            ) AS all_images,
            (SELECT image_url FROM product_images
                WHERE product_id=p.product_id AND is_active=1
                ORDER BY image_id ASC LIMIT 1
            ) AS image_url,
            (SELECT alt_text FROM product_images
                WHERE product_id=p.product_id AND is_active=1
                ORDER BY image_id ASC LIMIT 1
            ) AS alt_text,
            pd.display_type,pd.display_size,pd.brightness_nits,pd.battery_life,pd.connectivity,
            pd.strap_material,pd.case_material,pd.water_resistance,pd.warranty_months,pd.weight,
            COUNT(DISTINCT r.review_id) AS rating        
        FROM products p
        LEFT JOIN categories c ON p.category_id=c.category_id
        LEFT JOIN product_details pd ON p.product_id=pd.product_id
        LEFT JOIN product_reviews r ON p.product_id=r.product_id
        WHERE p.status='active' 
        GROUP BY p.product_id
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
        file       =request.files.get('attachment')
        if file and file.filename != '' and allowed_file(file.filename):
            os.makedirs(UPLOAD_FOLDER,exist_ok=True)
            filename =secure_filename(file.filename)
            save_path=os.path.join(UPLOAD_FOLDER, filename)
            file.save(save_path)
            form_path=save_path
        else:
            flash('File Type is not allowed!','danger')
            
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