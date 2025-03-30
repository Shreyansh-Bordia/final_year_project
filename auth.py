# from flask import Blueprint, request, jsonify, render_template, session, redirect, url_for, flash
# from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
# from werkzeug.security import generate_password_hash, check_password_hash
# from models import db, User
# import datetime
# from models import db, User, Patient, Doctor, Admin

# auth_bp = Blueprint('auth', __name__)

# @auth_bp.route('/login', methods=['POST'])
# def login():
#     data = request.json
#     username = data.get('username')
#     password = data.get('password')

#     user = User.query.filter_by(username=username).first()

#     if user and user.check_password(password):
#         access_token = create_access_token(identity={'username': username, 'role': user.role}, expires_delta=datetime.timedelta(hours=1))
#         return jsonify(access_token=access_token, role=user.role), 200

#     return jsonify({"error": "Invalid credentials"}), 401



# @auth_bp.route('/signup', methods=['POST'])
# def signup():
#     data = request.json
#     username = data.get('username')
#     password = data.get('password')
#     role = data.get('role')
#     email = data.get('email')
#     phone = data.get('phone')

#     # Role-specific fields
#     age = data.get('age')  # For patient
#     medical_history = data.get('medical_history')  
#     specialization = data.get('specialization')  # For doctor
#     license_number = data.get('license_number')
#     department = data.get('department')  # For admin

#     # Check if username already exists
#     if User.query.filter_by(username=username).first():
#         return jsonify({"error": "User already exists"}), 400

#     # Create new user
#     new_user = User(username=username, email=email, phone=phone, role=role)
#     new_user.set_password(password)
#     db.session.add(new_user)
#     db.session.commit()

#     # Create role-specific record
#     if role == 'patient':
#         new_patient = Patient(user_id=new_user.id, age=age, medical_history=medical_history)
#         db.session.add(new_patient)

#     elif role == 'doctor':
#         new_doctor = Doctor(user_id=new_user.id, specialization=specialization, license_number=license_number)
#         db.session.add(new_doctor)

#     elif role == 'admin':
#         new_admin = Admin(user_id=new_user.id, department=department)
#         db.session.add(new_admin)

#     db.session.commit()

#     # Generate JWT token
#     access_token = create_access_token(identity={'username': username, 'role': role}, expires_delta=datetime.timedelta(hours=1))
    
#     return jsonify(message="Signup successful!", access_token=access_token), 201






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
    age = data.get('age')
    medical_history = data.get('medical_history')
    specialization = data.get('specialization')
    license_number = data.get('license_number')
    department = data.get('department')

    # if User.query.filter_by(username=username).first():
    #     flash("User already exists. Please log in.", "danger")
    #     return redirect(url_for('auth.login', role=role))

    new_user = User(username=username, email=email, phone=phone, role=role)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()

    if role == 'patient':
        new_patient = Patient(user_id=new_user.id, age=age, medical_history=medical_history)
        db.session.add(new_patient)
    elif role == 'doctor':
        new_doctor = Doctor(user_id=new_user.id, specialization=specialization, license_number=license_number)
        db.session.add(new_doctor)
    elif role == 'admin':
        new_admin = Admin(user_id=new_user.id, department=department)
        db.session.add(new_admin)

    db.session.commit()

    flash("Signup successful! Please log in.", "success")
    return redirect(url_for('auth.login', role=role))
