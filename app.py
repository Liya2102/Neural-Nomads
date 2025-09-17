from flask import Flask, render_template
from flask_login import LoginManager
from config import Config
from models import db, User

# Blueprints
from auth.routes import auth
from alumni.routes import alumni_bp
from students.routes import students_bp
from admin.routes import admin_bp

app = Flask(__name__, instance_relative_config=True)
app.config.from_object(Config)

# Init DB
db.init_app(app)

# Flask-Login
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Register blueprints
app.register_blueprint(auth)
app.register_blueprint(alumni_bp, url_prefix="/alumni")
app.register_blueprint(students_bp, url_prefix="/students")
app.register_blueprint(admin_bp, url_prefix="/admin")

@app.route("/")
def home():
    return render_template("home.html")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
