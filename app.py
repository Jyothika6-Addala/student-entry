from flask import Flask, render_template, request, redirect, session
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = "supersecretkey123"

DATABASE = "students.db"

# First Login (Form Access)
FORM_USERNAME = "staff"
FORM_PASSWORD = "1111"

# Second Login (Admin Dashboard Access)
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "9999"

ADMIN_URL = "/dashboard123"


# -----------------------------
# Database Initialization
# -----------------------------
def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            phone1 TEXT,
            phone2 TEXT,
            course TEXT,
            place TEXT,
            school TEXT,
            busnumber TEXT,
            reference TEXT,
            date TEXT,
            time TEXT
        )
    """)

    conn.commit()
    conn.close()


# -----------------------------
# Phone Validation
# -----------------------------
def is_valid_indian_number(number):
    return number.isdigit() and len(number) == 10 and number[0] in "6789"


# -----------------------------
# First Login (Form Access)
# -----------------------------
@app.route("/", methods=["GET", "POST"])
def form_login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username == FORM_USERNAME and password == FORM_PASSWORD:
            session["form_user"] = True
            return redirect("/form")
        else:
            return "Invalid Form Login Credentials"

    return render_template("login.html")


# -----------------------------
# Student Form
# -----------------------------
@app.route("/form", methods=["GET", "POST"])
def form():
    if "form_user" not in session:
        return redirect("/")

    now = datetime.now()
    current_date = now.strftime("%Y-%m-%d")
    current_time = now.strftime("%H:%M:%S")

    if request.method == "POST":
        name = request.form["name"]
        phone1 = request.form["phone1"]
        phone2 = request.form["phone2"]
        course = request.form["course"]
        place = request.form["place"]
        school = request.form["school"]
        busnumber = request.form["busnumber"]
        reference = request.form["reference"]

        if not is_valid_indian_number(phone1):
            return "Invalid Phone Number 1"

        if not is_valid_indian_number(phone2):
            return "Invalid Phone Number 2"

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO students
            (name, phone1, phone2, course, place, school, busnumber, reference, date, time)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, phone1, phone2, course, place, school, busnumber, reference, current_date, current_time))

        conn.commit()
        conn.close()

        return redirect("/form")

    return render_template("index.html",
                           current_date=current_date,
                           current_time=current_time)


# -----------------------------
# Second Login (Admin Dashboard)
# -----------------------------
@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session["admin_user"] = True
            return redirect(ADMIN_URL)
        else:
            return "Invalid Admin Credentials"

    return render_template("admin_login.html")


# -----------------------------
# Admin Dashboard
# -----------------------------
@app.route(ADMIN_URL)
def admin_dashboard():
    if "admin_user" not in session:
        return redirect("/admin-login")

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()
    conn.close()

    return render_template("admin.html", students=students)


# -----------------------------
# Logout
# -----------------------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
