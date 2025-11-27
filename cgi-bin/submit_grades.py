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
        <link rel="icon" type="image/png" href="/public/images/results-icon-png-17974-removebg-preview.png">
        <link rel=" preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Roboto+Slab:wght@100..900&family=Science+Gothic:wght@100..900&display=swap" rel="stylesheet">
        <link href="https://fonts.googleapis.com/css2?family=Stack+Sans+Notch:wght@200..700&display=swap" rel="stylesheet">
        <link rel="stylesheet" href="/public/css/student_portal.css">
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
        print("<h3>Not authenticated. Please <a href='/public/index.html'>log in</a>.</h3>")
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
            "SELECT course_id FROM course WHERE course_id = %s AND lecturer_id = %s",
            (course_id, lec_id)
        )
    
        if not cursor.fetchone():
            print_header()
            print("<h3>Course not found or unauthorized</h3>")
            print_footer()
            exit()

        # Collect all submitted grades
        # Parse form: score_<result_id>, grade_<result_id>
        result_ids_str = form.getvalue("result_ids", "")
        result_ids = [rid.strip() for rid in result_ids_str.split(",") if rid.strip()]
        
        updates = []
    
        for result_id in result_ids:
            score_val = form.getvalue(f"score_{result_id}", "")
            grade_val = form.getvalue(f"grade_{result_id}", "")
        
            # Convert empty string to NULL (None)
            score = int(score_val) if score_val and score_val.strip() else None
            grade = grade_val.strip().upper() if grade_val and grade_val.strip() else None
        
            updates.append((score, grade, result_id))

        # Update all results (verify result belongs to this course)
        updated_count = 0
        for score, grade, result_id in updates:
            cursor.execute(
                "UPDATE result SET score = %s, grade = %s WHERE result_id = %s AND course_id = %s",
                (score, grade, result_id, course_id)
            )
            updated_count += cursor.rowcount
    
        db.commit()

        print_header()
        # # Debug: show what was sent
        # debug_updates = []
        # for score, grade, result_id in updates:
        #     debug_updates.append(f"Result {result_id}: score={score}, grade={grade}")
        
        # html_header("Grades Submitted")
        print(f"""
        <div class="card">
            <h2>&#10004 Grades Submitted Successfully</h2>
            <p>Updated {updated_count} student record(s).</p>
                <a href="/public/lecturer_portal.html"       class="menu-btn">
                &#8678 Back to Portal
                <img src="/public/images/corner.png"    width="15px" height="15px" alt="">
                <img src="/public/images/corner.png" width="15px" height="15px" alt="">
                </a>
            </p>
        </div>
        """)
        print_footer()

    except Exception as e:
        print_header()
        print(f"<h3>Server error: {str(e)}</h3>")
        print_footer()

    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()

if __name__ == "__main__":
    main()