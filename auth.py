from flask import Blueprint, make_response, request, jsonify, session, render_template, redirect, url_for, flash
from flask_jwt_extended import create_access_token, set_access_cookies, unset_jwt_cookies
from werkzeug.security import generate_password_hash
from models import db, User, Patient, Doctor, Admin, LoginLog
import datetime
from datetime import timezone
import pytz

IST = pytz.timezone('Asia/Kolkata')

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    role = request.args.get('role')

    if request.method == 'GET':
        response = make_response(render_template('login.html', role=role))
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response

    data = request.get_json() if request.is_json else request.form
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()

    if 'first_attempt_failed' not in session:
        session['first_attempt_failed'] = True
        flash("Invalid credentials. Please try again.", "danger")
        return redirect(url_for('auth.login', role=role))

    session.pop('first_attempt_failed', None)
    
    if user and user.check_password(password):
        access_token = create_access_token(identity={'username': username, 'role': user.role}, expires_delta=datetime.timedelta(hours=1))
        
        # Logging login attempt
        log_entry = LoginLog(
            ip_address=request.remote_addr,
            protocol_type=request.scheme.upper(),
            service="HTTP",
            src_bytes=request.content_length if request.content_length else 0,
            dst_bytes=0,
            flag="SF",
            user_agent=request.headers.get('User-Agent')
        )
        db.session.add(log_entry)
        db.session.commit()

        # Store token in session
        session['role'] = user.role
        session['username'] = user.username
        session['user_id'] = user.id
        session['start_time'] = datetime.datetime.now(timezone.utc).isoformat()

        # Set token as an HTTP-only cookie for security
        response = redirect(url_for(f'routes.{user.role}_dashboard'))
        set_access_cookies(response, access_token)

        return response

    flash("Invalid credentials. Please try again.", "danger")
    return redirect(url_for('auth.login', role=role))

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    role = request.args.get('role', 'patient')

    if request.method == 'GET':
        response = make_response(render_template('signup.html', role=role))
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response

    data = request.get_json() if request.is_json else request.form

    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    phone = data.get('phone')
    role = data.get('role')
    name = data.get('name')
    state = data.get('state')
    age = data.get('age')
    address = data.get('address')
    degree = data.get('degree')
    specialization = data.get('position')

    if User.query.filter_by(username=username).first():
        flash("User already exists. Please log in.", "danger")
        return redirect(url_for('auth.login', role=role))

    new_user = User(name=name, username=username, email=email, phone=phone, state=state, role=role)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()

    if role == 'patient':
        new_patient = Patient(user_id=new_user.id, age=age, address=address)
        db.session.add(new_patient)
    elif role == 'doctor':
        new_doctor = Doctor(user_id=new_user.id, specialization=specialization, degree=degree)
        db.session.add(new_doctor)
    elif role == 'admin':
        new_admin = Admin(user_id=new_user.id)
        db.session.add(new_admin)

    db.session.commit()

    flash("Signup successful! Please log in.", "success")
    return redirect(url_for('auth.login', role=role))
