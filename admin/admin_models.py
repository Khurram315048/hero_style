from utils.db import mysql
from werkzeug.security import generate_password_hash
from datetime import datetime


class AdminModel:
    @staticmethod
    def get_by_id(admin_id):
        cursor=mysql.connection.cursor()
        try:
            cursor.execute('SELECT email,username,first_name,last_name FROM admins WHERE admin_id=%s',(admin_id,))
            return cursor.fetchone()
        finally:
            cursor.close()

    @staticmethod
    def get_full_by_id(admin_id):
        cursor=mysql.connection.cursor()
        try:
            cursor.execute('SELECT * FROM admins WHERE admin_id=%s AND is_deleted=0',(admin_id,))
            return cursor.fetchone()
        finally:
            cursor.close()

    @staticmethod
    def get_by_email(email):
        cursor=mysql.connection.cursor()
        try:
            cursor.execute('SELECT * FROM admins WHERE email=%s AND is_deleted=0',(email,))
            return cursor.fetchone()
        finally:
            cursor.close()

    @staticmethod
    def email_exists(email):
        cursor=mysql.connection.cursor()
        try:
            cursor.execute('SELECT email FROM admins WHERE email=%s',(email,))
            return cursor.fetchone()
        finally:
            cursor.close()

    @staticmethod
    def create(first_name,last_name,username,email,plain_password):
        cursor=mysql.connection.cursor()
        try:
            hash_password=generate_password_hash(plain_password)
            cursor.execute('''INSERT INTO admins(role_id,first_name,last_name,username,email,password_hash)
                        VALUES(%s,%s,%s,%s,%s,%s)''',(1,first_name,last_name,username,email,hash_password))
            mysql.connection.commit()
        finally:
            cursor.close()

    @staticmethod
    def update_profile(admin_id,first_name,last_name,username,email):
        cursor=mysql.connection.cursor()
        try:
            cursor.execute('''UPDATE admins SET first_name=%s,last_name=%s,username=%s,email=%s
                           WHERE admin_id=%s AND is_deleted=0''',(first_name,last_name,username,email,admin_id))
            mysql.connection.commit()
        finally:
            cursor.close()

    @staticmethod
    def update_password(email,new_password):
        cursor=mysql.connection.cursor()
        try:
            hashed=generate_password_hash(new_password)
            cursor.execute('UPDATE admins SET password_hash=%s WHERE email=%s AND is_deleted=0',(hashed,email))
            mysql.connection.commit()
        finally:
            cursor.close()


class OTPModel:
    @staticmethod
    def delete_by_email(email):
        cursor=mysql.connection.cursor()
        try:
            cursor.execute('DELETE FROM password_reset_otps WHERE email=%s',(email,))
            mysql.connection.commit()
        finally:
            cursor.close()

    @staticmethod
    def create(email,otp,expires):
        cursor=mysql.connection.cursor()
        try:
            cursor.execute('INSERT INTO password_reset_otps(email,otp,expires_at) VALUES(%s,%s,%s)',(email,otp,expires))
            mysql.connection.commit()
        finally:
            cursor.close()

    @staticmethod
    def verify(email,otp_entered):
        cursor=mysql.connection.cursor()
        try:
            cursor.execute('''SELECT id FROM password_reset_otps
                       WHERE email=%s AND otp=%s AND is_used=0
                       AND expires_at > NOW()''',(email,otp_entered))
            return cursor.fetchone()
        finally:
            cursor.close()

    @staticmethod
    def mark_used(email):
        cursor=mysql.connection.cursor()
        try:
            cursor.execute('UPDATE password_reset_otps SET is_used=1 WHERE email=%s',(email,))
            mysql.connection.commit()
        finally:
            cursor.close()


class ProductModel:
    @staticmethod
    def get_all_paginated(per_page,offset):
        cursor=mysql.connection.cursor()
        try:
            cursor.execute('''SELECT pr.*,pi.*,cat.*,pd.*
                       FROM products pr
                       JOIN product_images pi ON pr.product_id=pi.product_id AND pi.is_active=1
                       JOIN categories cat ON pr.category_id=cat.category_id
                       JOIN product_details pd ON pr.product_id=pd.product_id
                       WHERE pr.status != 'archived'
                        LIMIT %s OFFSET %s''',(per_page,offset))
            return cursor.fetchall()
        finally:
            cursor.close()

    @staticmethod
    def count_all():
        cursor=mysql.connection.cursor()
        try:
            cursor.execute("SELECT COUNT(*) AS total_count FROM products")
            return cursor.fetchone()['total_count']
        finally:
            cursor.close()

    @staticmethod
    def get_status(product_id):
        cursor=mysql.connection.cursor()
        try:
            cursor.execute('SELECT status FROM products WHERE product_id=%s',(product_id,))
            return cursor.fetchone()
        finally:
            cursor.close()

    @staticmethod
    def create(product_no,category_id,title,base_price,sale_price,stock,status):
        cursor=mysql.connection.cursor()
        try:
            cursor.execute('''INSERT INTO products(product_no,category_id,title,base_price,sale_price,stock_quantity,status,created_at,updated_at)
                VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)''',(product_no,category_id,title,base_price,sale_price,stock,status,datetime.now(),datetime.now()))
            mysql.connection.commit()
            return cursor.lastrowid
        finally:
            cursor.close()

    @staticmethod
    def update(product_id,product_no,category_id,title,base_price,sale_price,stock,status):
        cursor=mysql.connection.cursor()
        try:
            cursor.execute('''UPDATE products SET product_no=%s,category_id=%s,title=%s,base_price=%s,sale_price=%s,
            stock_quantity=%s,status=%s,updated_at=%s WHERE product_id=%s''',
            (product_no,category_id,title,base_price,sale_price,stock,status,datetime.now(),product_id))
            mysql.connection.commit()
        finally:
            cursor.close()

    @staticmethod
    def soft_delete(product_id):
        cursor=mysql.connection.cursor()
        try:
            cursor.execute('UPDATE products SET status=%s,updated_at=%s WHERE product_id=%s',('archived',datetime.now(),product_id))
            cursor.execute('UPDATE product_images SET is_active=%s WHERE product_id=%s',(0,product_id))
            mysql.connection.commit()
        finally:
            cursor.close()

    @staticmethod
    def activate(product_id):
        cursor=mysql.connection.cursor()
        try:
            cursor.execute('UPDATE products SET status=%s,updated_at=%s WHERE product_id=%s',('active',datetime.now(),product_id))
            mysql.connection.commit()
        finally:
            cursor.close()

    @staticmethod
    def restore_stock_on_cancel(order_id):
        cursor=mysql.connection.cursor()
        try:
            cursor.execute('''UPDATE products p
                JOIN order_details od ON p.product_id=od.product_id
                SET p.stock_quantity=p.stock_quantity + od.quantity,
                p.status=CASE WHEN p.status='draft' THEN 'active' ELSE p.status END
                WHERE od.order_id=%s''',(order_id,))
            mysql.connection.commit()
        finally:
            cursor.close()


class ProductDetailsModel:
    @staticmethod
    def create(product_id,short_desc,long_desc,display_type,brightness_nits,battery_life,
               connectivity,strap_material,case_material,water_resistance,weight,warranty_month,always_display):
        cursor=mysql.connection.cursor()
        try:
            cursor.execute('''INSERT INTO product_details(product_id,short_description,long_description,display_type,brightness_nits,
             battery_life,connectivity,strap_material,case_material,water_resistance,
             weight,warranty_months,is_always_on_display,created_at,updated_at)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',(product_id,short_desc,long_desc,display_type,brightness_nits,
              battery_life,connectivity,strap_material,case_material,water_resistance,
              weight,warranty_month,always_display,datetime.now(),datetime.now()))
            mysql.connection.commit()
        finally:
            cursor.close()

    @staticmethod
    def update(product_id,short_desc,long_desc,display_type,brightness_nits,battery_life,
               connectivity,strap_material,case_material,water_resistance,weight,warranty_month,always_display):
        cursor=mysql.connection.cursor()
        try:
            cursor.execute('''UPDATE product_details SET product_id=%s,short_description=%s,long_description=%s,
                       display_type=%s,brightness_nits=%s,
             battery_life=%s,connectivity=%s,strap_material=%s,case_material=%s,water_resistance=%s,
             weight=%s,warranty_months=%s,is_always_on_display=%s,updated_at=%s WHERE product_id=%s''',
             (product_id,short_desc,long_desc,display_type,brightness_nits,
              battery_life,connectivity,strap_material,case_material,water_resistance,
              weight,warranty_month,always_display,datetime.now(),product_id))
            mysql.connection.commit()
        finally:
            cursor.close()


class ProductImageModel:
    @staticmethod
    def get_category_name(category_id):
        cursor=mysql.connection.cursor()
        try:
            cursor.execute('SELECT name FROM categories WHERE category_id=%s',(category_id,))
            return cursor.fetchone()
        finally:
            cursor.close()

    @staticmethod
    def create(product_id,image_url,title,width,height):
        cursor=mysql.connection.cursor()
        try:
            cursor.execute('''INSERT INTO product_images(product_id,image_url,alt_text,is_active,width,height,created_at)
                VALUES (%s,%s,%s,%s,%s,%s,%s)''',(product_id,image_url,title,1,width,height,datetime.now()))
            mysql.connection.commit()
        finally:
            cursor.close()

    @staticmethod
    def update_or_create(product_id,image_url,title,width,height):
        cursor=mysql.connection.cursor()
        try:
            cursor.execute('SELECT image_id FROM product_images WHERE product_id=%s',(product_id,))
            existing=cursor.fetchone()
            if existing:
                cursor.execute('''UPDATE product_images SET image_url=%s,alt_text=%s,
                           is_active=%s,width=%s,height=%s,created_at=%s WHERE product_id=%s''',
                        (image_url,title,1,width,height,datetime.now(),product_id))
            else:
                cursor.execute('''INSERT INTO product_images(product_id,image_url,alt_text,is_active,width,height,created_at)
                    VALUES (%s,%s,%s,%s,%s,%s,%s)''',(product_id,image_url,title,1,width,height,datetime.now()))
            mysql.connection.commit()
        finally:
            cursor.close()


class CategoryModel:
    @staticmethod
    def get_active():
        cursor=mysql.connection.cursor()
        try:
            cursor.execute('SELECT * FROM categories WHERE is_active=1')
            return cursor.fetchall()
        finally:
            cursor.close()


class OrderModel:
    @staticmethod
    def get_all_paginated(per_page,offset):
        cursor=mysql.connection.cursor()
        try:
            cursor.execute('''SELECT o.order_id,o.order_number,o.user_id,o.subtotal,o.status AS order_status,
                       o.discount_amount,o.shipping_charges,o.total_amount,o.ordered_at,
                       CONCAT(u.first_name,' ',u.last_name) AS customer_name,
                       SUM(d.quantity) AS total_items,
                       p.status AS pay_status,p.payment_method
                       FROM orders o
                       JOIN users u ON o.user_id=u.user_id
                       JOIN order_payments p ON o.order_id=p.order_id
                       JOIN order_details d ON o.order_id=d.order_id
                       WHERE o.is_deleted=0
                       GROUP BY o.order_id,o.order_number,o.user_id,customer_name,o.subtotal,
                        o.discount_amount,o.shipping_charges,o.total_amount,
                        p.payment_method,p.status,o.status,o.ordered_at
                       LIMIT %s OFFSET %s''',(per_page,offset))
            return cursor.fetchall()
        finally:
            cursor.close()

    @staticmethod
    def count_all():
        cursor=mysql.connection.cursor()
        try:
            cursor.execute("SELECT COUNT(*) AS total_count FROM orders WHERE is_deleted=0")
            return cursor.fetchone()['total_count']
        finally:
            cursor.close()


    @staticmethod
    def get_with_user_and_payment(order_id):
        cursor=mysql.connection.cursor()
        try:
            cursor.execute('''SELECT o.*,CONCAT(u.first_name,' ',u.last_name) AS customer_name,
                   u.email,p.payment_method,p.status AS pay_status,p.transaction_id
            FROM orders o
            JOIN users u ON o.user_id=u.user_id
            JOIN order_payments p ON o.order_id=p.order_id
            WHERE o.order_id=%s''',(order_id,))
            return cursor.fetchone()
        finally:
            cursor.close()


    @staticmethod
    def get_order_user_for_email(order_id):
        cursor=mysql.connection.cursor()
        try:
            cursor.execute('''SELECT o.order_number,u.email,u.first_name
                FROM orders o
                JOIN users u ON o.user_id=u.user_id
                WHERE o.order_id=%s''',(order_id,))
            return cursor.fetchone()
        finally:
            cursor.close()


    @staticmethod
    def update_status(order_id,status):
        cursor=mysql.connection.cursor()
        try:
            cursor.execute("UPDATE orders SET status=%s WHERE order_id=%s",(status,order_id))
            mysql.connection.commit()
        finally:
            cursor.close()


    @staticmethod
    def cancel(order_id):
        cursor=mysql.connection.cursor()
        try:
            cursor.execute("""UPDATE orders SET status='cancelled',is_cancelled=1,cancelled_at=%s
                          WHERE order_id=%s""",(datetime.now(),order_id))
            mysql.connection.commit()
        finally:
            cursor.close()

    @staticmethod
    def soft_delete(order_id):
        cursor=mysql.connection.cursor()
        try:
            cursor.execute("UPDATE orders SET is_deleted=%s WHERE order_id=%s",(1,order_id))
            mysql.connection.commit()
        finally:
            cursor.close()

    @staticmethod
    def get_cancelled_paginated(per_page,offset):
        cursor=mysql.connection.cursor()
        try:
            cursor.execute("""SELECT o.order_id,o.order_number,o.total_amount,o.cancelled_at,o.is_cancelled,
            CONCAT(u.first_name,' ',u.last_name) AS customer_name,
            COALESCE(op.payment_method,'N/A') AS payment_method,
            COALESCE(op.status,'pending') AS pay_status
        FROM orders o
        LEFT JOIN users u ON o.user_id=u.user_id
        LEFT JOIN order_payments op ON o.order_id=op.order_id
        WHERE(o.is_cancelled=1 OR o.status='cancelled')
        AND o.is_deleted=0
        ORDER BY o.cancelled_at DESC
                       LIMIT %s OFFSET %s""",(per_page,offset))
            return cursor.fetchall()
        finally:
            cursor.close()

    @staticmethod
    def count_cancelled():
        cursor=mysql.connection.cursor()
        try:
            cursor.execute("SELECT COUNT(*) AS total_count FROM orders WHERE is_cancelled=1")
            return cursor.fetchone()['total_count']
        finally:
            cursor.close()

    @staticmethod
    def get_items_with_product(order_id):
        cursor=mysql.connection.cursor()
        try:
            cursor.execute('''SELECT d.*,p.title,p.product_no,
                   (SELECT image_url FROM product_images
                    WHERE product_id=p.product_id
                    AND is_active=1 LIMIT 1) AS image_url
            FROM order_details d
            JOIN products p ON d.product_id=p.product_id
            WHERE d.order_id=%s''',(order_id,))
            return cursor.fetchall()
        finally:
            cursor.close()

    @staticmethod
    def get_by_user(user_id):
        cursor=mysql.connection.cursor()
        try:
            cursor.execute("""SELECT o.order_id,o.order_number,o.status,o.total_amount,
                   o.ordered_at,o.is_cancelled,
                   COALESCE(op.status,'pending') AS pay_status,
                   COALESCE(op.payment_method,'N/A') AS payment_method
            FROM orders o
            LEFT JOIN order_payments op ON o.order_id=op.order_id
            WHERE o.user_id=%s AND o.is_deleted=0
            ORDER BY o.ordered_at DESC""",(user_id,))
            return cursor.fetchall()
        finally:
            cursor.close()

    @staticmethod
    def get_recent(limit=4):
        cursor=mysql.connection.cursor()
        try:
            cursor.execute("""SELECT o.order_number,o.ordered_at,o.total_amount,o.status,o.order_id,
                CONCAT(u.first_name,' ',u.last_name) AS customer_name,u.email,
                p.payment_method,p.status AS pay_status
            FROM orders o
            JOIN users u ON o.user_id=u.user_id
            JOIN order_payments p ON o.order_id=p.order_id
            WHERE o.is_cancelled=0 AND o.is_deleted=0
            LIMIT %s""",(limit,))
            return cursor.fetchall()
        finally:
            cursor.close()


class OrderPaymentModel:
    @staticmethod
    def get_all_paginated(per_page,offset):
        cursor=mysql.connection.cursor()
        try:
            cursor.execute("""SELECT op.payment_id,op.order_id,op.payment_method,
                   op.amount,op.status,op.paid_at,op.created_at,o.order_number,o.is_cancelled,
                   CONCAT(u.first_name,' ',u.last_name) AS customer_name
            FROM order_payments op
            JOIN orders o ON op.order_id=o.order_id
            LEFT JOIN users u ON o.user_id=u.user_id
            WHERE o.is_deleted=0
            ORDER BY op.created_at DESC LIMIT %s OFFSET %s""",(per_page,offset))
            return cursor.fetchall()
        finally:
            cursor.close()


    @staticmethod
    def count_all():
        cursor=mysql.connection.cursor()
        try:
            cursor.execute("SELECT COUNT(*) AS total_count FROM order_payments")
            return cursor.fetchone()['total_count']
        finally:
            cursor.close()


    @staticmethod
    def get_with_order(order_id):
        cursor=mysql.connection.cursor()
        try:
            cursor.execute("""SELECT o.order_id,op.payment_id
                FROM orders o
                LEFT JOIN order_payments op ON o.order_id=op.order_id
                WHERE o.order_id=%s
                AND (o.is_cancelled=1 OR o.status='cancelled')
                AND o.is_deleted=0""",(order_id,))
            return cursor.fetchone()
        finally:
            cursor.close()


    @staticmethod
    def mark_refunded(payment_id):
        cursor=mysql.connection.cursor()
        try:
            cursor.execute("UPDATE order_payments SET status='refunded' WHERE payment_id=%s",(payment_id,))
            mysql.connection.commit()
        finally:
            cursor.close()


    @staticmethod
    def insert_cod_refunded(order_id):
        cursor=mysql.connection.cursor()
        try:
            cursor.execute("""INSERT INTO order_payments(order_id,payment_method,amount,status)
                SELECT order_id,'COD',total_amount,'refunded'
                FROM orders WHERE order_id=%s""",(order_id,))
            mysql.connection.commit()
        finally:
            cursor.close()


class OrderReturnModel:
    @staticmethod
    def get_order_returns_paginated(per_page,offset):
        cursor=mysql.connection.cursor()
        try:
            cursor.execute('''SELECT r.*,o.order_number,
                       CONCAT(u.first_name,' ',u.last_name) AS customer_name
                FROM order_returns r
                JOIN orders o ON r.order_id=o.order_id
                JOIN users u ON o.user_id=u.user_id
                WHERE r.is_cancelled=0
                ORDER BY r.requested_at DESC LIMIT %s OFFSET %s''',(per_page,offset))
            return cursor.fetchall()
        finally:
            cursor.close()

    @staticmethod
    def get_item_returns_paginated(per_page,offset):
        cursor=mysql.connection.cursor()
        try:
            cursor.execute('''SELECT ir.*,o.order_number,
                       CONCAT(u.first_name,' ',u.last_name) AS customer_name,
                       p.title AS product_title
                FROM order_item_returns ir
                JOIN orders o ON ir.order_id=o.order_id
                JOIN users u ON o.user_id=u.user_id
                JOIN order_details od ON ir.order_detail_id=od.order_detail_id
                JOIN products p ON od.product_id=p.product_id
                ORDER BY ir.requested_at DESC LIMIT %s OFFSET %s''',(per_page,offset))
            return cursor.fetchall()
        finally:
            cursor.close()


    @staticmethod
    def count_order_returns():
        cursor=mysql.connection.cursor()
        try:
            cursor.execute("SELECT COUNT(*) AS total_count FROM order_returns")
            return cursor.fetchone()['total_count']
        finally:
            cursor.close()


    @staticmethod
    def update_order_return_status(order_id,status):
        cursor=mysql.connection.cursor()
        try:
            cursor.execute('UPDATE order_returns SET status=%s,resolved_at=%s WHERE order_id=%s',(status,datetime.now(),order_id))
            mysql.connection.commit()
        finally:
            cursor.close()


    @staticmethod
    def update_item_return_status(order_id,status):
        cursor=mysql.connection.cursor()
        try:
            cursor.execute('UPDATE order_item_returns SET status=%s,resolved_at=%s WHERE order_id=%s',(status,datetime.now(),order_id))
            mysql.connection.commit()
        finally:
            cursor.close()


class CustomerModel:
    @staticmethod
    def count_customers():
        cursor=mysql.connection.cursor()
        try:
            cursor.execute("SELECT COUNT(*) AS total_count FROM users WHERE role_id=2")
            return cursor.fetchone()['total_count']
        finally:
            cursor.close()


    @staticmethod
    def get_all_paginated(per_page,offset):
        cursor=mysql.connection.cursor()
        try:
            cursor.execute("""SELECT u.user_id,u.first_name,u.last_name,u.email,
                   u.is_active,u.created_at,u.last_login_at,
                   COUNT(DISTINCT o.order_id) AS total_orders,
                   COALESCE(SUM(o.total_amount),0) AS total_spent
            FROM users u
            LEFT JOIN orders o ON u.user_id=o.user_id AND o.is_deleted=0
            WHERE u.role_id=2
            GROUP BY u.user_id
            ORDER BY u.created_at DESC LIMIT %s OFFSET %s""",(per_page,offset))
            return cursor.fetchall()
        finally:
            cursor.close()


    @staticmethod
    def get_by_id(user_id):
        cursor=mysql.connection.cursor()
        try:
            cursor.execute("""SELECT user_id,first_name,last_name,email,
                   is_active,created_at,last_login_at
            FROM users WHERE user_id=%s""",(user_id,))
            return cursor.fetchone()
        finally:
            cursor.close()


    @staticmethod
    def get_is_active(user_id):
        cursor=mysql.connection.cursor()
        try:
            cursor.execute('SELECT is_active FROM users WHERE user_id=%s',(user_id,))
            return cursor.fetchone()
        finally:
            cursor.close()


    @staticmethod
    def toggle_active(user_id,new_status):
        cursor=mysql.connection.cursor()
        try:
            cursor.execute('UPDATE users SET is_active=%s WHERE user_id=%s',(new_status,user_id))
            mysql.connection.commit()
        finally:
            cursor.close()


    @staticmethod
    def get_wishlist(user_id):
        cursor=mysql.connection.cursor()
        try:
            cursor.execute("""SELECT p.title,pi.image_url,p.sale_price,w.added_at
            FROM wishlist w
            JOIN products p ON w.product_id=p.product_id
            LEFT JOIN product_images pi ON p.product_id=pi.product_id
            WHERE w.user_id=%s""",(user_id,))
            return cursor.fetchall()
        finally:
            cursor.close()


class FormModel:
    @staticmethod
    def get_all_paginated(per_page,offset):
        cursor=mysql.connection.cursor()
        try:
            cursor.execute("""SELECT form_id,full_name,email,phone_number,
                   category,subject,message,overall_rating,
                   order_id,is_deleted
            FROM forms
            WHERE is_deleted=0
            ORDER BY form_id DESC LIMIT %s OFFSET %s""",(per_page,offset))
            return cursor.fetchall()
        finally:
            cursor.close()

    @staticmethod
    def count_all():
        cursor=mysql.connection.cursor()
        try:
            cursor.execute("SELECT COUNT(*) AS total_count FROM forms WHERE is_deleted=0")
            return cursor.fetchone()['total_count']
        finally:
            cursor.close()

    @staticmethod
    def soft_delete(form_id):
        cursor=mysql.connection.cursor()
        try:
            cursor.execute('UPDATE forms SET is_deleted=1 WHERE form_id=%s',(form_id,))
            mysql.connection.commit()
        finally:
            cursor.close()


class ReviewModel:
    @staticmethod
    def get_all_paginated(per_page,offset):
        cursor=mysql.connection.cursor()
        try:
            cursor.execute("""SELECT pr.review_id,pr.rating,pr.comment,pr.status,
                   pr.created_at,pr.is_deleted,
                   p.title AS product_title,p.product_id,
                   CONCAT(u.first_name,' ',u.last_name) AS customer_name,
                   u.user_id
            FROM product_reviews pr
            JOIN products p ON pr.product_id=p.product_id
            JOIN users u ON pr.user_id=u.user_id
            WHERE pr.is_deleted=0
            ORDER BY pr.created_at DESC LIMIT %s OFFSET %s""",(per_page,offset))
            return cursor.fetchall()
        finally:
            cursor.close()

    @staticmethod
    def count_all():
        cursor=mysql.connection.cursor()
        try:
            cursor.execute("SELECT COUNT(*) AS total_count FROM product_reviews")
            return cursor.fetchone()['total_count']
        finally:
            cursor.close()

    @staticmethod
    def update_status(review_id,status):
        cursor=mysql.connection.cursor()
        try:
            cursor.execute("UPDATE product_reviews SET status=%s WHERE review_id=%s",(status,review_id))
            mysql.connection.commit()
        finally:
            cursor.close()

    @staticmethod
    def soft_delete(review_id):
        cursor=mysql.connection.cursor()
        try:
            cursor.execute("UPDATE product_reviews SET is_deleted=1 WHERE review_id=%s",(review_id,))
            mysql.connection.commit()
        finally:
            cursor.close()


class SalesModel:
    @staticmethod
    def get_summary():
        cursor=mysql.connection.cursor()
        try:
            cursor.execute('SELECT SUM(total_amount) AS total_sales FROM orders WHERE is_cancelled=0 AND is_deleted=0')
            total_sales=cursor.fetchone()['total_sales'] or 0

            cursor.execute('SELECT SUM(quantity) AS total_units FROM order_details')
            total_units=cursor.fetchone()['total_units'] or 0

            cursor.execute('SELECT COUNT(*) AS total_orders FROM orders WHERE is_cancelled=0 AND is_deleted=0')
            total_orders=cursor.fetchone()['total_orders']

            avg_order=int(total_sales / total_units) if total_units else 0

            cursor.execute("""SELECT COUNT(order_id) AS total_return FROM order_returns WHERE status='approved'
                       AND is_cancelled=0""")
            total_returns=cursor.fetchone()['total_return']

            cursor.execute("""SELECT SUM(p.amount) AS pending_cod
                       FROM order_payments p
                       JOIN orders o ON p.order_id=o.order_id
                       WHERE p.status='pending' AND p.payment_method='COD' AND o.is_cancelled=0""")
            pending_cod=cursor.fetchone()['pending_cod'] or 0

            return {
                'total_sales':total_sales,
                'total_units':total_units,
                'total_orders':total_orders,
                'avg_order':avg_order,
                'total_returns':total_returns,
                'pending_cod':pending_cod,
            }
        finally:
            cursor.close()


    @staticmethod
    def get_category_sales():
        cursor=mysql.connection.cursor()
        try:
            cursor.execute("""SELECT
                c.name AS name,
                COALESCE(SUM(CASE WHEN o.order_id IS NOT NULL AND o.is_cancelled=0 AND o.is_deleted=0 THEN od.quantity ELSE 0 END),0) AS units_sold,
                COALESCE(SUM(CASE WHEN o.order_id IS NOT NULL AND o.is_cancelled=0 AND o.is_deleted=0 THEN od.subtotal ELSE 0 END),0) AS revenue,
                COALESCE(SUM(CASE WHEN o.order_id IS NOT NULL AND o.is_cancelled=0 AND o.is_deleted=0 AND (oir.status='approved' OR o.status='returned') THEN od.quantity ELSE 0 END),0) AS returns,
                (COALESCE(SUM(CASE WHEN o.order_id IS NOT NULL AND o.is_cancelled=0 AND o.is_deleted=0 THEN od.subtotal ELSE 0 END),0) -
                 COALESCE(SUM(CASE WHEN o.order_id IS NOT NULL AND o.is_cancelled=0 AND o.is_deleted=0 AND (oir.status='approved' OR o.status='returned') THEN od.subtotal ELSE 0 END),0)) AS net_revenue
            FROM categories c
            LEFT JOIN products p ON c.category_id=p.category_id
            LEFT JOIN order_details od ON p.product_id=od.product_id
            LEFT JOIN orders o ON od.order_id=o.order_id AND o.is_deleted=0
            LEFT JOIN order_item_returns oir ON od.order_detail_id=oir.order_detail_id AND oir.status='approved'
            GROUP BY c.category_id,c.name
            ORDER BY net_revenue DESC""")
            return cursor.fetchall()
        finally:
            cursor.close()

 
    @staticmethod
    def get_top_products(limit=5):
        cursor=mysql.connection.cursor()
        try:
            cursor.execute("""SELECT p.title,p.base_price,p.stock_quantity,
               c.name AS category_name,
               SUM(od.quantity) AS units_sold,
               SUM(od.subtotal) AS total_revenue
            FROM order_details od
            JOIN products p ON od.product_id=p.product_id
            JOIN categories c ON p.category_id=c.category_id
            JOIN orders o ON od.order_id=o.order_id
            WHERE o.is_cancelled=0 AND o.is_deleted=0 AND o.status='delivered' AND p.status='active'
            GROUP BY p.product_id,p.title,p.base_price,p.stock_quantity,c.name
            ORDER BY units_sold DESC
            LIMIT %s""",(limit,))
            return cursor.fetchall()
        finally:
            cursor.close()


class DashboardModel:
    @staticmethod
    def get_stats():
        cursor=mysql.connection.cursor()
        try:
            cursor.execute('SELECT COUNT(*) AS total_orders FROM orders WHERE is_cancelled=0 AND is_deleted=0')
            total_orders=cursor.fetchone()['total_orders']

            cursor.execute('SELECT COUNT(user_id) AS total_customers FROM orders WHERE is_cancelled=0 AND is_deleted=0')
            total_customers=cursor.fetchone()['total_customers']

            cursor.execute('SELECT SUM(total_amount) AS total_revenue FROM orders WHERE is_cancelled=0 AND is_deleted=0')
            total_revenue=cursor.fetchone()['total_revenue']

            cursor.execute('SELECT COUNT(*) AS total_forms FROM forms WHERE is_deleted=0')
            total_forms=cursor.fetchone()['total_forms']

            return {
                'total_orders':total_orders,
                'total_customers':total_customers,
                'total_revenue':total_revenue,
                'total_forms':total_forms,
            }
        finally:
            cursor.close()