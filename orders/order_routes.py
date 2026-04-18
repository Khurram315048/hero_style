from flask import render_template, session, request, redirect, url_for
from orders import order_bp
from datetime import datetime
from utils.db import mysql
import json, uuid
from MySQLdb.cursors import DictCursor



def get_or_create_cart_id():
    cursor=mysql.connection.cursor(DictCursor)
    cart_id=session.get('cart_id')
    if cart_id:
        return cart_id

    session_id=str(uuid.uuid4())
    cursor.execute(
        "INSERT INTO carts(session_id) VALUES(%s)",(session_id,)
    )
    mysql.connection.commit()
    cart_id=cursor.lastrowid
    cursor.close()

    session['cart_id']=cart_id
    session.modified=True
    return cart_id


def get_cart_items():
    cursor=mysql.connection.cursor(DictCursor)
    cart_id=session.get('cart_id')
    if not cart_id:
        return [], 0

    
    cursor.execute("""
        SELECT ci.product_id,ci.quantity,ci.price_at_add  AS price,
            p.title,pi.image_url,pd.short_description
        FROM cart_items ci
        JOIN products p  ON p.product_id=ci.product_id
        JOIN product_images pi ON pi.product_id=ci.product_id
        JOIN product_details pd ON pd.product_id=ci.product_id
        WHERE ci.cart_id=%s
    """,(cart_id,))
    rows=cursor.fetchall()
    cursor.close()

    items=[]
    grand_total=0
    for row in rows:
        price=float(row['price'])
        qty=int(row['quantity'])
        items.append({
            'product_id':row['product_id'],
            'id':row['product_id'],   
            'title':row['title'],
            'price':price,
            'quantity':qty,
            'image_url':row['image_url'] or '/static/uploads/default.jpg',
            'image':row['image_url'] or '/static/uploads/default.jpg',
            'short_description':row['short_description'] or ''
        })
        grand_total += price * qty

    return items,grand_total


def get_cart_count():
    cursor=mysql.connection.cursor(DictCursor)
    cart_id=session.get('cart_id')
    if not cart_id:
        return 0
   
    cursor.execute(
        "SELECT COALESCE(SUM(quantity),0) AS total FROM cart_items WHERE cart_id=%s",
        (cart_id,))
    row=cursor.fetchone()
    cursor.close()
    return int(row['total']) if row else 0


@order_bp.route('/cart/add',methods=['POST'])
def add_to_cart():
    cursor=mysql.connection.cursor(DictCursor)
    product_id=request.form.get('product_id','')
    quantity=int(request.form.get('quantity',1))
    redirect_to=request.form.get('redirect_to','/')

    if not product_id:
        return redirect(redirect_to)

    product_id=int(product_id)
    cart_id=get_or_create_cart_id()

    
    cursor.execute("SELECT title,sale_price,base_price FROM products WHERE product_id=%s",(product_id,))
    product=cursor.fetchone()
    if not product:
        cursor.close()
        return redirect(redirect_to)

    price=float(product['sale_price'] or product['base_price'])

    cursor.execute("""
        INSERT INTO cart_items(cart_id,product_id,quantity,price_at_add)
        VALUES (%s,%s,%s,%s)
        ON DUPLICATE KEY UPDATE quantity=quantity + VALUES(quantity)
    """,(cart_id,product_id,quantity,price))
    mysql.connection.commit()
    cursor.close()
    session['toast']=f"Added to cart: {product['title']}"
    session.modified=True

    return redirect(redirect_to)


@order_bp.route('/cart/update',methods=['POST'])
def update_cart():
    cursor=mysql.connection.cursor(DictCursor)
    product_id=int(request.form.get('product_id', 0))
    quantity=int(request.form.get('quantity', 1))
    cart_id =session.get('cart_id')

    if cart_id and product_id:
        if quantity <= 0:
            cursor.execute("DELETE FROM cart_items WHERE cart_id=%s AND product_id=%s",(cart_id,product_id))
        else:
            cursor.execute("UPDATE cart_items SET quantity=%s WHERE cart_id=%s AND product_id=%s",(quantity,cart_id,product_id))
        mysql.connection.commit()
        cursor.close()

    return redirect(url_for('orders.view_cart'))



@order_bp.route('/cart/remove',methods=['POST'])
def remove_from_cart():
    cursor=mysql.connection.cursor(DictCursor)
    product_id=int(request.form.get('product_id',0))
    cart_id=session.get('cart_id')

    if cart_id and product_id:
    
        cursor.execute("DELETE FROM cart_items WHERE cart_id=%s AND product_id=%s",(cart_id,product_id))
        mysql.connection.commit()
        cursor.close()

    return redirect(url_for('orders.view_cart'))



@order_bp.route('/cart')
def view_cart():
    cart_items,grand_total=get_cart_items()
    return render_template('cart.htm',cart_items=cart_items,grand_total=grand_total)



@order_bp.route('/checkout',methods=['GET', 'POST'])
def checkout():
    cart_items,grand_total=get_cart_items()
    if not cart_items:
        return redirect(url_for('orders.view_cart'))

    shipping=0 if grand_total >= 10000 else 250
    total=grand_total + shipping

    flask_cart_json=json.dumps([{
        'id':item['product_id'],
        'title':item['title'],
        'price':item['price'],
        'quantity':item['quantity'],
        'image':item['image_url']
    } for item in cart_items])

    return render_template('checkout.htm',cart_items=cart_items,subtotal=grand_total,
                           shipping=shipping,total_amount=total,
                           flask_cart_json=flask_cart_json)



@order_bp.route('/place_order',methods=['POST'])
def place_order():
    cart_items, grand_total=get_cart_items()
    if not cart_items:
        return redirect(url_for('orders.view_cart'))
 
    first_name=request.form.get('first_name', '').strip()
    last_name=request.form.get('last_name', '').strip()
    city=request.form.get('city', '').strip()
    postal_code=request.form.get('postal_code', '').strip()
    shipping_address=request.form.get('shipping_address', '').strip()
    payment_method=request.form.get('payment_method', 'COD')
    promo_code=request.form.get('promo_code', '').strip() or None
    email=request.form.get('email', '').strip() or None
 
    full_address=f"{shipping_address},{city} {postal_code}".strip(', ')
 
    subtotal=float(request.form.get('subtotal',grand_total))
    shipping_charges=float(request.form.get('shipping_charges',0))
    discount_amount=float(request.form.get('discount_amount',0))
    total_amount=float(request.form.get('total_amount',grand_total))
 
    if subtotal==0:
        subtotal=grand_total
        shipping_charges=0 if subtotal >= 10000 else 250
        total_amount=subtotal + shipping_charges - discount_amount
 
    order_number='HW-' + uuid.uuid4().hex[:8].upper()
    cursor=mysql.connection.cursor(DictCursor)
    user_id=None
 
    if session.get('user_id'):
        user_id=session['user_id']
 
    if not user_id and email:
        cursor.execute("SELECT user_id FROM users WHERE email=%s",(email,))
        existing=cursor.fetchone()
        if existing:
            user_id=existing['user_id']
 
    if not user_id:
        cursor.execute("""
            INSERT INTO users(role_id,first_name,last_name,email,password_hash,address,city,country)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        """, (2,first_name,last_name,email,'guest',shipping_address,city,'Pakistan'))
        mysql.connection.commit()
        user_id=cursor.lastrowid
 
    
    cursor.execute("""
        INSERT INTO orders(user_id,order_number,status,subtotal,discount_amount,
             promo_code,shipping_charges,total_amount,
             shipping_address,billing_address,ordered_at)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """, (user_id,order_number,'pending',subtotal,discount_amount,
          promo_code,shipping_charges,total_amount,
          full_address,full_address,datetime.now()))
    mysql.connection.commit()
    order_id=cursor.lastrowid
 
    for item in cart_items:
        item_subtotal=round(item['price'] * item['quantity'], 2)
        cursor.execute("""
            INSERT INTO order_details(order_id,product_id,product_amount,quantity,discount_per_item,subtotal)
            VALUES (%s,%s,%s,%s,%s,%s)
        """, (order_id,item['product_id'],item['price'],item['quantity'],0.00,item_subtotal))
 
   
    cursor.execute("""
        INSERT INTO order_payments(order_id,payment_method,amount,status)
        VALUES (%s,%s,%s,%s)
    """, (order_id,payment_method,total_amount,'pending'))
 
    mysql.connection.commit()
    cursor.close()
 
    cart_id=session.pop('cart_id', None)
    if cart_id:
        c=mysql.connection.cursor(DictCursor)
        c.execute("DELETE FROM cart_items WHERE cart_id=%s",(cart_id,))
        c.execute("DELETE FROM carts WHERE cart_id=%s",(cart_id,))
        mysql.connection.commit()
        c.close()
 
    session.modified=True
 
    return render_template('order_confirmed.htm',order_id=order_id,order_number=order_number,
                           total_amount=total_amount,payment_method=payment_method,
                           customer_name=f"{first_name} {last_name}")



@order_bp.route('/buy_now/<int:product_id>',methods=['POST'])
def buy_now(product_id):
    quantity=int(request.form.get('quantity', 1))
    cursor=mysql.connection.cursor(DictCursor)

    cursor.execute("""
        SELECT p.product_id,p.title,p.sale_price,p.base_price,pi.image_url
        FROM products p
        JOIN product_images pi ON p.product_id=pi.product_id
        WHERE p.product_id=%s AND pi.is_active=1
    """,(product_id,))
    product=cursor.fetchone()
    cursor.close()

    if not product:
        return redirect(url_for('products.homepage'))

    price=float(product['sale_price']
                  if product['sale_price'] and product['sale_price'] < product['base_price']
                  else product['base_price'])

    
    old_cart_id=session.pop('cart_id', None)   
    if old_cart_id:
        c=mysql.connection.cursor(DictCursor)
        c.execute("DELETE FROM cart_items WHERE cart_id=%s",(old_cart_id,))
        c.execute("DELETE FROM carts WHERE cart_id=%s",(old_cart_id,))
        mysql.connection.commit()
        c.close()

    session.modified=True
    cart_id=get_or_create_cart_id()

    cursor=mysql.connection.cursor(DictCursor)
    cursor.execute("""
        INSERT INTO cart_items(cart_id,product_id,quantity,price_at_add)
        VALUES (%s,%s,%s,%s)
        ON DUPLICATE KEY UPDATE quantity=VALUES(quantity)
    """,(cart_id,product_id,quantity,price))
    mysql.connection.commit()
    cursor.close()

    return redirect(url_for('orders.checkout'))


@order_bp.route('/wishlist/add',methods=['POST'])
def add_to_list():
    cursor=mysql.connection.cursor(DictCursor)
    product_id=request.form.get('product_id', '')
    redirect_to=request.form.get('redirect_to', '/')

    if not product_id:
        return redirect(redirect_to)

    if 'user_id' not in session:
        session['toast']='Please Login to add in the wishlist!'
        return redirect(url_for('users.user_login'))


    user_id=session['user_id']
    cursor.execute("SELECT * FROM wishlist WHERE user_id=%s AND product_id=%s",(user_id,product_id))
    already_exists=cursor.fetchone()
    if not already_exists:
        cursor.execute("""
            INSERT IGNORE INTO wishlist(user_id,product_id)VALUES(%s,%s)""",(user_id,int(product_id)))
        mysql.connection.commit()
        cursor.close()

        session['toast']='Added to wishlist!'
        session.modified=True
        return redirect(redirect_to)  
    else:
        session['toast']='Item Already in the wishlist!'
        cursor.close()
        return redirect(redirect_to)