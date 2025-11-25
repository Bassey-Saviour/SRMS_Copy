#!/usr/bin/python3
import cgi
import json
from db_config import get_connection
from utils import get_session_student_id

print("Content-Type: application/json\n")

form = cgi.FieldStorage()
lec_id = form.getvalue("id")

# Prefer session-based lecturer_id; fall back to URL param
if not lec_id:
    lec_id = get_session_student_id()

if not lec_id:
    print(json.dumps({"error": "Lecturer ID missing"}))
    exit()

db = None
cursor = None

try:
    db = get_connection()
    cursor = db.cursor()

    cursor.execute("""
        SELECT l.first_name, l.last_name, l.lecturer_id, d.department_name
        FROM lecturer l
        JOIN department d ON l.department_id = d.department_id
        WHERE l.lecturer_id = %s
    """, (lec_id,))

    row = cursor.fetchone()

    if not row:
        print(json.dumps({"error": "Lecturer not found"}))
    else:
        first_name, last_name, lecturer_id, department = row
        print(json.dumps({
            "first_name": first_name,
            "last_name": last_name,
            "lecturer_id": lecturer_id,
            "department": department
        }))

except Exception as e:
    print(json.dumps({"error": "Server error", "details": str(e)}))

finally:
    if cursor:
        cursor.close()
    if db:
        db.close()
