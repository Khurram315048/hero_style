from flask import flash, redirect, render_template, request, session, url_for

from users import user_bp
from users.user_models import (
    cancel_return_request, cancel_user_order, delete_product_review,
    get_dashboard_data, get_my_cancellations, get_my_returns, get_my_reviews,
    get_order_details, get_user_options, get_user_orders, get_user_profile,
    get_wishlist, login_user, register_user, remove_wishlist_item,
    send_reset_otp, submit_item_return, submit_order_return,
    submit_product_review, update_password, update_product_review,
    update_user_profile, verify_reset_otp
)
from utils.auth import login_required
from utils.limiter import limiter


# ─── Auth ─────────────────────────────────────────────────────────────────────

@user_bp.route('/user_login', methods=['GET', 'POST'])
@limiter.limit("6 per 15 minutes")
def user_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        result = login_user(email, password)

        if result is None:
            flash('Account does not exist', 'danger')
            return redirect(url_for('users.user_signup'))
        if result is False:
            session['toast'] = 'Password does not match!'
            return redirect(url_for('users.user_login'))

        session['user_id'] = result['user_id']
        session['role'] = 'user'
        session.permanent = True if request.form.get('remember_me') else False
        session['toast'] = 'Welcome back!'
        return redirect(url_for('users.user_dashboard'))

    return render_template('user_login.htm')


@user_bp.route('/user_signup', methods=['GET', 'POST'])
@limiter.limit("10 per hour")
def user_signup():
    if request.method == 'POST':
        status, msg = register_user(
            request.form.get('first_name'),
            request.form.get('last_name'),
            request.form.get('email'),
            request.form.get('password')
        )
        if status == 'weak_password':
            flash(msg, 'danger')
            return redirect(url_for('users.user_signup'))
        if status == 'email_exists':
            flash('Email Already Exist', 'danger')
            return redirect(url_for('users.user_login'))

        flash('Registeration Successfull', 'success')
        return redirect(url_for('users.user_login'))

    return render_template('user_signup.htm')


@user_bp.route('/logout')
def logout():
    session.clear()
    session['toast'] = 'You have been logged out.'
    return redirect(url_for('homepage'))


# ─── Password Reset ───────────────────────────────────────────────────────────

@user_bp.route('/reset_password', methods=['GET', 'POST'])
@limiter.limit("5 per hour")
def reset_password():
    if request.method == 'POST' and request.form.get('step') == 'send_otp':
        from main import mail
        email = request.form.get('email', '').strip()
        sent = send_reset_otp(email, mail)
        if not sent:
            session['toast'] = 'Email not found!'
            return redirect(url_for('users.user_signup'))
        session['reset_email'] = email
        session['toast'] = 'OTP sent to your email!'
        return redirect(url_for('users.verify_otp'))

    return render_template('reset_password.htm')


@user_bp.route('/verify_otp', methods=['GET', 'POST'])
def verify_otp():
    email = session.get('reset_email')
    if not email:
        return redirect(url_for('users.reset_password'))

    if request.method == 'POST' and request.form.get('step') == 'verify':
        # BUG FIX: removed unused 'from main import mail' that was here
        otp_entered = request.form.get('otp', '').strip()
        if not verify_reset_otp(email, otp_entered):
            session['toast'] = 'Invalid or expired OTP!'
            return redirect(url_for('users.verify_otp'))
        session['otp_verified'] = True
        return redirect(url_for('users.set_new_password'))

    return render_template('verify_otp.htm', email=email)


@user_bp.route('/set_new_password', methods=['GET', 'POST'])
def set_new_password():
    email = session.get('reset_email')
    verified = session.get('otp_verified')
    if not email or not verified:
        return redirect(url_for('users.reset_password'))

    if request.method == 'POST':
        result = update_password(
            email,
            request.form.get('new_password', '').strip(),
            request.form.get('confirm_password', '').strip()
        )
        if result == 'mismatch':
            session['toast'] = 'Passwords do not match!'
            return redirect(url_for('users.set_new_password'))
        if result == 'too_short':
            session['toast'] = 'Password must be at least 8 characters!'
            return redirect(url_for('users.set_new_password'))

        session.pop('reset_email', None)
        session.pop('otp_verified', None)
        session['toast'] = 'Password updated successfully!'
        return redirect(url_for('users.user_login'))

    return render_template('set_new_password.htm')


# ─── User Options & Profile ───────────────────────────────────────────────────

@user_bp.route('/user_options', methods=['GET', 'POST'])
@login_required  # BUG FIX: missing decorator added
def user_options():
    user = get_user_options(session.get('user_id'))
    return render_template('user_options.htm', user=user)


@user_bp.route('/user_dashboard', methods=['GET', 'POST'])
@login_required
def user_dashboard():
    user_exist, latest_order = get_dashboard_data(session.get('user_id'))
    return render_template('user_dashboard.htm', user_exist=user_exist, latest_order=latest_order)


@user_bp.route('/user_profile', methods=['GET', 'POST'])
@login_required
def user_profile():
    user_id = session.get('user_id')
    if request.method == 'POST':
        update_user_profile(
            user_id,
            request.form.get('first_name'),
            request.form.get('last_name'),
            request.form.get('email')
        )
        session['toast'] = 'Profile Updated Successfully!'
        return redirect(url_for('users.user_profile'))

    user_details = get_user_profile(user_id)
    return render_template('user_profile.htm', user_details=user_details)


# ─── Wishlist ─────────────────────────────────────────────────────────────────

@user_bp.route('/user_wishlist', methods=['GET', 'POST'])
@login_required
def user_wishlist():
    products = get_wishlist(session.get('user_id'))
    return render_template('user_wishlist.htm', products=products)


@user_bp.route('/remove_from_the_list', methods=['POST'])
@login_required
def remove_from_the_list():
    # BUG FIX: removed redundant if request.method=='POST' (route is POST-only)
    remove_wishlist_item(session.get('user_id'), request.form.get('product_id'))
    session['toast'] = 'Item removed from wishlist!'
    return redirect(request.form.get('redirect_to', url_for('users.user_wishlist')))


# ─── Orders ───────────────────────────────────────────────────────────────────

@user_bp.route('/user_orders')
@login_required
def user_orders():
    orders = get_user_orders(session.get('user_id'))
    return render_template('user_orders.htm', orders=orders)


@user_bp.route('/order_details/<int:order_id>', methods=['GET'])
@login_required
def order_details(order_id):
    result = get_order_details(session.get('user_id'), order_id)
    if not result:
        session['toast'] = 'Order not found!'
        return redirect(url_for('users.user_orders'))
    order, order_items, payment = result
    return render_template('order_details.htm', order=order, order_items=order_items, payment=payment)


@user_bp.route('/cancel_order/<int:order_id>', methods=['POST'])
@login_required
def cancel_order(order_id):
    status, val = cancel_user_order(session.get('user_id'), order_id)
    if status == 'not_found':
        session['toast'] = 'Order not found or already deleted!'
    elif status == 'not_pending':
        session['toast'] = f'Cannot cancel an order that is already {val}!'
    else:
        session['toast'] = 'Order has been cancelled successfully!'
    return redirect(url_for('users.user_orders'))


# ─── Reviews ──────────────────────────────────────────────────────────────────

@user_bp.route('/submit_review/<int:product_id>', methods=['GET', 'POST'])
@login_required
def submit_review(product_id):
    result = submit_product_review(
        session.get('user_id'), product_id,
        request.form.get('rating'),
        request.form.get('comment')
    )
    if result == 'missing_fields':
        session['toast'] = 'Please provide both a rating and a comment.'
    elif result == 'already_exists':
        session['toast'] = 'Review Already Exist!'
    else:
        session['toast'] = 'Thank You! your review has been posted'
    return redirect(request.referrer)


@user_bp.route('/my_reviews', methods=['GET'])
@login_required
def my_reviews():
    # BUG FIX: removed redundant if not user_id check (@login_required handles it)
    reviews = get_my_reviews(session.get('user_id'))
    return render_template('my_reviews.htm', reviews=reviews)


@user_bp.route('/update_review/<int:review_id>', methods=['GET', 'POST'])
@login_required
def update_review(review_id):
    update_product_review(
        session.get('user_id'), review_id,
        request.form.get('rating'),
        request.form.get('comment')
    )
    session['toast'] = 'Thank You! For updating the product review'
    return redirect(url_for('users.my_reviews'))


@user_bp.route('/delete_review/<int:review_id>', methods=['GET', 'POST'])
@login_required
def delete_review(review_id):
    delete_product_review(session.get('user_id'), review_id)
    session['toast'] = 'Thank You! Review has been deleted successfully'
    return redirect(url_for('users.my_reviews'))


# ─── Returns & Cancellations ──────────────────────────────────────────────────

@user_bp.route('/return_order/<int:order_id>', methods=['GET', 'POST'])
@login_required
def return_order(order_id):
    submit_order_return(order_id, request.form.get('reason'))
    session['toast'] = 'Return request submitted successfully!'
    return redirect(url_for('users.user_orders'))


@user_bp.route('/return_items/<int:order_detail_id>', methods=['GET', 'POST'])
@login_required
def return_items(order_detail_id):
    # BUG FIX: model returns False if order_detail_id not found
    success = submit_item_return(order_detail_id, request.form.get('reason'))
    if not success:
        session['toast'] = 'Order item not found!'
    else:
        session['toast'] = 'Item return request submitted successfully!'
    return redirect(url_for('users.user_orders'))


@user_bp.route('/my_returns', methods=['GET', 'POST'])
@login_required
def my_returns():
    # BUG FIX: removed redundant if not user_id check
    return_details = get_my_returns(session.get('user_id'))
    return render_template('my_returns.htm', return_details=return_details)


@user_bp.route('/return_cancel/<int:order_id>', methods=['GET', 'POST'])
@login_required
def return_cancel(order_id):
    cancel_return_request(order_id, request.form.get('reason'))
    session['toast'] = 'Request Send Successfully!'
    return redirect(request.referrer)


@user_bp.route('/my_cancellations', methods=['GET', 'POST'])
@login_required
def my_cancellations():
    # BUG FIX: removed redundant if not user_id check
    cancel_details = get_my_cancellations(session.get('user_id'))
    return render_template('my_cancellations.htm', cancel_details=cancel_details)