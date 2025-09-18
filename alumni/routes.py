from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import Event, AlumniProfile, JobOpening, Notice, db

alumni_bp = Blueprint("alumni", __name__)

@alumni_bp.route("/home", methods=["GET"])
@login_required
def alumni_home():
    notices = Notice.query.order_by(Notice.created_at.desc()).limit(5).all()
    job_openings = JobOpening.query.order_by(JobOpening.posted_at.desc()).limit(5).all()
    return render_template("alumni_home.html", notices=notices, job_openings=job_openings)

@alumni_bp.route("/post_job", methods=["GET", "POST"])
@login_required
def post_job():
    if current_user.role != "alumni":
        return "Unauthorized", 403
    if request.method == "POST":
        title = request.form.get("title")
        company = request.form.get("company")
        location = request.form.get("location")
        description = request.form.get("description")
        if not title or not company or not description:
            flash("Please fill in all required fields.", "danger")
            return redirect(url_for("alumni.post_job"))
        from datetime import datetime
        job = JobOpening(
            title=title,
            company=company,
            location=location,
            description=description,
            posted_by=current_user.id,
            posted_at=datetime.now()
        )
        db.session.add(job)
        db.session.commit()
        flash("Job opening posted successfully!", "success")
        return redirect(url_for("alumni.alumni_home"))
    return render_template("post_job.html")

@alumni_bp.route("/profile")
@login_required
def profile():
    if current_user.role != "alumni":
        return "Unauthorized", 403
    profile = AlumniProfile.query.filter_by(user_id=current_user.id).first()
    return render_template("alumni_profile.html", user=current_user, profile=profile)

@alumni_bp.route("/events")
@login_required
def events():
    from datetime import date
    upcoming_events = Event.query.filter(Event.date >= date.today()).order_by(Event.date.asc()).all()
    return render_template("events.html", events=upcoming_events)

@alumni_bp.route("/donate", methods=["GET", "POST"])
@login_required
def donate():
    from models import Donation, User
    if request.method == "POST":
        amount = request.form.get("amount", type=float)
        message = request.form.get("message")
        if not amount or amount <= 0:
            flash("Please enter a valid donation amount.", "danger")
            return redirect(url_for("alumni.donate"))
        from datetime import datetime
        donation = Donation(
            donor_id=current_user.id,
            amount=amount,
            message=message,
            donated_at=datetime.now()
        )
        db.session.add(donation)
        db.session.commit()
        flash("Thank you for your donation!", "success")
        return redirect(url_for("alumni.donate"))
    # Show previous donations
    donations = Donation.query.order_by(Donation.donated_at.desc()).limit(10).all()
    # Attach donor info for display
    for d in donations:
        d.donor = User.query.get(d.donor_id)
    return render_template("donate.html", donations=donations)

@alumni_bp.route("/jobs", methods=["GET"])
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
