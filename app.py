from flask import Flask, render_template, request, redirect, session, flash
import sqlite3
from datetime import datetime
from chatbot import get_response, model, words, classes, intents
import random
from flask import jsonify

app = Flask(__name__)
app.secret_key = "supersecretkey"
DB = "alumni.db"

# ---------- DB Helper ----------
def query_db(query, args=(), one=False):
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    cur = conn.execute(query, args)
    rv = cur.fetchall()
    conn.commit()
    conn.close()
    return (rv[0] if rv else None) if one else rv

@app.route("/chatbot", methods=["POST"])
def chatbot_reply():
    user_input = request.json.get("message")
    answer = get_response(user_input, model, words, classes, intents)
    return jsonify({"reply": answer})

# ---------- HOME ----------
@app.route("/")
def index():
    notices = query_db("SELECT * FROM notices ORDER BY rowid DESC LIMIT 5")
    return render_template("index.html", notices=notices)


# ---------- LOGIN ----------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        role = request.form["role"]

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if role == "admin":
            user = query_db("SELECT * FROM admins WHERE Email=? AND Password=?", [email, password], one=True)
            if user:
                session["role"] = "admin"; session["user"] = email
                query_db("UPDATE admins SET login_count = COALESCE(login_count,0)+1, last_login=? WHERE Email=?", [now, email])
                return redirect("/admin_dashboard")

        elif role == "alumni":
            user = query_db("SELECT * FROM registered_alumni WHERE Email=? AND Password=?", [email, password], one=True)
            if user:
                session["role"] = "alumni"; session["user"] = email
                query_db("UPDATE registered_alumni SET login_count = COALESCE(login_count,0)+1, last_login=? WHERE Email=?", [now, email])
                return redirect("/alumni_dashboard")

        elif role == "student":
            user = query_db("SELECT * FROM students WHERE Email=? AND Password=?", [email, password], one=True)
            if user:
                session["role"] = "student"; session["user"] = email
                query_db("UPDATE students SET login_count = COALESCE(login_count,0)+1, last_login=? WHERE Email=?", [now, email])
                return redirect("/student_dashboard")

        flash("❌ Invalid credentials or role!")

    notices = query_db("SELECT * FROM notices ORDER BY rowid DESC LIMIT 5")
    return render_template("login.html", notices=notices)


# ---------- REGISTER ----------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        role = request.form["role"]
        name = request.form["name"]
        batch = request.form.get("batch")
        dept = request.form.get("department")
        email = request.form["email"]
        phone = request.form["phone"]
        password = request.form["password"]

        if role == "student":
            query_db("INSERT INTO students (Name,Batch,Department,Email,Phone,Password,login_count) VALUES (?,?,?,?,?,?,0)",
                     [name, batch, dept, email, phone, password])
            flash("✅ Student registered successfully! Please login.")
            return redirect("/login")

        elif role == "alumni":
            query_db("INSERT INTO registered_alumni (Name,Batch,Department,Email,Phone,Password,login_count) VALUES (?,?,?,?,?,?,0)",
                     [name, batch, dept, email, phone, password])
            flash("✅ Alumni registered successfully! Please login.")
            return redirect("/login")

    notices = query_db("SELECT * FROM notices ORDER BY rowid DESC LIMIT 5")
    return render_template("register.html", notices=notices)


# ---------- LOGOUT ----------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# ---------- ADMIN DASHBOARD ----------
@app.route("/admin_dashboard")
def admin_dashboard():
    if session.get("role") != "admin":
        return redirect("/login")

    # -------- Summary Panel Data --------
    total_alumni = query_db("SELECT COUNT(*) as c FROM registered_alumni", one=True)["c"]
    active_alumni = query_db("SELECT COUNT(*) as c FROM registered_alumni WHERE login_count > 0", one=True)["c"]

    total_students = query_db("SELECT COUNT(*) as c FROM students", one=True)["c"]
    active_students = query_db("SELECT COUNT(*) as c FROM students WHERE login_count > 0", one=True)["c"]

    top_batch = query_db("""
        SELECT Batch, COUNT(*) as c FROM registered_alumni 
        WHERE login_count > 0 
        GROUP BY Batch ORDER BY c DESC LIMIT 1
    """, one=True)
    top_batch_info = f"{top_batch['Batch']} ({top_batch['c']} active)" if top_batch else "N/A"

    top_course = query_db("""
        SELECT Department, COUNT(*) as c FROM registered_alumni 
        WHERE login_count > 0 
        GROUP BY Department ORDER BY c DESC LIMIT 1
    """, one=True)
    top_course_info = f"{top_course['Department']} ({top_course['c']} active)" if top_course else "N/A"

    # -------- Alumni Search --------
    alumni = []
    alumni_query = "SELECT * FROM registered_alumni WHERE 1=1"
    alumni_args = []
    if request.args.get("alumni_name"):
        alumni_query += " AND Name LIKE ?"
        alumni_args.append(f"%{request.args['alumni_name']}%")
    if request.args.get("alumni_email"):
        alumni_query += " AND Email LIKE ?"
        alumni_args.append(f"%{request.args['alumni_email']}%")
    if request.args.get("alumni_batch"):
        alumni_query += " AND Batch=?"
        alumni_args.append(request.args['alumni_batch'])
    if request.args.get("alumni_dept"):
        alumni_query += " AND Department LIKE ?"
        alumni_args.append(f"%{request.args['alumni_dept']}%")

    if alumni_args:
        alumni = query_db(alumni_query, alumni_args)

    # -------- Student Search --------
    students = []
    student_query = "SELECT * FROM students WHERE 1=1"
    student_args = []
    if request.args.get("student_name"):
        student_query += " AND Name LIKE ?"
        student_args.append(f"%{request.args['student_name']}%")
    if request.args.get("student_email"):
        student_query += " AND Email LIKE ?"
        student_args.append(f"%{request.args['student_email']}%")
    if request.args.get("student_batch"):
        student_query += " AND Batch=?"
        student_args.append(request.args['student_batch'])
    if request.args.get("student_dept"):
        student_query += " AND Department LIKE ?"
        student_args.append(f"%{request.args['student_dept']}%")

    if student_args:
        students = query_db(student_query, student_args)

    # -------- Other Data --------
    jobs = query_db("SELECT * FROM job_openings ORDER BY id DESC")
    notices = query_db("SELECT * FROM notices ORDER BY rowid DESC")

    return render_template(
        "admin_dashboard.html",
        alumni=alumni,
        students=students,
        jobs=jobs,
        notices=notices,
        total_alumni=total_alumni,
        active_alumni=active_alumni,
        total_students=total_students,
        active_students=active_students,
        top_batch_info=top_batch_info,
        top_course_info=top_course_info
    )


# ---------- DELETE USER ----------
@app.route("/delete_user/<role>/<email>")
def delete_user(role, email):
    if session.get("role") != "admin":
        return redirect("/login")
    if role == "student":
        query_db("DELETE FROM students WHERE Email=?", [email])
    elif role == "alumni":
        query_db("DELETE FROM registered_alumni WHERE Email=?", [email])
    flash("✅ User deleted successfully")
    return redirect("/admin_dashboard")


# ---------- ALUMNI DASHBOARD ----------
@app.route("/alumni_dashboard", methods=["GET", "POST"])
def alumni_dashboard():
    if session.get("role") != "alumni":
        return redirect("/login")

    alum = query_db("SELECT * FROM registered_alumni WHERE Email=?", [session["user"]], one=True)

    # Post job
    if request.method == "POST":
        title = request.form["title"]
        company = request.form["company"]
        role = request.form["role"]
        location = request.form["location"]
        desc = request.form["description"]
        query_db("INSERT INTO job_openings (alumni_email,title,company,role,location,description) VALUES (?,?,?,?,?,?)",
                 [session["user"], title, company, role, location, desc])
        flash("✅ Job Opening Posted")
        return redirect("/alumni_dashboard")

    jobs = query_db("SELECT * FROM job_openings WHERE alumni_email=? ORDER BY id DESC", [session["user"]])
    notices = query_db("SELECT * FROM notices ORDER BY rowid DESC LIMIT 5")

    return render_template("alumni_dashboard.html", alum=alum, jobs=jobs, notices=notices)


# ---------- STUDENT DASHBOARD ----------
@app.route("/student_dashboard", methods=["GET"])
def student_dashboard():
    if session.get("role") != "student":
        return redirect("/login")

    student = query_db("SELECT * FROM students WHERE Email=?", [session["user"]], one=True)

    batch = request.args.get("batch")
    company = request.args.get("company")
    dept = request.args.get("department")

    query = "SELECT * FROM registered_alumni WHERE 1=1"
    args = []
    if batch:
        query += " AND Batch=?"; args.append(batch)
    if company:
        query += " AND Company LIKE ?"; args.append(f"%{company}%")
    if dept:
        query += " AND Department LIKE ?"; args.append(f"%{dept}%")

    results = query_db(query, args)
    jobs = query_db("SELECT * FROM job_openings ORDER BY id DESC LIMIT 10")
    notices = query_db("SELECT * FROM notices ORDER BY rowid DESC LIMIT 5")

    return render_template("student_dashboard.html", student=student, results=results, jobs=jobs, notices=notices)


# ---------- RUN APP ----------
if __name__ == "__main__":
    app.run(debug=True)
