from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

# -----------------------------
# Create Database Table
# -----------------------------
def init_db():
    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            phone TEXT,
            course TEXT,
            location TEXT,
            school TEXT,
            marks TEXT,
            facultyname TEXT
        )
    """)
    conn.commit()
    conn.close()


# -----------------------------
# Home Route
# -----------------------------
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        name = request.form["name"]
        phone = request.form["phone"]
        course = request.form["course"]
        location = request.form["location"]
        school = request.form["school"]
        marks = request.form["marks"]
        facultyname = request.form["facultyname"]

        conn = sqlite3.connect("students.db")
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO students 
            (name, phone, course, location, school, marks, facultyname)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (name, phone, course, location, school, marks, facultyname))

        conn.commit()
        conn.close()

        return redirect("/")

    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()
    conn.close()

    return render_template("index.html", students=students)


# -----------------------------
# Run App
# -----------------------------
if __name__ == "__main__":
    init_db()
    app.run(debug=True)
