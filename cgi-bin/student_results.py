#!/usr/bin/python3

import cgi
import traceback
from db_config import get_connection
from utils import get_session_student_id


def print_header():
    print("Content-Type: text/html\n")
    print("""
    <html>
    <head>
        <title>Student Results</title>
        <link rel="icon" type="image/png" href="/public/images/results-icon-png-17974-removebg-preview.png"">
        <link rel=" preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Roboto+Slab:wght@100..900&family=Science+Gothic:wght@100..900&display=swap" rel="stylesheet">
        <link href="https://fonts.googleapis.com/css2?family=Stack+Sans+Notch:wght@200..700&display=swap" rel="stylesheet">
        <link rel="stylesheet" href="/public/css/student_portal.css">
        <style>
            body {
                font-family: 'Roboto Slab', serif;
            }

            .container {
                width: 90%;
                max-width: 900px;
                margin: auto;
                padding-top: 40px;
            }

            table {
                width: 100%;
                background: white;
                margin-top: 15px;
            }

            th, td {
                padding: 12px;
                border: 1px solid #ccc;
                border-radius: 6px;
                text-align: left;
            }
            th {
                background: #1b4965;
                color: white;
            }
        </style>
    </head>
    <body>
    <img src="/public/images/image-removebg-preview.png" class="bg-img" alt="">
    <div class="container">
    """)

def print_footer():
    print("</div></body></html>")

def main():
    form = cgi.FieldStorage()
    student_id = form.getvalue("student_id")

    # prefer session cookie over URL param
    if not student_id:
        student_id = get_session_student_id()

    print_header()

    if not student_id:
        print("<div class='card'><h3>No student specified</h3></div>")
        print_footer()
        return

    try:
        db = get_connection()
        cursor = db.cursor()

        # Student info
        cursor.execute("""
            SELECT s.first_name, s.last_name, s.matric_no, s.level, d.department_name
            FROM student s
            JOIN department d ON s.department_id = d.department_id
            WHERE s.student_id = %s
        """, (student_id,))
        srow = cursor.fetchone()

        if not srow:
            print("<div class='card'><h3>Student not found</h3></div>")
            print_footer()
            return

        first_name, last_name, matric_no, level, department_name = srow

        print(f"""
        <div class="card">
            <h2>Results for {first_name} {last_name}</h2>
            <p><strong>Matric Number:</strong> {matric_no}</p>
            <p><strong>Department:</strong> {department_name}</p>
            <p><strong>Level:</strong> {level}</p>
        </div>
        """)

        # Results
        cursor.execute("""
            SELECT c.course_code, c.course_title, c.credit_units, r.score, r.grade
            FROM result r
            JOIN course c ON r.course_id = c.course_id
            WHERE r.student_id = %s
        """, (student_id,))
        results = cursor.fetchall()

        print("<div class='card'>")
        print("<h2>Course Results</h2>")

        if not results:
            print("<p>No results uploaded yet.</p>")
        else:
            print("""
            <table>
                <tr>
                    <th>Course Code</th>
                    <th>Course Title</th>
                    <th>Units</th>
                    <th>Score</th>
                    <th>Grade</th>
                </tr>

                
            """)

            for code, title, credit_units, score, grade in results:
                print(f"""
                <tr>
                    <td>{code}</td>
                    <td>{title}</td>
                    <td>{credit_units}</td>
                    <td>{score}</td>
                    <td>{grade}</td>
                </tr>
                """)

            print("</table>")

        print("</div>")

        # Back button to student portal (portal will use session)
        print(f"""
        <a class='menu-btn res' href="/public/student_portal.html">
        &#8678 Back to Dashboard
        <img src="/public/images/corner.png" width="15px" height="15px" alt="">
        <img src="/public/images/corner.png" width="15px" height="15px" alt="">
        </a>
        """)

    except Exception as e:
        print(f"<div class='card'><h3>Error: {e}</h3></div>")

    print_footer()

if __name__ == "__main__":
    main()
