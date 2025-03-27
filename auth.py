from flask import Blueprint, request, jsonify, render_template, session, redirect, url_for, flash
from flask_jwt_extended import create_access_token
import datetime

auth_bp = Blueprint('auth', __name__)

# Dummy User Data
users = {
    'patient': {'username': 'patient', 'password': 'pass123'},
    'doctor': {'username': 'doctor', 'password': 'doc123'},
    'admin': {'username': 'admin', 'password': 'admin123'}
}

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    role = request.args.get('role', '')

    if request.method == 'GET':
        return render_template('login.html', role=role)  

    if request.content_type == 'application/json':  
        data = request.json
        username = data.get('username')
        password = data.get('password')
    else:
        username = request.form['username']
        password = request.form['password']

    for user_role, user in users.items():
        if user['username'] == username and user['password'] == password:
            access_token = create_access_token(identity={'username': username, 'role': user_role}, expires_delta=datetime.timedelta(hours=1))

            if request.content_type == 'application/json':
                return jsonify(access_token=access_token, role=user_role), 200

            session['role'] = user_role
            return redirect(url_for(f'routes.{user_role}_dashboard'))  # 🔥 FIX HERE

    if request.content_type == 'application/json':
        return jsonify({"error": "Invalid credentials"}), 401
    else:
        flash('Invalid credentials. Please try again.')
        return redirect(url_for('auth.login', role=role))  # 🔥 FIX HERE



@auth_bp.route('/signup', methods=['POST'])
def signup():
    data = request.json
    role = data.get('role', 'patient')
    username = data.get('username')
    password = data.get('password')
    name = data.get('name')
    email = data.get('email')
    phone = data.get('phone')

    # Check if user already exists
    if any(user['username'] == username for user in users.values()):
        return jsonify({"error": "User already exists. Please log in."}), 400

    users[role] = {
        'username': username,
        'password': password,
        'name': name,
        'email': email,
        'phone': phone
    }

    access_token = create_access_token(identity={'username': username, 'role': role}, expires_delta=datetime.timedelta(hours=1))
    return jsonify(message="Signup successful!", access_token=access_token), 201
