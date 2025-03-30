from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
import smtplib
from email.message import EmailMessage

app = Flask(__name__)
app.secret_key ='a3f1b0c7d9e4f8a1b2c3d4e5f6a7b8c9' 
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Dummy User Data
users = {
    'patient': {'username': 'patient', 'password': 'pass123'},
    'doctor': {'username': 'doctor', 'password': 'doc123'},
    'admin': {'username': 'admin', 'password': 'admin123'}
}

# Home Page
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    role = request.args.get('role')  # Added query parameter handling

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # $$$ Hardcoded login check
        if username == 'patient' and password == 'pass123':
            session['role'] = 'patient'
            return redirect(url_for('patient_dashboard'))
        
        if username == 'doctor' and password == 'doc123':
            session['role'] = 'doctor'
            return redirect(url_for('doctor_dashboard'))
        
        if role in users and users[role]['username'] == username and users[role]['password'] == password:
            session['role'] = role
            return redirect(url_for(f'{role}_dashboard'))
        else:
            flash('Invalid credentials. Please try again.')
            return redirect(url_for('login', role=role))

    return render_template('login.html', role=role)

# <$> Signup Route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    role = request.args.get('role', 'patient')

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']

        # Check if user already exists
        for user in users[role]:
            if user['username'] == username:
                flash('User already exists. Please log in.', 'danger')
                return redirect(url_for('login', role=role))

        # Patient-specific fields
        if role == 'patient':
            home_address = request.form['home_address']
            alt_contact = request.form.get('alt_contact', '')  # Optional
            age = request.form['age']

            users['patient'].append({
                'username': username,
                'password': password,
                'name': name,
                'email': email,
                'phone': phone,
                'home_address': home_address,
                'alt_contact': alt_contact,
                'age': age
            })

        # Doctor-specific fields
        elif role == 'doctor':
            degree = request.form['degree']
            prev_hospital = request.form['prev_hospital']
            position = request.form['position']

            users['doctor'].append({
                'username': username,
                'password': password,
                'name': name,
                'email': email,
                'phone': phone,
                'degree': degree,
                'prev_hospital': prev_hospital,
                'position': position
            })

        flash('Signup successful! Please log in.', 'success')
        return redirect(url_for('login', role=role))

    return render_template('signup.html', role=role)

# Role-Based Dashboards
@app.route('/patient_dashboard')
def patient_dashboard():
    return render_template('patient_dashboard.html')

@app.route('/doctor_dashboard')
def doctor_dashboard():
    return render_template('doctor_dashboard.html')

@app.route('/admin_dashboard')
def admin_dashboard():
    return render_template('admin_dashboard.html')

# File Upload Logic
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file uploaded.')
        return redirect(request.referrer)

    file = request.files['file']
    if file.filename == '':
        flash('No selected file.')
        return redirect(request.referrer)

    if file:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        flash('File uploaded successfully.')
        return redirect(request.referrer)
    
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
        msg['From'] = 'shreyanshbordia@gmail.com'
        msg['To'] = 'shreyansh.is21@bmsce.ac.in'

        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login('shreyanshbordia@gmail.com', 'krqd jxpd nuiw atqw')
            server.send_message(msg)

        flash('Message sent successfully!', 'success')
    except Exception as e:
        flash('Failed to send message. Please try again later.', 'danger')

    return redirect(url_for('contact'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/get-appointment')
def get_appointment():
    return render_template('doctor_list.html')  # Ensure doctor_list.html exists


@app.route('/patients')
def patients():
    return render_template('patients.html')

@app.route('/history')
def history():
    return render_template('history.html')

@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0, private"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

if __name__ == '__main__':
    app.run(debug=True)
