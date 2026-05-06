from flask import render_template,request,flash,redirect,url_for,session,g
from werkzeug.security import generate_password_hash,check_password_hash
from utils.auth import admin_required
import uuid
from datetime import datetime
from categories import cat_bp
from utils.db import mysql
import os
from werkzeug.utils import secure_filename



@cat_bp.route('/all_categories')
@admin_required
def all_categories():
    cursor = mysql.connection.cursor()
    admin_id=session.get('admin_id')
    cursor.execute('SELECT first_name,last_name,username FROM admins WHERE admin_id=%s',(admin_id,))
    admin=cursor.fetchone()

    cursor.execute("""SELECT c.category_id,c.name,c.description,c.is_active,c.created_at,
        COUNT(DISTINCT p.product_id) AS total_products,
        SUM(CASE WHEN p.status='active' THEN 1 ELSE 0 END) AS active_products,
        COALESCE(SUM(od.subtotal),0) AS total_revenue
    FROM categories c
    LEFT JOIN products p ON c.category_id=p.category_id
    LEFT JOIN order_details od ON p.product_id=od.product_id
    GROUP BY c.category_id
    ORDER BY total_revenue DESC
    """)
    rows=cursor.fetchall()
    categories=[dict(row) for row in rows]

    max_revenue=max((cat['total_revenue'] for cat in categories),default=0)

    for cat in categories:
        cat['is_top']=(cat['total_revenue']==max_revenue and max_revenue>0)  

    cursor.close()
    
    return render_template('all_categories.htm',admin=admin,categories=categories)


@cat_bp.route('/category_product/<int:category_id>')
@admin_required
def category_product(category_id):
    cursor=mysql.connection.cursor()
 
    cursor.execute("SELECT * FROM admins WHERE admin_id=%s",(session.get('admin_id'),))
    admin=cursor.fetchone()

    cursor.execute("SELECT * FROM categories WHERE category_id=%s", (category_id,))
    category=cursor.fetchone()

    cursor.execute("""SELECT p.product_id, p.product_no, p.title,p.base_price,p.sale_price,p.stock_quantity,
            p.status,p.created_at,p.updated_at,pi.image_url
        FROM products p
        LEFT JOIN product_images pi ON p.product_id=pi.product_id
        WHERE p.category_id=%s
        ORDER BY p.created_at DESC
    """,(category_id,))
    products=cursor.fetchall()
    cursor.close()

    return render_template('category_product.htm',admin=admin,category=category,products=products)



@cat_bp.route('/category_delete/<int:category_id>')
@admin_required
def delete_category(category_id):
    cursor=mysql.connection.cursor()

    cursor.execute('DELETE categories  WHERE category_id=%s',(category_id))
    mysql.connection.commit()
    cursor.close()
    session['admin_toast']='Category Deleted Successfully!'
    return redirect(request.referrer)


@cat_bp.route('/toggle_category/<int:category_id>')
@admin_required
def toggle_category(category_id):
    cursor=mysql.connection.cursor()

    cursor.execute("SELECT is_active FROM categories WHERE category_id=%s",(category_id,))
    cat=cursor.fetchone()

    if not cat:
        flash('Category not found.', 'danger')
        cursor.close()
        return redirect(url_for('categories.all_categories'))


    new_status=0 if cat['is_active'] else 1

    cursor.execute("UPDATE categories SET is_active=%s WHERE category_id=%s",
                (new_status,category_id))
    mysql.connection.commit()
    cursor.close()

    session['admin_toast']='Category activated' if new_status == 1 else 'Category deactivated.'
    return redirect(url_for('categories.all_categories'))


@cat_bp.route('/add_category',methods=['GET','POST'])
@admin_required
def add_category():
    cursor=mysql.connection.cursor()
    name=request.form.get('name')
    description=request.form.get('description')
    status=request.form.get('is_active')

    cursor.execute('SELECT category_id FROM categories WHERE name=%s',(name,))
    category_id=cursor.fetchone()
    if category_id:
        session['admin_toast']='Category with this ',name,' already exist'
        return redirect(url_for('categories.all_categories'))
    
    cursor.execute('''INSERT INTO categories(name,description,is_active,created_at)
                   VALUES(%s,%s,%s,%s)''',(name,description,status,datetime.now()))
    mysql.connection.commit()
    cursor.close()
    session['admin_toast']=name +' category added to the system successfully!'
    return redirect(url_for('categories.all_categories'))



@cat_bp.route('/edit_category/<int:category_id>',methods=['GET','POST'])
@admin_required
def edit_category(category_id):
    if request.method=='POST':
        cursor=mysql.connection.cursor()

        name=request.form.get('name')
        description=request.form.get('description')
        is_active=request.form.get('is_active') 

        cursor.execute('SELECT * FROM categories WHERE category_id=%s',(category_id,))
        category=cursor.fetchone()
        if not category:
            session['admin_toast']='Category desnot exist!'
            cursor.close()
            return redirect(url_for('categories.all_categories'))

        cursor.execute('SELECT category_id FROM categories WHERE name=%s AND category_id !=%s',
            (name,category_id))
        name_exists=cursor.fetchone()
        if name_exists:
            session['admin_toast']=name +'category already exist'
            cursor.close()
            return redirect(url_for('categories.all_categories'))

        cursor.execute(''' UPDATE categories SET name=%s,description=%s,is_active=%s
            WHERE category_id=%s
        ''',(name,description,is_active,category_id))

        mysql.connection.commit()
        cursor.close()
        session['admin_toast']=name + 'category updated successfully!'
        return redirect(url_for('categories.all_categories'))

    return redirect(url_for('categories.all_categories'))