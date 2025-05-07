from flask import Blueprint, flash, render_template, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, Patient, Doctor, Admin, Appointment
from extensions import socketio 

routes_bp = Blueprint('routes', __name__)

def check_user_role(required_role):
    user_identity = get_jwt_identity()
    user = User.query.filter_by(username=user_identity['username']).first()
    
    if not user or user.role != required_role:
        return None
    return user

@routes_bp.route('/patient_dashboard')
@jwt_required()
def patient_dashboard():
    user = check_user_role('patient')
    if not user:
        return "Unauthorized", 403

    patient = Patient.query.filter_by(user_id=user.id).first()
    return render_template('patient_dashboard.html')

@routes_bp.route('/doctor_dashboard')
@jwt_required()
def doctor_dashboard():
    user = check_user_role('doctor')
    if not user:
        return "Unauthorized", 403

    doctor = Doctor.query.filter_by(user_id=user.id).first()
    return render_template('doctor_dashboard.html')

@routes_bp.route('/admin_dashboard')
@jwt_required()
def admin_dashboard():
    user = check_user_role('admin')
    if not user:
        return "Unauthorized", 403

    admin = Admin.query.filter_by(user_id=user.id).first()
    return render_template('admin_dashboard.html')

@routes_bp.route('/create_appointment', methods=['POST'])
@jwt_required()
def create_appointment():
    user_identity = get_jwt_identity()
    user = User.query.filter_by(username=user_identity['username']).first()

    if not user or user.role != 'patient':
        flash('Unauthorized access', 'danger')
        return render_template('patient_dashboard.html')

    patient = Patient.query.filter_by(user_id=user.id).first()
    if not patient:
        flash('Patient record not found.', 'danger')
        return render_template('patient_dashboard.html')

    specialization = request.form.get('specialization')
    description = request.form.get('description')

    if not specialization or not description:
        flash('All fields are required.', 'warning')
        return render_template('patient_dashboard.html')

    appointment = Appointment(
        specialisation=specialization,
        illness=description,
        patient_id=patient.id
    )
    db.session.add(appointment)
    db.session.commit()

    import uuid
    room_id = str(uuid.uuid4())

    socketio.emit('new_appointment', {
        'specialisation': specialization,
        'description': description,
        'patient_name': user.username,
        'room_id': room_id
    }, namespace='/notifications')

    return render_template('chat_room.html', room_id=room_id, username=user.username)


@routes_bp.route('/chat/<room_id>')
@jwt_required()
def chat_room(room_id):
    user = get_jwt_identity()
    return render_template('chat_room.html', room_id=room_id, username=user['username'])

