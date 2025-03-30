# from flask import Flask, render_template, request, redirect, url_for, session, flash
# from flask_jwt_extended import JWTManager
# from models import db
# from auth import auth_bp
# from routes import routes_bp
# import os
# import smtplib
# from email.message import EmailMessage
# from flask_sqlalchemy import SQLAlchemy
# from datetime import datetime, timezone
# import pytz
# from dotenv import load_dotenv
# from functools import wraps

# IST = pytz.timezone('Asia/Kolkata')

# app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.config['JWT_SECRET_KEY'] = 'your-secret-key'

# db.init_app(app)
# jwt = JWTManager(app)

# app.register_blueprint(auth_bp, url_prefix='/auth')
# app.register_blueprint(routes_bp)
# load_dotenv(r'final_year_project\credentials.env')

# EMAIL_USER = os.getenv('EMAIL_USER')
# EMAIL_PASS = os.getenv('EMAIL_PASS')

# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///login_logs.db'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# db = SQLAlchemy(app)

# class LoginLog(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     timestamp = db.Column(db.DateTime, default=lambda: datetime.now(IST))
#     ip_address = db.Column(db.String(50))
#     protocol_type = db.Column(db.String(10))
#     service = db.Column(db.String(20))
#     src_bytes = db.Column(db.Integer)
#     dst_bytes = db.Column(db.Integer)
#     flag = db.Column(db.String(10))
#     user_agent = db.Column(db.String(200))
#     duration = db.Column(db.Integer, default=0)

#     def __repr__(self):
#         return f"<LoginLog {self.ip_address} - {self.timestamp}>"

# with app.app_context():
#     db.create_all()

# # Dummy User Data
# users = {
#     'patient': {'username': 'patient', 'password': 'pass123'},
#     'doctor': {'username': 'doctor', 'password': 'doc123'},
#     'admin': {'username': 'admin', 'password': 'admin123'}
# }

# # Home Page
# @app.route('/')
# def home():
#     return render_template('index.html')

# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     role = request.args.get('role')
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']

#         if role in users and users[role]['username'] == username and users[role]['password'] == password:
#             session['role'] = role

#             ip_address = request.remote_addr
#             user_agent = request.headers.get('User-Agent')
#             protocol_type = request.scheme.upper()
#             service = "HTTP"
#             src_bytes = request.content_length if request.content_length else 0
#             dst_bytes = 0
#             flag = "SF"
#             session['start_time'] = datetime.now(timezone.utc).isoformat() 

#             log_entry = LoginLog(
#                 ip_address=ip_address,
#                 protocol_type=protocol_type,
#                 service=service,
#                 src_bytes=src_bytes,
#                 dst_bytes=dst_bytes,
#                 flag=flag,
#                 user_agent=user_agent
#             )
#             db.session.add(log_entry)
#             db.session.commit()
#             return redirect(url_for(f'{role}_dashboard'))
#         else:
#             flash('Invalid credentials. Please try again.')
#             return redirect(url_for('login', role=role))
#     return render_template('login.html', role=role)

# # <$> Signup Route
# @app.route('/signup', methods=['GET', 'POST'])
# def signup():
#     role = request.args.get('role', 'patient')

#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
#         name = request.form['name']
#         email = request.form['email']
#         phone = request.form['phone']

#         for user in users[role]:
#             if user['username'] == username:
#                 flash('User already exists. Please log in.', 'danger')
#                 return redirect(url_for('login', role=role))

#         if role == 'patient':
#             home_address = request.form['home_address']
#             alt_contact = request.form.get('alt_contact', '') 
#             age = request.form['age']

#             users['patient'].append({
#                 'username': username,
#                 'password': password,
#                 'name': name,
#                 'email': email,
#                 'phone': phone,
#                 'home_address': home_address,
#                 'alt_contact': alt_contact,
#                 'age': age
#             })

#         elif role == 'doctor':
#             degree = request.form['degree']
#             prev_hospital = request.form['prev_hospital']
#             position = request.form['position']

#             users['doctor'].append({
#                 'username': username,
#                 'password': password,
#                 'name': name,
#                 'email': email,
#                 'phone': phone,
#                 'degree': degree,
#                 'prev_hospital': prev_hospital,
#                 'position': position
#             })

#         flash('Signup successful! Please log in.', 'success')
#         return redirect(url_for('login', role=role))

#     return render_template('signup.html', role=role)

# def role_required(role):
#     def decorator(f):
#         @wraps(f)
#         def decorated_function(*args, **kwargs):
#             if 'role' not in session or session['role'] != role:
#                 flash("Unauthorized access!!", "danger")
#                 return redirect(url_for(session['role'] + '_dashboard'))
#             return f(*args, **kwargs)
#         return decorated_function
#     return decorator

# @app.route('/patient_dashboard')
# @role_required('patient')
# def patient_dashboard():
#     return render_template('patient_dashboard.html')

# @app.route('/doctor_dashboard')
# @role_required('doctor')
# def doctor_dashboard():
#     return render_template('doctor_dashboard.html')

# @app.route('/admin_dashboard')
# @role_required('admin')
# def admin_dashboard():
#     return render_template('admin_dashboard.html')

# # File Upload Logic
# @app.route('/upload', methods=['POST'])
# def upload_file():
#     if 'file' not in request.files:
#         flash('No file uploaded.')
#         return redirect(request.referrer)

#     file = request.files['file']
#     if file.filename == '':
#         flash('No selected file.')
#         return redirect(request.referrer)

#     if file:
#         file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
#         file.save(file_path)
#         flash('File uploaded successfully.')
#         return redirect(request.referrer)
    
# @app.route('/contact')
# def contact():
#     return render_template('contact.html')

# @app.route('/send_mail', methods=['POST'])
# def send_mail():
#     name = request.form['name']
#     phone = request.form['phone']
#     message = request.form['message']

#     email_body = f"Name: {name}\nPhone: {phone}\nMessage: {message}"
    
#     try:
#         msg = EmailMessage()
#         msg.set_content(email_body)
#         msg['Subject'] = 'New Contact Form Submission'
#         msg['From'] = EMAIL_USER
#         msg['To'] = 'shreyansh.is21@bmsce.ac.in'

#         with smtplib.SMTP('smtp.gmail.com', 587) as server:
#             server.starttls()
#             server.login(EMAIL_USER, EMAIL_PASS)
#             server.send_message(msg)

#         flash('Message sent successfully!', 'success')
#     except Exception as e:
#         flash('Failed to send message. Please try again later.', 'danger')

#     return redirect(url_for('contact'))

# @app.route('/logout')
# def logout():
#     if 'start_time' in session:
#         start_time = session.pop('start_time', None)
#         if start_time:
#             if isinstance(start_time, str):
#                 start_time = datetime.fromisoformat(start_time)

#             duration = (datetime.now(timezone.utc) - start_time).seconds
#             latest_entry = LoginLog.query.order_by(LoginLog.timestamp.desc()).first()
#             if latest_entry:
#                 latest_entry.duration = duration
#                 db.session.commit()
#     session.clear()
#     return redirect(url_for('home'))


# @app.after_request
# def add_header(response):
#     response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, post-check=0, pre-check=0"
#     response.headers["Pragma"] = "no-cache"
#     response.headers["Expires"] = "0"
#     return response

# if __name__ == '__main__':
#     with app.app_context():
#         db.create_all()
#     app.run(debug=True)













from flask import Flask, make_response, render_template, request, redirect, url_for, session, flash
from flask_jwt_extended import JWTManager, unset_jwt_cookies
from models import db, User, LoginLog
from auth import auth_bp
from routes import routes_bp
import os
import smtplib
from email.message import EmailMessage
from datetime import datetime, timezone
import pytz
from dotenv import load_dotenv

IST = pytz.timezone('Asia/Kolkata')

app = Flask(__name__)
app.secret_key ='a3f1b0c7d9e4f8a1b2c3d4e5f6a7b8c9'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///default.db'
app.config['SQLALCHEMY_BINDS'] = {
    'users': 'sqlite:///users.db',
    'login_logs': 'sqlite:///login_logs.db'
}

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'My@Sec123Key'

db.init_app(app)

app.config['JWT_TOKEN_LOCATION'] = ['cookies'] 
app.config['JWT_COOKIE_SECURE'] = False
app.config['JWT_COOKIE_CSRF_PROTECT'] = False 
jwt = JWTManager(app)


app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(routes_bp)

load_dotenv(r'final_year_project\credentials.env')

EMAIL_USER = os.getenv('EMAIL_USER')
EMAIL_PASS = os.getenv('EMAIL_PASS')

with app.app_context():
    db.create_all() 

@app.route('/')
def home():
    return render_template('index.html')

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
    except Exception as e:
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
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
