from flask import Blueprint, request, jsonify, render_template, session, redirect, url_for, flash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User
import datetime
from models import db, User, Patient, Doctor, Admin

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()

    if user and user.check_password(password):
        access_token = create_access_token(identity={'username': username, 'role': user.role}, expires_delta=datetime.timedelta(hours=1))
        return jsonify(access_token=access_token, role=user.role), 200

    return jsonify({"error": "Invalid credentials"}), 401



@auth_bp.route('/signup', methods=['POST'])
def signup():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    role = data.get('role')
    email = data.get('email')
    phone = data.get('phone')

    # Role-specific fields
    age = data.get('age')  # For patient
    medical_history = data.get('medical_history')  
    specialization = data.get('specialization')  # For doctor
    license_number = data.get('license_number')
    department = data.get('department')  # For admin

    # Check if username already exists
    if User.query.filter_by(username=username).first():
        return jsonify({"error": "User already exists"}), 400

    # Create new user
    new_user = User(username=username, email=email, phone=phone, role=role)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()

    # Create role-specific record
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

    # Generate JWT token
    access_token = create_access_token(identity={'username': username, 'role': role}, expires_delta=datetime.timedelta(hours=1))
    
    return jsonify(message="Signup successful!", access_token=access_token), 201
