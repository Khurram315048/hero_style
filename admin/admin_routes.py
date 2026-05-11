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

    cursor.execute("""
        UPDATE products p
        JOIN order_details od ON p.product_id=od.product_id
        SET p.stock_quantity=p.stock_quantity + od.quantity,
        p.status=CASE WHEN p.status='draft' THEN 'active' ELSE p.status END
        WHERE od.order_id=%s
        """,(order_id,))

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

  
    return render_template('order_detail.htm',order=order,items=items,admin=admin)



@admin_bp.route('/returns_orders')
@admin_required
def returns_orders():
    cursor = mysql.connection.cursor()
    admin_id=session.get('admin_id')
    cursor.execute('SELECT email,username,first_name,last_name FROM admins WHERE admin_id=%s',(admin_id,))
    admin=cursor.fetchone()

    active_tab=request.args.get('tab','order')  

    if active_tab == 'order':
        cursor.execute('''SELECT r.*, o.order_number,
                   CONCAT(u.first_name,' ',u.last_name) AS customer_name
            FROM order_returns r
            JOIN orders o ON r.order_id=o.order_id
            JOIN users u ON o.user_id=u.user_id
            WHERE r.is_cancelled=0
            ORDER BY r.requested_at DESC''')
    else:
        cursor.execute('''SELECT ir.*, o.order_number,
                   CONCAT(u.first_name,' ',u.last_name) AS customer_name,
                   p.title AS product_title
            FROM order_item_returns ir
            JOIN orders o ON ir.order_id=o.order_id
            JOIN users u ON o.user_id=u.user_id
            JOIN order_details od ON ir.order_detail_id=od.order_detail_id
            JOIN products p ON od.product_id=p.product_id
            ORDER BY ir.requested_at DESC''')

    returns=cursor.fetchall()
    return render_template('returns_orders.htm',returns=returns,active_tab=active_tab,admin=admin)



@admin_bp.route('/returns_order_request/<int:order_id>',methods=['POST'])
@admin_required
def returns_order_request(order_id):
    cursor=mysql.connection.cursor()

    cursor.execute('''UPDATE order_returns SET status=%s,resolved_at=%s WHERE order_id=%s''',('approved',datetime.now(),order_id))
    mysql.connection.commit()
    session['admin_toast']='Request approved successfully!'
    return redirect(request.referrer)


@admin_bp.route('/returns_order_reject/<int:order_id>',methods=['POST'])
@admin_required
def returns_order_reject(order_id):
    cursor=mysql.connection.cursor()

    cursor.execute('''UPDATE order_returns SET status=%s,resolved_at=%s WHERE order_id=%s''',('rejected',datetime.now(),order_id))
    mysql.connection.commit()
    session['admin_toast']='Request rejected successfully!'
    return redirect(request.referrer)


@admin_bp.route('/returns_items_approved/<int:order_id>',methods=['POST'])
@admin_required
def returns_items_approved(order_id):
    cursor=mysql.connection.cursor()

    cursor.execute('''UPDATE order_item_returns SET status=%s,resolved_at=%s WHERE order_id=%s''',('approved',datetime.now(),order_id))
    mysql.connection.commit()
    session['admin_toast']='Request approved successfully!'
    return redirect(request.referrer)



@admin_bp.route('/returns_items_reject/<int:order_id>',methods=['POST'])
@admin_required
def returns_items_reject(order_id):
    cursor=mysql.connection.cursor()

    cursor.execute('''UPDATE order_item_returns SET status=%s,resolved_at=%s WHERE order_id=%s''',('rejected',datetime.now(),order_id))
    mysql.connection.commit()
    session['admin_toast']='Request rejected successfully!'
    return redirect(request.referrer)



@admin_bp.route('/orders_cancels')
@admin_required
def orders_cancels():
    cursor=mysql.connection.cursor()
    cursor.execute("""SELECT o.order_id,o.order_number,o.total_amount,o.cancelled_at,o.is_cancelled,
        CONCAT(u.first_name, ' ', u.last_name) AS customer_name,
        COALESCE(op.payment_method, 'N/A')  AS payment_method,
        COALESCE(op.status, 'pending')  AS pay_status
    FROM orders o
    LEFT JOIN users u ON o.user_id=u.user_id
    LEFT JOIN order_payments op ON o.order_id=op.order_id
    WHERE(o.is_cancelled=1 OR o.status='cancelled')
    AND o.is_deleted=0
    ORDER BY o.cancelled_at DESC""")
    cancelled_orders=cursor.fetchall()

    admin_id=session.get('admin_id')
    cursor.execute(
        'SELECT email,username,first_name,last_name FROM admins WHERE admin_id=%s',(admin_id,))
    admin=cursor.fetchone()
    cursor.close()

    return render_template('orders_cancels.htm',cancelled_orders=cancelled_orders,admin=admin)


@admin_bp.route('/mark_refunded/<int:order_id>',methods=['POST'])
@admin_required
def mark_refunded(order_id):
    cursor=mysql.connection.cursor()

    cursor.execute("""SELECT o.order_id,op.payment_id
        FROM orders o
        LEFT JOIN order_payments op ON o.order_id=op.order_id
        WHERE o.order_id=%s
        AND (o.is_cancelled=1 OR o.status='cancelled')
        AND o.is_deleted=0""",(order_id,))
    row=cursor.fetchone()

    if not row:
        cursor.close()
        session['admin_toast']='Order not found or not eligible for refund.'
        return redirect(request.referrer)

    payment_id=row['payment_id']

    if payment_id:
        
        cursor.execute("""UPDATE order_payments 
            SET status='refunded'
            WHERE payment_id=%s""",(payment_id,))
    else:
        
        cursor.execute("""
            INSERT INTO order_payments(order_id,payment_method,amount,status)
            SELECT order_id,'COD',total_amount,'refunded'
            FROM orders WHERE order_id=%s""",(order_id,))

    mysql.connection.commit()
    cursor.close()

    session['admin_toast']='Order marked as refunded successfully.'
    return redirect(request.referrer)



@admin_bp.route('/customers')
@admin_required
def customers():
    cursor=mysql.connection.cursor()
    cursor.execute("""SELECT u.user_id,u.first_name,u.last_name,u.email,
               u.is_active,u.created_at,u.last_login_at,
               COUNT(DISTINCT o.order_id) AS total_orders,
               COALESCE(SUM(o.total_amount),0) AS total_spent
        FROM users u
        LEFT JOIN orders o ON u.user_id=o.user_id AND o.is_deleted=0
        WHERE u.role_id=2
        GROUP BY u.user_id
        ORDER BY u.created_at DESC""")
    customers=cursor.fetchall()
    admin_id=session.get('admin_id')
    cursor.execute('SELECT email,username,first_name,last_name FROM admins WHERE admin_id=%s',(admin_id,))
    admin=cursor.fetchone()
    cursor.close()
    return render_template('customers.htm',customers=customers,admin=admin)


@admin_bp.route('/customers/<int:user_id>/toggle',methods=['POST'])
@admin_required
def toggle_customer(user_id):
    cursor=mysql.connection.cursor()
    cursor.execute('SELECT is_active FROM users WHERE user_id=%s',(user_id,))
    row=cursor.fetchone()
    if not row:
        cursor.close()
        session['admin_toast']='Customer not found.'
        return redirect(url_for('admin.customers'))
    
    new_status=0 if row['is_active'] else 1
    cursor.execute('UPDATE users SET is_active=%s WHERE user_id=%s',(new_status,user_id))
    mysql.connection.commit()
    cursor.close()
    session['admin_toast']='Customer status updated.'
    return redirect(url_for('admin.customers'))



@admin_bp.route('/customers/<int:user_id>')
@admin_required
def customer_detail(user_id):
    cursor=mysql.connection.cursor()
    cursor.execute("""SELECT user_id,first_name,last_name,email,
               is_active,created_at,last_login_at
        FROM users WHERE user_id=%s""",(user_id,))
    customer=cursor.fetchone()
    if not customer:
        cursor.close()
        session['admin_toast']='Customer not found.'
        return redirect(url_for('admin.customers'))
    
    cursor.execute("""SELECT o.order_id,o.order_number,o.status,o.total_amount,
               o.ordered_at,o.is_cancelled,
               COALESCE(op.status,'pending') AS pay_status,
               COALESCE(op.payment_method,'N/A') AS payment_method
        FROM orders o
        LEFT JOIN order_payments op ON o.order_id=op.order_id
        WHERE o.user_id=%s AND o.is_deleted=0
        ORDER BY o.ordered_at DESC""",(user_id,))
    orders=cursor.fetchall()
    
    cursor.execute("""SELECT p.title,pi.image_url,p.sale_price,w.added_at
        FROM wishlist w
        JOIN products p ON w.product_i =p.product_id
        LEFT JOIN product_images pi ON p.product_id=pi.product_id
        WHERE w.user_id=%s""",(user_id,))
    wishlist=cursor.fetchall()
    admin_id=session.get('admin_id')
    cursor.execute('SELECT email,username,first_name,last_name FROM admins WHERE admin_id=%s',(admin_id,))
    admin=cursor.fetchone()
    cursor.close()
    return render_template('customer_detail.htm',customer=customer,orders=orders,wishlist=wishlist,admin=admin)




@admin_bp.route('/payments')
@admin_required
def all_payments():
    cursor=mysql.connection.cursor()
    cursor.execute("""SELECT op.payment_id,op.order_id,op.payment_method,
               op.amount, op.status,op.paid_at,op.created_at,o.order_number,o.is_cancelled,
               CONCAT(u.first_name,' ',u.last_name) AS customer_name
        FROM order_payments op
        JOIN orders o ON op.order_id=o.order_id
        LEFT JOIN users u ON o.user_id=u.user_id
        WHERE o.is_deleted=0
        ORDER BY op.created_at DESC""")
    payments=cursor.fetchall()
    admin_id=session.get('admin_id')
    cursor.execute('SELECT email,username,first_name,last_name FROM admins WHERE admin_id=%s',(admin_id,))
    admin=cursor.fetchone()
    cursor.close()
    return render_template('payments.htm',payments=payments,admin=admin)



@admin_bp.route('/support_forms')
@admin_required
def support_forms():
    cursor=mysql.connection.cursor()
    cursor.execute("""SELECT form_id,full_name,email,phone_number,
               category,subject,message,overall_rating,
               order_id,is_deleted
        FROM forms
        WHERE is_deleted=0
        ORDER BY form_id DESC""")
    forms=cursor.fetchall()
    admin_id=session.get('admin_id')
    cursor.execute('SELECT email,username,first_name,last_name FROM admins WHERE admin_id=%s',(admin_id,))
    admin=cursor.fetchone()
    cursor.close()
    return render_template('support_forms.htm',forms=forms,admin=admin)


@admin_bp.route('/support_forms/<int:form_id>/delete', methods=['POST'])
@admin_required
def delete_form(form_id):
    cursor=mysql.connection.cursor()
    cursor.execute('UPDATE forms SET is_deleted=1 WHERE form_id=%s',(form_id,))
    mysql.connection.commit()
    cursor.close()
    session['admin_toast']='Form submission deleted.'
    return redirect(url_for('admin.support_forms'))



@admin_bp.route('/reviews')
@admin_required
def all_reviews():
    cursor=mysql.connection.cursor()
    cursor.execute("""SELECT pr.review_id,pr.rating,pr.comment,pr.status,
               pr.created_at,pr.is_deleted,
               p.title AS product_title,p.product_id,
               CONCAT(u.first_name,' ',u.last_name) AS customer_name,
               u.user_id
        FROM product_reviews pr
        JOIN products p ON pr.product_id=p.product_id
        JOIN users u ON pr.user_id=u.user_id
        WHERE pr.is_deleted=0
        ORDER BY pr.created_at DESC""")
    reviews=cursor.fetchall()
    admin_id=session.get('admin_id')
    cursor.execute('SELECT email,username,first_name,last_name FROM admins WHERE admin_id=%s',(admin_id,))
    admin=cursor.fetchone()
    cursor.close()
    return render_template('all_reviews.htm',reviews=reviews,admin=admin)


@admin_bp.route('/reviews/<int:review_id>/status',methods=['POST'])
@admin_required
def update_review_status(review_id):
    cursor=mysql.connection.cursor()
    new_status=request.form.get('status')
    if new_status not in ('approved','hidden','pending'):
        session['admin_toast']='Invalid status.'
        return redirect(url_for('admin.all_reviews'))
    
    
    cursor.execute("""UPDATE product_reviews SET status=%s WHERE review_id=%s""",(new_status,review_id))
    mysql.connection.commit()
    cursor.close()
    session['admin_toast']=f'Review marked as {new_status}.'
    return redirect(url_for('admin.all_reviews'))


@admin_bp.route('/reviews/<int:review_id>/delete',methods=['POST'])
@admin_required
def delete_review(review_id):
    cursor=mysql.connection.cursor()
    cursor.execute("""UPDATE product_reviews SET is_deleted=1 WHERE review_id=%s""",(review_id,))
    mysql.connection.commit()
    cursor.close()
    session['admin_toast']='Review deleted.'
    return redirect(url_for('admin.all_reviews'))



@admin_bp.route('/sales')
@admin_required
def sales():
    cursor=mysql.connection.cursor()
    cursor.execute('SELECT SUM(total_amount) AS total_sales FROM orders WHERE is_cancelled=0 AND is_deleted=0')
    result_sum=cursor.fetchone()
    total_sales=result_sum['total_sales']


    cursor.execute('SELECT SUM(quantity) AS total_units FROM order_details')
    result_units=cursor.fetchone()
    total_units=result_units['total_units']

    cursor.execute('SELECT COUNT(*) AS total_orders FROM orders WHERE is_cancelled=0 AND is_deleted=0')
    result=cursor.fetchone()
    total_orders=result['total_orders'] 

    avg_order=int(total_sales / total_units)

    cursor.execute("""SELECT COUNT(order_id) AS total_return FROM order_returns WHERE status='approved' 
                   AND is_cancelled=0 """)
    return_result=cursor.fetchone()
    total_returns=return_result['total_return']

    cursor.execute("""SELECT SUM(p.amount) AS pending_cod 
                   FROM order_payments  p
                   JOIN orders o ON p.order_id=o.order_id
                   WHERE p.status='pending' AND p.payment_method='COD' AND o.is_cancelled=0  """)
    pending_result=cursor.fetchone()
    pending_cod=pending_result['pending_cod']


    cursor.execute("""
        SELECT 
            c.name AS name,
            COALESCE(SUM(CASE WHEN o.order_id IS NOT NULL AND o.is_cancelled=0 AND o.is_deleted=0 THEN od.quantity ELSE 0 END), 0) AS units_sold,
            COALESCE(SUM(CASE WHEN o.order_id IS NOT NULL AND o.is_cancelled=0 AND o.is_deleted=0 THEN od.subtotal ELSE 0 END), 0) AS revenue,
            COALESCE(SUM(CASE WHEN o.order_id IS NOT NULL AND o.is_cancelled=0 AND o.is_deleted=0 AND (oir.status='approved' OR o.status='returned') THEN od.quantity ELSE 0 END), 0) AS returns,
            (COALESCE(SUM(CASE WHEN o.order_id IS NOT NULL AND o.is_cancelled=0 AND o.is_deleted=0 THEN od.subtotal ELSE 0 END), 0) - 
             COALESCE(SUM(CASE WHEN o.order_id IS NOT NULL AND o.is_cancelled=0 AND o.is_deleted=0 AND (oir.status='approved' OR o.status='returned') THEN od.subtotal ELSE 0 END), 0)) AS net_revenue
        FROM categories c
        LEFT JOIN products p ON c.category_id=p.category_id
        LEFT JOIN order_details od ON p.product_id=od.product_id
        LEFT JOIN orders o ON od.order_id=o.order_id AND o.is_deleted=0
        LEFT JOIN order_item_returns oir ON od.order_detail_id=oir.order_detail_id AND oir.status='approved'
        GROUP BY c.category_id,c.name
        ORDER BY net_revenue DESC
    """)
    category_sales=cursor.fetchall()

    cursor.execute("""
                   SELECT p.title,p.base_price,p.stock_quantity,
           c.name AS category_name,
           SUM(od.quantity) AS units_sold,
           SUM(od.subtotal) AS total_revenue
    FROM order_details od
    JOIN products p ON od.product_id=p.product_id
    JOIN categories c ON p.category_id=c.category_id
    JOIN orders o ON od.order_id=o.order_id
    WHERE o.is_cancelled=0 AND o.is_deleted=0 AND o.status='delivered' AND p.status='active'
    GROUP BY p.product_id,p.title,p.base_price,p.stock_quantity,c.name
    ORDER BY units_sold DESC
    LIMIT 5 
    """)
    top_products=cursor.fetchall()

    cursor.execute("""
    SELECT o.order_number,o.ordered_at,o.total_amount,o.status,o.order_id,
        CONCAT(u.first_name,' ',u.last_name) AS customer_name,u.email,
                   p.payment_method,p.status AS pay_status
                   FROM orders o 
                   JOIN users u ON o.user_id=u.user_id
                   JOIN order_payments p ON o.order_id=p.order_id
                   WHERE o.is_cancelled=0 AND o.is_deleted=0
                   LIMIT 4
     """)
    recent_orders=cursor.fetchall()
    
    

    

    return render_template('sales.htm',total_sales=total_sales,total_returns=total_returns,
                           recent_orders=recent_orders,
                           pending_cod=pending_cod,total_units=total_units,top_products=top_products,
                           total_orders=total_orders,avg_order=avg_order,category_sales=category_sales)




@admin_bp.route('/bulk_delete',methods=['POST'])
def bulk_delete():
    cursor=mysql.connection.cursor()
    ids=request.form.getlist('bulk_ids')
    table=request.form.get('table')   
    column=request.form.get('column')  
     
    ALLOWED={
    'orders':('order_id','is_deleted', 1),
    'product_reviews':('review_id','is_deleted',1),
    'forms':('form_id','is_deleted',1),
    'products':('product_id','is_deleted',1),
    'users':('user_id','is_active',0), 
    }

    if not ids or table not in ALLOWED or ALLOWED[table][0] != column:
        session['admin_toast']='Invalid request.'
        return redirect(request.referrer)

    col_id, col_flag, flag_val=ALLOWED[table]
    cursor.executemany(
        f"UPDATE {table} SET {col_flag}=%s WHERE {col_id}=%s",
        [(flag_val, i) for i in ids]
    )
    mysql.connection.commit()
    cursor.close()

    session['admin_toast']=f'{len(ids)} item(s) deleted.'
    return redirect(request.referrer)



