from flask import render_template,session,request,redirect,url_for
from orders import order_bp
from datetime import datetime
import json,uuid
from orders.order_models import (CartModel,ProductStockModel,UserModel,
    OrderPlacementModel,WishlistModel)


def get_or_create_cart_id():
    cart_id=session.get('cart_id')
    if cart_id:
        return cart_id

    session_id=str(uuid.uuid4())
    cart_id=CartModel.create_cart(session_id)
    session['cart_id']=cart_id
    session.modified=True
    return cart_id


def get_cart_items():
    cart_id=session.get('cart_id')
    if not cart_id:
        return [],0

    rows=CartModel.get_items(cart_id)
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
    cart_id=session.get('cart_id')
    if not cart_id:
        return 0
    return CartModel.get_count(cart_id)


@order_bp.route('/cart/add',methods=['POST'])
def add_to_cart():
    product_id=request.form.get('product_id','')
    quantity=int(request.form.get('quantity',1))
    redirect_to=request.form.get('redirect_to','/')

    if not product_id:
        return redirect(redirect_to)

    product_id=int(product_id)
    cart_id=get_or_create_cart_id()

    product=ProductStockModel.get_by_id(product_id)
    if not product:
        return redirect(redirect_to)

    if product['stock_quantity'] < 1:
        session['toast']=f"'{product['title']}' is out of stock."
        return redirect(redirect_to)

    price=float(product['sale_price'] or product['base_price'])
    CartModel.add_item(cart_id,product_id,quantity,price)
    session['toast']=f"Added to cart: {product['title']}"
    session.modified=True
    return redirect(redirect_to)


@order_bp.route('/cart/update',methods=['POST'])
def update_cart():
    product_id=int(request.form.get('product_id',0))
    quantity=int(request.form.get('quantity',1))
    cart_id=session.get('cart_id')

    if cart_id and product_id:
        CartModel.update_item(cart_id,product_id,quantity)

    return redirect(url_for('orders.view_cart'))


@order_bp.route('/cart/remove',methods=['POST'])
def remove_from_cart():
    product_id=int(request.form.get('product_id',0))
    cart_id=session.get('cart_id')

    if cart_id and product_id:
        CartModel.remove_item(cart_id,product_id)

    return redirect(url_for('orders.view_cart'))


@order_bp.route('/cart')
def view_cart():
    cart_items,grand_total=get_cart_items()
    return render_template('cart.htm',cart_items=cart_items,grand_total=grand_total)


@order_bp.route('/checkout',methods=['GET','POST'])
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
    cart_items,grand_total=get_cart_items()
    if not cart_items:
        return redirect(url_for('orders.view_cart'))

    first_name=request.form.get('first_name','').strip()
    last_name=request.form.get('last_name','').strip()
    city=request.form.get('city','').strip()
    postal_code=request.form.get('postal_code','').strip()
    shipping_address=request.form.get('shipping_address','').strip()
    payment_method=request.form.get('payment_method','COD')
    promo_code=request.form.get('promo_code','').strip() or None
    email=request.form.get('email','').strip() or None

    full_address=f"{shipping_address},{city} {postal_code}".strip(', ')

    subtotal=float(request.form.get('subtotal',grand_total))
    shipping_charges=float(request.form.get('shipping_charges',0))
    discount_amount=float(request.form.get('discount_amount',0))
    total_amount=float(request.form.get('total_amount',grand_total))

    if subtotal==0:
        subtotal=grand_total
        shipping_charges=0 if subtotal >= 10000 else 250
        total_amount=subtotal + shipping_charges - discount_amount

    for item in cart_items:
        stock_row=ProductStockModel.check_stock(item['product_id'])

        if not stock_row:
            session['toast']=f"'{item['title']}' is no longer available."
            return redirect(url_for('orders.view_cart'))

        if stock_row['stock_quantity'] < item['quantity']:
            session['toast']=f"Only {stock_row['stock_quantity']} unit(s) of '{stock_row['title']}' left in stock."
            return redirect(url_for('orders.view_cart'))

    order_number='HW-'+uuid.uuid4().hex[:8].upper()
    user_id=None

    if session.get('user_id'):
        user_id=session['user_id']

    if not user_id and email:
        existing=UserModel.get_by_email(email)
        if existing:
            user_id=existing['user_id']

    if not user_id:
        user_id=UserModel.create_guest(first_name,last_name,email)

    order_id=OrderPlacementModel.create_order(user_id,order_number,subtotal,discount_amount,
        promo_code,shipping_charges,total_amount,full_address)

    for item in cart_items:
        item_subtotal=round(item['price'] * item['quantity'],2)
        OrderPlacementModel.create_order_detail(order_id,item['product_id'],item['price'],item['quantity'],item_subtotal)
        ProductStockModel.deduct_stock(item['product_id'],item['quantity'])

    OrderPlacementModel.create_payment(order_id,payment_method,total_amount)

    cart_id=session.pop('cart_id',None)
    if cart_id:
        CartModel.delete_cart(cart_id)
    else:
        session['toast']='Error deleting the cart! Try Again Please.'

    session.modified=True
    return render_template('order_confirmed.htm',order_id=order_id,order_number=order_number,
                           total_amount=total_amount,payment_method=payment_method,
                           customer_name=f"{first_name} {last_name}")


@order_bp.route('/buy_now/<int:product_id>',methods=['POST'])
def buy_now(product_id):
    quantity=int(request.form.get('quantity',1))
    product=ProductStockModel.get_active_with_image(product_id)

    if not product:
        return redirect(url_for('homepage'))

    if product['stock_quantity'] < quantity:
        session['toast']=f"Only {product['stock_quantity']} unit(s) available."
        return redirect(f"/products/{product_id}")

    price=float(product['sale_price']
                if product['sale_price'] and product['sale_price'] < product['base_price']
                else product['base_price'])

    old_cart_id=session.pop('cart_id',None)
    if old_cart_id:
        CartModel.delete_cart(old_cart_id)

    session.modified=True
    cart_id=get_or_create_cart_id()
    CartModel.set_buy_now_item(cart_id,product_id,quantity,price)
    return redirect(url_for('orders.checkout'))


@order_bp.route('/wishlist/add',methods=['POST'])
def add_to_list():
    product_id=request.form.get('product_id','')
    redirect_to=request.form.get('redirect_to','/')

    if not product_id:
        return redirect(redirect_to)

    if 'user_id' not in session:
        session['toast']='Please Login to add in the wishlist!'
        return redirect(url_for('users.user_login'))

    user_id=session['user_id']

    if WishlistModel.exists(user_id,product_id):
        session['toast']='Item Already in the wishlist!'
    else:
        WishlistModel.add(user_id,product_id)
        session['toast']='Added to wishlist!'
        session.modified=True

    return redirect(redirect_to)