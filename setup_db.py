import pandas as pd
import sqlite3
import random
from datetime import datetime, timedelta

# ---------- Load Excel Files ----------
alumni = pd.read_excel("data/alumni_data.xlsx")
registered = pd.read_excel("data/alumni_registered.xlsx")
credentials = pd.read_excel("data/alumni_login_credentials.xlsx")
admins = pd.read_excel("data/admin_dataset.xlsx")
students = pd.read_excel("data/student_data.xlsx")

# Merge registered + credentials (on Email)
registered = registered.merge(credentials, on="Email", how="left")

# ---------- Create SQLite DB ----------
DB = "alumni.db"
conn = sqlite3.connect(DB)

# Save base tables
alumni.to_sql("alumni", conn, if_exists="replace", index=False)
registered.to_sql("registered_alumni", conn, if_exists="replace", index=False)
admins.to_sql("admins", conn, if_exists="replace", index=False)
students.to_sql("students", conn, if_exists="replace", index=False)

# ---------- Notices ----------
notices = pd.DataFrame({
    "title": [
        "Alumni Meet 2025 – Jan 15th",
        "Webinar on AI – Dec 2024",
        "Batch 2015 Reunion – Oct 2024",
        "Placement Guidance Session – Sep 2024"
    ],
    "file": [
        "alumni_meet.pdf",
        "webinar_ai.pdf",
        "batch2015.pdf",
        "placement.pdf"
    ]
})
notices.to_sql("notices", conn, if_exists="replace", index=False)

# ---------- Job Openings ----------
conn.execute("""
CREATE TABLE IF NOT EXISTS job_openings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    alumni_email TEXT,
    title TEXT,
    company TEXT,
    role TEXT,
    location TEXT,
    description TEXT
)
""")

# ---------- Engagement Tracking Columns ----------
tables = ["students", "registered_alumni", "admins"]

for table in tables:
    # login_count
    try:
        conn.execute(f"ALTER TABLE {table} ADD COLUMN login_count INTEGER DEFAULT 0")
        print(f"✅ Added login_count to {table}")
    except sqlite3.OperationalError:
        print(f"ℹ️ {table} already has login_count")

    # last_login
    try:
        conn.execute(f"ALTER TABLE {table} ADD COLUMN last_login TEXT")
        print(f"✅ Added last_login to {table}")
    except sqlite3.OperationalError:
        print(f"ℹ️ {table} already has last_login")

# ---------- Seed Engagement Activity ----------
def random_date(days_back=60):
    """Generate a random datetime string within the last X days."""
    date = datetime.now() - timedelta(days=random.randint(0, days_back))
    return date.strftime("%Y-%m-%d %H:%M:%S")

# Seed Alumni Activity
conn.execute("""
UPDATE registered_alumni
SET login_count = ABS(RANDOM() % 15) + 1,
    last_login = ?
WHERE Batch = '2022'
""", [random_date()])

conn.execute("""
UPDATE registered_alumni
SET login_count = ABS(RANDOM() % 10) + 1,
    last_login = ?
WHERE Department = 'CSE'
""", [random_date()])

# Seed Student Activity
conn.execute("""
UPDATE students
SET login_count = ABS(RANDOM() % 5) + 1,
    last_login = ?
WHERE Batch = '2024'
""", [random_date()])

conn.commit()
conn.close()

print("✅ Database setup complete: alumni.db created with engagement tracking + seeded activity")
