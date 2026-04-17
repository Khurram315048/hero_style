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
        if user:
            if check_password_hash(user['password_hash'],password):
                session['user_id']=user['user_id']
                session.permanent=True if request.form.get('remember_me') else False
                flash('User Logined','success')
                return redirect(url_for('users.user_dashboard'))
            else:
                flash('Password Doesnot Match','danger')
                return redirect(url_for('users.user_login'))
            
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
        phone_num=request.form.get('phone_num')
        plain_password=request.form.get('password')
        hashed_password=generate_password_hash(plain_password)

        cursor.execute('SELECT email FROM users WHERE email=%s',(email,))
        user_exist=cursor.fetchone()
        if user_exist:
            flash('Email Already Exist','success')
            return redirect(url_for('users.user_login'))
        
        cursor.execute('''INSERT INTO users
                    (role_id,first_name,last_name,email,phone,password_hash,last_login_at,created_at,updated_at)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)''',(2,first_name,last_name,email,phone_num,
                                                hashed_password,datetime.now(),datetime.now(),datetime.now()))
        mysql.connection.commit()
        cursor.close()
        flash('Registeration Successfull','success')
        return redirect(url_for('users.user_login'))
    
    return render_template('user_signup.htm')


@user_bp.route('/user_options',methods=['GET','POST'])
def user_options():
    cursor=mysql.connection.cursor()
    user_id=session.get('user_id')
    cursor.execute('SELECT email,CONCAT(first_name,'',last_name) AS username FROM users WHERE user_id=%s',(user_id,))
    user=cursor.fetchone()
    return render_template('user_options.htm',user=user)


@user_bp.route('/reset_password')
def reset_password():
    return render_template('reset_password.htm')



@user_bp.route('/user_dashboard',methods=['GET','POST'])
@login_required
def user_dashboard():
    cursor=mysql.connection.cursor()
    user_id=session.get('user_id')

    cursor.execute('''
        SELECT u.*,COUNT(o.order_id) AS total_orders 
        FROM users u 
        LEFT JOIN orders o ON u.user_id=o.user_id 
        WHERE u.user_id=%s 
        GROUP BY u.user_id
    ''',(user_id,))
    
    user_exist=cursor.fetchone()
    cursor.close()
    
    return render_template('user_dashboard.htm',user_exist=user_exist)



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
        phone=request.form.get('phone')
        country=request.form.get('country')
        city=request.form.get('city')
        address=request.form.get('address')

        cursor.execute('''UPDATE users SET first_name=%s,last_name=%s,email=%s,
                       phone=%s,country=%s,city=%s,address=%s
                       WHERE user_id=%s AND is_active=%s''',(first_name,last_name,email,phone,country,city,address,user_id,1))
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
    user_id = session.get('user_id')
    cursor = mysql.connection.cursor()

    # Query mein ORDER BY add kiya gaya hai takay naye orders pehle nazar aayein
    cursor.execute('''
        SELECT * FROM orders 
        WHERE user_id = %s AND is_deleted = 0 
        ORDER BY ordered_at DESC
    ''', (user_id,))
    
    orders = cursor.fetchall()
    cursor.close() # Connection close karna zaroori hai

    return render_template('user_orders.htm', orders=orders)