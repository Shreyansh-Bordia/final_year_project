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

if __name__ == '__main__':
    app.run(debug=True)
