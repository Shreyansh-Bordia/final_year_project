from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_jwt_extended import jwt_required, get_jwt_identity
import os
import json

routes_bp = Blueprint('routes', __name__)
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@routes_bp.route('/')
def home():
    return render_template('index.html')

@routes_bp.route('/patient_dashboard')
@jwt_required()
def patient_dashboard():
    user = (get_jwt_identity())  # Convert JSON string back to dictionary
    if user['role'] != 'patient':
        return "Unauthorized", 403
    return render_template('patient_dashboard.html')

@routes_bp.route('/doctor_dashboard')
@jwt_required()
def doctor_dashboard():
    user = (get_jwt_identity())
    if user['role'] != 'doctor':
        return "Unauthorized", 403
    return render_template('doctor_dashboard.html')

@routes_bp.route('/admin_dashboard')
@jwt_required()
def admin_dashboard():
    user = (get_jwt_identity())
    if user['role'] != 'admin':
        return "Unauthorized", 403
    return render_template('admin_dashboard.html')

@routes_bp.route('/upload', methods=['POST'])
@jwt_required()
def upload_file():
    if 'file' not in request.files:
        flash('No file uploaded.', 'danger')
        return redirect(request.referrer)

    file = request.files['file']
    if file.filename == '':
        flash('No selected file.', 'danger')
        return redirect(request.referrer)

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)
    flash('File uploaded successfully.', 'success')
    return redirect(request.referrer)