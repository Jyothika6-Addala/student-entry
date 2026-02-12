from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

# Create database table
def init_db():
    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            roll TEXT NOT NULL,
            course TEXT NOT NULL,
            email TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        name = request.form["name"]
        roll = request.form["roll"]
        course = request.form["course"]
        email = request.form["email"]

        conn = sqlite3.connect("students.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO students (name, roll, course, email) VALUES (?, ?, ?, ?)",
                       (name, roll, course, email))
        conn.commit()
        conn.close()

        return redirect("/")

    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()
    conn.close()

    return render_template("index.html", students=students)

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
