#!/usr/bin/python3
import cgi
import bcrypt
import sys
import os
import traceback
from db_config import get_connection
from utils import html_header, html_footer, create_session_cookie_value, SESSION_COOKIE_NAME


def main():
  form = cgi.FieldStorage()
  username = form.getvalue('username')
  password = form.getvalue('password')

  if not username or not password:
    html_header()
    print("<h3>Missing credentials</h3>")
    html_footer()
    return

  db = None
  cursor = None
  try:
    db = get_connection()
    cursor = db.cursor()

    cursor.execute(
      """
      SELECT lecturer_id, password
      FROM lecturer
      WHERE first_name = %s
      """,
      (username,)
    )

    row = cursor.fetchone()

    if not row:
      html_header()
      print("<h3>Invalid ID</h3>")
      html_footer()
      return

    user_db_id, hashed_pw = row

    # Ensure types are bytes for bcrypt
    if isinstance(hashed_pw, str):
      hashed_pw_bytes = hashed_pw.encode('utf-8')
    else:
      hashed_pw_bytes = hashed_pw

    password_bytes = password.encode('utf-8')

    if bcrypt.checkpw(password_bytes, hashed_pw_bytes):
      # create session cookie value
      cookie_val, max_age = create_session_cookie_value(str(user_db_id))
      # Redirect to the lecturer portal
      target = f"/public/lecturer_portal.html"
      print("Status: 303 See Other")
      print(f"Location: {target}")
      # set cookie before printing the blank line that ends headers
      print(f"Set-Cookie: {SESSION_COOKIE_NAME}={cookie_val}; HttpOnly; Path=/; Max-Age={max_age}")
      print("Content-Type: text/html")
      print()
      print("<html><head>")
      print(f"  <meta http-equiv=\"refresh\" content=\"0;url={target}\">")
      print("</head><body>")
      print("</body></html>")
      return
    else:
      html_header()
      print("<h3>Incorrect Password</h3>")
      html_footer()
      return

  except Exception as e:
    # Avoid exposing internal errors to most users; show a full traceback when DEBUG_CGI=1
    debug = os.environ.get('DEBUG_CGI') == '1'
    html_header()
    print("<h3>Server error. Please try again later.</h3>")
    if debug:
      print("<pre>")
      print(traceback.format_exc())
      print("</pre>")
    else:
      # keep a compact comment with the exception message for minimal diagnostics
      print(f"<!-- Error: {e} -->")
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