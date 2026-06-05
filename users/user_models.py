import random
import string
from datetime import datetime, timedelta

import MySQLdb.cursors
from flask_mail import Message
from werkzeug.security import check_password_hash, generate_password_hash

from utils.db import mysql


# ─── Auth ─────────────────────────────────────────────────────────────────────

def login_user(email, password):
    """
    Validates login credentials.
    Returns user dict if valid, None if not found, False if password wrong.
    BUG FIX: DictCursor used so user['password_hash'] works correctly.
    """
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    try:
        cursor.execute('SELECT * FROM users WHERE email=%s AND is_active=1', (email,))
        user = cursor.fetchone()
        if not user:
            return None
        if not check_password_hash(user['password_hash'], password):
            return False
        return user
    finally:
        cursor.close()


def register_user(first_name, last_name, email, plain_password):
    """
    Validates and inserts a new user.
    Returns 'email_exists' if duplicate, 'weak_password' with reason, or 'ok'.
    BUG FIX: DictCursor for consistent dict-style row access.
    """
    if not plain_password or len(plain_password.strip()) < 8:
        return 'weak_password', 'Password Must be at least 8 characters long!'
    if not any(c.isupper() for c in plain_password):
        return 'weak_password', 'Password must contain at least one uppercase letter!'
    if not any(c.isdigit() for c in plain_password):
        return 'weak_password', 'Password must contain at least one number!'

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    try:
        cursor.execute('SELECT email FROM users WHERE email=%s', (email,))
        if cursor.fetchone():
            return 'email_exists', None

        hashed = generate_password_hash(plain_password)
        cursor.execute('''INSERT INTO users
                (role_id, first_name, last_name, email, password_hash,
                 last_login_at, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)''',
            (2, first_name, last_name, email, hashed,
             datetime.now(), datetime.now(), datetime.now()))
        mysql.connection.commit()
        return 'ok', None
    finally:
        cursor.close()


# ─── Password Reset ───────────────────────────────────────────────────────────

def send_reset_otp(email, mail):
    """
    Checks email exists, generates OTP, saves to DB, sends email.
    Returns True if sent, False if email not found.
    """
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    try:
        cursor.execute('SELECT email FROM users WHERE email=%s AND is_active=1', (email,))
        if not cursor.fetchone():
            return False

        otp = ''.join(random.choices(string.digits, k=6))
        expires = datetime.now() + timedelta(minutes=10)

        cursor.execute('DELETE FROM password_reset_otps WHERE email=%s', (email,))
        cursor.execute(
            'INSERT INTO password_reset_otps(email, otp, expires_at) VALUES(%s, %s, %s)',
            (email, otp, expires))
        mysql.connection.commit()

        msg = Message(
            subject='Hero Style — Password Reset OTP',
            recipients=[email],
            body=f"""Your OTP for password reset is: {otp}
This code expires in 10 minutes.
If you did not request this, ignore this email.
— Hero Style Team""")
        mail.send(msg)
        return True
    finally:
        cursor.close()


def verify_reset_otp(email, otp_entered):
    """
    Verifies OTP is valid, unused, and not expired.
    Marks as used if valid.
    Returns True if valid, False otherwise.
    """
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    try:
        cursor.execute('''SELECT id FROM password_reset_otps
            WHERE email=%s AND otp=%s AND is_used=0 AND expires_at > NOW()''',
            (email, otp_entered))
        if not cursor.fetchone():
            return False
        cursor.execute('UPDATE password_reset_otps SET is_used=1 WHERE email=%s', (email,))
        mysql.connection.commit()
        return True
    finally:
        cursor.close()


def update_password(email, new_password, confirm_password):
    """
    Validates and updates password for given email.
    Returns 'mismatch', 'too_short', or 'ok'.
    """
    if new_password != confirm_password:
        return 'mismatch'
    if len(new_password) < 8:
        return 'too_short'
    hashed = generate_password_hash(new_password)
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    try:
        cursor.execute('UPDATE users SET password_hash=%s WHERE email=%s AND is_active=1',
                       (hashed, email))
        mysql.connection.commit()
        return 'ok'
    finally:
        cursor.close()


# ─── User Profile & Options ───────────────────────────────────────────────────

def get_user_options(user_id):
    """Returns email and full username for user_options page."""
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    try:
        cursor.execute(
            "SELECT email, CONCAT(first_name,' ',last_name) AS username FROM users WHERE user_id=%s",
            (user_id,))
        return cursor.fetchone()
    finally:
        cursor.close()


def get_dashboard_data(user_id):
    """
    Returns (user_exist dict, latest_order dict or None) for dashboard.
    Includes total_orders count and latest order details.
    """
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    try:
        cursor.execute('''
            SELECT u.*, COUNT(o.order_id) AS total_orders,
                MAX(o.order_id) AS latest_order_id
            FROM users u
            LEFT JOIN orders o ON u.user_id=o.user_id AND o.is_deleted=0
            WHERE u.user_id=%s
            GROUP BY u.user_id
        ''', (user_id,))
        user_exist = cursor.fetchone()

        latest_order = None
        if user_exist and user_exist['latest_order_id']:
            cursor.execute('''
                SELECT order_number, status, total_amount, ordered_at
                FROM orders WHERE order_id=%s
            ''', (user_exist['latest_order_id'],))
            latest_order = cursor.fetchone()

        return user_exist, latest_order
    finally:
        cursor.close()


def get_user_profile(user_id):
    """Returns full user row for profile page."""
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    try:
        cursor.execute('SELECT * FROM users WHERE user_id=%s', (user_id,))
        return cursor.fetchone()
    finally:
        cursor.close()


def update_user_profile(user_id, first_name, last_name, email):
    """Updates first_name, last_name, email for active user."""
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    try:
        cursor.execute('''UPDATE users SET first_name=%s, last_name=%s, email=%s
                    WHERE user_id=%s AND is_active=1''',
                    (first_name, last_name, email, user_id))
        mysql.connection.commit()
    finally:
        cursor.close()


# ─── Wishlist ─────────────────────────────────────────────────────────────────

def get_wishlist(user_id):
    """
    Returns wishlist products with active image.
    BUG FIX: AND pi.is_active=1 added to exclude inactive images.
    """
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    try:
        cursor.execute('''SELECT p.*, pi.image_url, pi.alt_text
            FROM products p
            JOIN wishlist w ON p.product_id=w.product_id
            JOIN product_images pi ON p.product_id=pi.product_id AND pi.is_active=1
            WHERE w.user_id=%s
        ''', (user_id,))
        return cursor.fetchall()
    finally:
        cursor.close()


def remove_wishlist_item(user_id, product_id):
    """Deletes a product from user's wishlist."""
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    try:
        cursor.execute('DELETE FROM wishlist WHERE product_id=%s AND user_id=%s',
                       (product_id, user_id))
        mysql.connection.commit()
    finally:
        cursor.close()


# ─── Orders ───────────────────────────────────────────────────────────────────

def get_user_orders(user_id):
    """Returns all orders with return status, newest first."""
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    try:
        cursor.execute('''
            SELECT o.*, r.status AS return_status
            FROM orders o
            LEFT JOIN order_returns r ON o.order_id=r.order_id
            WHERE o.user_id=%s
            ORDER BY o.ordered_at DESC
        ''', (user_id,))
        return cursor.fetchall()
    finally:
        cursor.close()


def get_order_details(user_id, order_id):
    """
    Returns (order, order_items, payment) for order detail page.
    BUG FIX: AND pi.is_active=1 added on product_images join.
    Returns None if order not found or doesn't belong to user.
    """
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    try:
        cursor.execute('''
            SELECT o.*, r.status AS return_status, r.reason AS return_reason
            FROM orders o
            LEFT JOIN order_returns r ON o.order_id=r.order_id
            WHERE o.order_id=%s AND o.user_id=%s AND is_deleted=0
        ''', (order_id, user_id))
        order = cursor.fetchone()
        if not order:
            return None

        cursor.execute('''
            SELECT od.order_detail_id, od.quantity, od.subtotal,
                p.title, p.product_id,
                pi.image_url,
                ir.status AS item_return_status
            FROM order_details od
            JOIN products p ON p.product_id=od.product_id
            JOIN product_images pi ON pi.product_id=od.product_id AND pi.is_active=1
            LEFT JOIN order_item_returns ir ON ir.order_detail_id=od.order_detail_id
            WHERE od.order_id=%s
        ''', (order_id,))
        order_items = cursor.fetchall()

        cursor.execute('''
            SELECT payment_method, amount, status
            FROM order_payments WHERE order_id=%s
        ''', (order_id,))
        payment = cursor.fetchone()

        return order, order_items, payment
    finally:
        cursor.close()


def cancel_user_order(user_id, order_id):
    """
    Cancels a pending order, restores stock.
    Returns 'not_found', 'not_pending' with status string, or 'ok'.
    """
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    try:
        cursor.execute('''SELECT status FROM orders
                        WHERE order_id=%s AND user_id=%s AND is_deleted=0''',
                       (order_id, user_id))
        order = cursor.fetchone()
        if not order:
            return 'not_found', None
        if order['status'] != 'pending':
            return 'not_pending', order['status']

        cursor.execute('''UPDATE orders
                        SET status='cancelled', updated_at=%s, is_cancelled=1, cancelled_at=%s
                        WHERE order_id=%s AND user_id=%s AND is_deleted=0''',
                       (datetime.now(), datetime.now(), order_id, user_id))
        # Restore stock; reactivate product if it was draft
        cursor.execute("""UPDATE products p
            JOIN order_details od ON p.product_id=od.product_id
            SET p.stock_quantity=p.stock_quantity + od.quantity,
                p.status=CASE WHEN p.status='draft' THEN 'active' ELSE p.status END
            WHERE od.order_id=%s
        """, (order_id,))
        mysql.connection.commit()
        return 'ok', None
    finally:
        cursor.close()


# ─── Reviews ──────────────────────────────────────────────────────────────────

def submit_product_review(user_id, product_id, rating, comment):
    """
    Inserts a new pending review.
    Returns 'missing_fields', 'already_exists', or 'ok'.
    """
    if not rating or not comment:
        return 'missing_fields'
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    try:
        cursor.execute('SELECT review_id FROM product_reviews WHERE product_id=%s AND user_id=%s',
                       (product_id, user_id))
        if cursor.fetchone():
            return 'already_exists'
        cursor.execute('''INSERT INTO product_reviews
                (product_id, user_id, rating, comment, status, created_at)
            VALUES(%s, %s, %s, %s, %s, %s)''',
            (product_id, user_id, rating, comment, 'pending', datetime.now()))
        mysql.connection.commit()
        return 'ok'
    finally:
        cursor.close()


def get_my_reviews(user_id):
    """Returns all non-deleted reviews by user with product image."""
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    try:
        cursor.execute('''SELECT r.review_id, r.user_id, r.rating, r.comment,
                r.created_at, r.status,
                p.product_id, p.title, pi.image_url
            FROM product_reviews r
            JOIN products p ON r.product_id=p.product_id
            LEFT JOIN product_images pi ON p.product_id=pi.product_id AND pi.is_active=1
            WHERE r.user_id=%s AND r.is_deleted=0
            ORDER BY r.created_at DESC
        ''', (user_id,))
        return cursor.fetchall()
    finally:
        cursor.close()


def update_product_review(user_id, review_id, rating, comment):
    """Updates rating and comment for a user's own review."""
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    try:
        cursor.execute('''UPDATE product_reviews SET rating=%s, comment=%s
                        WHERE user_id=%s AND review_id=%s''',
                       (rating, comment, user_id, review_id))
        mysql.connection.commit()
    finally:
        cursor.close()


def delete_product_review(user_id, review_id):
    """Soft deletes a user's review."""
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    try:
        cursor.execute('UPDATE product_reviews SET is_deleted=1 WHERE review_id=%s AND user_id=%s',
                       (review_id, user_id))
        mysql.connection.commit()
    finally:
        cursor.close()


# ─── Returns ──────────────────────────────────────────────────────────────────

def submit_order_return(order_id, reason):
    """Inserts a new order return request."""
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    try:
        cursor.execute('''INSERT INTO order_returns(order_id, reason, status, requested_at)
                    VALUES(%s, %s, %s, %s)''',
                       (order_id, reason, 'requested', datetime.now()))
        mysql.connection.commit()
    finally:
        cursor.close()


def submit_item_return(order_detail_id, reason):
    """
    Inserts a return for a specific order item.
    BUG FIX: Returns False if order_detail_id not found (prevents NoneType crash).
    Returns True on success.
    """
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    try:
        cursor.execute('SELECT order_id FROM order_details WHERE order_detail_id=%s',
                       (order_detail_id,))
        row = cursor.fetchone()
        if not row:
            return False
        cursor.execute('''INSERT INTO order_item_returns
                (order_id, order_detail_id, reason, status, requested_at, resolved_at)
            VALUES(%s, %s, %s, %s, %s, %s)''',
            (row['order_id'], order_detail_id, reason, 'requested',
             datetime.now(), datetime.now()))
        mysql.connection.commit()
        return True
    finally:
        cursor.close()


def get_my_returns(user_id):
    """Returns all active (non-cancelled) return requests for user's orders."""
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    try:
        cursor.execute('''SELECT o.order_id, o.order_number, o.status AS order_status,
                o.total_amount, o.shipping_address, o.ordered_at,
                o.discount_amount, o.promo_code, o.subtotal,
                od.product_amount, od.quantity, od.subtotal AS item_subtotal,
                op.payment_method, op.status AS payment_status,
                orr.reason AS return_reason,
                orr.requested_at AS return_date,
                orr.status AS return_status,
                p.title AS product_title,
                pi.image_url
            FROM order_returns orr
            JOIN orders o ON orr.order_id=o.order_id
            JOIN order_payments op ON o.order_id=op.order_id
            JOIN order_details od ON o.order_id=od.order_id
            JOIN products p ON od.product_id=p.product_id
            JOIN product_images pi ON od.product_id=pi.product_id AND pi.is_active=1
            WHERE o.is_deleted=0 AND orr.is_cancelled=0 AND o.user_id=%s
        ''', (user_id,))
        return cursor.fetchall()
    finally:
        cursor.close()


def cancel_return_request(order_id, reason):
    """Marks an order return as cancelled with updated reason."""
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    try:
        cursor.execute('''UPDATE order_returns SET reason=%s, is_cancelled=1, requested_at=%s
                        WHERE order_id=%s''',
                       (reason, datetime.now(), order_id))
        mysql.connection.commit()
    finally:
        cursor.close()


def get_my_cancellations(user_id):
    """Returns all cancelled orders with product and payment details."""
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    try:
        cursor.execute('''SELECT o.order_id, o.order_number, o.status AS order_status,
                o.total_amount, o.shipping_address, o.ordered_at,
                o.discount_amount, o.promo_code, o.subtotal,
                od.product_amount, od.quantity, od.subtotal AS item_subtotal,
                o.cancelled_at AS cancellation_date,
                op.payment_method, op.status AS payment_status,
                p.title AS product_title,
                pi.image_url
            FROM orders o
            JOIN order_payments op ON o.order_id=op.order_id
            JOIN order_details od ON o.order_id=od.order_id
            JOIN products p ON od.product_id=p.product_id
            JOIN product_images pi ON od.product_id=pi.product_id AND pi.is_active=1
            WHERE o.is_deleted=0 AND o.user_id=%s AND o.is_cancelled=1
        ''', (user_id,))
        return cursor.fetchall()
    finally:
        cursor.close()