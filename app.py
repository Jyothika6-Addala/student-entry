from flask import Flask, render_template, request, redirect, session, send_file, flash, jsonify
from datetime import datetime
import pandas as pd
import sqlite3
import psycopg2
import pytz
import os

app = Flask(__name__)
app.secret_key = "secretkey"

# -----------------------------
# DATABASE SETUP
# -----------------------------

DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    DB_TYPE = "postgres"
    PARAM = "%s"
else:
    DB_TYPE = "sqlite"
    PARAM = "?"

def get_db():
    if DB_TYPE == "postgres":
        conn = psycopg2.connect(DATABASE_URL)
    else:
        conn = sqlite3.connect("students.db")
    return conn


# -----------------------------
# CREATE TABLE
# -----------------------------

def init_db():

    conn = get_db()
    cursor = conn.cursor()

    if DB_TYPE == "postgres":

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS students(
            id SERIAL PRIMARY KEY,
            name TEXT,
            phone1 TEXT,
            phone2 TEXT,
            phone3 TEXT,
            hallticket TEXT UNIQUE,
            course TEXT,
            place TEXT,
            school TEXT,
            busnumber TEXT,
            reference TEXT,
            reference_department TEXT,
            date TEXT,
            time TEXT
        )
        """)

    else:

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS students(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            phone1 TEXT,
            phone2 TEXT,
            phone3 TEXT,
            hallticket TEXT UNIQUE,
            course TEXT,
            place TEXT,
            school TEXT,
            busnumber TEXT,
            reference TEXT,
            reference_department TEXT,
            date TEXT,
            time TEXT
        )
        """)

    conn.commit()
    conn.close()

init_db()


# -----------------------------
# LOGIN PAGE
# -----------------------------

@app.route("/", methods=["GET","POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        if username == "staff" and password == "123":

            session["user"] = username
            return redirect("/form")

        flash("Invalid Login")

    return render_template("login.html")


# -----------------------------
# STUDENT FORM
# -----------------------------

@app.route("/form", methods=["GET","POST"])
def form():

    if "user" not in session:
        return redirect("/")

    if request.method == "POST":

        name = request.form.get("name")
        phone1 = request.form.get("phone1")
        phone2 = request.form.get("phone2")
        phone3 = request.form.get("phone3")
        hallticket = request.form.get("hallticket")
        course = request.form.get("course")
        place = request.form.get("place")
        school = request.form.get("school")
        busnumber = request.form.get("busnumber")
        reference = request.form.get("reference")
        reference_department = request.form.get("reference_department")

        india = pytz.timezone('Asia/Kolkata')
        now = datetime.now(india)

        date = now.strftime("%d-%m-%Y")
        time = now.strftime("%I:%M:%S %p")

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute(f"SELECT * FROM students WHERE hallticket={PARAM}", (hallticket,))
        existing = cursor.fetchone()

        if existing:
            flash("Hallticket number already entered")
            conn.close()
            return render_template("index.html")

        cursor.execute(f"""
        INSERT INTO students
        (name,phone1,phone2,phone3,hallticket,course,place,school,
        busnumber,reference,reference_department,date,time)

        VALUES ({PARAM},{PARAM},{PARAM},{PARAM},{PARAM},{PARAM},{PARAM},{PARAM},{PARAM},{PARAM},{PARAM},{PARAM},{PARAM})
        """,
        (name,phone1,phone2,phone3,hallticket,course,place,
        school,busnumber,reference,reference_department,date,time))

        conn.commit()
        conn.close()

        flash("Student Registered Successfully")

        return redirect("/form")

    return render_template("index.html")


# -----------------------------
# LIVE HALLTICKET CHECK
# -----------------------------

@app.route("/check-hallticket", methods=["POST"])
def check_hallticket():

    hallticket = request.form.get("hallticket")

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(f"SELECT * FROM students WHERE hallticket={PARAM}", (hallticket,))
    data = cursor.fetchone()

    conn.close()

    return jsonify({"exists": bool(data)})


# -----------------------------
# ADMIN LOGIN
# -----------------------------

@app.route("/admin-login", methods=["GET","POST"])
def admin_login():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        if username == "admin" and password == "admin123":

            session["admin"] = True
            return redirect("/dashboard")

        flash("Invalid Login")

    return render_template("admin_login.html")


# -----------------------------
# DASHBOARD
# -----------------------------

@app.route("/dashboard")
def dashboard():

    if "admin" not in session:
        return redirect("/admin-login")

    search = request.args.get("search")

    conn = get_db()
    cursor = conn.cursor()

    if search:
        cursor.execute(f"SELECT * FROM students WHERE hallticket={PARAM}", (search,))
    else:
        cursor.execute("SELECT * FROM students ORDER BY id DESC")

    students = cursor.fetchall()

    conn.close()

    return render_template("admin.html", students=students)


# -----------------------------
# EDIT STUDENT
# -----------------------------

@app.route("/edit/<int:id>", methods=["GET","POST"])
def edit(id):

    if "admin" not in session:
        return redirect("/admin-login")

    conn = get_db()
    cursor = conn.cursor()

    if request.method == "POST":

        name = request.form.get("name")
        phone1 = request.form.get("phone1")
        phone2 = request.form.get("phone2")
        phone3 = request.form.get("phone3")
        course = request.form.get("course")
        place = request.form.get("place")
        school = request.form.get("school")
        busnumber = request.form.get("busnumber")
        reference = request.form.get("reference")
        reference_department = request.form.get("reference_department")

        cursor.execute(f"""
        UPDATE students
        SET name={PARAM},phone1={PARAM},phone2={PARAM},phone3={PARAM},
        course={PARAM},place={PARAM},school={PARAM},busnumber={PARAM},
        reference={PARAM},reference_department={PARAM}
        WHERE id={PARAM}
        """,
        (name,phone1,phone2,phone3,course,place,
        school,busnumber,reference,reference_department,id))

        conn.commit()
        conn.close()

        return redirect("/dashboard")

    cursor.execute(f"SELECT * FROM students WHERE id={PARAM}", (id,))
    student = cursor.fetchone()

    conn.close()

    return render_template("edit.html", student=student)


# -----------------------------
# EXPORT EXCEL
# -----------------------------

@app.route("/export")
def export():

    conn = get_db()

    df = pd.read_sql_query("SELECT * FROM students", conn)

    file = "students.xlsx"
    df.to_excel(file, index=False)

    conn.close()

    return send_file(file, as_attachment=True)


# -----------------------------
# RESET DATABASE
# -----------------------------

@app.route("/reset-db")
def reset_db():

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM students")

    conn.commit()
    conn.close()

    return redirect("/dashboard")


# -----------------------------
# LOGOUT
# -----------------------------

@app.route("/logout")
def logout():

    session.clear()
    return redirect("/")


# -----------------------------
# RUN SERVER
# -----------------------------

if __name__ == "__main__":
    app.run(debug=True)