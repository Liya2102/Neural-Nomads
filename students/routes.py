from flask import Blueprint, render_template, request
from flask_login import login_required, current_user

from models import User, StudentProfile, Event, JobOpening


students_bp = Blueprint("students", __name__)

@students_bp.route("/home")
def student_home():
    return render_template("student_home.html")

@students_bp.route("/profile")
@login_required
def profile():
    if current_user.role != "student":
        return "Unauthorized", 403
    profile = StudentProfile.query.filter_by(user_id=current_user.id).first()
    return render_template("student_profile.html", user=current_user, profile=profile)

@students_bp.route("/search")
@login_required
def search():
    if current_user.role != "student":
        return "Unauthorized", 403
    alumni = User.query.filter_by(role="alumni").all()
    return render_template("search.html", alumni=alumni)


# Mentor Matching Form
@students_bp.route("/mentor-matching", methods=["GET", "POST"])
@login_required
def mentor_matching():
    if request.method == "POST":
        mentee = {
            "id": current_user.id,
            "name": request.form["name"],
            "interests": [s.strip() for s in request.form["interests"].split(",")],
            "goal": request.form["goal"],
            "location": request.form["location"]
        }
        from models import AlumniProfile
        mentors = AlumniProfile.query.all()
        if 'find_best_mentors' in globals():
            best_matches = find_best_mentors(mentee, mentors)
        else:
            best_matches = mentors
        return render_template("results.html", matches=best_matches, mentee=mentee)
    return render_template("mentor_matching.html", user=current_user)

@students_bp.route("/events")
@login_required
def events():
    from datetime import date
    upcoming_events = Event.query.filter(Event.date >= date.today()).order_by(Event.date.asc()).all()
    return render_template("events.html", events=upcoming_events)

@students_bp.route("/jobs")
@login_required
def jobs():
    query = request.args.get("q", "")
    jobs_query = JobOpening.query
    if query:
        jobs_query = jobs_query.filter(
            (JobOpening.title.ilike(f"%{query}%")) |
            (JobOpening.company.ilike(f"%{query}%")) |
            (JobOpening.location.ilike(f"%{query}%"))
        )
    jobs = jobs_query.order_by(JobOpening.posted_at.desc()).all()
    return render_template("jobs.html", jobs=jobs)
