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

# Set time zone
IST = pytz.timezone('Asia/Kolkata')

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'a3f1b0c7d9e4f8a1b2c3d4e5f6a7b8c9'

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///default.db'
app.config['SQLALCHEMY_BINDS'] = {
    'users': 'sqlite:///users.db',
    'login_logs': 'sqlite:///login_logs.db'
}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# JWT Configuration
app.config['JWT_SECRET_KEY'] = 'My@Sec123Key'
app.config['JWT_TOKEN_LOCATION'] = ['cookies'] 
app.config['JWT_COOKIE_SECURE'] = False
app.config['JWT_COOKIE_CSRF_PROTECT'] = False 
jwt = JWTManager(app)

# Initialize Extensions
db.init_app(app)

# Load environment variables
load_dotenv(r'final_year_project\credentials.env')

# Email Credentials
EMAIL_USER = os.getenv('EMAIL_USER')
EMAIL_PASS = os.getenv('EMAIL_PASS')

# Create Database Tables
with app.app_context():
    db.create_all()

# Initialize SocketIO
socketio.init_app(app)

# Register Blueprints
from routes import routes_bp
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(routes_bp)

# SocketIO event handlers
@socketio.on('connect', namespace='/notifications')
def handle_notification_connect():
    print('Doctor connected to notifications')

@socketio.on('join', namespace='/chat')
def on_join(data):
    room = data['room']
    join_room(room)
    emit('message', 'Someone joined the room.', to=room)

@socketio.on('send_message', namespace='/chat')
def handle_message(data):
    room = data['room']
    msg = data['message']
    emit('message', msg, to=room)

# Route to home
@app.route('/')
def home():
    session.clear()
    response = make_response(redirect(url_for('home')))
    response.set_cookie('session', '', expires=0)
    response.set_cookie('auth_token', '', expires=0)
    return render_template('index.html')

# Route to contact page
@app.route('/contact')
def contact():
    return render_template('contact.html')

# Route to send email from contact form
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
    except Exception as e:
        flash('Failed to send message. Please try again later.', 'danger')

    return redirect(url_for('contact'))

# Route to logout
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
    
    session.pop('first_attempt_failed', None)
    session.clear()
    flash("You have been logged out.", "info")
    response = make_response(redirect(url_for('home')))
    unset_jwt_cookies(response)
    return redirect(url_for('home'))

# Main entry point for running the app with socketio
if __name__ == '__main__':
    socketio.run(app, debug=True)
