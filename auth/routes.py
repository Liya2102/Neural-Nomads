from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required
from models import db, User

auth = Blueprint("auth", __name__)

@auth.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = generate_password_hash(request.form["password"], method="pbkdf2:sha256")
        role = request.form["role"]

        if User.query.filter_by(email=email).first():
            flash("Email already exists.")
            return redirect(url_for("auth.signup"))

        user = User(name=name, email=email, password=password, role=role)
        db.session.add(user)
        db.session.commit()
        flash("Signup successful! Please login.")
        return redirect(url_for("auth.login"))

    return render_template("signup.html")

@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            if user.role == "alumni":
                return redirect(url_for("alumni.alumni_home"))
            elif user.role == "student":
                return redirect(url_for("students.student_home"))
            elif user.role == "admin":
                return redirect(url_for("admin.admin_home"))
            return redirect(url_for("home"))
        flash("Invalid login credentials")
    return render_template("login.html")

@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))
