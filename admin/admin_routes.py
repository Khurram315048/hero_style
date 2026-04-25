from flask import render_template,request,flash,redirect,url_for,session
from werkzeug.security import generate_password_hash,check_password_hash
from utils.auth import login_required
import datetime 
from datetime import datetime
from admin import admin_bp
from utils.db import mysql


@admin_bp.route('/admin_dashboard')
def admin_dashboard():
    return render_template('admin_dashboard.htm')