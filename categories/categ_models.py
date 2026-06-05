from utils.db import mysql
from datetime import datetime


class CategoryModel:
    @staticmethod
    def get_admin(admin_id):
        cursor=mysql.connection.cursor()
        try:
            cursor.execute('SELECT first_name,last_name,username FROM admins WHERE admin_id=%s',(admin_id,))
            return cursor.fetchone()
        finally:
            cursor.close()

    @staticmethod
    def get_full_admin(admin_id):
        cursor=mysql.connection.cursor()
        try:
            cursor.execute('SELECT * FROM admins WHERE admin_id=%s',(admin_id,))
            return cursor.fetchone()
        finally:
            cursor.close()

    @staticmethod
    def get_all_paginated(per_page,offset):
        cursor=mysql.connection.cursor()
        try:
            cursor.execute("""SELECT c.category_id,c.name,c.description,c.is_active,c.created_at,
            COUNT(DISTINCT p.product_id) AS total_products,
            SUM(CASE WHEN p.status='active' THEN 1 ELSE 0 END) AS active_products,
            COALESCE(SUM(od.subtotal),0) AS total_revenue
        FROM categories c
        LEFT JOIN products p ON c.category_id=p.category_id
        LEFT JOIN order_details od ON p.product_id=od.product_id
        GROUP BY c.category_id
        ORDER BY total_revenue DESC
        LIMIT %s OFFSET %s""",(per_page,offset))
            return cursor.fetchall()
        finally:
            cursor.close()

    @staticmethod
    def count_all():
        cursor=mysql.connection.cursor()
        try:
            cursor.execute("SELECT COUNT(*) AS total_count FROM categories")
            return cursor.fetchone()['total_count']
        finally:
            cursor.close()

    @staticmethod
    def get_by_id(category_id):
        cursor=mysql.connection.cursor()
        try:
            cursor.execute('SELECT * FROM categories WHERE category_id=%s',(category_id,))
            return cursor.fetchone()
        finally:
            cursor.close()

    @staticmethod
    def get_is_active(category_id):
        cursor=mysql.connection.cursor()
        try:
            cursor.execute('SELECT is_active FROM categories WHERE category_id=%s',(category_id,))
            return cursor.fetchone()
        finally:
            cursor.close()

    @staticmethod
    def name_exists(name):
        cursor=mysql.connection.cursor()
        try:
            cursor.execute('SELECT category_id FROM categories WHERE name=%s',(name,))
            return cursor.fetchone()
        finally:
            cursor.close()

    @staticmethod
    def name_exists_other(name,category_id):
        cursor=mysql.connection.cursor()
        try:
            cursor.execute('SELECT category_id FROM categories WHERE name=%s AND category_id !=%s',(name,category_id))
            return cursor.fetchone()
        finally:
            cursor.close()

    @staticmethod
    def create(name,description,status):
        cursor=mysql.connection.cursor()
        try:
            cursor.execute('''INSERT INTO categories(name,description,is_active,created_at)
                    VALUES(%s,%s,%s,%s)''',(name,description,status,datetime.now()))
            mysql.connection.commit()
        finally:
            cursor.close()

    @staticmethod
    def update(category_id,name,description,is_active):
        cursor=mysql.connection.cursor()
        try:
            cursor.execute('''UPDATE categories SET name=%s,description=%s,is_active=%s
                WHERE category_id=%s''',(name,description,is_active,category_id))
            mysql.connection.commit()
        finally:
            cursor.close()

    @staticmethod
    def toggle_active(category_id,new_status):
        cursor=mysql.connection.cursor()
        try:
            cursor.execute('UPDATE categories SET is_active=%s WHERE category_id=%s',(new_status,category_id))
            mysql.connection.commit()
        finally:
            cursor.close()

    @staticmethod
    def delete(category_id):
        cursor=mysql.connection.cursor()
        try:
            cursor.execute('DELETE FROM categories WHERE category_id=%s',(category_id,))
            mysql.connection.commit()
        finally:
            cursor.close()


    @staticmethod
    def get_products_by_category(category_id):
        cursor=mysql.connection.cursor()
        try:
            cursor.execute("""SELECT p.product_id,p.product_no,p.title,p.base_price,p.sale_price,p.stock_quantity,
                p.status,p.created_at,p.updated_at,
                (SELECT image_url FROM product_images
                 WHERE product_id=p.product_id AND is_active=1 LIMIT 1) AS image_url
            FROM products p
            WHERE p.category_id=%s
            ORDER BY p.created_at DESC""",(category_id,))
            return cursor.fetchall()
        finally:
            cursor.close()