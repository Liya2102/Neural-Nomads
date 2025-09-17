from flask import Blueprint, render_template
from flask_login import login_required, current_user
from models import User


students_bp = Blueprint("students", __name__)

@students_bp.route("/home")
def student_home():
    return render_template("student_home.html")

@students_bp.route("/search")
@login_required
def search():
    if current_user.role != "student":
        return "Unauthorized", 403
    alumni = User.query.filter_by(role="alumni").all()
    return render_template("search.html", alumni=alumni)
