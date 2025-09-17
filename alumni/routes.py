from flask import Blueprint, render_template
from flask_login import login_required, current_user
from models import Event

alumni_bp = Blueprint("alumni", __name__)

@alumni_bp.route("/home")
def alumni_home():
    return render_template("alumni_home.html")

@alumni_bp.route("/profile")
@login_required
def profile():
    if current_user.role != "alumni":
        return "Unauthorized", 403
    return render_template("profile.html", user=current_user)

@alumni_bp.route("/events")
@login_required
def events():
    from datetime import date
    upcoming_events = Event.query.filter(Event.date >= date.today()).order_by(Event.date.asc()).all()
    return render_template("events.html", events=upcoming_events)

@alumni_bp.route("/donate")
@login_required
def donate():
    return "Donation Page (to be implemented)"
