from flask import Flask, jsonify, make_response, render_template, request, redirect, url_for, session, flash
from flask_jwt_extended import JWTManager, unset_jwt_cookies
from models import Appointment, db, User, LoginLog
from auth import auth_bp
import os
import smtplib
from email.message import EmailMessage
from datetime import datetime, timezone
import pytz
from dotenv import load_dotenv
from flask_socketio import emit, join_room
from extensions import socketio 
from extensions import mail

IST = pytz.timezone('Asia/Kolkata')

app = Flask(__name__)
app.secret_key = 'a3f1b0c7d9e4f8a1b2c3d4e5f6a7b8c9'

from ids import ids_bp
app.register_blueprint(ids_bp)
load_dotenv(r'final_year_project\credentials.env')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///default.db'
app.config['SQLALCHEMY_BINDS'] = {
    'users': 'sqlite:///users.db',
    'login_logs': 'sqlite:///login_logs.db'
}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['JWT_SECRET_KEY'] = 'My@Sec123Key'
app.config['JWT_TOKEN_LOCATION'] = ['cookies'] 
app.config['JWT_COOKIE_SECURE'] = False
app.config['JWT_COOKIE_CSRF_PROTECT'] = False 

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_DEFAULT_SENDER'] = 'shreyansh.is21@bmsce.ac.in'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')

mail.init_app(app)
jwt = JWTManager(app)

db.init_app(app)

EMAIL_USER = os.getenv('EMAIL_USER')
EMAIL_PASS = os.getenv('EMAIL_PASS')

with app.app_context():
    db.create_all()

socketio.init_app(app)

from routes import routes_bp
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(routes_bp)

@socketio.on('connect', namespace='/notifications')
def handle_notification_connect():
    print('Doctor connected to notifications')

@socketio.on('join', namespace='/chat')
def on_join(data):
    room = data['room']
    role = data.get('role', 'User')
    username = data.get('username', 'Someone')
    join_room(room)

    if role.lower() == 'doctor':
        message = f"👨‍⚕️ Dr. {username} (doctor) joined the room."
    elif role.lower() == 'patient':
        message = f"🙎‍♂️ {username} (patient) joined the room."
    else:
        message = f"{username} joined the room."

    emit('message', message, to=room)


@socketio.on('send_message', namespace='/chat')
def handle_send_message(data):
    room = data.get('room')
    msg_type = data.get('type', 'text')
    role = data.get('role', 'patient')  # Default to 'patient' if not provided

    if msg_type == 'text':
        message = data.get('message')
        emit('message', {
            'type': 'text',
            'message': message,
            'role': role
        }, to=room)

    elif msg_type == 'file':
        filename = data.get('message')
        file_data = data.get('fileData')
        file_type = data.get('fileType')
        emit('message', {
            'type': 'file',
            'message': filename,
            'fileUrl': file_data,
            'fileType': file_type,
            'role': role
        }, to=room)


@app.route('/')
def home():
    session.clear()
    response = make_response(render_template('index.html'))
    response.set_cookie('session', '', expires=0)
    response.set_cookie('auth_token', '', expires=0)
    return response

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/send_mail', methods=['POST'])
def send_mail():
    name = request.form['name']
    phone = request.form['phone']
    message = request.form['message']
    email_body = f"Name: {name}\nPhone: {phone}\nMessage: {message}"

    try:
        msg = EmailMessage()
        msg.set_content(email_body)
        msg['Subject'] = 'New Contact Form Submission'
        msg['From'] = EMAIL_USER
        msg['To'] = 'shreyansh.is21@bmsce.ac.in'

        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASS)
            server.send_message(msg)

        flash('Message sent successfully!', 'success')
    except Exception:
        flash('Failed to send message. Please try again later.', 'danger')

    return redirect(url_for('contact'))

@app.route('/logout')
def logout():
    if 'start_time' in session:
        start_time = session.pop('start_time', None)
        if start_time:
            if isinstance(start_time, str):
                start_time = datetime.fromisoformat(start_time)
            duration = (datetime.now(timezone.utc) - start_time).seconds
            latest_entry = LoginLog.query.order_by(LoginLog.timestamp.desc()).first()
            if latest_entry:
                latest_entry.duration = duration
                db.session.commit()

    session.clear()
    flash("You have been logged out.", "info")
    response = make_response(redirect(url_for('home')))
    unset_jwt_cookies(response)
    return response

if __name__ == '__main__':
    socketio.run(app, debug=True)
