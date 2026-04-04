from flask import render_template, session, request, redirect, url_for
from orders import order_bp
from datetime import datetime
from utils.db import mysql
import json
import uuid
from MySQLdb.cursors import DictCursor




@order_bp.route('/cart')
def cart():
  
    return render_template('cart.htm')
    



@order_bp.route('/checkout',methods=['GET', 'POST'])
def checkout():
    if request.method=='POST':
        cart_data=request.form.get('cart_data')
 
        if not cart_data:
            return redirect(url_for('orders.cart'))
 
        cart_items=json.loads(cart_data)
        session['pending_cart']=cart_items         
        return render_template('checkout.htm',cart=cart_items)
 
    cart_items=session.get('pending_cart',[])
    return render_template('checkout.htm',cart=cart_items)



@order_bp.route('/place_order',methods=['POST'])
def place_order():
    cart_data=request.form.get('cart_data')
    if cart_data:
        cart_items=json.loads(cart_data)
        session['pending_cart']=cart_items
    else:
        cart_items=session.get('pending_cart', [])

    if not cart_items:
        return redirect(url_for('orders.cart'))

    first_name=request.form.get('first_name','').strip()
    last_name=request.form.get('last_name','').strip()
    phone=request.form.get('phone','').strip()
    city=request.form.get('city','').strip()
    postal_code=request.form.get('postal_code','').strip()
    shipping_address=request.form.get('shipping_address', '').strip()
    payment_method=request.form.get('payment_method')
    promo_code=request.form.get('promo_code', '').strip() or None
    email=request.form.get('email', '').strip()

    full_address=f"{shipping_address},{city} {postal_code}".strip(', ')
    billing_address=f"{full_address}"

    subtotal=float(request.form.get('subtotal',0))
    shipping_charges=float(request.form.get('shipping_charges',0))
    discount_amount=float(request.form.get('discount_amount',0))
    total_amount=float(request.form.get('total_amount',0))

    if subtotal==0:
        subtotal=sum(item['price'] * item['quantity'] for item in cart_items)
        shipping_charges=0 if subtotal >= 10000 else 250
        total_amount=subtotal + shipping_charges - discount_amount

    order_number='HW-' + uuid.uuid4().hex[:8].upper()

    cursor=mysql.connection.cursor(DictCursor)

    try:
        cursor.execute("SELECT user_id FROM users WHERE phone=%s",(phone,))
        existing_user=cursor.fetchone()

        if existing_user:
            user_id=existing_user['user_id']
        else:
            cursor.execute(
                '''INSERT INTO users(role_id,first_name,last_name,email,phone,
                      password_hash,address,city,country)
                   VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)''',
                (2,first_name,last_name,email,phone,
                 'guest',shipping_address,city,'Pakistan')
            )
            user_id=cursor.lastrowid

        cursor.execute(
            '''INSERT INTO orders(user_id,order_number,status,subtotal,discount_amount,
                promo_code,shipping_charges,total_amount,shipping_address,billing_address,
                ordered_at)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',
            (user_id,order_number,'pending',subtotal,discount_amount,
             promo_code,shipping_charges,total_amount,full_address,billing_address,datetime.now()))
        order_id=cursor.lastrowid

        for item in cart_items:
            product_id=int(item['id'])
            quantity=int(item['quantity'])
            product_amount=float(item['price'])
            item_subtotal=round(product_amount * quantity, 2)

            cursor.execute(
                '''INSERT INTO order_details
                     (order_id,product_id,product_amount,quantity,
                      discount_per_item,subtotal)
                   VALUES (%s,%s,%s,%s,%s,%s)''',
                (order_id,product_id,product_amount,quantity,0.00,item_subtotal)
            )

        cursor.execute(
            '''INSERT INTO order_payments
                (order_id,payment_method,amount,status)
               VALUES (%s, %s, %s, %s)''',
            (order_id,payment_method,total_amount,'pending')
        )

        mysql.connection.commit()

    except Exception as e:
        mysql.connection.rollback()
        cursor.close()
        return f"Order failed: {str(e)}", 500

    cursor.close()
    session.pop('pending_cart', None)

    return render_template('order_confirmed.htm',order_id=order_id,order_number=order_number,
        total_amount=total_amount,payment_method=payment_method,customer_name=f"{first_name} {last_name}")









@order_bp.route('/buy_now/<int:product_id>', methods=['POST'])
def buy_now(product_id):
    cursor=mysql.connection.cursor(DictCursor)
    quantity=int(request.form.get('quantity', 1))

    cursor.execute('''SELECT p.product_id,p.title,p.sale_price,p.base_price,pi.image_url 
                   FROM products p 
                   JOIN product_images pi ON p.product_id=pi.product_id
                    WHERE p.product_id=%s AND pi.is_active=%s''', (product_id,1,))
    product=cursor.fetchone()
    cursor.close()

    if not product:
        return redirect(url_for('products.homepage')) 


    price_to_use=product['base_price']
    if product['sale_price'] and product['sale_price'] < product['base_price']:
        price_to_use=product['sale_price']

   
    pending_cart = [{
        'id':product['product_id'],
        'title':product['title'],
        'price':float(price_to_use),
        'quantity':quantity,
        'image_url':product['image_url']
    }]

    session['pending_cart']=pending_cart
    session.modified=True
    return redirect(url_for('orders.checkout'))