from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required
from models import db, User, AlumniProfile
from models import StudentProfile

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
            return render_template("signup.html")

        user = User(name=name, email=email, password=password, role=role)
        db.session.add(user)
        db.session.commit()

        if role == "alumni":
            return redirect(url_for("auth.complete_alumni_profile", user_id=user.id))
        elif role == "student":
            return redirect(url_for("auth.complete_student_profile", user_id=user.id))
        else:
            flash("Signup successful! Please login.")
            return redirect(url_for("auth.login"))
    return render_template("signup.html")

@auth.route("/complete-student-profile/<int:user_id>", methods=["GET", "POST"])
def complete_student_profile(user_id):
    user = User.query.get_or_404(user_id)
    if request.method == "POST":
        profile = StudentProfile(
            user_id=user.id,
            name=user.name,
            email=user.email,
            batch=request.form.get("batch"),
            department=request.form.get("department"),
            phone=request.form.get("phone"),
            linkedin=request.form.get("linkedin"),
            skills=request.form.get("skills"),
            bio=request.form.get("bio")
        )
        db.session.add(profile)
        db.session.commit()
        flash("Profile completed! Please login.")
        return redirect(url_for("auth.login"))
    return render_template("student_profile_form.html")
   


@auth.route("/complete-alumni-profile/<int:user_id>", methods=["GET", "POST"])
def complete_alumni_profile(user_id):
    user = User.query.get_or_404(user_id)
    if request.method == "POST":
        profile = AlumniProfile(
            user_id=user.id,
            name=user.name,
            email=user.email,
            graduation_year=request.form.get("graduation_year"),
            batch=request.form.get("batch"),
            degree=request.form.get("degree"),
            department=request.form.get("department"),
            phone=request.form.get("phone"),
            linkedin=request.form.get("linkedin"),
            company=request.form.get("company"),
            occupation=request.form.get("occupation"),
            location=request.form.get("location"),
            skills=request.form.get("skills"),
            bio=request.form.get("bio")
        )
        db.session.add(profile)
        db.session.commit()
        flash("Profile completed! Please login.")
        return redirect(url_for("auth.login"))
    return render_template("alumni_profile_form.html")

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
