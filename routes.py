from flask import Blueprint, flash, redirect, render_template, request, url_for, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, Patient, Doctor, Admin, Appointment
from extensions import socketio 
import uuid
from datetime import datetime, timedelta

routes_bp = Blueprint('routes', __name__)

doctor_availability = {}

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
    return render_template('patient_dashboard.html')

@routes_bp.route('/doctor_dashboard')
@jwt_required()
def doctor_dashboard():
    user = check_user_role('doctor')
    if not user:
        return "Unauthorized", 403
    doctor = Doctor.query.filter_by(user_id=user.id).first()
    return render_template('doctor_dashboard.html', specialization=doctor.specialization)

@routes_bp.route('/admin_dashboard')
@jwt_required()
def admin_dashboard():
    user = check_user_role('admin')
    if not user:
        return "Unauthorized", 403
    return redirect(url_for('ids.index'))

@routes_bp.route('/create_appointment', methods=['POST'])
@jwt_required()
def create_appointment():
    user_identity = get_jwt_identity()
    user = User.query.filter_by(username=user_identity['username']).first()
    if not user or user.role != 'patient':
        flash('Unauthorized access', 'danger')
        return render_template('patient_dashboard.html')

    patient = Patient.query.filter_by(user_id=user.id).first()
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

    doctors = Doctor.query.filter_by(specialization=specialization).all()
    doctor_usernames = [doc.user.username for doc in doctors]

    room_id = str(uuid.uuid4())

    socketio.emit('new_appointment', {
        'specialisation': specialization,
        'description': description,
        'patient_name': user.username,
        'doctor_usernames': doctor_usernames,
        'room_id': room_id
    }, namespace='/notifications')

    return render_template('chat_room.html', room_id=room_id, role=user.role, username=user.username)

@routes_bp.route('/chat/<room_id>')
@jwt_required()
def chat_room(room_id):
    user = get_jwt_identity()
    return render_template(
        'chat_room.html',
        room_id=room_id,
        username=user.get('username'),
        role=user.get('role')
    )

# NEW: Doctor calendar view
@routes_bp.route('/appointment')
@jwt_required()
def appointment_calendar():
    user = check_user_role('doctor')
    if not user:
        return "Unauthorized", 403
    return render_template('doctor_appointments.html')

# NEW: API to fetch appointments and availability
@routes_bp.route('/api/appointments')
@jwt_required()
def get_appointments():
    user_identity = get_jwt_identity()
    user = User.query.filter_by(username=user_identity['username']).first()
    doctor = Doctor.query.filter_by(user_id=user.id).first()

    events = []

    # Appointments
    appointments = Appointment.query.filter_by(doctor_id=doctor.id).all()
    for appt in appointments:
        patient = Patient.query.get(appt.patient_id)
        start = appt.timestamp or datetime.now()
        end = start + (appt.duration or timedelta(minutes=30))
        events.append({
            "title": f"Appt with {patient.user.username}",
            "start": start.isoformat(),
            "end": end.isoformat(),
            "color": "#007bff"  # blue
        })

    # Availability
    if doctor.id in doctor_availability:
        for slot in doctor_availability[doctor.id]:
            events.append({
                "title": "Available Slot",
                "start": slot['start'],
                "end": slot['end'],
                "color": "#28a745"  # green
            })

    return jsonify(events)

# API to set availability
@routes_bp.route('/api/set_availability', methods=['POST'])
@jwt_required()
def set_availability():
    user_identity = get_jwt_identity()
    user = User.query.filter_by(username=user_identity['username']).first()
    doctor = Doctor.query.filter_by(user_id=user.id).first()

    data = request.get_json()
    start = data.get('start')
    end = data.get('end')

    try:
        # Validate ISO 8601 datetime
        datetime.fromisoformat(start)
        datetime.fromisoformat(end)
    except Exception:
        return jsonify({"error": "Invalid datetime format"}), 400

    if doctor.id not in doctor_availability:
        doctor_availability[doctor.id] = []

    doctor_availability[doctor.id].append({
        "start": start,
        "end": end
    })

    return jsonify({"message": "Availability added"}), 200

# API to clear availability
@routes_bp.route('/api/reset_availability', methods=['DELETE'])
@jwt_required()
def reset_availability():
    user_identity = get_jwt_identity()
    user = User.query.filter_by(username=user_identity['username']).first()
    doctor = Doctor.query.filter_by(user_id=user.id).first()

    doctor_availability[doctor.id] = []

    return jsonify({"message": "Availability reset"}), 200


@routes_bp.route('/medical_history')
@jwt_required()
def medical_history():
    user = check_user_role('patient')
    if not user:
        return "Unauthorized", 403

    records = [
        {"doctor": "Dr. James Jacob", "specialist": "General Physician", "prescription": "Prescription.pdf", "remarks": "Recovered well", "next_date": "2025-06-01", "tests": "Blood Test"},
        {"doctor": "Dr. Rajiv Vyas", "specialist": "Cardiologist", "prescription": "Prescription.pdf", "remarks": "Continue medication", "next_date": None, "tests": None},
        {"doctor": "Dr. Meera Nair", "specialist": "Orthopedologist", "prescription": "Prescription.pdf", "remarks": "Requires physiotherapy", "next_date": "2025-06-15", "tests": None},
        {"doctor": "Dr. Nikhil Shah", "specialist": "Dermatologist", "prescription": "Prescription.pdf", "remarks": "Apply ointment", "next_date": None, "tests": "Allergy Test"},
        {"doctor": "Dr. James Jacob", "specialist": "General Physician", "prescription": "Prescription.pdf", "remarks": "Healthy", "next_date": None, "tests": None},
    ]

    return render_template('patient_history.html', records=records)


@routes_bp.route('/patient_history')
@jwt_required()
def patient_history():
    user = check_user_role('doctor')
    if not user:
        return "Unauthorized", 403

    patients = [
        {"name": "John Doe", "illness": "Flu", "prescription": "Prescription.pdf", "remarks": "Recovered well", "next_date": "2025-06-05", "tests": "Blood Test"},
        {"name": "Mary Smith", "illness": "Diabetes", "prescription": "Prescription.pdf", "remarks": "Monitor sugar levels", "next_date": None, "tests": None},
        {"name": "Alice Johnson", "illness": "Fracture", "prescription": "Prescription.pdf", "remarks": "Requires physiotherapy", "next_date": "2025-06-20", "tests": None},
        {"name": "Bob Lee", "illness": "Skin Allergy", "prescription": "Prescription.pdf", "remarks": "Apply ointment", "next_date": None, "tests": "Allergy Test"},
        {"name": "Charlie Brown", "illness": "Cold", "prescription": "Prescription.pdf", "remarks": "Healthy", "next_date": None, "tests": None},
    ]

    return render_template('doctor_history.html', patients=patients)
