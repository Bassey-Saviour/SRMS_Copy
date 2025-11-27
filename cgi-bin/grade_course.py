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
                max-width: 1000px;       
            }

            table {
                width: 100%;
                background: white;
                margin: 20px 0;
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
                font-weight: bold;
            }
            
            input[type="number"],
            input[type="text"],
            select {
                width: 90%;
                padding: 6px;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-family: 'Roboto Slab', serif;
                -webkit-appearance: none;
                -moz-appearance: none;
                appearance: none;
                box-sizing: border-box;
                font-size: 0.95rem;
            }
            
            button[type="submit"] {
                border: none;
                font-family: "Roboto Slab", serif;
            }
        </style>
        <script>
            function getGradeFromScore(score) {
                score = parseInt(score);
                if (isNaN(score)) return '';
                if (score >= 80) return 'A';
                if (score >= 60) return 'B';
                if (score >= 50) return 'C';
                if (score >= 45) return 'D';
                if (score >= 40) return 'E';
                if (score >= 0) return 'F';

                return '';
            }

            function autoFillGrade(resultId) {
                const scoreInput = document.querySelector(`input[name="score_${resultId}"]`);
                const gradeInput = document.querySelector(`input[name="grade_${resultId}"]`);
                
                if (scoreInput && gradeInput) {
                    // If score is empty or cleared, clear the grade
                    if (!scoreInput.value || scoreInput.value.trim() === '') {
                        gradeInput.value = '';
                    } else {
                        const grade = getGradeFromScore(scoreInput.value);
                        if (grade) {
                            gradeInput.value = grade;
                        } else {
                            gradeInput.value = '';
                        }
                    }
                }
            }

            window.addEventListener('DOMContentLoaded', function() {
                const scoreInputs = document.querySelectorAll('input[type="number"][name*="score_"]');
                scoreInputs.forEach(input => {
                    input.addEventListener('change', function() {
                        const resultId = this.name.replace('score_', '');
                        autoFillGrade(resultId);
                    });
                    input.addEventListener('input', function() {
                        const resultId = this.name.replace('score_', '');
                        autoFillGrade(resultId);
                    });
                });
            });
        </script>
    </head>
    <body>
    <img src="/public/images/image-removebg-preview.png" class="bg-img" alt="">
    <div class="container">
    """)

def print_footer():
    print("</div></body></html>")

def main():
    # Get lecturer ID from session
    lec_id = get_session_student_id()

    if not lec_id:
        print_header()
        print("<div class='card'><h3>Not authenticated. Please <a href='/public/index.html'>log in</a>.</h3></div>")
        print_footer()
        exit()

    form = cgi.FieldStorage()
    course_id = form.getvalue("course_id")

    db = None
    cursor = None

    try:
        db = get_connection()
        cursor = db.cursor()

        # Verify course belongs to this lecturer
        cursor.execute(
            "SELECT course_code, course_title FROM course WHERE course_id = %s AND lecturer_id = %s",
            (course_id, lec_id)
        )
        course_row = cursor.fetchone()
        
        if not course_row:
            print_header()
            print("<div class='card'><h3>Course not found or unauthorized</h3></div>")
            print_footer()
            exit()
        
        course_code, course_title = course_row

        # Get all students enrolled in this course
        cursor.execute("""
            SELECT 
                s.student_id,
                s.matric_no,
                s.first_name,
                s.last_name,
                r.result_id,
                r.score,
                r.grade
            FROM student s
            JOIN result r ON s.student_id = r.student_id
            WHERE r.course_id = %s
            ORDER BY s.matric_no
        """, (course_id,))

        rows = cursor.fetchall()

        print_header()
        print(f"""
        <div class="card">
            <h2>{course_code}: {course_title}</h2>
            <p><a href="/public/lecturer_courses.html" class='menu-btn'>&#8678 Back to Courses
            <img src="/public/images/corner.png" width="15px" height="15px" alt="">
        <img src="/public/images/corner.png" width="15px" height="15px" alt="">
        </a></p>
        </div>
        """)

        if not rows:
            print("<div class='card'><h2>No students enrolled in this course.</h2></div>")
        else:
            print("""
            <div class="card">
                <form method="POST" action="/cgi-bin/submit_grades.py">
            """)
            print(f'<input type="hidden" name="course_id" value="{course_id}">')
            
            # Add hidden field with all result IDs so we know which ones to update
            result_ids = [str(row[4]) for row in rows]
            print(f'<input type="hidden" name="result_ids" value="{",".join(result_ids)}">')
            
            print("""
                    <table>
                        <thead>
                            <tr>
                                <th>Matric No</th>
                                <th>Student Name</th>
                                <th>Score</th>
                                <th>Grade</th>
                            </tr>
                        </thead>
                        <tbody>
            """)

            for row in rows:
                student_id, matric, fname, lname, result_id, score, grade = row
                score_val = score if score is not None else ""
                grade_val = grade if grade is not None else ""
                
                print(f"""
                            <tr>
                                <td>{matric}</td>
                                <td>{fname} {lname}</td>
                                <td>
                                    <input type="hidden" name="student_id_{result_id}" value="{student_id}">
                                    <input type="hidden" name="result_id_{result_id}" value="{result_id}">
                                    <input type="number" name="score_{result_id}" value="{score_val}" 
                                    min="0" max="100">
                                </td>
                                <td>
                                    <input type="text" name="grade_{result_id}" value="{grade_val}" readonly>
                                </td>
                            </tr>
                """)

            print("""
                        </tbody>
                    </table>
                    
                    <button type="submit" class="menu-btn submit-btn">Submit Grades
                        <img src="/public/images/corner.png" width="15px" height="15px" alt="">
                        <img src="/public/images/corner.png" width="15px" height="15px" alt="">
                    </button>
                </form>
            </div>
            """)

        print_footer()

    except Exception as e:
        debug = os.environ.get('DEBUG_CGI') == '1'
        print_header()
        print(f"<div class='card'><h3>Server error: {str(e)}</h3>")
        if debug:
            print("<pre>")
            print(traceback.format_exc())
            print("</pre>")
        print("</div>")
        print_footer()

    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()

if __name__ == "__main__":
    main()
