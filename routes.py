from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_jwt_extended import jwt_required, get_jwt_identity
import os
from models import db, User
from models import db, User, Patient, Doctor, Admin

routes_bp = Blueprint('routes', __name__)
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@routes_bp.route('/patient_dashboard')
@jwt_required()
def patient_dashboard():
    user_identity = get_jwt_identity()
    user = User.query.filter_by(username=user_identity['username']).first()

    if user.role != 'patient':
        return "Unauthorized", 403

    patient = Patient.query.filter_by(user_id=user.id).first()
    return render_template('patient_dashboard.html', patient=patient)

@routes_bp.route('/doctor_dashboard')
@jwt_required()
def doctor_dashboard():
    user_identity = get_jwt_identity()
    user = User.query.filter_by(username=user_identity['username']).first()

    if user.role != 'doctor':
        return "Unauthorized", 403

    doctor = Doctor.query.filter_by(user_id=user.id).first()
    return render_template('doctor_dashboard.html', doctor=doctor)

@routes_bp.route('/admin_dashboard')
@jwt_required()
def admin_dashboard():
    user_identity = get_jwt_identity()
    user = User.query.filter_by(username=user_identity['username']).first()

    if user.role != 'admin':
        return "Unauthorized", 403

    admin = Admin.query.filter_by(user_id=user.id).first()
    return render_template('admin_dashboard.html', admin=admin)
