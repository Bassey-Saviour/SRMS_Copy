#!/usr/bin/python3
# -*- coding: utf-8 -*-
import cgi
import traceback
import os
from db_config import get_connection
from utils import get_session_student_id


def print_header():
    print("Content-Type: text/html\n")
    print("""
    <html>
    <head>
        <title>Transcript</title>
        <link rel="icon" type="image/png" href="/public/images/results-icon-png-17974-removebg-preview.png">
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Roboto+Slab:wght@100..900&family=Science+Gothic:wght@100..900&display=swap" rel="stylesheet">
        <link rel="stylesheet" href="/public/css/student_portal.css">
        <style>
            body { font-family: 'Roboto Slab', serif; }
            .container { 
                max-width: 1000px; 
                padding-top: 30px; 
            }
            
            table {
                width: 100%;
                background: white;
                margin: 12px 0;
            }

            th, td { 
                padding: 10px; 
                border: 1px solid #ccc;
                border-radius: 6px; 
                text-align: left 
            }
          
            th { 
                background: #1b4965; 
                color: white;
                font-weight: bold;
            }
          
            .summary { 
                margin-top: 1rem; 
                padding: 1rem; 
                background: #f7f7f7; 
                border-radius: 6px 
            }
          
            .small { 
                font-size: 0.9rem; 
                color: #555 
            }

            .watermark {
                position: fixed;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                opacity: 0.08;
                z-index: -1;
                pointer-events: none;
            }

            .watermark img {
                width: 500px;
            }

            .branding {
                display: flex;
                align-items: center;
                gap: 20px;
                margin-bottom: 25px;
                padding-bottom: 20px;
                border-bottom: 2px solid #ccc;
            }

            .brand-logo {
                width: 90px;
                height: 90px;
            }

            .brand-text h1 {
                margin: 0;
                font-size: 28px;
                color: #1a73e8;
                font-weight: bold;
            }

            .brand-text p {
                margin: 5px 0 0 0;
                font-size: 1rem;
                color: #333;
            }

            .print-btn {
                border: none;
                cursor: pointer; 
                font-family: "Roboto Slab", serif;
            }

            @media print {
                .menu-btn { display: none; }
                body { background: white !important; }
                .watermark img { opacity: 0.05; }
                .card { box-shadow: none; padding: 10px; margin: 0; border: none;}
                th, td {
                font-size: 12pt;}
                .container { width: 100%; padding: 10px; }
            }
        </style>
    </head>
    <body>
    <div class="watermark">
        <img src="/public/images/results-icon-png-17974-removebg-preview-black.png">
    </div>
    
    <div class="container">
    <div class="branding card">
        <img src="/public/images/results-icon-png-17974-removebg-preview-black.png" class="brand-logo">
        <div class="brand-text">
            <h1>Babcock University</h1>
            <p><strong>Official Academic Transcript</strong></p>
        </div>
    </div>
    """)


def print_footer():
    print("</div></body></html>")


GRADE_POINTS = {
    'A': 5,
    'B': 4,
    'C': 3,
    'D': 2,
    'E': 1,
    'F': 0,
}


def main():
    form = cgi.FieldStorage()
    student_id = form.getvalue('student_id')

    # prefer session cookie
    if not student_id:
        student_id = get_session_student_id()

    print_header()

    if not student_id:
        print("<div class='card'><h3>No student specified. Please log in.</h3></div>")
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

        first_name, last_name, matric_no, level, department = srow

        # Results with course info and lecturer
        cursor.execute("""
            SELECT c.course_code, c.course_title, c.credit_units, r.score, r.grade, 
                   CONCAT(l.first_name, ' ', l.last_name) as lecturer_name
            FROM result r
            JOIN course c ON r.course_id = c.course_id
            JOIN lecturer l ON c.lecturer_id = l.lecturer_id
            WHERE r.student_id = %s
            ORDER BY c.course_code
        """, (student_id,))
        rows = cursor.fetchall()

        print(f"""
            <div class='card'>
                <h2>Transcript — {first_name} {last_name}</h2>""")
        print(f"""<p class='small'><strong>Matric No:</strong> {matric_no} &nbsp; 
                    <strong>Dept:</strong> {department} &nbsp; 
                    <strong>Level:</strong> {level}</p>""")
        print("</div>")

        if not rows:
            print("<div class='card'><p>No results available.</p></div>")
            print_footer()
            return

        # Table header
        print("<div class='card'>")
        print("<h3>Course Records</h3>")
        print("<table>")
        print("""<thead>
                    <tr>
                    <th>Course Code</th>
                    <th>Course Title</th>
                    <th>Lecturer</th>
                    <th>Units</th>
                    <th>Score</th>
                    <th>Grade</th>
                    <th>Points</th>
                    </tr>
                </thead>""")
        print("<tbody>")

        total_units = 0
        total_weighted_points = 0
        graded_count = 0

        for code, title, units, score, grade, lecturer_name in rows:
            grade_display = grade if grade is not None else ''
            gp = None
            if grade_display:
                gp = GRADE_POINTS.get(grade_display.upper())
                if gp is not None:
                    total_units += units
                    total_weighted_points += gp * units
                    graded_count += 1

            gp_display = str(gp) if gp is not None else ''
            score_display = score if score is not None else ''
            print(f"""<tr>
                        <td>{code}</td>
                        <td>{title}</td>
                        <td>{lecturer_name}</td>
                        <td>{units}</td>
                        <td>{score_display}</td>
                        <td>{grade_display}</td>
                        <td>{gp_display}</td>
                    </tr>""")

        print("</tbody></table>")

        # GPA computation
        if total_units > 0:
            gpa = total_weighted_points / total_units
            gpa_str = f"{gpa:.2f}"
        else:
            gpa_str = 'N/A'

        print(f"<div class='summary'><p><strong>Total Units (graded):</strong> {total_units}</p>")
        print(f"<p><strong>GPA:</strong> {gpa_str}</p></div>")

        print("</div>")

        # Notes about scale
        print("<p class='small'>Grade to points mapping: A=5, B=4, C=3, D=2, E=1, F=0. GPA is weighted by course units.</p>")

        # Registrar signature section
        print("""
        <div class="card" style="margin-top: 2rem;">
            <h3>Registrar's Office</h3>
            <p>Date Issued: <strong id="dateIssued"></strong></p>
            <div style="margin-top: 40px;">
                <p>_____________________________</p>
                <p><strong>Registrar</strong></p>
            </div>
        </div>
        <script>
            document.getElementById("dateIssued").textContent =
                new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });
        </script>
        """)

        print(f"""
            <a class='menu-btn' href="/public/student_portal.html">
                &#8678 Back to Dashboard
                <img src="/public/images/corner.png" width="15px" height="15px" alt="">
                <img src="/public/images/corner.png" width="15px" height="15px" alt="">
            </a>
        """)

        # Print button
        print("""
        <div style="float: right;">
            <button type="button" class="menu-btn print-btn" onclick="window.print()">Print Transcript
                <img src="/public/images/corner.png" width="15px" height="15px" alt="">
                <img src="/public/images/corner.png" width="15px" height="15px" alt="">
            </button>
        </div>""")

    except Exception as e:
        debug = os.environ.get('DEBUG_CGI') == '1'
        print("<div class='card'><h3>Server error</h3>")
        if debug:
            print("<pre>")
            print(traceback.format_exc())
            print("</pre>")
        print("</div>")

    finally:
        try:
            if cursor:
                cursor.close()
            if db:
                db.close()
        except Exception:
            pass

    print_footer()


if __name__ == '__main__':
    main()
