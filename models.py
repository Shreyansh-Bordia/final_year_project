# from flask_sqlalchemy import SQLAlchemy
# from werkzeug.security import generate_password_hash, check_password_hash

# db = SQLAlchemy()

# class User(db.Model):
#     __tablename__ = 'users'
    
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(50), unique=True, nullable=False)
#     password = db.Column(db.String(200), nullable=False)  # Hashed password
#     email = db.Column(db.String(100), unique=True, nullable=False)
#     phone = db.Column(db.String(20), nullable=False)
#     role = db.Column(db.String(20), nullable=False)  # patient, doctor, admin

#     def set_password(self, password):
#         self.password = generate_password_hash(password)

#     def check_password(self, password):
#         return check_password_hash(self.password, password)


# class Patient(db.Model):
#     __tablename__ = 'patients'
    
#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
#     age = db.Column(db.Integer, nullable=False)
#     medical_history = db.Column(db.Text, nullable=True)
    
#     user = db.relationship('User', backref=db.backref('patient', uselist=False))


# class Doctor(db.Model):
#     __tablename__ = 'doctors'
    
#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
#     specialization = db.Column(db.String(100), nullable=False)
#     license_number = db.Column(db.String(50), unique=True, nullable=False)

#     user = db.relationship('User', backref=db.backref('doctor', uselist=False))


# class Admin(db.Model):
#     __tablename__ = 'admins'
    
#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
#     department = db.Column(db.String(100), nullable=False)

#     user = db.relationship('User', backref=db.backref('admin', uselist=False))



from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone
import pytz

IST = pytz.timezone('Asia/Kolkata')

db = SQLAlchemy()

class User(db.Model):
    __bind_key__ = 'users' 
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)  
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    state = db.Column(db.String(20), nullable=False)
    role = db.Column(db.String(20), nullable=False) 

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


class Appointment(db.Model):
    __bind_key__ = 'users'  
    __tablename__ = 'appointments'

    id = db.Column(db.Integer, primary_key=True)
    specialisation = db.Column(db.String(100), nullable=False)
    illness = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), default="waiting")
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(IST), nullable=False)

class Patient(db.Model):
    __bind_key__ = 'users'  
    __tablename__ = 'patients'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    age = db.Column(db.Integer, nullable=False)
    address = db.Column(db.String(400), nullable=True)
    
    user = db.relationship('User', backref=db.backref('patient', uselist=False))


class Doctor(db.Model):
    __bind_key__ = 'users'  
    __tablename__ = 'doctors'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    specialization = db.Column(db.String(100), nullable=False)
    degree = db.Column(db.String(50), nullable=False)

    user = db.relationship('User', backref=db.backref('doctor', uselist=False))


class Admin(db.Model):
    __bind_key__ = 'users'  
    __tablename__ = 'admins'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)

    user = db.relationship('User', backref=db.backref('admin', uselist=False))


class LoginLog(db.Model):
    __bind_key__ = 'login_logs' 
    __tablename__ = 'login_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(45), nullable=False)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(IST), nullable=False)
    protocol_type = db.Column(db.String(10), nullable=False) 
    service = db.Column(db.String(20), nullable=False)
    src_bytes = db.Column(db.Integer, nullable=False)
    dst_bytes = db.Column(db.Integer, nullable=False)
    flag = db.Column(db.String(10), nullable=False) 
    user_agent = db.Column(db.String(255), nullable=True)
    duration = db.Column(db.Integer, nullable=True) 
