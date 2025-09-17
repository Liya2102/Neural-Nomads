from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, Event


admin_bp = Blueprint("admin", __name__)

@admin_bp.route("/home")
def admin_home():
    return render_template("admin_home.html")


@admin_bp.route("/add-event", methods=["GET", "POST"])
@login_required
def add_event():
    if current_user.role != "admin":
        return "Unauthorized", 403
    if request.method == "POST":
        title = request.form["title"]
        description = request.form["description"]
        date = request.form["date"]
        try:
            event = Event(title=title, description=description, date=date)
            db.session.add(event)
            db.session.commit()
            flash("Event added successfully!")
            return redirect(url_for("admin.add_event"))
        except Exception as e:
            flash("Error adding event: {}".format(e))
    return render_template("add_event.html")

@admin_bp.route("/dashboard")
@login_required
def dashboard():
    if current_user.role != "admin":
        return "Unauthorized", 403
    return render_template("base.html", message="Admin Dashboard")
