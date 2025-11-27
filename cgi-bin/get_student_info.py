#!/usr/bin/python3
import cgi
import json
from db_config import get_connection
from utils import get_session_student_id

def main():
    print("Content-Type: application/json\n")

    form = cgi.FieldStorage()
    student_id = form.getvalue('id')

    # If no id provided in query, try session cookie
    if not student_id:
        student_id = get_session_student_id()

    if not student_id:
        print(json.dumps({"error": "Missing student_id"}))
        return

    db = None
    cursor = None
    try:
        db = get_connection()
        cursor = db.cursor()

        # Fetch student details including department name
        cursor.execute("""
            SELECT s.first_name, s.last_name, s.matric_no, s.level, d.department_name
            FROM student s
            JOIN department d ON s.department_id = d.department_id
            WHERE s.student_id = %s
        """, (student_id,))

        row = cursor.fetchone()

        if not row:
            print(json.dumps({"error": "Student not found"}))
            return

        first_name, last_name, matric_no, level, department = row

        # Return data as JSON
        print(json.dumps({
            "first_name": first_name,
            "last_name": last_name,
            "matric_no": matric_no,
            "level": level,
            "department": department
        }))

    except Exception as e:
        print(json.dumps({"error": "Server error", "details": str(e)}))

    finally:
        if cursor:
            try: cursor.close()
            except: pass
        if db:
            try: db.close()
            except: pass

if __name__ == "__main__":
    main()
