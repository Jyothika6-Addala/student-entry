from flask import Flask, render_template, request, redirect, session, send_file, flash
import sqlite3
from datetime import datetime
import pandas as pd

app = Flask(__name__)
app.secret_key = "secretkey"

DATABASE = "students.db"


# -----------------------------
# Create Database Table
# -----------------------------
def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

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
# Login Page
# -----------------------------
@app.route("/", methods=["GET","POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        if username == "student" and password == "123":
            return redirect("/form")

        else:
            flash("Invalid Login")

    return render_template("login.html")


# -----------------------------
# Student Registration
# -----------------------------
@app.route("/form", methods=["GET","POST"])
def form():

    if request.method == "POST":

        name = request.form["name"]
        phone1 = request.form["phone1"]
        phone2 = request.form["phone2"]
        phone3 = request.form["phone3"]
        hallticket = request.form["hallticket"]
        course = request.form["course"]
        place = request.form["place"]
        school = request.form["school"]
        busnumber = request.form["busnumber"]
        reference = request.form["reference"]
        reference_department = request.form["reference_department"]

        now = datetime.now()
        date = now.strftime("%d-%m-%Y")
        time = now.strftime("%H:%M:%S")

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        # Check duplicate hallticket
        cursor.execute("SELECT 1 FROM students WHERE hallticket=?", (hallticket,))
        exists = cursor.fetchone()

        if exists:
            conn.close()
            flash("Hallticket number is already entered")
            return redirect("/form")

        try:
            cursor.execute("""
            INSERT INTO students
            (name, phone1, phone2, phone3, hallticket, course, place, school,
            busnumber, reference, reference_department, date, time)

            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            (name, phone1, phone2, phone3, hallticket, course, place,
             school, busnumber, reference, reference_department, date, time))

            conn.commit()

        except sqlite3.IntegrityError:
            flash("Hallticket number is already entered")

        conn.close()

        flash("Student Registered Successfully")

        return redirect("/form")

    return render_template("index.html")


# -----------------------------
# Hallticket Live Check
# -----------------------------
@app.route("/check-hallticket", methods=["POST"])
def check_hallticket():

    hallticket = request.form["hallticket"]

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM students WHERE hallticket=?", (hallticket,))
    data = cursor.fetchone()

    conn.close()

    if data:
        return {"exists": True}
    else:
        return {"exists": False}


# -----------------------------
# Admin Login
# -----------------------------
@app.route("/admin-login", methods=["GET","POST"])
def admin_login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        if username == "admin" and password == "admin123":
            session["admin"] = True
            return redirect("/dashboard")

        else:
            flash("Invalid Login")

    return render_template("admin_login.html")


# -----------------------------
# Dashboard
# -----------------------------
@app.route("/dashboard")
def dashboard():

    if "admin" not in session:
        return redirect("/admin-login")

    search = request.args.get("search")

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    if search:
        cursor.execute("SELECT * FROM students WHERE hallticket=?", (search,))
    else:
        cursor.execute("SELECT * FROM students")

    students = cursor.fetchall()
    conn.close()

    return render_template("admin.html", students=students)


# -----------------------------
# Edit Student
# -----------------------------
@app.route("/edit/<int:id>", methods=["GET","POST"])
def edit(id):

    if "admin" not in session:
        return redirect("/admin-login")

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    if request.method == "POST":

        name = request.form["name"]
        phone1 = request.form["phone1"]
        phone2 = request.form["phone2"]
        phone3 = request.form["phone3"]
        course = request.form["course"]
        place = request.form["place"]
        school = request.form["school"]
        busnumber = request.form["busnumber"]
        reference = request.form["reference"]
        reference_department = request.form["reference_department"]

        cursor.execute("""
        UPDATE students
        SET name=?, phone1=?, phone2=?, phone3=?, course=?, place=?, school=?, busnumber=?, reference=?, reference_department=?
        WHERE id=?
        """,
        (name, phone1, phone2, phone3, course, place,
         school, busnumber, reference, reference_department, id))

        conn.commit()
        conn.close()

        flash("Student Updated Successfully")

        return redirect("/dashboard")

    cursor.execute("SELECT * FROM students WHERE id=?", (id,))
    student = cursor.fetchone()

    conn.close()

    return render_template("edit.html", student=student)


# -----------------------------
# Export Excel
# -----------------------------
@app.route("/export")
def export():

    if "admin" not in session:
        return redirect("/admin-login")

    conn = sqlite3.connect(DATABASE)

    df = pd.read_sql_query("SELECT * FROM students", conn)

    file = "students.xlsx"
    df.to_excel(file, index=False)

    conn.close()

    return send_file(file, as_attachment=True)


# -----------------------------
# Logout
# -----------------------------
@app.route("/logout")
def logout():

    session.clear()
    return redirect("/")


# -----------------------------
# Run Server
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)