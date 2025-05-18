import random
import string
import datetime
import pytz
from flask import Blueprint, make_response, request, session, render_template, redirect, url_for, flash
from flask_jwt_extended import create_access_token, set_access_cookies
from models import db, User, LoginLog
from flask_mail import Message
from extensions import mail
from models import Patient, Doctor, Admin

IST = pytz.timezone('Asia/Kolkata')
auth_bp = Blueprint('auth', __name__)

import random
import string

def generate_mfa_code():
    length = random.randint(6, 8)
    characters = (
        string.ascii_uppercase +
        string.ascii_lowercase +
        string.digits +
        "!@#$%^&*()-_=+[]{}|;:,.<>?/~`"
    )
    
    # Ensure at least one character from each category
    code = [
        random.choice(string.ascii_uppercase),
        random.choice(string.ascii_lowercase),
        random.choice(string.digits),
        random.choice("!@#$%^&*()-_=+[]{}|;:,.<>?/~`")
    ]

    # Fill the rest of the code
    code += random.choices(characters, k=length - len(code))
    random.shuffle(code)
    
    return ''.join(code)



@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    role = request.args.get('role')
    lockout_until = session.get('lockout_until')
    now_ts = datetime.datetime.now().timestamp()

    if request.method == 'GET':
        # If cooldown active, show message but render login page without redirect
        if lockout_until and now_ts < lockout_until:
            flash("Too many failed attempts. Please login back.", "danger")
            # Just render login page with flash message, no redirect
            response = make_response(render_template('login.html', role=role))
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
            return response
        
        # Normal login page render if no lockout
        response = make_response(render_template('login.html', role=role))
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response
    
    data = request.form
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()

    if user and user.check_password(password):
        # Log login attempt
        log_entry = LoginLog(
            ip_address=request.remote_addr,
            protocol_type=request.scheme.upper(),
            service="HTTP",
            src_bytes=request.content_length or 0,
            dst_bytes=0,
            flag="SF",
            user_agent=request.headers.get('User-Agent')
        )
        db.session.add(log_entry)
        db.session.commit()

        # Store session info
        session['role'] = user.role
        session['username'] = user.username
        session['user_id'] = user.id
        session['start_time'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        session['mfa_attempts'] = 0  # Reset attempts
        session.pop('lockout_until', None)  # Reset lockout if exists

        return render_template('mfa_email.html', username=username)

    flash("Invalid credentials. Please try again.", "danger")
    return redirect(url_for('auth.login', role=role))


@auth_bp.route('/send_mfa', methods=['POST'])
def send_mfa():
    email = request.form.get('email')
    username = session.get('username')

    user = User.query.filter_by(username=username).first()

    if not email:
        email = session.get('email')

    if not user or user.email != email:
        flash("Email does not match our records.", "danger")
        return render_template('mfa_email.html', username=username)

    session['email'] = email

    # Generate and send MFA code
    mfa_code = generate_mfa_code()
    session['mfa_code'] = mfa_code
    session['mfa_sent_time'] = datetime.datetime.now().timestamp()

    msg = Message("Your MFA Code", recipients=[email])
    msg.html = f"""
    <html>
      <body style="font-family: Arial, sans-serif; line-height: 1.6;">
        <p style="font-size: 16px;">Welcome to <strong style="color: #006400;">Jeevan Kavach</strong> - Your Secured Telemedicine Service.</p>

        <p>At Jeevan Kavach, we believe that every piece of medical data is invaluable, and protecting it is as vital as saving a life. We are committed to delivering the most trusted and secure telemedicine experience right at your fingertips.</p>

        <p style="color: #006400;">As part of our multi-layered security approach, please use the following Multi-Factor Authentication (MFA) code to proceed securely:</p>

        <div style="margin: 20px 0; padding: 10px; background-color: #f4f4f4; border-left: 5px solid #2E86C1; font-size: 18px;">
            <strong style="color: #2E86C1;">{mfa_code}</strong>
        </div>

        <p>We hope you have a smooth experience and receive the accurate diagnostic consultation you deserve.</p>

        <p>Wishing you a happy, healthy, and safe life ahead.</p>

        <p>- The Jeevan Kavach Team</p>
      </body>
    </html>
    """

    mail.send(msg)

    return render_template('mfa_code.html', email=email, resend_allowed=False)


@auth_bp.route('/verify_mfa', methods=['POST'])
def verify_mfa():
    code = request.form.get('code')
    correct_code = session.get('mfa_code')
    email = session.get('email')

    # Initialize or increment attempt counter
    session['mfa_attempts'] = session.get('mfa_attempts', 0) + 1

    if session['mfa_attempts'] > 4:
        session.pop('mfa_code', None)
        session.pop('mfa_sent_time', None)
        session.pop('mfa_attempts', None)
        session['lockout_until'] = datetime.datetime.now().timestamp() + 600  # 10 minutes
        return redirect(url_for('auth.login'))

    if code and code == correct_code:
        username = session.get('username')
        user = User.query.filter_by(username=username).first()

        access_token = create_access_token(
            identity={'username': username, 'role': user.role},
            expires_delta=datetime.timedelta(hours=1)
        )

        response = redirect(url_for(f'routes.{user.role}_dashboard'))
        set_access_cookies(response, access_token)

        # Clean up session MFA data
        session.pop('mfa_code', None)
        session.pop('mfa_sent_time', None)
        session.pop('mfa_attempts', None)
        session.pop('lockout_until', None)

        return response

    flash("Invalid MFA code.", "danger")
    resend_allowed = (datetime.datetime.now().timestamp() - session.get('mfa_sent_time', 0)) > 60
    return render_template('mfa_code.html', email=email, resend_allowed=resend_allowed)

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
    name = data.get('name')
    state = data.get('state')
    age = data.get('age')
    address = data.get('address')
    degree = data.get('degree')
    specialization = data.get('position')

    if User.query.filter_by(username=username).first():
        flash("User already exists. Please log in.", "danger")
        return redirect(url_for('auth.login', role=role))

    new_user = User(name=name, username=username, email=email, phone=phone, state=state, role=role)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()

    if role == 'patient':
        new_patient = Patient(user_id=new_user.id, age=age, address=address)
        db.session.add(new_patient)
    elif role == 'doctor':
        new_doctor = Doctor(user_id=new_user.id, specialization=specialization, degree=degree)
        db.session.add(new_doctor)
    elif role == 'admin':
        new_admin = Admin(user_id=new_user.id)
        db.session.add(new_admin)

    db.session.commit()

    flash("Signup successful! Please log in.", "success")
    return redirect(url_for('auth.login', role=role))

