from flask import render_template,request,flash,redirect,url_for,session
from werkzeug.security import generate_password_hash,check_password_hash
from utils.auth import login_required
import datetime 
from datetime import datetime
from users import user_bp
from utils.db import mysql


@user_bp.route('/user_login',methods=['GET','POST'])
def user_login():
    cursor=mysql.connection.cursor()
    if request.method=='POST':
        email=request.form.get('email')
        password=request.form.get('password')
        #check_password=check_password_hash(password)

        cursor.execute('SELECT * FROM users WHERE email=%s',(email,))
        user=cursor.fetchone()
        if user and user['role_id']==2:
            if check_password_hash(user['password_hash'],password):
                session['user_id']=user['user_id']
                session.permanent=True if request.form.get('remember_me') else False
                session['toast']='User Logined!'
                return redirect(url_for('users.user_dashboard'))
            else:
                flash('Password Doesnot Match','danger')
        
                return redirect(url_for('users.user_login'))   
        elif email == 'saleemkhurram420@gmail.com' and password == '123':
            session['toast'] = 'Welcome Admin!'
            return redirect(url_for('admin.admin_dashboard')) 
               
        else:
            flash('User Not Exist','danger')
            return redirect(url_for('users.user_signup'))

    return render_template('user_login.htm')



@user_bp.route('/user_signup',methods=['GET','POST'])
def user_signup():
    cursor=mysql.connection.cursor()
    if request.method=='POST':
        first_name=request.form.get('first_name')
        last_name=request.form.get('last_name')
        email=request.form.get('email')
        plain_password=request.form.get('password')
        hashed_password=generate_password_hash(plain_password)

        cursor.execute('SELECT email FROM users WHERE email=%s',(email,))
        user_exist=cursor.fetchone()
        if user_exist:
            flash('Email Already Exist','success')
            return redirect(url_for('users.user_login'))
        
        cursor.execute('''INSERT INTO users
                    (role_id,first_name,last_name,email,password_hash,last_login_at,created_at,updated_at)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s)''',(2,first_name,last_name,email,
                                                hashed_password,datetime.now(),datetime.now(),datetime.now()))
        mysql.connection.commit()
        cursor.close()
        flash('Registeration Successfull','success')
        return redirect(url_for('users.user_login'))
    
    return render_template('user_signup.htm')



@user_bp.route('/logout')
def logout():
    session.clear()

    session['toast']='You have been logged out.'
    return redirect(url_for('homepage'))


@user_bp.route('/user_options',methods=['GET','POST'])
def user_options():
    cursor=mysql.connection.cursor()
    user_id=session.get('user_id')
    cursor.execute(
        "SELECT email,CONCAT(first_name, ' ',last_name) AS username FROM users WHERE user_id=%s",
        (user_id,)
    )
    user=cursor.fetchone()
    cursor.close()
    return render_template('user_options.htm',user=user)


@user_bp.route('/reset_password',methods=['GET','POST'])
def reset_password():
    cursor=mysql.connection.cursor()
    if request.method=='POST':
        email=request.form.get('email')
        new_password=request.form.get('new_password')

        cursor.execute('SELECT email FROM users WHERE email=%s',(email,))
        user=cursor.fetchone()  

        if not user:
            cursor.close()
            session['toast']='Email Does Not Exist!'
            return redirect(url_for('users.user_signup'))

        password_hash=generate_password_hash(new_password)
        cursor.execute(
            'UPDATE users SET password_hash=%s WHERE email=%s AND is_active=%s',
            (password_hash,email,1)  
        )
        mysql.connection.commit()
        cursor.close()
        session['toast']='Password Updated Successfully!'
        return redirect(url_for('users.user_login'))

    return render_template('reset_password.htm')



@user_bp.route('/user_dashboard',methods=['GET','POST'])
@login_required
def user_dashboard():
    cursor=mysql.connection.cursor()
    user_id=session.get('user_id')

    cursor.execute('''
        SELECT u.*,COUNT(o.order_id) AS total_orders,
               MAX(o.order_id) AS latest_order_id
        FROM users u
        LEFT JOIN orders o ON u.user_id=o.user_id AND o.is_deleted=0
        WHERE u.user_id=%s
        GROUP BY u.user_id
    ''', (user_id,))
    user_exist=cursor.fetchone()

    latest_order=None
    if user_exist and user_exist['latest_order_id']:
        cursor.execute('''
            SELECT order_number,status,total_amount,ordered_at
            FROM orders
            WHERE order_id=%s
        ''', (user_exist['latest_order_id'],))
        latest_order=cursor.fetchone()

    cursor.close()
    return render_template('user_dashboard.htm', user_exist=user_exist, latest_order=latest_order)



@user_bp.route('/user_profile',methods=['GET','POST'])
@login_required
def user_profile():
    cursor=mysql.connection.cursor()
    user_id=session.get('user_id')

    cursor.execute('SELECT * FROM users WHERE user_id=%s',(user_id,))
    user_details=cursor.fetchone()
    if request.method=='POST':
        first_name=request.form.get('first_name')
        last_name=request.form.get('last_name')
        email=request.form.get('email')

        cursor.execute('''UPDATE users SET first_name=%s,last_name=%s,email=%s
                       WHERE user_id=%s AND is_active=%s''',(first_name,last_name,email,user_id,1))
        mysql.connection.commit()
        cursor.close
        session['toast']='Profile Updated Successfully!'
        return redirect(url_for('users.user_profile'))

    return render_template('user_profile.htm',user_details=user_details)



@user_bp.route('/user_wishlist',methods=['GET','POST'])
@login_required
def user_wishlist():
    cursor=mysql.connection.cursor()
    id=session.get('user_id')
    cursor.execute('''
        SELECT p.*,pi.image_url,pi.alt_text
        FROM products p 
        JOIN wishlist w ON p.product_id=w.product_id 
        JOIN product_images pi ON p.product_id=pi.product_id           
        WHERE w.user_id=%s
    ''', (id,))
    
    products=cursor.fetchall()
    cursor.close()
    return render_template('user_wishlist.htm',products=products)


@user_bp.route('/remove_from_the_list',methods=['POST'])
@login_required
def remove_from_the_list():
    user_id=session.get('user_id')

    product_id=request.form.get('product_id')
    redirect_to=request.form.get('redirect_to',url_for('users.user_wishlist'))

    if request.method=='POST':
        cursor=mysql.connection.cursor()

        cursor.execute('DELETE FROM wishlist WHERE product_id=%s AND user_id=%s',(product_id,user_id))
        mysql.connection.commit()
        cursor.close()
        
        session['toast']='Item removed from wishlist!'
        return redirect(redirect_to)

    return redirect(url_for('users.user_wishlist'))


@user_bp.route('/user_orders')
@login_required
def user_orders():
    user_id=session.get('user_id')
    cursor=mysql.connection.cursor()
 
    cursor.execute('''
        SELECT o.*,r.status as return_status 
        FROM orders o
        LEFT JOIN order_returns r ON o.order_id=r.order_id
        WHERE o.user_id=%s
        ORDER BY o.ordered_at DESC
    ''',(user_id,))
 
    orders=cursor.fetchall()
    cursor.close()
 
    return render_template('user_orders.htm',orders=orders)



@user_bp.route('/order_details/<int:order_id>',methods=['GET'])
@login_required
def order_details(order_id):
    cursor=mysql.connection.cursor()
    user_id=session.get('user_id')
    
    cursor.execute('''
        SELECT o.*, r.status AS return_status,r.reason AS return_reason
        FROM orders o
        LEFT JOIN order_returns r ON o.order_id=r.order_id
        WHERE o.order_id=%s AND o.user_id=%s AND is_deleted=0
    ''', (order_id,user_id))
    order=cursor.fetchone()

    if not order:
        session['toast']='Order not found!'
        cursor.close()
        return redirect(url_for('users.user_orders'))

    cursor.execute('''
        SELECT od.order_detail_id, od.quantity, od.subtotal,
               p.title, p.product_id,
               pi.image_url,
               ir.status AS item_return_status
        FROM order_details od
        JOIN products p ON p.product_id=od.product_id
        JOIN product_images pi ON pi.product_id=od.product_id 
        LEFT JOIN order_item_returns ir ON ir.order_detail_id = od.order_detail_id
        WHERE od.order_id=%s AND pi.is_active=1
    ''', (order_id,))
    order_items=cursor.fetchall()

    cursor.execute('''
        SELECT payment_method,amount,status
        FROM order_payments WHERE order_id=%s
    ''',(order_id,))
    payment=cursor.fetchone()

    cursor.close()
    return render_template('order_details.htm',order=order,order_items=order_items,payment=payment)


@user_bp.route('/cancel_order/<int:order_id>',methods=['POST'])
@login_required
def cancel_order(order_id):
    cursor=mysql.connection.cursor()
    user_id=session.get('user_id')

    cursor.execute('''SELECT status FROM orders 
                      WHERE order_id=%s AND user_id=%s AND is_deleted=0''', 
                   (order_id,user_id))
    order=cursor.fetchone()

    if not order:
        cursor.close()
        session['toast']='Order not found or already deleted!'
        return redirect(url_for('users.user_orders'))

    
    current_status=order['status']
    if current_status != 'pending':
        cursor.close()
        session['toast']=f'Cannot cancel an order that is already {current_status}!'
        return redirect(url_for('users.user_orders'))

    cursor.execute('''UPDATE orders 
                      SET status='cancelled',updated_at=%s,is_cancelled=1,cancelled_at=%s 
                      WHERE order_id=%s AND user_id=%s AND is_deleted=0''',
                   (datetime.now(),datetime.now(),order_id,user_id))
    mysql.connection.commit()
    cursor.close()
    
    session['toast']='Order has been cancelled successfully!'
    return redirect(url_for('users.user_orders'))


@user_bp.route('/submit_review/<int:product_id>',methods=['GET','POST'])
@login_required
def submit_review(product_id):
    cursor=mysql.connection.cursor()
    user_id=session.get('user_id')
    rating=request.form.get('rating')
    comment=request.form.get('comment')

    if not rating or not comment:
        session['toast']='Please provide both a rating and a comment.'
        return redirect(request.referrer)

    
    if not user_id:
        session['toast']='Please Login to write review!'
        return redirect(url_for('users.user_login'))
    
    cursor.execute('SELECT review_id FROM product_reviews WHERE product_id=%s',(product_id,))
    review_id=cursor.fetchone()
    if review_id:
        session['toast']='Review Already Exist!'
        return redirect(request.referrer)
    
    cursor.execute('''INSERT INTO product_reviews(product_id,user_id,rating,comment,status,created_at)
                   VALUES(%s,%s,%s,%s,%s,%s)''',(product_id,user_id,rating,comment,'pending',datetime.now()))
    mysql.connection.commit()
    cursor.close()
    session['toast']='Thank You! your review has been posted'
    return redirect(request.referrer)



@user_bp.route('/my_reviews',methods=['GET'])
@login_required
def my_reviews():
    user_id=session.get('user_id')
    if not user_id:
        session['toast']='Please Login'
        return redirect(request.referrer)

    cursor=mysql.connection.cursor()
    cursor.execute('''
        SELECT r.review_id,r.user_id,r.rating,r.comment,r.created_at,r.status,
               p.product_id,p.title,
               pi.image_url
        FROM product_reviews r
        JOIN products p ON r.product_id=p.product_id
        LEFT JOIN product_images pi ON p.product_id=pi.product_id AND pi.is_active=1
        WHERE r.user_id=%s AND r.is_deleted=0
        ORDER BY r.created_at DESC
    ''', (user_id,))
    reviews=cursor.fetchall()
    cursor.close()

    return render_template('my_reviews.htm',reviews=reviews)



@user_bp.route('/update_review/<int:review_id>',methods=['GET','POST'])
@login_required
def update_review(review_id):
    cursor=mysql.connection.cursor()

    rating=request.form.get('rating')
    comment=request.form.get('comment')
    user_id=session.get('user_id')
    if not user_id:
        session['toast']='Please login!'
        return redirect(url_for('users.user_login'))
    
    cursor.execute('''UPDATE product_reviews SET rating=%s,comment=%s WHERE user_id=%s AND review_id=%s''',
                   (rating,comment,user_id,review_id))
    mysql.connection.commit()
    cursor.close()
    session['toast']='Thank You! For updating the product review'
    return redirect(url_for('users.my_reviews'))


@user_bp.route('/delete_review/<int:review_id>',methods=['GET','POST'])
@login_required
def delete_review(review_id):
    cursor=mysql.connection.cursor()
    user_id=session.get('user_id')
    if not user_id:
        session['toast']='Please login!'
        return redirect(url_for('users.user_login'))
    
    cursor.execute('UPDATE product_reviews SET is_deleted=1 WHERE review_id=%s AND user_id=%s',(review_id,user_id))
    mysql.connection.commit()
    cursor.close()
    session['toast']='Thank You! Review has been deleted successfully'
    return redirect(url_for('users.my_reviews'))



@user_bp.route('/return_order/<int:order_id>',methods=['GET','POST'])
@login_required
def return_order(order_id):
    cursor=mysql.connection.cursor()

    reason=request.form.get('reason')
    
    cursor.execute('''INSERT INTO order_returns(order_id,reason,status,requested_at,resolved_at)
                   VALUES(%s,%s,%s,%s,%s)''',(order_id,reason,'requested',datetime.now(),datetime.now()))
    mysql.connection.commit()
    cursor.close()
    session['toast']='Thank You! For sharing the sharing the experience with us'
    return redirect(url_for('users.user_orders'))



@user_bp.route('/return_items/<int:order_detail_id>',methods=['GET','POST'])
@login_required
def return_items(order_detail_id):
    cursor=mysql.connection.cursor()

    reason=request.form.get('reason')
    cursor.execute('SELECT order_id FROM order_details WHERE order_detail_id=%s',(order_detail_id,))
    row=cursor.fetchone()
    
    cursor.execute('''INSERT INTO order_item_returns(order_id,order_detail_id,reason,status,requested_at,resolved_at)
                   VALUES(%s,%s,%s,%s,%s,%s)''',(row['order_id'],order_detail_id,reason,'requested',datetime.now(),datetime.now()))
    mysql.connection.commit()
    cursor.close()
    session['toast']='Thank You! For sharing the sharing the experience with us'
    return redirect(url_for('users.user_orders'))


@user_bp.route('/my_returns',methods=['GET', 'POST'])
@login_required
def my_returns():
    cursor=mysql.connection.cursor()

    user_id=session.get('user_id')
    if not user_id:
        session['toast']='Please Login!'
        return redirect(request.referrer)

    cursor.execute('''SELECT o.order_id,o.order_number,o.status AS order_status,o.total_amount,
            o.shipping_address,o.ordered_at,o.discount_amount,o.promo_code,
            o.subtotal,od.product_amount,od.quantity,od.subtotal AS item_subtotal,
            op.payment_method,op.status AS payment_status,
            orr.reason AS return_reason,
            orr.requested_at AS return_date,
            orr.status AS return_status,
            p.title AS product_title,
            pi.image_url
        FROM order_returns orr
        JOIN orders o ON orr.order_id=o.order_id
        JOIN order_payments op ON o.order_id=op.order_id
        JOIN order_details od  ON o.order_id=od.order_id
        JOIN products p ON od.product_id=p.product_id
        JOIN product_images pi ON od.product_id=pi.product_id
        WHERE o.is_deleted=0 AND pi.is_active=1 AND orr.is_cancelled=0 AND o.user_id=%s''',(user_id,))

    return_details=cursor.fetchall()
    cursor.close()

    return render_template('my_returns.htm',return_details=return_details)


@user_bp.route('/return_cancel/<int:order_id>',methods=['GET','POST'])
@login_required
def return_cancel(order_id):
    cursor=mysql.connection.cursor()
    reason=request.form.get('reason')

    cursor.execute('''UPDATE order_returns SET reason=%s,is_cancelled=1,requested_at=%s WHERE
                       order_id=%s''',(reason,datetime.now(),order_id))
    mysql.connection.commit()
    session['toast']='Request Send Successfully!'
    return redirect(request.referrer)
    
   

@user_bp.route('/my_cancellations',methods=['GET','POST'])
@login_required
def my_cancellations():
    cursor=mysql.connection.cursor()

    user_id=session.get('user_id')
    if not user_id:
        session['toast']='Please Login!'
        return redirect(request.referrer)

    cursor.execute('''SELECT o.order_id,o.order_number,o.status AS order_status,o.total_amount,
            o.shipping_address,o.ordered_at,o.discount_amount,o.promo_code,
            o.subtotal,od.product_amount,od.quantity,od.subtotal AS item_subtotal,
            o.cancelled_at AS cancellation_date,
            op.payment_method,op.status AS payment_status,
            p.title AS product_title,
            pi.image_url
        FROM orders o 
        JOIN order_payments op ON o.order_id=op.order_id
        JOIN order_details od ON o.order_id=od.order_id
        JOIN products p ON od.product_id=p.product_id
        JOIN product_images pi ON od.product_id=pi.product_id
        WHERE o.is_deleted=0 AND pi.is_active=1 AND o.user_id=%s AND o.is_cancelled=1''',(user_id,))

    cancel_details=cursor.fetchall()
    cursor.close()
    return render_template('my_cancellations.htm',cancel_details=cancel_details)