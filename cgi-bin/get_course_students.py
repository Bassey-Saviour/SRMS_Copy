#!/usr/bin/python3
import cgi
import json
from db_config import get_connection
from utils import get_session_student_id

print("Content-Type: application/json\n")

# Get lecturer ID from session
lec_id = get_session_student_id()

if not lec_id:
    print(json.dumps({"error": "Not authenticated"}))
    exit()

form = cgi.FieldStorage()
course_id = form.getvalue("course_id")

if not course_id:
    print(json.dumps({"error": "Course ID required"}))
    exit()

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
        print(json.dumps({"error": "Course not found or unauthorized"}))
        exit()
    
    course_code, course_title = course_row

    # Get all students enrolled in this course with their current scores
    cursor.execute("""
        SELECT 
            s.student_id,
            s.matric_no,
            s.first_name,
            s.last_name,
            r.score,
            r.grade
        FROM student s
        JOIN result r ON s.student_id = r.student_id
        WHERE r.course_id = %s
        ORDER BY s.matric_no
    """, (course_id,))

    rows = cursor.fetchall()
    students = []
    for row in rows:
        student_id, matric, fname, lname, score, grade = row
        students.append({
            "student_id": student_id,
            "matric_no": matric,
            "first_name": fname,
            "last_name": lname,
            "score": score,
            "grade": grade
        })

    print(json.dumps({
        "course_id": course_id,
        "course_code": course_code,
        "course_title": course_title,
        "students": students
    }))

except Exception as e:
    print(json.dumps({"error": "Server error", "details": str(e)}))

finally:
    if cursor:
        cursor.close()
    if db:
        db.close()
