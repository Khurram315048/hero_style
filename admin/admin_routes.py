from flask import render_template,request,flash,redirect,url_for,session
from werkzeug.security import generate_password_hash,check_password_hash
from utils.auth import admin_required
import datetime 
from datetime import datetime
from admin import admin_bp
from utils.db import mysql




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
        session['toast']='Welcome back!'
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
            session['toast']='Already Registered!'
            return redirect(url_for('admin.admin_login'))
        
        cursor.execute('''INSERT INTO admins(role_id,first_name,last_name,username,email,password_hash)
                    VALUES(%s,%s,%s,%s,%s,%s)''',(1,first_name,last_name,username,email,hash_password))
        mysql.connection.commit()
        session['toast']='You have been registered successfully!'
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
            session['toast']='Email Does Not Exist!'
            return redirect(url_for('admin.admin_signup'))

        password_hash=generate_password_hash(new_password)
        cursor.execute(
            'UPDATE admins SET password_hash=%s WHERE email=%s AND is_deleted=%s',
            (password_hash,email,0)  
        )
        mysql.connection.commit()
        cursor.close()
        session['toast']='Password Updated Successfully!'
        return redirect(url_for('admin.admin_login'))

    return render_template('admin_reset.htm')


@admin_bp.route('/logout')
@admin_required
def logout():
    session.clear()

    session['toast']='You have been logged out.'
    return redirect(url_for('admin.admin_login'))



@admin_bp.route('/admin_options',methods=['GET','POST'])
@admin_required
def admin_options():
    cursor=mysql.connection.cursor()
    admin_id=session.get('admin_id')
    cursor.execute(
        '''SELECT email,username FROM admins WHERE admin_id=%s''',
        (admin_id,)
    )
    admin=cursor.fetchone()
    cursor.close()
    return render_template('admin_options.htm',admin=admin)


@admin_bp.route('/admin_dashboard',methods=['GET','POST'])
@admin_required
def admin_dashboard():
    cursor=mysql.connection.cursor()
    admin_id=session.get('admin_id')
    cursor.execute(
        '''SELECT email,username,first_name,last_name FROM admins WHERE admin_id=%s''',
        (admin_id,)
    )
    admin=cursor.fetchone()
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
    return render_template('admin_dashboard.htm',admin=admin,total_forms=total_forms,
                           total_orders=total_orders,total_customers=total_customers,total_revenue=total_revenue)


