from flask import Flask
from flask_jwt_extended import JWTManager
from routes import routes_bp
from auth import auth_bp

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['JWT_SECRET_KEY'] = 'jwtsecretkey'  # Used for encoding JWT tokens
app.config['UPLOAD_FOLDER'] = 'static/uploads'

jwt = JWTManager(app)

# Register Blueprints
app.register_blueprint(routes_bp)
app.register_blueprint(auth_bp)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0, private"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

if __name__ == '__main__':
    app.run(debug=True)
