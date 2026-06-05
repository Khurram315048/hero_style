from flask import render_template,request,flash,redirect,url_for,session
from utils.auth import admin_required
import math
from categories import cat_bp
from categories.categ_models import CategoryModel


@cat_bp.route('/all_categories')
@admin_required
def all_categories():
    admin_id=session.get('admin_id')
    admin=CategoryModel.get_admin(admin_id)

    page=request.args.get('page',1,type=int)
    if page<1:
        page=1

    per_page=10
    offset=(page - 1) * per_page

    rows=CategoryModel.get_all_paginated(per_page,offset)
    categories=[dict(row) for row in rows]

    max_revenue=max((cat['total_revenue'] for cat in categories),default=0)
    for cat in categories:
        cat['is_top']=(cat['total_revenue']==max_revenue and max_revenue>0)

    total_rows=CategoryModel.count_all()
    total_pages=math.ceil(total_rows / per_page)
    return render_template('all_categories.htm',admin=admin,categories=categories,page=page,total_pages=total_pages)


@cat_bp.route('/category_product/<int:category_id>')
@admin_required
def category_product(category_id):
    admin=CategoryModel.get_full_admin(session.get('admin_id'))
    category=CategoryModel.get_by_id(category_id)
    products=CategoryModel.get_products_by_category(category_id)
    return render_template('category_product.htm',admin=admin,category=category,products=products)


@cat_bp.route('/category_delete/<int:category_id>')
@admin_required
def delete_category(category_id):
    CategoryModel.delete(category_id)
    session['admin_toast']='Category Deleted Successfully!'
    return redirect(request.referrer)


@cat_bp.route('/toggle_category/<int:category_id>')
@admin_required
def toggle_category(category_id):
    cat=CategoryModel.get_is_active(category_id)

    if not cat:
        flash('Category not found.','danger')
        return redirect(url_for('categories.all_categories'))

    new_status=0 if cat['is_active'] else 1
    CategoryModel.toggle_active(category_id,new_status)
    session['admin_toast']='Category activated.' if new_status==1 else 'Category deactivated.'
    return redirect(url_for('categories.all_categories'))



@cat_bp.route('/add_category',methods=['POST'])
@admin_required
def add_category():
    name=request.form.get('name')
    description=request.form.get('description')
    status=request.form.get('is_active')

    if CategoryModel.name_exists(name):
        session['admin_toast']=f'Category with this {name} already exist'
        return redirect(url_for('categories.all_categories'))

    CategoryModel.create(name,description,status)
    session['admin_toast']=name+' category added to the system successfully!'
    return redirect(url_for('categories.all_categories'))


@cat_bp.route('/edit_category/<int:category_id>',methods=['GET','POST'])
@admin_required
def edit_category(category_id):
    if request.method=='POST':
        name=request.form.get('name')
        description=request.form.get('description')
        is_active=request.form.get('is_active')

        category=CategoryModel.get_by_id(category_id)
        if not category:
            session['admin_toast']='Category does not exist!'
            return redirect(url_for('categories.all_categories'))


        if CategoryModel.name_exists_other(name,category_id):
            session['admin_toast']=f'{name} category already exist'
            return redirect(url_for('categories.all_categories'))


        CategoryModel.update(category_id,name,description,is_active)
        session['admin_toast']=f'{name} category updated successfully!'

    return redirect(url_for('categories.all_categories'))