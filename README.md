# 🛡️ Secure Telemedicine API Gateway using AI and Zero Trust Architecture

This project implements a **Secure API Gateway** for telemedicine systems using **AI-based intrusion detection** and **Zero Trust Architecture (ZTA)** principles. It features real-time doctor-patient communication, strict access controls, anomaly detection, and protection from common web-based attacks.

---

## 🔧 Tech Stack

* **Frontend:** HTML, CSS
* **Backend:** Flask (Python)
* **Security:** JWT-based Authentication, Least Privilege Access, AI Monitoring, TLS, ZTA Principles
* **AI:** Isolation Forest for real-time intrusion detection

---

## 🚀 Getting Started

Follow these steps to set up and run the project locally.

### 1. Clone the Repository

```bash
git clone https://github.com/your-repo/secure-telemedicine-gateway.git
cd secure-telemedicine-gateway
```

### 2. Install Dependencies

Make sure you have Python installed (preferably Python 3.8+), then run:

```bash
pip install -r requirements.txt
```

### 3. Start the Application

```bash
python app.py
```

### 4. Access the Dashboard

Once running, open your browser and navigate to:

```
http://127.0.0.1:5000
```

---

## 👥 User Roles

### 👨‍⚕️ Doctor Login / Registration

* Register as a doctor.
* Log in (credentials must be entered **twice** to prevent brute-force attacks).
* Accept incoming patient consultation requests.
* Perform secure real-time consultation.

### 👨‍💻 Patient Login / Registration

* Register as a patient.
* Log in securely with double authentication.
* Raise a doctor consultation request.
* Wait for a doctor to accept.

---

## 🔐 Security Features

This system is designed with Zero Trust Architecture (ZTA) principles, including:

* ✅ **Authentication & Authorization** (via OAuth2 and JWT)
* ✅ **Least Privilege Access** (scoped tokens for specific actions)
* ✅ **Double Login Entry** to prevent brute-force attacks
* ✅ **Secure Communication** using TLS encryption
* ✅ **AI-Powered Intrusion Detection** using Isolation Forest
* ✅ **Protection against common web attacks** (e.g., token replay, session hijacking)

---

## 📦 Folder Structure

```
├── app.py                 # Main Flask application
├── requirements.txt       # Required Python packages
├── templates/             # HTML files
├── static/                # CSS & JS files
├── auth.py                # Login & Registration logic
├── routes.py              # Routing and business logic
├── model/                 # AI intrusion detection logic
├── logs/                  # Request logs and alerts
```

---

## 🧠 AI Monitoring

* Behavioral anomaly detection using **Random Forest**
* Logs request patterns, token behaviors, endpoint usage, etc.
* Flags suspicious activity in real-time for further analysis

---

## 📬 Contact

For any queries or contributions, feel free to open an issue or pull request.
Email: \[[shreyansh.is21@bmsce.ac.in](mailto:shreyansh.is21@bmsce.ac.in)]
