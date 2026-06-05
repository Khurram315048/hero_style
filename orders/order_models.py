from utils.db import mysql
from MySQLdb.cursors import DictCursor
from datetime import datetime
import uuid


class CartModel:
    @staticmethod
    def create_cart(session_id):
        cursor=mysql.connection.cursor(DictCursor)
        try:
            cursor.execute("INSERT INTO carts(session_id) VALUES(%s)",(session_id,))
            mysql.connection.commit()
            return cursor.lastrowid
        finally:
            cursor.close()

    @staticmethod
    def delete_cart(cart_id):
        cursor=mysql.connection.cursor(DictCursor)
        try:
            cursor.execute("DELETE FROM cart_items WHERE cart_id=%s",(cart_id,))
            cursor.execute("DELETE FROM carts WHERE cart_id=%s",(cart_id,))
            mysql.connection.commit()
        finally:
            cursor.close()

    @staticmethod
    def get_count(cart_id):
        cursor=mysql.connection.cursor(DictCursor)
        try:
            cursor.execute("SELECT COALESCE(SUM(quantity),0) AS total FROM cart_items WHERE cart_id=%s",(cart_id,))
            row=cursor.fetchone()
            return int(row['total']) if row else 0
        finally:
            cursor.close()

    @staticmethod
    # BUG FIX: added AND pi.is_active=1 - multiple images caused duplicate cart rows
    def get_items(cart_id):
        cursor=mysql.connection.cursor(DictCursor)
        try:
            cursor.execute("""SELECT ci.product_id,ci.quantity,ci.price_at_add AS price,
                p.title,pi.image_url,pd.short_description
            FROM cart_items ci
            JOIN products p ON p.product_id=ci.product_id
            JOIN product_images pi ON pi.product_id=ci.product_id AND pi.is_active=1
            JOIN product_details pd ON pd.product_id=ci.product_id
            WHERE ci.cart_id=%s""",(cart_id,))
            return cursor.fetchall()
        finally:
            cursor.close()

    @staticmethod
    def add_item(cart_id,product_id,quantity,price):
        cursor=mysql.connection.cursor(DictCursor)
        try:
            cursor.execute("""INSERT INTO cart_items(cart_id,product_id,quantity,price_at_add)
                VALUES (%s,%s,%s,%s)
                ON DUPLICATE KEY UPDATE quantity=quantity + VALUES(quantity)""",(cart_id,product_id,quantity,price))
            mysql.connection.commit()
        finally:
            cursor.close()

    @staticmethod
    def update_item(cart_id,product_id,quantity):
        cursor=mysql.connection.cursor(DictCursor)
        try:
            if quantity<=0:
                cursor.execute("DELETE FROM cart_items WHERE cart_id=%s AND product_id=%s",(cart_id,product_id))
            else:
                cursor.execute("UPDATE cart_items SET quantity=%s WHERE cart_id=%s AND product_id=%s",(quantity,cart_id,product_id))
            mysql.connection.commit()
        finally:
            cursor.close()

    @staticmethod
    def remove_item(cart_id,product_id):
        cursor=mysql.connection.cursor(DictCursor)
        try:
            cursor.execute("DELETE FROM cart_items WHERE cart_id=%s AND product_id=%s",(cart_id,product_id))
            mysql.connection.commit()
        finally:
            cursor.close()

    @staticmethod
    def set_buy_now_item(cart_id,product_id,quantity,price):
        cursor=mysql.connection.cursor(DictCursor)
        try:
            cursor.execute("""INSERT INTO cart_items(cart_id,product_id,quantity,price_at_add)
                VALUES (%s,%s,%s,%s) ON DUPLICATE KEY UPDATE quantity=VALUES(quantity)""",(cart_id,product_id,quantity,price))
            mysql.connection.commit()
        finally:
            cursor.close()


class ProductStockModel:
    @staticmethod
    def get_by_id(product_id):
        cursor=mysql.connection.cursor(DictCursor)
        try:
            cursor.execute("SELECT title,sale_price,base_price,stock_quantity FROM products WHERE product_id=%s",(product_id,))
            return cursor.fetchone()
        finally:
            cursor.close()

    @staticmethod
    def get_active_with_image(product_id):
        cursor=mysql.connection.cursor(DictCursor)
        try:
            cursor.execute("""SELECT p.product_id,p.title,p.sale_price,p.base_price,pi.image_url,p.stock_quantity
            FROM products p
            JOIN product_images pi ON p.product_id=pi.product_id
            WHERE p.product_id=%s AND pi.is_active=1""",(product_id,))
            return cursor.fetchone()
        finally:
            cursor.close()

    @staticmethod
    def check_stock(product_id):
        cursor=mysql.connection.cursor(DictCursor)
        try:
            cursor.execute("SELECT stock_quantity,title FROM products WHERE product_id=%s AND status='active'",(product_id,))
            return cursor.fetchone()
        finally:
            cursor.close()

    @staticmethod
    def deduct_stock(product_id,quantity):
        cursor=mysql.connection.cursor(DictCursor)
        try:
            # BUG FIX: combined stock deduct + draft status into single query - removes race condition window
            cursor.execute("""UPDATE products
                SET stock_quantity=GREATEST(stock_quantity - %s,0),
                status=CASE WHEN GREATEST(stock_quantity - %s,0)=0 THEN 'draft' ELSE status END
                WHERE product_id=%s""",(quantity,quantity,product_id))
            mysql.connection.commit()
        finally:
            cursor.close()


class UserModel:
    @staticmethod
    def get_by_email(email):
        cursor=mysql.connection.cursor(DictCursor)
        try:
            cursor.execute("SELECT user_id FROM users WHERE email=%s",(email,))
            return cursor.fetchone()
        finally:
            cursor.close()

    @staticmethod
    def create_guest(first_name,last_name,email):
        cursor=mysql.connection.cursor(DictCursor)
        try:
            cursor.execute("""INSERT INTO users(role_id,first_name,last_name,email,password_hash)
                VALUES (%s,%s,%s,%s,%s)""",(2,first_name,last_name,email,'guest'))
            mysql.connection.commit()
            return cursor.lastrowid
        finally:
            cursor.close()


class OrderPlacementModel:
    @staticmethod
    def create_order(user_id,order_number,subtotal,discount_amount,promo_code,
                     shipping_charges,total_amount,full_address):
        cursor=mysql.connection.cursor(DictCursor)
        try:
            cursor.execute("""INSERT INTO orders(user_id,order_number,status,subtotal,discount_amount,
                promo_code,shipping_charges,total_amount,shipping_address,billing_address,ordered_at)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",(user_id,order_number,'pending',subtotal,discount_amount,
                promo_code,shipping_charges,total_amount,full_address,full_address,datetime.now()))
            mysql.connection.commit()
            return cursor.lastrowid
        finally:
            cursor.close()

    @staticmethod
    def create_order_detail(order_id,product_id,price,quantity,item_subtotal):
        cursor=mysql.connection.cursor(DictCursor)
        try:
            cursor.execute("""INSERT INTO order_details(order_id,product_id,product_amount,quantity,discount_per_item,subtotal)
                VALUES (%s,%s,%s,%s,%s,%s)""",(order_id,product_id,price,quantity,0.00,item_subtotal))
            mysql.connection.commit()
        finally:
            cursor.close()

    @staticmethod
    def create_payment(order_id,payment_method,total_amount):
        cursor=mysql.connection.cursor(DictCursor)
        try:
            cursor.execute("""INSERT INTO order_payments(order_id,payment_method,amount,status)
                VALUES (%s,%s,%s,%s)""",(order_id,payment_method,total_amount,'pending'))
            mysql.connection.commit()
        finally:
            cursor.close()


class WishlistModel:
    @staticmethod
    def exists(user_id,product_id):
        cursor=mysql.connection.cursor(DictCursor)
        try:
            cursor.execute("SELECT * FROM wishlist WHERE user_id=%s AND product_id=%s",(user_id,product_id))
            return cursor.fetchone()
        finally:
            cursor.close()

    @staticmethod
    def add(user_id,product_id):
        cursor=mysql.connection.cursor(DictCursor)
        try:
            cursor.execute("INSERT IGNORE INTO wishlist(user_id,product_id) VALUES(%s,%s)",(user_id,int(product_id)))
            mysql.connection.commit()
        finally:
            cursor.close()