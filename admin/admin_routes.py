from flask import render_template,flash,redirect,url_for,session,g,request
from werkzeug.security import generate_password_hash,check_password_hash
from utils.auth import admin_required
import uuid
import random,string
from flask_mail import Message
import math
from utils.limiter import limiter
from datetime import datetime,timedelta
from admin import admin_bp
from utils.db import mysql
import os
from werkzeug.utils import secure_filename
from pydantic import ValidationError
from admin.admin_validators import(
    AdminSignupValidator,AdminLoginValidator,
    ProductValidator,CategoryValidator,OrderStatusValidator,
    AdminProfileValidator,AdminResetEmailValidator,
    AdminOTPVerifyValidator,AdminNewPasswordValidator,ReviewStatusValidator
)
from utils.validators import extract_errors
from admin.admin_models import (
    AdminModel,OTPModel,ProductModel,ProductDetailsModel,
    ProductImageModel,CategoryModel,OrderModel,OrderPaymentModel,
    OrderReturnModel,CustomerModel,FormModel,ReviewModel,SalesModel,DashboardModel)


@admin_bp.context_processor
def inject_admin():
    admin=None
    admin_id=session.get('admin_id')
    if admin_id:
        admin=AdminModel.get_by_id(admin_id)
    return dict(admin=admin)






@admin_bp.route('/admin_login',methods=['GET','POST'])
@limiter.limit("5 per 15 minutes")
def admin_login():
    if request.method=='POST':
        try:
            data=AdminLoginValidator(
                email=request.form.get('email', ''),
                password=request.form.get('password', '')
            )
        except ValidationError as e:
            flash(extract_errors(e)[0],'danger')
            return redirect(url_for('admin.admin_login'))

        admin=AdminModel.get_by_email(data.email)
        if not admin:
            flash('Account does not exist','danger')
            

        if not check_password_hash(admin['password_hash'],data.password):
            flash('Password does not match','danger')
            return redirect(url_for('admin.admin_login'))

        session['admin_id']=admin['admin_id']
        session['role']='admin'
        session.permanent=True if request.form.get('remember_me') else False
        session['admin_toast']='Welcome back!'
        return redirect(url_for('admin.admin_dashboard'))

    return render_template('admin_login.htm')






@admin_bp.route('/admin_reset',methods=['GET','POST'])
def admin_reset():
    from main import mail
    if request.method=='POST':
        step=request.form.get('step')

        if step=='send_otp':
            try:
                data=AdminResetEmailValidator(
                    email=request.form.get('email','')
                )
            except ValidationError as e:
                session['admin_toast']=extract_errors(e)[0]
                return redirect(url_for('admin.admin_reset'))

            admin=AdminModel.get_by_email(data.email)

            if not admin:
                session['admin_toast']='Email not found!'
                

            otp=''.join(random.choices(string.digits,k=6))
            expires=datetime.now() + timedelta(minutes=10)

            OTPModel.delete_by_email(data.email)
            OTPModel.create(data.email,otp,expires)

            msg=Message(
                subject='Hero Style — Password Reset OTP',
                recipients=[data.email],
                body=f"""Your OTP for password reset is: {otp}
                            This code expires in 10 minutes.
                            If you did not request this, ignore this email.
                            — Hero Style Team Developed By Muhammad Khurram""",)
            mail.send(msg)
            session['reset_email']=data.email
            session['admin_toast']='OTP sent to your email!'
            return redirect(url_for('admin.verify_admin_otp'))

    return render_template('admin_reset.htm')


@admin_bp.route('/verify_admin_otp',methods=['GET','POST'])
def verify_admin_otp():
    email=session.get('reset_email')

    if not email:
        return redirect(url_for('admin.admin_reset'))

    if request.method=='POST':
        step=request.form.get('step')

        if step=='verify':
            try:
                data=AdminOTPVerifyValidator(
                    otp=request.form.get('otp','')
                )
            except ValidationError as e:
                session['admin_toast']=extract_errors(e)[0]
                return redirect(url_for('admin.verify_admin_otp'))

            record=OTPModel.verify(email,data.otp)

            if not record:
                session['admin_toast']='Invalid or expired OTP!'
                return redirect(url_for('admin.verify_admin_otp'))

            session['otp_verified']=True
            OTPModel.mark_used(email)
            return redirect(url_for('admin.set_new_pass_admin'))

    return render_template('verify_admin_otp.htm',email=email)


@admin_bp.route('/set_new_pass_admin',methods=['GET','POST'])
def set_new_pass_admin():
    email=session.get('reset_email')
    verified=session.get('otp_verified')

    if not email or not verified:
        return redirect(url_for('admin.admin_reset'))

    if request.method=='POST':
        try:
            data=AdminNewPasswordValidator(
                new_password=request.form.get('new_password',''),
                confirm_password=request.form.get('confirm_password','')
            )
        except ValidationError as e:
            session['admin_toast']=extract_errors(e)[0]
            return redirect(url_for('admin.set_new_pass_admin'))

        AdminModel.update_password(email,data.new_password)
        session.pop('reset_email',None)
        session.pop('otp_verified',None)
        session['admin_toast']='Password updated successfully!'
        return redirect(url_for('admin.admin_login'))

    return render_template('set_new_pass_admin.htm')


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
    stats=DashboardModel.get_stats()
    return render_template('admin_dashboard.htm',
        total_forms=stats['total_forms'],
        total_orders=stats['total_orders'],
        total_customers=stats['total_customers'],
        total_revenue=stats['total_revenue'])


@admin_bp.route('/main_products',methods=['GET','POST'])
@admin_required
def main_products():
    page=request.args.get('page',1,type=int)
    if page<1:
        page=1

    per_page=10
    offset=(page - 1) * per_page

    products=ProductModel.get_all_paginated(per_page,offset)
    categories=CategoryModel.get_active()
    total_rows=ProductModel.count_all()
    total_pages=math.ceil(total_rows / per_page)
    return render_template('main_products.htm',products=products,page=page,
                           categories=categories,total_pages=total_pages)


@admin_bp.route('/admin_profile',methods=['GET','POST'])
@admin_required
def admin_profile():
    admin_id=session.get('admin_id')
    if request.method=='POST':
        try:
            data=AdminProfileValidator(
                first_name=request.form.get('first_name',''),
                last_name=request.form.get('last_name',''),
                username=request.form.get('user_name',''),
                email=request.form.get('email','')
            )
        except ValidationError as e:
            session['admin_toast']=extract_errors(e)[0]
            return redirect(request.referrer)

        AdminModel.update_profile(admin_id,data.first_name,data.last_name,data.username,data.email)
        session['admin_toast']='Profile Updated Success!'
        return redirect(request.referrer)

    admin_details=AdminModel.get_full_by_id(admin_id)
    return render_template('admin_profile.htm',admin_details=admin_details)


# @admin_bp.route('/add_product',methods=['POST'])
# @admin_required
# def add_product():
#     title=request.form.get('title')
#     category_id=request.form.get('category')
#     base_price=request.form.get('base_price')
#     sale_price=request.form.get('sale_price')
#     stock=request.form.get('stock',0)
#     status=request.form.get('status','active')
#     short_desc=request.form.get('short_description')
#     long_desc=request.form.get('long_description')
#     display_type=request.form.get('display_type')
#     brightness_nits=request.form.get('brightness_nits') or None
#     battery_life=request.form.get('battery_life')
#     connectivity=request.form.get('connectivity')
#     strap_material=request.form.get('strap_material')
#     case_material=request.form.get('case_material')
#     water_resistance=request.form.get('water_resistance')
#     weight=request.form.get('weight')
#     warranty_month=request.form.get('warranty_month',12)
#     always_display=request.form.get('always_display',0)
#     product_no=request.form.get('product_no')
#     image=request.files.get('image')
#     width=12
#     height=12

#     product_id=ProductModel.create(product_no,category_id,title,base_price,sale_price,stock,status)
#     ProductDetailsModel.create(product_id,short_desc,long_desc,display_type,brightness_nits,
#         battery_life,connectivity,strap_material,case_material,water_resistance,
#         weight,warranty_month,always_display)

#     if image and image.filename != '':
#         cat=ProductImageModel.get_category_name(category_id)
#         cat_name=cat['name'].lower().replace(' ','_')
#         filename=secure_filename(image.filename)
#         upload_folder=os.path.join('static','uploads',cat_name)
#         os.makedirs(upload_folder,exist_ok=True)
#         image_path=os.path.join(upload_folder,filename)
#         image.save(image_path)
#         image_url='/'+image_path.replace('\\','/')
#         ProductImageModel.create(product_id,image_url,title,width,height)

#     session['admin_toast']='Product Added Successfully!'
#     return redirect(url_for('admin.main_products'))


@admin_bp.route('/add_product',methods=['POST'])
@admin_required
def add_product():
    try:
        data=ProductValidator(
            title=request.form.get('title',''),
            product_no=request.form.get('product_no',''),
            category_id=request.form.get('category',0),
            base_price=request.form.get('base_price',0),
            sale_price=request.form.get('sale_price') or None,
            stock=request.form.get('stock',0),
            status=request.form.get('status', 'active'),
            short_description=request.form.get('short_description'),
            long_description=request.form.get('long_description'),
            display_type=request.form.get('display_type'),
            battery_life=request.form.get('battery_life'),
            connectivity=request.form.get('connectivity'),
            strap_material=request.form.get('strap_material'),
            case_material=request.form.get('case_material'),
            water_resistance=request.form.get('water_resistance'),
            weight=request.form.get('weight'),
            warranty_month=request.form.get('warranty_month',12),
            always_display=request.form.get('always_display',0),
            brightness_nits=request.form.get('brightness_nits') or None,
        )
    except ValidationError as e:
        session['admin_toast']=extract_errors(e)[0]
        return redirect(url_for('admin.main_products'))

    image=request.files.get('image')
    width=12
    height=12

    product_id=ProductModel.create(
        data.product_no,data.category_id,data.title,
        data.base_price,data.sale_price,data.stock,data.status
    )
    ProductDetailsModel.create(
        product_id,data.short_description,data.long_description,
        data.display_type,data.brightness_nits,data.battery_life,
        data.connectivity,data.strap_material,data.case_material,
        data.water_resistance,data.weight,data.warranty_month,
        data.always_display
    )

    if image and image.filename != '':
        cat=ProductImageModel.get_category_name(data.category_id)
        cat_name=cat['name'].lower().replace(' ', '_')
        filename=secure_filename(image.filename)
        folder=os.path.join('static','uploads',cat_name)
        os.makedirs(folder,exist_ok=True)
        path=os.path.join(folder, filename)
        image.save(path)
        image_url='/' + path.replace('\\', '/')
        ProductImageModel.create(product_id,image_url,data.title,width,height)

    session['admin_toast']='Product Added Successfully!'
    return redirect(url_for('admin.main_products'))





@admin_bp.route('/delete_product/<int:product_id>',methods=['GET','POST'])
@admin_required
def delete_product(product_id):
    result=ProductModel.get_status(product_id)
    if result['status'] == 'archived':
        session['admin_toast']='Product already deleted!'
        return redirect(request.referrer)

    ProductModel.soft_delete(product_id)
    session['admin_toast']='Product has been deleted successfully!'
    return redirect(url_for('admin.main_products'))


# @admin_bp.route('/edit_product/<int:product_id>',methods=['POST'])
# @admin_required
# def edit_product(product_id):
#     title=request.form.get('title')
#     category_id=request.form.get('category')
#     base_price=request.form.get('base_price')
#     sale_price=request.form.get('sale_price')
#     stock=request.form.get('stock')
#     status=request.form.get('status','active')
#     short_desc=request.form.get('short_description')
#     long_desc=request.form.get('long_description')
#     display_type=request.form.get('display_type')
#     brightness_nits=request.form.get('brightness_nits') or None
#     battery_life=request.form.get('battery_life')
#     connectivity=request.form.get('connectivity')
#     strap_material=request.form.get('strap_material')
#     case_material=request.form.get('case_material')
#     water_resistance=request.form.get('water_resistance')
#     weight=request.form.get('weight')
#     warranty_month=request.form.get('warranty_month')
#     always_display=request.form.get('always_display')
#     product_no=request.form.get('product_no')
#     image=request.files.get('image')
#     width=12
#     height=12

#     ProductModel.update(product_id,product_no,category_id,title,base_price,sale_price,stock,status)
#     ProductDetailsModel.update(product_id,short_desc,long_desc,display_type,brightness_nits,
#         battery_life,connectivity,strap_material,case_material,water_resistance,
#         weight,warranty_month,always_display)

#     if image and image.filename != '':
#         cat=ProductImageModel.get_category_name(category_id)
#         cat_name=cat['name'].lower().replace(' ','_')
#         filename=secure_filename(image.filename)
#         upload_folder=os.path.join('static','uploads',cat_name)
#         os.makedirs(upload_folder,exist_ok=True)
#         image_path=os.path.join(upload_folder,filename)
#         image.save(image_path)
#         image_url='/'+image_path.replace('\\','/')
#         ProductImageModel.update_or_create(product_id,image_url,title,width,height)

#     session['admin_toast']='Product Updated Successfully!'
#     return redirect(url_for('admin.main_products'))



@admin_bp.route('/edit_product/<int:product_id>',methods=['POST'])
@admin_required
def edit_product(product_id):
    try:
        data=ProductValidator(
            title=request.form.get('title', ''),
            product_no=request.form.get('product_no', ''),
            category_id=request.form.get('category', 0),
            base_price=request.form.get('base_price', 0),
            sale_price=request.form.get('sale_price') or None,
            stock=request.form.get('stock', 0),
            status=request.form.get('status', 'active'),
            short_description=request.form.get('short_description'),
            long_description=request.form.get('long_description'),
            display_type=request.form.get('display_type'),
            battery_life=request.form.get('battery_life'),
            connectivity=request.form.get('connectivity'),
            strap_material=request.form.get('strap_material'),
            case_material=request.form.get('case_material'),
            water_resistance=request.form.get('water_resistance'),
            weight=request.form.get('weight'),
            warranty_month=request.form.get('warranty_month', 12),
            always_display=request.form.get('always_display', 0),
            brightness_nits=request.form.get('brightness_nits') or None,
        )
    except ValidationError as e:
        session['admin_toast']=extract_errors(e)[0]
        return redirect(url_for('admin.main_products'))

    image=request.files.get('image')
    width=12
    height=12

    ProductModel.update(
        product_id,data.product_no,data.category_id,data.title,
        data.base_price,data.sale_price,data.stock,data.status
    )

    ProductDetailsModel.update(
        product_id,data.short_description,data.long_description,
        data.display_type,data.brightness_nits,data.battery_life,
        data.connectivity,data.strap_material,data.case_material,
        data.water_resistance,data.weight,data.warranty_month,
        data.always_display
    )

    if image and image.filename != '':
        cat=ProductImageModel.get_category_name(data.category_id)
        cat_name=cat['name'].lower().replace(' ', '_')
        filename=secure_filename(image.filename)
        folder=os.path.join('static', 'uploads', cat_name)
        os.makedirs(folder,exist_ok=True)
        path=os.path.join(folder, filename)
        image.save(path)
        image_url='/' + path.replace('\\', '/')
        ProductImageModel.update_or_create(
            product_id,image_url,data.title,width,height)

    session['admin_toast']='Product Updated Successfully!'
    return redirect(url_for('admin.main_products'))


@admin_bp.route('/active_product/<int:product_id>',methods=['GET','POST'])
@admin_required
def active_product(product_id):
    result=ProductModel.get_status(product_id)
    if result['status'] != 'archived':
        session['admin_toast']='Cannot perform this operation'
        return redirect(url_for('admin.main_products'))

    ProductModel.activate(product_id)
    session['admin_toast']='Product activated successfully!'
    return redirect(url_for('admin.main_products'))


@admin_bp.route('/all_orders')
@admin_required
def all_orders():
    page=request.args.get('page',1,type=int)
    if page<1:
        page=1

    per_page=10
    offset=(page - 1) * per_page

    orders=OrderModel.get_all_paginated(per_page,offset)
    total_rows=OrderModel.count_all()
    total_pages=math.ceil(total_rows / per_page)
    return render_template('all_orders.htm',orders=orders,page=page,total_pages=total_pages)


# @admin_bp.route('/update_order_status/<int:order_id>',methods=['POST'])
# @admin_required
# def update_order_status(order_id):
#     from main import mail,app
#     from flask_mail import Message

#     status=request.form.get('status')
#     valid=['pending','confirmed','shipped','delivered']

#     if status in valid:
#         order_data=OrderModel.get_order_user_for_email(order_id)
#         OrderModel.update_status(order_id,status)

#         if order_data:
#             user_email=order_data['email']
#             order_number=order_data['order_number']
#             first_name=order_data['first_name']
#             order_link=f"{request.host_url}user_orders"

#             msg=Message(
#                 subject=f'Order {order_number} has been {status.capitalize()} - Hero Style',
#                 recipients=[user_email],
#                 html=f"""
#                     <html>
#                         <body style="font-family: Arial, sans-serif; line-height: 1.6;">
#                             <h2>Order Update</h2>
#                             <p>Hi {first_name},</p>
#                             <p>Your order <strong>{order_number}</strong> from Hero Style has been <strong>{status.upper()}</strong>.</p>
#                             <p>Click the button below to view your order status:</p>
#                             <p>
#                                 <a href="{order_link}"
#                                    style="background-color: #c9a84c; color: #0d1b2a; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold;">
#                                     View Order Status
#                                 </a>
#                             </p>
#                             <p>If you have any questions, please contact our support team.</p>
#                             <p>Best regards,<br>Hero Style Team</p>
#                         </body>
#                     </html>""")
#             mail.send(msg)

#         session['admin_toast']='Status updated successfully & Email sent!'

#     return redirect(url_for('admin.all_orders'))


@admin_bp.route('/update_order_status/<int:order_id>',methods=['POST'])
@admin_required
def update_order_status(order_id):
    from main import mail
    try:
        data=OrderStatusValidator(status=request.form.get('status', ''))
    except ValidationError as e:
        session['admin_toast']=extract_errors(e)[0]
        return redirect(url_for('admin.all_orders'))

    order_data=OrderModel.get_order_user_for_email(order_id)
    OrderModel.update_status(order_id,data.status)

    if order_data:
        user_email=order_data['email']
        order_number=order_data['order_number']
        first_name=order_data['first_name']
        order_link=f"{request.host_url}user_orders"

        msg=Message(
            subject=f'Order {order_number} has been {data.status.capitalize()} - Hero Style',
            recipients=[user_email],
            html=f"""<html><body>
                <p>Hi {first_name}, your order <strong>{order_number}</strong>
                has been <strong>{data.status.upper()}</strong>.</p>
                <a href="{order_link}">View Order Status</a>
            </body></html>"""
        )
        mail.send(msg)

    session['admin_toast']='Status updated successfully & Email sent!'
    return redirect(url_for('admin.all_orders'))




@admin_bp.route('/cancel_order_status/<int:order_id>',methods=['POST'])
@admin_required
def cancel_order_status(order_id):
    OrderModel.cancel(order_id)
    ProductModel.restore_stock_on_cancel(order_id)
    session['admin_toast']='Order cancelled successfully!'
    return redirect(url_for('admin.all_orders'))


@admin_bp.route('/delete_order/<int:order_id>',methods=['POST'])
@admin_required
def delete_order(order_id):
    OrderModel.soft_delete(order_id)
    session['admin_toast']='Order Deleted successfully!'
    return redirect(url_for('admin.all_orders'))


@admin_bp.route('/order_detail/<int:order_id>')
@admin_required
def order_detail(order_id):
    admin_id=session.get('admin_id')
    admin=AdminModel.get_by_id(admin_id)

    order=OrderModel.get_with_user_and_payment(order_id)
    if not order:
        return redirect(url_for('admin.all_orders'))

    items=OrderModel.get_items_with_product(order_id)
    return render_template('order_detail.htm',order=order,items=items,admin=admin)


@admin_bp.route('/returns_orders')
@admin_required
def returns_orders():
    admin_id=session.get('admin_id')
    admin=AdminModel.get_by_id(admin_id)

    active_tab=request.args.get('tab','order')

    page=request.args.get('page',1,type=int)
    if page<1:
        page=1

    per_page=10
    offset=(page - 1) * per_page

    if active_tab == 'order':
        returns=OrderReturnModel.get_order_returns_paginated(per_page,offset)
    else:
        returns=OrderReturnModel.get_item_returns_paginated(per_page,offset)

    total_rows=OrderReturnModel.count_order_returns()
    total_pages=math.ceil(total_rows / per_page)
    return render_template('returns_orders.htm',returns=returns,active_tab=active_tab,
                           admin=admin,page=page,total_pages=total_pages)


@admin_bp.route('/returns_order_request/<int:order_id>',methods=['POST'])
@admin_required
def returns_order_request(order_id):
    OrderReturnModel.update_order_return_status(order_id,'approved')
    session['admin_toast']='Request approved successfully!'
    return redirect(request.referrer)


@admin_bp.route('/returns_order_reject/<int:order_id>',methods=['POST'])
@admin_required
def returns_order_reject(order_id):
    OrderReturnModel.update_order_return_status(order_id,'rejected')
    session['admin_toast']='Request rejected successfully!'
    return redirect(request.referrer)


@admin_bp.route('/returns_items_approved/<int:order_id>',methods=['POST'])
@admin_required
def returns_items_approved(order_id):
    OrderReturnModel.update_item_return_status(order_id,'approved')
    session['admin_toast']='Request approved successfully!'
    return redirect(request.referrer)


@admin_bp.route('/returns_items_reject/<int:order_id>',methods=['POST'])
@admin_required
def returns_items_reject(order_id):
    OrderReturnModel.update_item_return_status(order_id,'rejected')
    session['admin_toast']='Request rejected successfully!'
    return redirect(request.referrer)


@admin_bp.route('/orders_cancels')
@admin_required
def orders_cancels():
    page=request.args.get('page',1,type=int)
    if page<1:
        page=1

    per_page=10
    offset=(page - 1) * per_page

    cancelled_orders=OrderModel.get_cancelled_paginated(per_page,offset)
    admin_id=session.get('admin_id')
    admin=AdminModel.get_by_id(admin_id)
    total_rows=OrderModel.count_cancelled()
    total_pages=math.ceil(total_rows / per_page)
    return render_template('orders_cancels.htm',cancelled_orders=cancelled_orders,
                           admin=admin,page=page,total_pages=total_pages)


@admin_bp.route('/mark_refunded/<int:order_id>',methods=['POST'])
@admin_required
def mark_refunded(order_id):
    row=OrderPaymentModel.get_with_order(order_id)

    if not row:
        session['admin_toast']='Order not found or not eligible for refund.'
        return redirect(request.referrer)

    payment_id=row['payment_id']

    if payment_id:
        OrderPaymentModel.mark_refunded(payment_id)
    else:
        OrderPaymentModel.insert_cod_refunded(order_id)

    session['admin_toast']='Order marked as refunded successfully.'
    return redirect(request.referrer)


@admin_bp.route('/customers')
@admin_required
def customers():
    page=request.args.get('page',1,type=int)
    if page<1:
        page=1

    per_page=10
    offset=(page - 1) * per_page

    customers=CustomerModel.get_all_paginated(per_page,offset)
    admin_id=session.get('admin_id')
    admin=AdminModel.get_by_id(admin_id)
    total_rows=CustomerModel.count_customers()
    total_pages=math.ceil(total_rows / per_page)
    return render_template('customers.htm',customers=customers,admin=admin,page=page,total_pages=total_pages)


@admin_bp.route('/customers/<int:user_id>/toggle',methods=['POST'])
@admin_required
def toggle_customer(user_id):
    row=CustomerModel.get_is_active(user_id)
    if not row:
        session['admin_toast']='Customer not found.'
        return redirect(url_for('admin.customers'))

    new_status=0 if row['is_active'] else 1
    CustomerModel.toggle_active(user_id,new_status)
    session['admin_toast']='Customer status updated.'
    return redirect(url_for('admin.customers'))


@admin_bp.route('/customers/<int:user_id>')
@admin_required
def customer_detail(user_id):
    customer=CustomerModel.get_by_id(user_id)
    if not customer:
        session['admin_toast']='Customer not found.'
        return redirect(url_for('admin.customers'))

    orders=OrderModel.get_by_user(user_id)
    wishlist=CustomerModel.get_wishlist(user_id)
    admin_id=session.get('admin_id')
    admin=AdminModel.get_by_id(admin_id)
    return render_template('customer_detail.htm',customer=customer,orders=orders,wishlist=wishlist,admin=admin)


@admin_bp.route('/payments')
@admin_required
def all_payments():
    page=request.args.get('page',1,type=int)
    if page<1:
        page=1

    per_page=10
    offset=(page - 1) * per_page

    payments=OrderPaymentModel.get_all_paginated(per_page,offset)
    admin_id=session.get('admin_id')
    admin=AdminModel.get_by_id(admin_id)
    total_rows=OrderPaymentModel.count_all()
    total_pages=math.ceil(total_rows / per_page)
    return render_template('payments.htm',payments=payments,admin=admin,page=page,total_pages=total_pages)


@admin_bp.route('/support_forms')
@admin_required
def support_forms():
    page=request.args.get('page',1,type=int)
    if page<1:
        page=1

    per_page=10
    offset=(page - 1) * per_page

    forms=FormModel.get_all_paginated(per_page,offset)
    admin_id=session.get('admin_id')
    admin=AdminModel.get_by_id(admin_id)
    total_rows=FormModel.count_all()
    total_pages=math.ceil(total_rows / per_page)
    return render_template('support_forms.htm',forms=forms,admin=admin,page=page,total_pages=total_pages)


@admin_bp.route('/support_forms/<int:form_id>/delete',methods=['POST'])
@admin_required
def delete_form(form_id):
    FormModel.soft_delete(form_id)
    session['admin_toast']='Form submission deleted.'
    return redirect(url_for('admin.support_forms'))


@admin_bp.route('/reviews')
@admin_required
def all_reviews():
    page=request.args.get('page',1,type=int)
    if page<1:
        page=1

    per_page=10
    offset=(page - 1) * per_page

    reviews=ReviewModel.get_all_paginated(per_page,offset)
    admin_id=session.get('admin_id')
    admin=AdminModel.get_by_id(admin_id)
    total_rows=ReviewModel.count_all()
    total_pages=math.ceil(total_rows / per_page)
    return render_template('all_reviews.htm',reviews=reviews,admin=admin,page=page,total_pages=total_pages)


@admin_bp.route('/reviews/<int:review_id>/status',methods=['POST'])
@admin_required
def update_review_status(review_id):
    try:
        data=ReviewStatusValidator(status=request.form.get('status',''))
    except ValidationError as e:
        session['admin_toast']=extract_errors(e)[0]
        return redirect(url_for('admin.all_reviews'))

    ReviewModel.update_status(review_id,data.status)
    session['admin_toast']=f'Review marked as {data.status}.'
    return redirect(url_for('admin.all_reviews'))


@admin_bp.route('/reviews/<int:review_id>/delete',methods=['POST'])
@admin_required
def delete_review(review_id):
    ReviewModel.soft_delete(review_id)
    session['admin_toast']='Review deleted.'
    return redirect(url_for('admin.all_reviews'))


@admin_bp.route('/sales')
@admin_required
def sales():
    stats=SalesModel.get_summary()
    category_sales=SalesModel.get_category_sales()
    top_products=SalesModel.get_top_products()
    recent_orders=OrderModel.get_recent()
    admin_id=session.get('admin_id')
    admin=AdminModel.get_by_id(admin_id)

    return render_template('sales.htm',
        total_sales=stats['total_sales'],
        total_returns=stats['total_returns'],
        recent_orders=recent_orders,
        admin=admin,
        pending_cod=stats['pending_cod'],
        total_units=stats['total_units'],
        top_products=top_products,
        total_orders=stats['total_orders'],
        avg_order=stats['avg_order'],
        category_sales=category_sales)