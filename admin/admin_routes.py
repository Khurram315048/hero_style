from flask import render_template,request,flash,redirect,url_for,session,g
from werkzeug.security import generate_password_hash,check_password_hash
from utils.auth import admin_required
import uuid
from datetime import datetime
from admin import admin_bp
from utils.db import mysql
import os
from werkzeug.utils import secure_filename


@admin_bp.context_processor
def inject_admin():
    admin=None
    admin_id=session.get('admin_id')
    if admin_id:
        cursor=mysql.connection.cursor()
        cursor.execute(
            'SELECT email,username,first_name,last_name FROM admins WHERE admin_id=%s',
            (admin_id,))
        admin=cursor.fetchone()
        cursor.close()
    return dict(admin=admin)


@admin_bp.route('/admin_login',methods=['GET','POST'])
def admin_login():
    cursor=mysql.connection.cursor()
    if request.method=='POST':
        email=request.form.get('email')
        password=request.form.get('password')
        
        cursor.execute('SELECT * FROM admins WHERE email=%s AND is_deleted=%s',(email,0,))
        admin=cursor.fetchone()
        cursor.close()

        if not admin:
            flash('Account does not exist','danger')
            return redirect(url_for('admin.admin_signup'))

        if not check_password_hash(admin['password_hash'],password):
            flash('Password does not match','danger')
            return redirect(url_for('admin.admin_login'))

        session['admin_id']=admin['admin_id']
        session['role']='admin'
        session.permanent=True if request.form.get('remember_me') else False
        session['admin_toast']='Welcome back!'
        return redirect(url_for('admin.admin_dashboard'))

    return render_template('admin_login.htm')




@admin_bp.route('/admin_signup',methods=['GET','POST'])
def admin_signup():
    cursor=mysql.connection.cursor()
    if request.method=='POST':

        first_name=request.form['first_name']
        last_name=request.form['last_name']
        username=request.form['username']
        email=request.form['email']
        plain_password=request.form['password']
        hash_password=generate_password_hash(plain_password)

        cursor.execute('SELECT email FROM admins WHERE email=%s',(email,))
        exist=cursor.fetchone()
        if exist:
            session['admin_toast']='Already Registered!'
            return redirect(url_for('admin.admin_login'))
        
        cursor.execute('''INSERT INTO admins(role_id,first_name,last_name,username,email,password_hash)
                    VALUES(%s,%s,%s,%s,%s,%s)''',(1,first_name,last_name,username,email,hash_password))
        mysql.connection.commit()
        session['admin_toast']='You have been registered successfully!'
        return redirect(url_for('admin.admin_login'))
    
    return render_template('admin_signup.htm')
    

@admin_bp.route('/admin_reset',methods=['GET','POST'])
def admin_reset():
    cursor=mysql.connection.cursor()
    if request.method=='POST':
        email=request.form.get('email')
        new_password=request.form.get('new_password')

        cursor.execute('SELECT email FROM admins WHERE email=%s',(email,))
        admin=cursor.fetchone()  

        if not admin:
            cursor.close()
            session['admin_toast']='Email Does Not Exist!'
            return redirect(url_for('admin.admin_signup'))

        password_hash=generate_password_hash(new_password)
        cursor.execute(
            'UPDATE admins SET password_hash=%s WHERE email=%s AND is_deleted=%s',
            (password_hash,email,0)  
        )
        mysql.connection.commit()
        cursor.close()
        session['admin_toast']='Password Updated Successfully!'
        return redirect(url_for('admin.admin_login'))

    return render_template('admin_reset.htm')


@admin_bp.route('/logout')
@admin_required
def logout():
    session.clear()

    session['admin_toast']='You have been logged out.'
    return redirect(url_for('admin.admin_login'))



@admin_bp.route('/admin_options')
@admin_required
def admin_options():
    return render_template('admin_options.htm')


@admin_bp.route('/admin_dashboard',methods=['GET','POST'])
@admin_required
def admin_dashboard():
    cursor=mysql.connection.cursor()

    cursor.execute('SELECT COUNT(*) AS total_orders FROM orders WHERE is_cancelled=0 AND is_deleted=0')
    result=cursor.fetchone()
    total_orders=result['total_orders'] 
    cursor.execute('SELECT COUNT(user_id) AS total_customers FROM orders WHERE is_cancelled=0 AND is_deleted=0')
    result_cust=cursor.fetchone()
    total_customers=result_cust['total_customers']
    cursor.execute('SELECT SUM(total_amount) AS total_revenue FROM orders WHERE is_cancelled=0 AND is_deleted=0')
    result_sum=cursor.fetchone()
    total_revenue=result_sum['total_revenue']
    cursor.execute('SELECT COUNT(*) AS total_forms FROM forms WHERE is_deleted=0')
    result_form=cursor.fetchone()
    total_forms=result_form['total_forms']
    cursor.close()
    return render_template('admin_dashboard.htm',total_forms=total_forms,
                           total_orders=total_orders,total_customers=total_customers,total_revenue=total_revenue)



@admin_bp.route('/main_products',methods=['GET','POST'])
@admin_required
def main_products():
    cursor=mysql.connection.cursor()
    cursor.execute('''SELECT pr.* , pi.* , cat.*, pd.*
                   FROM products pr
                   JOIN product_images pi ON pr.product_id=pi.product_id
                   JOIN categories cat ON pr.category_id=cat.category_id
                   JOIN product_details pd ON pr.product_id=pd.product_id
                ''')
    products=cursor.fetchall()
    cursor.execute('SELECT * FROM categories WHERE is_active=1')
    categories=cursor.fetchall()
    cursor.close()
    return render_template('main_products.htm',products=products,categories=categories)


@admin_bp.route('/admin_profile',methods=['GET','POST'])
@admin_required
def admin_profile():
    cursor=mysql.connection.cursor()
    admin_id=session.get('admin_id')
    if request.method=='POST':
        first_name=request.form.get('first_name')
        last_name=request.form.get('last_name')
        user_name=request.form.get('user_name')
        email=request.form.get('email')

        cursor.execute('''UPDATE admins SET first_name=%s,last_name=%s,username=%s,email=%s 
                       WHERE admin_id=%s AND is_deleted=0''',(first_name,last_name,user_name,email,admin_id))
        mysql.connection.commit()
        session['admin_toast']='Profile Updated Success!'
        return redirect(request.referrer)


    cursor.execute('SELECT * FROM admins WHERE admin_id=%s AND is_deleted=0',(admin_id,))
    admin_details=cursor.fetchone()
    cursor.close()
    return render_template('admin_profile.htm',admin_details=admin_details)



@admin_bp.route('/add_product',methods=['POST'])
@admin_required
def add_product():
    cursor=mysql.connection.cursor()

    title=request.form.get('title')
    category_id=request.form.get('category')
    base_price=request.form.get('base_price')
    sale_price=request.form.get('sale_price')
    stock=request.form.get('stock', 0)
    status=request.form.get('status','active')
    short_desc=request.form.get('short_description')
    long_desc=request.form.get('long_description')
    display_type=request.form.get('display_type')
    brightness_nits=request.form.get('brightness_nits') or None
    battery_life=request.form.get('battery_life')
    connectivity=request.form.get('connectivity')
    strap_material=request.form.get('strap_material')
    case_material=request.form.get('case_material')
    water_resistance=request.form.get('water_resistance')
    weight=request.form.get('weight')
    warranty_month=request.form.get('warranty_month', 12)
    always_display=request.form.get('always_display', 0)
    product_no=request.form.get('product_no')
    image=request.files.get('image')
    width=12
    height=12

    cursor.execute('''
        INSERT INTO products(product_no,category_id,title,base_price,sale_price,stock_quantity,status,created_at,updated_at)
        VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)
    ''', (product_no,category_id,title,base_price,sale_price,stock,status,datetime.now(),datetime.now()))
    mysql.connection.commit()
    product_id=cursor.lastrowid

    cursor.execute('''
        INSERT INTO product_details(product_id,short_description,long_description,display_type,brightness_nits,
         battery_life,connectivity,strap_material,case_material,water_resistance,
         weight,warranty_months,is_always_on_display,created_at,updated_at)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    ''',(product_id,short_desc,long_desc,display_type,brightness_nits,
          battery_life,connectivity,strap_material,case_material,water_resistance,
          weight,warranty_month,always_display,datetime.now(),datetime.now()))
    mysql.connection.commit()


    if image and image.filename != '':

        cursor.execute('SELECT name FROM categories WHERE category_id=%s',(category_id,))
        cat=cursor.fetchone()
        cat_name=cat['name'].lower().replace(' ', '_')  
        filename=secure_filename(image.filename)
        upload_folder=os.path.join('static','uploads',cat_name)
        os.makedirs(upload_folder,exist_ok=True)
        image_path=os.path.join(upload_folder,filename)
        image.save(image_path)
        image_url='/' + image_path.replace('\\', '/')

        cursor.execute('''
            INSERT INTO product_images(product_id,image_url,alt_text,is_active,width,height,created_at)
            VALUES (%s,%s,%s,%s,%s,%s,%s)
        ''', (product_id,image_url,title,1,width,height,datetime.now()))
        mysql.connection.commit()

    cursor.close()
    session['admin_toast']='Product Added Successfully!'
    return redirect(url_for('admin.main_products'))


@admin_bp.route('/delete_product/<int:product_id>',methods=['GET','POST'])
@admin_required
def delete_product(product_id):
    cursor=mysql.connection.cursor()
    cursor.execute('SELECT status FROM products WHERE product_id=%s',(product_id,))
    result=cursor.fetchone()
    if result['status'] == 'archived':
        session['admin_toast']='Product already deleted!'
        cursor.close()
        return redirect(request.referrer)
    
    cursor.execute('''UPDATE products SET status=%s,updated_at=%s WHERE product_id=%s''',('archived',datetime.now(),product_id))
    cursor.execute('''UPDATE product_images SET is_active=%s WHERE product_id=%s''',(0,product_id))
    mysql.connection.commit()
    cursor.close()
    session['admin_toast']='Product has been deleted successfully!'
    return redirect(url_for('admin.main_products'))




@admin_bp.route('/edit_product/<int:product_id>',methods=['POST'])
@admin_required
def edit_product(product_id):
    cursor=mysql.connection.cursor()

    title=request.form.get('title')
    category_id=request.form.get('category')
    base_price=request.form.get('base_price')
    sale_price=request.form.get('sale_price')
    stock=request.form.get('stock')
    status=request.form.get('status','active')
    short_desc=request.form.get('short_description')
    long_desc=request.form.get('long_description')
    display_type=request.form.get('display_type')
    brightness_nits=request.form.get('brightness_nits') or None
    battery_life=request.form.get('battery_life')
    connectivity=request.form.get('connectivity')
    strap_material=request.form.get('strap_material')
    case_material=request.form.get('case_material')
    water_resistance=request.form.get('water_resistance')
    weight=request.form.get('weight')
    warranty_month=request.form.get('warranty_month')
    always_display=request.form.get('always_display')
    product_no=request.form.get('product_no')
    image=request.files.get('image')
    width=12
    height=12

    cursor.execute('''
        UPDATE products SET product_no=%s,category_id=%s,title=%s,base_price=%s,sale_price=%s,
        stock_quantity=%s,status=%s,updated_at=%s WHERE product_id=%s''', 
        (product_no,category_id,title,base_price,sale_price,stock,status,datetime.now(),product_id))
    mysql.connection.commit()
    product_id=cursor.lastrowid

    cursor.execute('''
        UPDATE  product_details SET product_id=%s,short_description=%s,long_description=%s,
                   display_type=%s,brightness_nits=%s,
         battery_life=%s,connectivity=%s,strap_material=%s,case_material=%s,water_resistance=%s,
         weight=%s,warranty_months=%s,is_always_on_display=%s,updated_at=%s WHERE product_id=%s''',
         (product_id,short_desc,long_desc,display_type,brightness_nits,
          battery_life,connectivity,strap_material,case_material,water_resistance,
          weight,warranty_month,always_display,datetime.now(),product_id))
    mysql.connection.commit()


    if image and image.filename != '':

        cursor.execute('SELECT name FROM categories WHERE category_id=%s',(category_id,))
        cat=cursor.fetchone()
        cat_name=cat['name'].lower().replace(' ', '_')  
        filename=secure_filename(image.filename)
        upload_folder=os.path.join('static','uploads',cat_name)
        os.makedirs(upload_folder,exist_ok=True)
        image_path=os.path.join(upload_folder,filename)
        image.save(image_path)
        image_url='/' + image_path.replace('\\', '/')

        cursor.execute('''
            UPDATE  product_images SET product_id=%s,image_url=%s,alt_text=%s,
                       is_active=%s,width=%s,height=%s,created_at=%s WHERE product_id=%s''', 
                    (product_id,image_url,title,1,width,height,datetime.now(),product_id))
        mysql.connection.commit()

    cursor.close()
    session['admin_toast']='Product Updated Successfully!'
    return redirect(url_for('admin.main_products'))


@admin_bp.route('/active_product<int:product_id>',methods=['GET','POST'])
@admin_required
def active_product(product_id):
    cursor=mysql.connection.cursor()

    cursor.execute('SELECT status FROM products WHERE product_id=%s',(product_id,))
    id=cursor.fetchone()
    if id['status'] != 'archived':
        session['admin_toast']='Cannot perform this operation'
        return redirect(url_for('admin.main_products'))
    
    cursor.execute('UPDATE products SET status=%s,updated_at=%s WHERE product_id=%s',('active',datetime.now(),product_id))
    mysql.connection.commit()
    session['admin_toast']='Product activated successfully!'
    return redirect(url_for('admin.main_products'))



@admin_bp.route('/all_orders')
@admin_required
def all_orders():
    cursor=mysql.connection.cursor()

    cursor.execute('''SELECT o.order_id,o.order_number,o.user_id,o.subtotal,o.status AS order_status,
                   o.discount_amount,o.shipping_charges,o.total_amount,o.ordered_at, 
                   CONCAT(u.first_name,' ',u.last_name) AS customer_name,
                   SUM(d.quantity) AS total_items,
                   p.status AS pay_status,p.payment_method
                   FROM orders o
                   JOIN users u ON o.user_id=u.user_id
                   JOIN order_payments p ON o.order_id=p.order_id
                   JOIN order_details d ON o.order_id=d.order_id
                   WHERE o.is_deleted=0 
                   GROUP BY o.order_id,o.order_number,o.user_id,customer_name,o.subtotal,
                    o.discount_amount,o.shipping_charges,o.total_amount,
                    p.payment_method,p.status,o.status,o.ordered_at''')
    
    orders=cursor.fetchall()
    return render_template('all_orders.htm',orders=orders)



@admin_bp.route('/update_order_status/<int:order_id>',methods=['POST'])
@admin_required
def update_order_status(order_id):
    cursor=mysql.connection.cursor()
    status=request.form.get('status')
    valid=['pending','confirmed','shipped','delivered']
    if status in valid:
        cursor.execute("UPDATE orders SET status=%s WHERE order_id=%s",(status,order_id))
        mysql.connection.commit()
        session['admin_toast']='Status updated successfully!'
    return redirect(url_for('admin.all_orders'))




@admin_bp.route('/cancel_order_status/<int:order_id>',methods=['POST'])
@admin_required
def cancel_order_status(order_id):
    cursor=mysql.connection.cursor()
    cursor.execute("""UPDATE orders SET status='cancelled',is_cancelled=1,cancelled_at=%s 
                      WHERE order_id=%s""",
                   (datetime.now(),order_id))
    mysql.connection.commit()
    session['admin_toast']='Order cancelled successfully!'
    return redirect(url_for('admin.all_orders'))



@admin_bp.route('/delete_order/<int:order_id>',methods=['POST'])
@admin_required
def delete_order(order_id):
    cursor=mysql.connection.cursor()
    cursor.execute("UPDATE orders SET is_deleted=%s WHERE order_id=%s",(1,order_id))
    mysql.connection.commit()
    session['admin_toast']='Order Deleted successfully!'
    return redirect(url_for('admin.all_orders'))


@admin_bp.route('/order_detail/<int:order_id>')
@admin_required
def order_detail(order_id):
    cursor=mysql.connection.cursor()
    admin_id=session.get('admin_id')
    cursor.execute('SELECT email,username,first_name,last_name FROM admins WHERE admin_id=%s',(admin_id,))
    admin=cursor.fetchone()
    
    cursor.execute('''SELECT o.*, CONCAT(u.first_name, ' ', u.last_name) AS customer_name,
               u.email,p.payment_method,p.status AS pay_status,p.transaction_id
        FROM orders o
        JOIN users u ON o.user_id=u.user_id
        JOIN order_payments p ON o.order_id=p.order_id
        WHERE o.order_id=%s''',(order_id,))
    order=cursor.fetchone()

    if not order:
        return redirect(url_for('admin.all_orders'))

    
    cursor.execute('''SELECT d.*,p.title,p.product_no,
               (SELECT image_url FROM product_images 
                WHERE product_id=p.product_id 
                AND is_active=1 LIMIT 1) AS image_url
        FROM order_details d
        JOIN products p ON d.product_id=p.product_id
        WHERE d.order_id=%s''',(order_id,))
    items=cursor.fetchall()

    cursor.execute('''SELECT * FROM order_returns 
        WHERE order_id=%s
        ORDER BY requested_at DESC''',(order_id,))
    returns=cursor.fetchall()

    return render_template('order_detail.htm',order=order,items=items,returns=returns,admin=admin)