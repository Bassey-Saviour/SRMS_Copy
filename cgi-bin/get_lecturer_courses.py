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

db = None
cursor = None

try:
    db = get_connection()
    cursor = db.cursor()

    # Get all courses for this lecturer
    cursor.execute("""
        SELECT course_id, course_code, course_title, credit_units
        FROM course
        WHERE lecturer_id = %s
        ORDER BY course_code
    """, (lec_id,))

    rows = cursor.fetchall()
    courses = []
    for row in rows:
        course_id, code, title, credits = row
        courses.append({
            "course_id": course_id,
            "course_code": code,
            "course_title": title,
            "credit_units": credits
        })

    print(json.dumps({"courses": courses}))

except Exception as e:
    print(json.dumps({"error": "Server error", "details": str(e)}))

finally:
    if cursor:
        cursor.close()
    if db:
        db.close()
