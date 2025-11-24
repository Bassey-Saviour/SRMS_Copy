#!/usr/bin/python3
import cgi
import bcrypt
import os
import traceback
from db_config import get_connection
from utils import (
    html_header,
    html_footer,
    create_session_cookie_value,
    SESSION_COOKIE_NAME,
)


def main():
    form = cgi.FieldStorage()
    # Support either a role parameter or implicit detection by fields
    role = (form.getvalue('role') or '').lower()
    # student uses `matric_no`, lecturer uses `username` (first_name)
    matric_no = form.getvalue('matric_no')
    username = form.getvalue('username')
    password = form.getvalue('password')

    # Determine role if not provided
    if not role:
        if matric_no:
            role = 'student'
        elif username:
            role = 'lecturer'

    if role == 'student':
        identifier = matric_no
        id_col = 'student_id'
        table = 'student'
        where = 'matric_no'
        redirect = '/public/student_portal.html'
        missing_msg = 'Missing credentials (matric_no/password)'
    elif role == 'lecturer':
        identifier = username
        id_col = 'lecturer_id'
        table = 'lecturer'
        # currently your lecturer login matches on first_name; consider using username/email
        where = 'first_name'
        redirect = '/public/lecturer_portal.html'
        missing_msg = 'Missing credentials (username/password)'
    else:
        html_header()
        print('<h3>Unknown role</h3>')
        html_footer()
        return

    if not identifier or not password:
        html_header()
        print(f"<h3>{missing_msg}</h3>")
        html_footer()
        return

    db = None
    cursor = None
    try:
        db = get_connection()
        cursor = db.cursor()

        # parameterized query
        cursor.execute(
            f"SELECT {id_col}, password FROM {table} WHERE {where} = %s",
            (identifier,),
        )
        row = cursor.fetchone()

        if not row:
            html_header()
            print("<h3>Invalid credentials</h3>")
            html_footer()
            return

        user_db_id, hashed_pw = row

        if isinstance(hashed_pw, str):
            hashed_pw_bytes = hashed_pw.encode('utf-8')
        else:
            hashed_pw_bytes = hashed_pw

        password_bytes = password.encode('utf-8')



        if bcrypt.checkpw(password_bytes, hashed_pw_bytes):
            cookie_val, max_age = create_session_cookie_value(str(user_db_id))
            print('Status: 303 See Other')
            print(f'Location: {redirect}')
            print(f'Set-Cookie: {SESSION_COOKIE_NAME}={cookie_val}; HttpOnly; Path=/; Max-Age={max_age}')
            print('Content-Type: text/html')
            print()
            print('<html><head>')
            print(f'  <meta http-equiv="refresh" content="0;url={redirect}">')
            print('</head><body>')
            print('</body></html>')
            return
        else:
            html_header()
            print('<h3>Incorrect Password</h3>')
            html_footer()
            return

    except Exception as e:
        debug = os.environ.get('DEBUG_CGI') == '1'
        html_header()
        print('<h3>Server error. Please try again later.</h3>')
        if debug:
            print('<pre>')
            print(traceback.format_exc())
            print('</pre>')
        else:
            print(f'<!-- {e} -->')
        html_footer()
    finally:
        if cursor:
            try:
                cursor.close()
            except Exception:
                pass
        if db:
            try:
                db.close()
            except Exception:
                pass


if __name__ == '__main__':
    main()